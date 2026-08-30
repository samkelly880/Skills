---
name: domain
description: >
  Connect the current project to the provided domain name by adding or updating
  a reverse_proxy site block in the system Caddyfile (/etc/caddy/Caddyfile).
  Use when the user runs /domain <domain_name>, asks to "point domain at this",
  "add caddy domain for project", "expose via domain", or similar.
argument-hint: <domain_name>[:port]
---

# /domain — Project to Domain via Caddy

Connect the **current working project** (git root or cwd) to a domain using Caddy reverse proxy. The Caddyfile lives at `/etc/caddy/Caddyfile` and uses `tls internal` for local certs.

## Invocation

`/domain <domain_name>`

- `<domain_name>` can be bare (e.g. `myapp.i.ynet.nz`) or include port hint (`myapp.i.ynet.nz:5173`).
- Optional port can also be discovered.

## Steps

1. **Parse arguments**
   - Extract the domain (strip any `:port` suffix if present).
   - If port was provided after `:`, capture it as `target_port`.
   - The remainder after `/domain ` is the full argument string.

2. **Find project root**
   ```bash
   git rev-parse --show-toplevel 2>/dev/null || pwd
   ```
   Store as `PROJECT_ROOT`. Use this as context for port guessing (look for configs relative to it).

3. **Determine target local port**
   - If port was supplied in the domain arg, use it.
   - Otherwise, attempt auto-detection (run these in order, stop at first confident hit):
     a. Look for PORT or dev server port in env files:
        ```bash
        grep -hE '^(PORT|VITE_PORT|DEV_PORT|APP_PORT)=' "$PROJECT_ROOT"/.env* 2>/dev/null | tail -1 | cut -d= -f2 | tr -d ' \r'
        ```
     b. Inspect common config files for explicit ports (vite, next, etc.):
        - `grep -oE 'port:\s*[0-9]+' "$PROJECT_ROOT"/vite.config.* "$PROJECT_ROOT"/next.config.* 2>/dev/null | ...`
        - Parse package.json:
          ```bash
          node -e '
            const p = require(process.argv[1]+"/package.json");
            const dev = (p.scripts && p.scripts.dev) || "";
            const m = dev.match(/--port[=\s]+(\d+)/) || dev.match(/ -p (\d+)/);
            if (m) console.log(m[1]);
          ' "$PROJECT_ROOT"
          ```
     c. Scan currently listening ports and pick a likely dev server (prefer high ports, localhost):
        ```bash
        ss -ltnp 2>/dev/null | awk '/LISTEN/ && /127.0.0.1|localhost/ {print}' | grep -E ':(3000|5173|5174|8000|8080|4000|9000|3773|1234)[^0-9]' || ss -ltnp 2>/dev/null | grep LISTEN
        ```
     d. Common fallbacks: 5173 (Vite), 3000 (Next/Create-React), 8000 (Python/FastAPI), 8080.

   - If no port found after detection, **ask the user**:
     "What port is the dev server for this project listening on? (default common: 5173, 3000, 8000)"

   Store final `target_port` (integer).

4. **Read and inspect current Caddyfile**
   ```bash
   cat /etc/caddy/Caddyfile
   ```
   - Check whether the exact `<domain_name>` (or a line containing it) already exists.
   - If it does, note the existing block and decide whether to replace or update the port.

5. **Build the site block**
   Use this template (match style of existing blocks):

   ```
   <domain_name> {
   	tls internal
   	reverse_proxy 127.0.0.1:<target_port>
   }
   ```

   For blocks that previously had header_up (e.g. the 3773 one), you may include if it matches pattern, but the simple form is sufficient and safe for most projects.

6. **Backup and update the Caddyfile (use sudo)**
   ```bash
   sudo cp /etc/caddy/Caddyfile "/etc/caddy/Caddyfile.bak.$(date +%s)"
   ```

   Append the block. Example using heredoc (run via shell):
   ```bash
   sudo tee -a /etc/caddy/Caddyfile > /dev/null << 'CADDYEOF'

   <domain_name> {
   	tls internal
   	reverse_proxy 127.0.0.1:<target_port>
   }
   CADDYEOF
   ```

   (Replace the placeholders in the actual command with real values.)

   Alternative (if you prefer full rewrite for cleanliness): read full file, append in memory, write back via `sudo bash -c 'cat > /etc/caddy/Caddyfile << "EOF" ... EOF'`.

7. **Validate and reload Caddy**
   ```bash
   sudo caddy fmt --overwrite /etc/caddy/Caddyfile
   sudo caddy reload --config /etc/caddy/Caddyfile
   ```
   Or if reload via service:
   ```bash
   sudo systemctl reload caddy
   ```

   Capture output. If reload fails, show the error and suggest `caddy validate --config /etc/caddy/Caddyfile`.

8. **Register domain in the /domains-used inventory**
   After a successful Caddy reload, ensure the bare hostname (no `:port`) is listed in the shared inventory so `/domains-used` will show it:

   ```bash
   INVENTORY="$HOME/.config/hawk-geek/known-domains.txt"
   mkdir -p "$(dirname "$INVENTORY")"
   touch "$INVENTORY"
   DOMAIN="<domain_name>"   # bare hostname only
   if ! grep -qxF "$DOMAIN" "$INVENTORY"; then
     echo "$DOMAIN" >> "$INVENTORY"
     echo "Registered $DOMAIN in domain inventory"
   fi
   ```

   - Path is always `~/.config/hawk-geek/known-domains.txt` (shared by Grok and Claude).
   - Idempotent: skip if already present.
   - Do this even when updating an existing Caddy block for that domain (first-time registration still matters).
   - Do **not** require sudo for the inventory file (user-owned).

9. **Verify and report**
   - Confirm the block is present: `grep -A 5 "<domain_name>" /etc/caddy/Caddyfile`
   - Tell the user:
     "✅ Connected project to domain.
      https://<domain_name>  →  http://127.0.0.1:<target_port>
      (tls internal cert — your browser may show a warning on first visit.)
      Caddy reloaded successfully.
      Domain registered in /domains-used inventory."

   - If the project needs a specific path prefix or handle blocks (like the existing hawk-geek-app1), mention that a simple reverse proxy was added and they can edit further if required.

## Edge Cases & Notes
- The Caddyfile requires root to edit. All write/reload steps must use `sudo`.
- Do not remove existing blocks unless the user explicitly asks to replace one for the same domain.
- Domains often follow the pattern `*.i.ynet.nz` in this environment — suggest similar if user provides a bare name.
- After reload, it may take a few seconds for TLS renewal messages (visible in `journalctl -u caddy -f`).
- The skill works from any chat/project because it is installed under `~/.grok/skills/`.
- Domain inventory for `/domains-used`: `~/.config/hawk-geek/known-domains.txt`. New binds must be appended there.

## Tools you are expected to use
- `run_terminal_command` (with `sudo` where needed for Caddyfile)
- `read_file` (only for project files to detect ports)
- Never use the `write` / `search_replace` tools directly on `/etc/caddy/Caddyfile` — shell + sudo is required.
