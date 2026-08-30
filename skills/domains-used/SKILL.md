---
name: domains-used
description: >
  List all known hawk-geek / i.ynet.nz domains and what each is bound to in the
  system Caddyfile (/etc/caddy/Caddyfile): project, reverse_proxy port, static
  root, or free/empty. Use when the user runs /domains-used, or asks "what
  domains are in use", "which domains are free", "list my domains", "domain
  inventory", or "what's bound to hawk-geek".
---

# /domains-used — Domain inventory

Report which local/dev domains exist, what each is bound to (Caddy reverse proxy
or static root), and which are free.

## Sources of truth

1. **Known pool (inventory file)** — `~/.config/hawk-geek/known-domains.txt`
   - One hostname per line (`#` comments and blank lines ignored).
   - Seeded with the hawk-geek slots; **`/domain` appends here** whenever it binds a new domain.
   - Domains in this file but missing from the Caddyfile are **Free**.
2. **Live bindings** — `/etc/caddy/Caddyfile`
   - Actual reverse_proxy / file_server config.

Do not hardcode the domain list in this skill. Always read the inventory file.

## Invocation

`/domains-used`

No arguments required.

## Steps

1. **Load the known domain pool**
   ```bash
   INVENTORY="$HOME/.config/hawk-geek/known-domains.txt"
   mkdir -p "$(dirname "$INVENTORY")"
   if [ ! -f "$INVENTORY" ]; then
     printf '%s\n' \
       '# Known hawk-geek / i.ynet.nz domain inventory for /domains-used' \
       '# One hostname per line. /domain appends here when binding a new domain.' \
       'hawk-geek-rubix.i.ynet.nz' \
       'hawk-geek-app1.i.ynet.nz' \
       'hawk-geek-app2.i.ynet.nz' \
       'hawk-geek-app3.i.ynet.nz' \
       'hawk-geek-garden.i.ynet.nz' \
       'hawk-geek-warriors.i.ynet.nz' \
       > "$INVENTORY"
   fi
   grep -vE '^\s*(#|$)' "$INVENTORY"
   ```
   Store the resulting hostnames as `KNOWN_DOMAINS` (preserve file order).

2. **Read the live Caddyfile**
   ```bash
   cat /etc/caddy/Caddyfile
   ```
   Do not invent bindings. Parse only what is on disk.

3. **Parse site blocks**
   - A site block starts with one or more hostnames (comma-separated) followed by `{`.
   - Capture for each hostname:
     - `reverse_proxy` targets (`127.0.0.1:PORT` or similar)
     - `handle` path routes and their proxies (if multi-route)
     - `root * <path>` + `file_server` (static binding)
     - Any comment on the line above `reverse_proxy` / `root` (often names the project)
   - Hostnames that appear only as aliases on the same block share the same binding.

4. **Classify each inventory domain**
   - **In use** — present as a site address in the Caddyfile → report binding.
   - **Free / empty** — in the inventory but **not** present in the Caddyfile.

5. **Optional: enrich with listening state** (only if quick and useful)
   ```bash
   ss -ltnp 2>/dev/null | grep -E '127\.0\.0\.1:[0-9]+' || true
   ```
   Note which bound ports are actually listening vs down. Do not fail if `ss` is unavailable.

6. **Present the report** using this layout:

   ### Known domains

   | Domain | Status | Bound to |
   |--------|--------|----------|
   | `hawk-geek-garden.i.ynet.nz` | In use | Gardenbound — reverse_proxy `127.0.0.1:5176` |
   | `hawk-geek-app3.i.ynet.nz` | **Free** | — |

   One row per inventory domain (file order). For multi-route blocks, summarize all routes in the Bound-to cell.

   ### Free domains
   Bullet list of inventory domains with no Caddyfile site block.

   ### Other sites in Caddyfile
   Hostnames found in the Caddyfile that are **not** in the inventory (e.g. `hawk-geek.i.ynet.nz`, `t3-vm.i.ynet.nz`), with the same binding summary.
   Do not auto-add these to the inventory unless the user asks (or they run `/domain` on them).

   ### Summary
   - N in use / M free (inventory)
   - Optionally: which free domain to suggest for a new project

## Binding summary rules

- Prefer project names from Caddy comments when present (e.g. `# Gardenbound — ...`).
- Otherwise describe the config: `reverse_proxy 127.0.0.1:PORT` or `file_server root <path>`.
- Multi-handle blocks: list each path → backend briefly.
- Never mark a domain free if it appears as a site address (including comma-shared blocks).

## How the inventory grows

- `/domain <hostname>` registers the hostname into `~/.config/hawk-geek/known-domains.txt` after a successful Caddy reload.
- Manual edits to that file are fine (one hostname per line) if you want to track a free slot before binding it.
- Removing a line drops it from `/domains-used` (it may still appear under Other sites if still in the Caddyfile).

## Tools

- Shell: read inventory + `cat /etc/caddy/Caddyfile` (read-only for Caddy; no sudo needed for listing)
- Optional: `ss` for port liveness
- Do **not** edit the Caddyfile in this skill. Binding changes belong to `/domain`.
