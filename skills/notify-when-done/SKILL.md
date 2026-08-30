---
name: notify-when-done
description: Post a Google Chat notification at the end of a task. Triggers when the user says "notify me when done", "ping me when finished", "send a chat when ready", asks for a webhook ping, or when another skill (e.g. /pullrequest) finishes. Reads the webhook URL from the GOOGLE_CHAT_WEBHOOK environment variable, then falls back to ~/.claude/.env or ~/.grok/.env, then the project .env only when TRUST_PROJECT_WEBHOOK=1. Use $ARGUMENTS as the message body if provided; otherwise compose a short summary of what was just done. Supports --optional flag to silently skip if webhook is not configured.
---

# notify-when-done

Send a concise completion notification to a Google Chat space via an incoming webhook.

## When to use
- The user explicitly asked to be notified at the end of this task.
- Another skill (typically `/pullrequest`) reaches its completion step.
- A long-running operation (PR review wait, CI watch, deploy) is wrapping up.

Do **not** invoke this skill mid-task, only when the work is genuinely done (or has hit a terminal failure that the user should know about).

## Flags

`--optional`: If specified, silently skip notification if `GOOGLE_CHAT_WEBHOOK` is not configured. Without this flag, missing webhook configuration stops and warns the user.

## Locating the webhook URL

Resolve in this order; use the first value that is non-empty:

1. `$GOOGLE_CHAT_WEBHOOK` from the current shell environment.
2. `GOOGLE_CHAT_WEBHOOK=...` line in `~/.claude/.env` or `~/.grok/.env`.
3. `GOOGLE_CHAT_WEBHOOK=...` line in the project `.env` (current working directory) **only if** `TRUST_PROJECT_WEBHOOK=1` is set in the environment.

If none of those is set:
- **With `--optional` flag**: silently exit without sending a notification.
- **Without `--optional` flag**: stop and tell the user the webhook isn't configured — don't fabricate or guess a URL, and don't reuse one from earlier in the conversation. Suggest they add `GOOGLE_CHAT_WEBHOOK=https://chat.googleapis.com/v1/spaces/...` to one of those files.

A one-liner that prints whichever it finds:

```bash
# Check for --optional flag
OPTIONAL=0
if [[ "$ARGUMENTS" == *"--optional"* ]]; then
  OPTIONAL=1
fi

get_webhook() {
  if [ -n "$GOOGLE_CHAT_WEBHOOK" ]; then printf '%s' "$GOOGLE_CHAT_WEBHOOK"; return 0; fi
  # Always allow user harness env files (Claude and/or Grok).
  files="$HOME/.claude/.env $HOME/.grok/.env"
  # Only read project .env when explicitly trusted (forks/clones can plant webhooks).
  if [ "${TRUST_PROJECT_WEBHOOK:-0}" = "1" ]; then
    files="$files $PWD/.env"
  fi
  for f in $files; do
    if [ -r "$f" ]; then
      v=$(grep -E '^[[:space:]]*GOOGLE_CHAT_WEBHOOK=' "$f" \
            | tail -n1 | sed -E 's/^[[:space:]]*GOOGLE_CHAT_WEBHOOK=//; s/^["'\'']//; s/["'\'']$//')
      [ -n "$v" ] && { printf '%s' "$v"; return 0; }
    fi
  done
  return 1
}

if ! WEBHOOK=$(get_webhook); then
  if [ "$OPTIONAL" -eq 1 ]; then
    exit 0
  else
    echo "GOOGLE_CHAT_WEBHOOK not set" >&2
    exit 2
  fi
fi

# Reject SSRF/metadata targets — only Google Chat incoming-webhook URLs are allowed.
validate_webhook() {
  case "$1" in
    https://chat.googleapis.com/*) return 0 ;;
    *) echo "GOOGLE_CHAT_WEBHOOK must be an https://chat.googleapis.com/... URL" >&2; return 1 ;;
  esac
}
validate_webhook "$WEBHOOK" || exit 2
```

In **untrusted clones** (forks, third-party repos), do not set `TRUST_PROJECT_WEBHOOK=1`. Prefer `~/.claude/.env` / `~/.grok/.env` / `$GOOGLE_CHAT_WEBHOOK` only unless the user explicitly confirms they trust that repo's `.env`.

## Composing the message

- First strip any `--optional` token from `$ARGUMENTS` so it doesn't leak into the message body.
- If the remaining `$ARGUMENTS` is non-empty, use it verbatim as the message (after stripping surrounding quotes).
- Otherwise, write a short summary of what just finished (one or two sentences, max). Include links to the PR/branch/commit if one was created in this session. Avoid emoji unless the user already used some in this conversation.

Keep it under ~600 chars — Google Chat truncates long messages awkwardly.

## Posting

Use `curl` to POST a JSON `{"text": "..."}` body. Properly escape the message — prefer `jq` to construct the JSON so embedded backticks/newlines/quotes are safe:

```bash
# WEBHOOK was resolved and passed validate_webhook above.
MSG="<your message here>"
BODY=$(jq -n --arg t "$MSG" '{text:$t}')
curl -sS -m 10 -H 'Content-Type: application/json' -d "$BODY" "$WEBHOOK" > /tmp/notify-resp.json
```

Check the HTTP status — if `curl` exits non-zero or the response isn't a JSON object containing `name` or `createTime`, surface that to the user rather than claiming success. Don't echo the webhook URL itself back to the conversation (treat it as a low-grade secret).

## When you're done

- If webhook was sent: print `Notification sent.`
- If `--optional` flag was used and webhook was not configured: exit silently with no output to the user.
- Otherwise: print the failure reason.

Do not narrate the curl invocation.
