---
name: monitor
description: Spin up a one-off, disposable HTML dashboard to monitor a large or long-running task, then keep it updated live with progress, findings, and results. When the task hits a problem needing complex human judgement, surface all the relevant data on the dashboard so a human (local or remote) can decide. Serves over a tiny local HTTP server; if localtunnel is installed it also exposes a public tunnel URL (otherwise prints install instructions); opens the URL with xdg-open when available; cleans everything up when the task finishes. Trigger when the user says "/monitor", "monitor this long task", "set up a progress dashboard", "create a live dashboard for this run", or "give me a dashboard to watch this".
---

# monitor

Spin up a **one-off, disposable dashboard** for a large or long-running task, then keep it
updated as the task runs. The dashboard shows live progress, findings, and results — and
when the task hits a problem that needs complex human judgement, it surfaces **all the
relevant data** for that decision so a human can answer (from the terminal, or remotely).

This skill is deliberately **general**. It does not lock you into one rendering. On the
first run you decide — based on the task — how best to surface the information, and you
keep that decision open as the task evolves.

## When to use

- A task that will run for a while (a big migration, a long audit, a multi-step build, a
  batch job) where the user wants to *watch* progress without staring at the terminal.
- A task someone may want to monitor **remotely** (the tunnel gives a public view-only URL;
  Remote Control gives an org-only steerable session).
- Any run where you anticipate hitting a decision that needs human input and want the full
  context laid out cleanly when you do.

Do **not** use it for short tasks that finish in a few tool calls — the setup/teardown
overhead isn't worth it.

## Core model

Everything lives in a dedicated dashboard directory **inside your session scratchpad** (the
scratchpad path is given in your system context). Nothing is written into the user's
project. The whole thing is disposable and torn down at the end.

The dashboard is **always served over a tiny local HTTP server**, never opened as a bare
`file://`. Two reasons: a `file://` page can't `fetch()` a sibling `state.json` (CORS), and
localtunnel needs a local port to expose anyway. One uniform path for both the local-only
and tunnelled cases.

### Pick a rendering approach (run-time decision)

On the first run, look at the task and choose how to surface its state. The skill ships a
solid default; deviate when the task warrants it.

- **Default — HTML shell + polled `state.json`.** Write `index.html` **once**; it polls a
  small `state.json` every couple of seconds and re-renders. Updates are then just cheap
  JSON writes — no markup regeneration, the browser refreshes itself, scroll position is
  preserved. Best for steady, structured progress (a timeline, findings, results, a
  progress bar). **Use this unless you have a reason not to.**
- **Bespoke — regenerate the HTML yourself.** If the data is rich, irregular, or benefits
  from a custom layout (charts, tables, diffs, grouped sections that change shape), skip
  `state.json` and re-author `index.html` periodically with a light `<meta http-equiv="refresh" content="5">`
  so the browser reloads. More tokens per update, but full presentational freedom.

You can also start with the default and switch to bespoke later if the task turns out to
need it. The point is: **you choose how best to surface the info**, the skill just gives you
the plumbing.

## Step 1 — Setup

1. **Create the dashboard dir** under your session scratchpad, e.g.
   `"$SCRATCHPAD/monitor-dashboard"` (use the actual scratchpad path from your context).
   Use one fixed dir for the whole task so the URL is stable.

2. **Decide the approach** (above) and write the initial files:
   - Default: write `index.html` (template in the appendix) and an initial `state.json`.
   - Bespoke: write a first `index.html` with a `<meta refresh>` and your own layout.

3. **Pick a free port and decide whether you'll tunnel.** The dashboard is always served
   over a loopback-bound server. If `localtunnel` is installed you'll *also* expose it
   publicly — and **a public tunnel must be password-protected**, so in that case the server
   enforces HTTP Basic Auth and the credentials are embedded in the handback URL
   (`https://user:password@host`). A loopback-only dashboard (no tunnel) needs no auth.

   ```bash
   DIR="$SCRATCHPAD/monitor-dashboard"   # served content (index.html, state.json)
   RUN="$SCRATCHPAD/monitor-run"         # operational files (auth script, pids, logs) — NOT served
   mkdir -p "$DIR" "$RUN"
   PORT=$(python3 -c 'import socket;s=socket.socket();s.bind(("127.0.0.1",0));print(s.getsockname()[1]);s.close()')
   command -v lt >/dev/null 2>&1 && TUNNEL=1 || TUNNEL=0
   ```

4. **Start the server** (loopback-bound either way), recording its PID for cleanup.

**If you'll tunnel (`TUNNEL=1`):** generate credentials and start a tiny **auth-enforcing**
server. Write `$RUN/authserver.py` (it lives in `$RUN`, which is never served) with exactly
this content — write it verbatim with **no leading indentation** (Python is
indentation-sensitive):

```python
import http.server, socketserver, base64, os
DIR  = os.environ["MON_DIR"]
PORT = int(os.environ["MON_PORT"])
TOKEN = "Basic " + base64.b64encode(
    (os.environ["MON_USER"] + ":" + os.environ["MON_PASS"]).encode()).decode()
class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=DIR, **k)
    def _authed(self):
        return self.headers.get("Authorization") == TOKEN
    def _challenge(self):
        self.send_response(401)
        self.send_header("WWW-Authenticate", 'Basic realm="monitor"')
        self.send_header("Content-Length", "0")
        self.end_headers()
    def do_GET(self):
        if self._authed(): super().do_GET()
        else: self._challenge()
    def do_HEAD(self):
        if self._authed(): super().do_HEAD()
        else: self._challenge()
    def log_message(self, *a):
        pass
class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
with Server(("127.0.0.1", PORT), Handler) as httpd:
    httpd.serve_forever()
```

Then start it (every request — local or tunnelled — must present the credentials, so the
public URL is safe to hand out):

```bash
USER=monitor
PASS=$(python3 -c 'import secrets;print(secrets.token_urlsafe(12))')   # URL-safe — no escaping needed
MON_DIR="$DIR" MON_PORT="$PORT" MON_USER="$USER" MON_PASS="$PASS" \
  nohup python3 "$RUN/authserver.py" >"$RUN/server.log" 2>&1 &
echo $! >"$RUN/server.pid"
LOCAL_URL="http://$USER:$PASS@localhost:$PORT/"
```

**If local-only (`TUNNEL=0`):** a plain loopback server is enough (not network-reachable, so
no auth needed):

```bash
nohup python3 -m http.server "$PORT" --bind 127.0.0.1 --directory "$DIR" >"$RUN/server.log" 2>&1 &
echo $! >"$RUN/server.pid"
LOCAL_URL="http://localhost:$PORT/"
```

   If `python3` is unavailable, fall back to a loopback-bound static server
   (`php -S "127.0.0.1:$PORT" -t "$DIR"` or `npx --yes http-server "$DIR" -p "$PORT" -a 127.0.0.1`).
   These have **no Basic Auth**, so do **not** tunnel them — keep them local-only. If no
   static server is available at all, tell the user and stop.

5. **Open the tunnel** (only when `TUNNEL=1`). Start localtunnel and build the authed URL:

   ```bash
   nohup lt --port "$PORT" >"$RUN/lt.log" 2>&1 &
   echo $! >"$RUN/lt.pid"
   # lt prints "your url is: https://xxxx.loca.lt" within ~1-3s; read it back
   # (retry with a fresh read if empty — issue it as a separate command, don't sleep):
   HOST=$(grep -oE 'https://[a-z0-9.-]+\.loca\.lt' "$RUN/lt.log" | head -1)
   PUBLIC_URL="https://$USER:$PASS@${HOST#https://}/"     # password-protected, safe to share
   echo "$PUBLIC_URL"
   ```

   The first browser visit may show localtunnel's interstitial asking for a password — that
   is the **public IP of this machine** (`curl -s https://loca.lt/mytunnelpassword` or
   `curl -s ifconfig.me`). It is localtunnel's own anti-abuse gate, **separate** from the
   Basic Auth above; surface the IP alongside the URL so the user can get past it.

   If localtunnel **isn't installed** (`TUNNEL=0`), there's no public URL — tell the user how
   to enable it next time:

   ```
   localtunnel isn't installed — the dashboard is local-only.
   To get a shareable (password-protected) public URL next time: npm install -g localtunnel
   ```

6. **Auto-open if possible.** If `command -v xdg-open` succeeds, open the local URL:
   `xdg-open "$LOCAL_URL" >/dev/null 2>&1 &`. When tunnelling, `$LOCAL_URL` already carries
   the Basic-Auth credentials, so the browser authenticates automatically. The public URL is
   for sharing; the local one is for the operator.

7. **Hand back** a concise block to the user:
   - **Local URL** — `$LOCAL_URL`.
   - **Public URL** — `$PUBLIC_URL` (password-protected; it embeds `user:password`, plus the
     interstitial-IP note) **or** the `npm install -g localtunnel` hint if it wasn't installed.
   - The Remote Control line, verbatim:
     > Run `/remote-control` to also control this session from the web at claude.ai/code.
   - The privacy warning (see below).

   Make clear the two remote channels are different: the **dashboard URL is public but
   password-protected and view-only**; **Remote Control is org-only and lets a viewer steer
   the session**.

## Step 2 — Keep it updated

As the monitored task runs, update the dashboard at every meaningful checkpoint — a step
completed, a finding discovered, a result produced, a status change.

- **Default approach:** rewrite `state.json` (overwrite the whole file; it's small). Always
  refresh the `updated` timestamp (`date -u +%FT%TZ` style) and `status`. Append to
  `timeline`; add to `findings` / `results`; update `progress`. See the schema in the
  appendix.
- **Bespoke approach:** regenerate `index.html`.

Keep updates frequent enough to be useful but don't spam — checkpoints, not every line.
Treat dashboard updates as a side-effect of doing the real work, never as the work itself.

## Step 3 — When you need complex human input

When the task hits a decision that genuinely needs a human (an ambiguous trade-off,
destructive choice, missing credential, conflicting data), **surface everything needed to
decide on the dashboard** and set `status` to `blocked`:

- Set `blocker` (default approach) — or render a prominent card (bespoke) — containing:
  - **question** — the decision to be made, in one sentence.
  - **context** — why this came up and what's at stake.
  - **options** — the concrete choices and their trade-offs.
  - **recommendation** — what you'd do and why (always give one).
  - **data** — the actual evidence: the conflicting values, the error, the diff, the rows —
    whatever a human needs to see to judge. This is the whole point; don't make them dig.
- The dashboard is **read-only** — it does not capture input. Direct the human to answer
  **in the Claude session**: locally in the terminal, or remotely via `/remote-control` →
  claude.ai/code. (This is exactly where the tunnel + Remote Control pairing pays off: you
  spot the blocker on the public dashboard from your phone, then use Remote Control to
  actually answer.)
- Then wait for their answer as you normally would. Once answered, clear the blocker, set
  `status` back to `running`, and continue.

## Step 4 — Cleanup

When the monitored task finishes (or fails):

1. Set a **final status** on the dashboard (`done` / `failed`) with a closing summary, so a
   late viewer sees the outcome. Give the user a moment to read it if they're watching.
2. **Tear down** the processes and files:

   ```bash
   DIR="$SCRATCHPAD/monitor-dashboard"; RUN="$SCRATCHPAD/monitor-run"
   for p in lt server; do
     [ -f "$RUN/$p.pid" ] && kill "$(cat "$RUN/$p.pid")" 2>/dev/null || true
   done
   rm -rf "$DIR" "$RUN"
   ```

3. Confirm cleanup in your handback.

The PID-based kill above covers both server types (plain `http.server` and the auth
server) since it kills the recorded PIDs. If the session dies abruptly before cleanup, the
background server and `lt` processes may leak (they're harmless, local). Tell the user they
can kill them by port with `fuser -k "$PORT/tcp"` (kills whatever is listening, regardless
of server type) and `pkill -f "lt --port $PORT"` (substituting the real port) if needed.

## Privacy & security

The local server binds to **loopback only** (`127.0.0.1`), so it is not reachable from the
LAN. The one deliberate public surface is the **localtunnel URL**, which is **protected by
HTTP Basic Auth** — only someone with the `user:password` link can open it (never tunnel a
no-auth fallback server). Still treat it as sensitive: **never surface secrets, credentials,
tokens, API keys, or customer PII on the dashboard**, since the authed URL can be shared or
logged. Keep operational files (the auth script, pids, logs) out of the served directory so
they can't be fetched over the tunnel (the setup above writes them to a separate run dir).
Redact or omit sensitive values; show enough to monitor and decide, no more. If a blocker
genuinely needs a secret to resolve, describe it ("the production DB password") rather than
printing it, and have the human supply it in the session, not on the dashboard.

---

## Appendix — default `state.json` schema

Overwrite this whole file on each update. `status` is one of `running`, `blocked`, `done`,
`failed`. `blocker` is `null` unless you need human input. `level` (on timeline/findings) is
one of `info`, `ok`, `warn`, `error` and just drives colour.

```json
{
  "title": "Short name of the task being monitored",
  "status": "running",
  "updated": "2026-06-26T14:32:10Z",
  "progress": { "label": "Step 3 of 8 — migrating sessions", "percent": 38 },
  "timeline": [
    { "time": "14:30:01", "text": "Started migration", "level": "info" },
    { "time": "14:31:40", "text": "Backed up 12,400 rows", "level": "ok" }
  ],
  "findings": [
    { "title": "Orphaned sessions", "detail": "318 rows reference deleted users", "level": "warn" }
  ],
  "results": [
    { "title": "Tables migrated", "detail": "6 of 9" }
  ],
  "blocker": null
}
```

A populated `blocker`:

```json
"blocker": {
  "question": "Drop the 318 orphaned sessions, or remap them to a placeholder user?",
  "context": "These rows reference user IDs deleted before the FK constraint existed. The migration can't proceed until they're resolved.",
  "options": ["Drop them (irreversible)", "Remap to user id 0 (keeps audit trail)"],
  "recommendation": "Remap to id 0 — preserves the audit trail and is reversible.",
  "data": "session ids: 4471, 4488, 4502, … (318 total); affected date range 2021-03 to 2021-08"
}
```

## Appendix — default `index.html`

Write this **once** at setup. It is self-contained (inline CSS/JS), responsive, polls
`state.json` every 2.5s, shows "stream ended" when the server goes away (e.g. after
cleanup), and reveals the blocker card only when one is present. Adjust freely.

```html
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Monitor</title>
<style>
  :root{--bg:#0d1117;--card:#161b22;--line:#30363d;--fg:#e6edf3;--mut:#8b949e;
    --ok:#3fb950;--warn:#d29922;--err:#f85149;--info:#58a6ff;--accent:#58a6ff}
  *{box-sizing:border-box}
  body{margin:0;background:var(--bg);color:var(--fg);
    font:15px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
  .wrap{max-width:1100px;margin:0 auto;padding:24px 20px 64px}
  header{display:flex;flex-wrap:wrap;align-items:center;gap:12px;margin-bottom:8px}
  h1{font-size:20px;margin:0;font-weight:600}
  .badge{font-size:12px;font-weight:600;padding:3px 10px;border-radius:999px;
    text-transform:uppercase;letter-spacing:.04em}
  .badge.running{background:#1f6feb33;color:var(--info)}
  .badge.blocked{background:#d2992233;color:var(--warn)}
  .badge.done{background:#3fb95033;color:var(--ok)}
  .badge.failed{background:#f8514933;color:var(--err)}
  .updated{color:var(--mut);font-size:13px;margin-left:auto}
  .updated.stale{color:var(--err)}
  .progress-label{color:var(--mut);font-size:13px;margin:14px 0 6px}
  .bar{height:8px;background:var(--card);border-radius:999px;overflow:hidden}
  .bar>i{display:block;height:100%;width:0;background:var(--accent);
    transition:width .4s ease}
  .grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));
    gap:16px;margin-top:22px}
  .card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:16px}
  .card h2{font-size:13px;text-transform:uppercase;letter-spacing:.05em;color:var(--mut);
    margin:0 0 12px}
  ul{list-style:none;margin:0;padding:0}
  li{padding:7px 0;border-bottom:1px solid var(--line);font-size:14px}
  li:last-child{border-bottom:0}
  li .t{color:var(--mut);font-variant-numeric:tabular-nums;margin-right:8px;font-size:12px}
  li.ok{border-left:3px solid var(--ok);padding-left:9px}
  li.warn{border-left:3px solid var(--warn);padding-left:9px}
  li.error{border-left:3px solid var(--err);padding-left:9px}
  li .d{color:var(--mut);display:block;font-size:13px}
  .empty{color:var(--mut);font-style:italic;font-size:13px}
  .blocker{background:#d299221a;border:1px solid var(--warn);border-radius:10px;
    padding:18px;margin-top:22px}
  .blocker h2{color:var(--warn);margin:0 0 10px;font-size:15px;text-transform:none;
    letter-spacing:0}
  .blocker .q{font-weight:600;font-size:16px;margin-bottom:10px}
  .blocker dt{color:var(--mut);font-size:12px;text-transform:uppercase;
    letter-spacing:.05em;margin-top:10px}
  .blocker dd{margin:4px 0 0}
  .blocker pre{background:#0d1117;border:1px solid var(--line);border-radius:6px;
    padding:10px;overflow-x:auto;font-size:13px;white-space:pre-wrap}
  .blocker .how{margin-top:12px;color:var(--fg);font-size:14px}
  footer{margin-top:32px;color:var(--mut);font-size:13px;border-top:1px solid var(--line);
    padding-top:16px}
  footer code{background:var(--card);padding:2px 6px;border-radius:4px}
  .warnline{color:var(--warn)}
</style>
</head>
<body>
<div class="wrap">
  <header>
    <h1 id="title">Monitor</h1>
    <span class="badge running" id="status">running</span>
    <span class="updated" id="updated">—</span>
  </header>

  <div id="progress-wrap" hidden>
    <div class="progress-label" id="progress-label"></div>
    <div class="bar"><i id="progress-bar"></i></div>
  </div>

  <div class="blocker" id="blocker" hidden>
    <h2>⚠ Needs your input</h2>
    <div class="q" id="b-question"></div>
    <dl>
      <dt>Context</dt><dd id="b-context"></dd>
      <dt>Options</dt><dd id="b-options"></dd>
      <dt>Recommendation</dt><dd id="b-rec"></dd>
      <dt>Data</dt><dd><pre id="b-data"></pre></dd>
    </dl>
    <div class="how">→ Respond in your Claude Code session (terminal), or remotely via
      <code>/remote-control</code> → claude.ai/code.</div>
  </div>

  <div class="grid">
    <div class="card"><h2>Timeline</h2><ul id="timeline"></ul></div>
    <div class="card"><h2>Findings</h2><ul id="findings"></ul></div>
    <div class="card"><h2>Results</h2><ul id="results"></ul></div>
  </div>

  <footer>
    <div>Run <code>/remote-control</code> to also control this session from the web at
      claude.ai/code.</div>
    <div class="warnline">This dashboard may be public — don't expect secrets or PII to
      be shown here.</div>
  </footer>
</div>

<script>
const $ = id => document.getElementById(id);
function row(item){
  const li = document.createElement('li');
  if(item.level) li.className = item.level;
  const time = item.time ? `<span class="t">${esc(item.time)}</span>` : '';
  const detail = item.detail ? `<span class="d">${esc(item.detail)}</span>` : '';
  li.innerHTML = `${time}${esc(item.title||item.text||'')}${detail}`;
  return li;
}
function esc(s){return String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));}
function fill(id, items){
  const ul = $(id); ul.innerHTML='';
  if(!items||!items.length){ul.innerHTML='<li class="empty">None yet</li>';return;}
  items.forEach(it=>ul.appendChild(row(it)));
}
async function tick(){
  try{
    const r = await fetch('state.json?_='+Date.now(),{cache:'no-store'});
    if(!r.ok) throw 0;
    const s = await r.json();
    document.title = (s.title||'Monitor');
    $('title').textContent = s.title||'Monitor';
    const st = (s.status||'running');
    $('status').textContent = st; $('status').className = 'badge '+st;
    if(s.updated){
      const ago = Math.round((Date.now()-new Date(s.updated).getTime())/1000);
      $('updated').textContent = 'updated '+(ago<2?'just now':ago+'s ago');
      $('updated').className = 'updated'+(ago>30?' stale':'');
    }
    if(s.progress){
      $('progress-wrap').hidden=false;
      $('progress-label').textContent = s.progress.label||'';
      $('progress-bar').style.width = (s.progress.percent||0)+'%';
    } else $('progress-wrap').hidden=true;
    const b = s.blocker;
    if(b){
      $('blocker').hidden=false;
      $('b-question').textContent=b.question||'';
      $('b-context').textContent=b.context||'';
      $('b-options').textContent=(b.options||[]).join('  •  ');
      $('b-rec').textContent=b.recommendation||'';
      $('b-data').textContent=b.data||'';
    } else $('blocker').hidden=true;
    fill('timeline', s.timeline);
    fill('findings', s.findings);
    fill('results', s.results);
  }catch(e){
    $('updated').textContent='stream ended';
    $('updated').className='updated stale';
  }
}
tick(); setInterval(tick, 2500);
</script>
</body>
</html>
```
