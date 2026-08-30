---
name: impeccable
description: >
  Use Impeccable (https://github.com/pbakaus/impeccable) for frontend UI/UX work: design, redesign, critique, audit, polish, typography, layout, color, motion, accessibility/responsive checks, design-system consistency, and visual polish. Prefers the official Impeccable skill install + CLI (`npx impeccable`) rather than reinventing it. Use when the user runs /impeccable, or asks to review/improve UI/UX, polish a frontend, fix visual hierarchy/spacing/typography, redesign a component without changing functionality, make UI responsive, or run a visual/UX audit. Not for backend, database, API-only, game logic, or infrastructure work.
argument-hint: "[init|document|extract|shape|critique|audit|polish|bolder|quieter|distill|harden|onboard|animate|colorize|typeset|layout|delight|overdrive|clarify|adapt|optimize|live|craft|pin|hooks|doctor] [target]"
metadata:
  short-description: "Use Impeccable for UI/UX (official skill + CLI)"
---

# /impeccable — Impeccable UI/UX Integration (T3)

This skill teaches the agent how to **use upstream Impeccable** for frontend UI/UX. It does **not** reimplement Impeccable, fork it, or vendor its monorepo.

**Upstream (source of truth):** https://github.com/pbakaus/impeccable · docs: https://impeccable.style

Impeccable provides: **1 agent skill** (`/impeccable <command> <target>`), **23 commands**, **live browser iteration**, a **design hook**, and a **CLI detector** (61 deterministic rules). Install it into the harness; then run its commands.

## Hard rules

1. **Do not invent Impeccable commands.** Only use commands listed below (from upstream README / skill).
2. **Prefer the official install.** If the full upstream skill is present (`reference/` playbooks + `scripts/`), load and follow **that** skill’s `SKILL.md` and the one command playbook for the request. Do not paste or rewrite those playbooks here.
3. **Do not fork, modify upstream, or copy large amounts of Impeccable source** into T3.
4. **Frontend/UI only.** Refuse as the default path for backend, DB, API-only, unrelated debugging, game logic, or infra.
5. **Inspect before changing.** Understand current components/styles; apply targeted edits; preserve behavior; no blind redesign rewrites.
6. **Read-only vs mutating:** `audit` / `critique` / `detect` document issues — they do not auto-fix. Mutating commands (`polish`, `layout`, `typeset`, etc.) edit UI — require clear user intent for large/destructive scope.
7. Coordinate with `/accessibility-auditor` for deep a11y-only work if Impeccable isn’t installed; when Impeccable **is** available, prefer `/impeccable audit` + command follow-ups for design-system UI surfaces.

## Setup — consume existing Impeccable

### Detect install

Search (project then user), in order:

| Harness | Typical skill base |
|---------|--------------------|
| Grok | `<project>/.grok/skills/impeccable` then `~/.grok/skills/impeccable` |
| Claude | `<project>/.claude/skills/impeccable` then `~/.claude/skills/impeccable` |

**Full install signals:** `SKILL.md` plus `reference/` and `scripts/` (e.g. `scripts/context.mjs`, `scripts/detect.mjs`).

**Thin T3-only install:** this file alone, without upstream `reference/` / `scripts/` → treat as integration stub; install upstream before deep command work.

### Install (do not vendor the repo)

**Harness library caution:** If you install skills from the shared Skills git repo via bulk `rsync skills/ ~/.grok/skills/`, **exclude `impeccable/`** so you do not replace a full upstream Impeccable skill (with `reference/` + `scripts/`) with this thin T3 stub. Prefer project-scoped official install for playbooks.

From the **user’s project root** (preferred):

```bash
npx impeccable install --providers=grok,claude --scope=project
```

Or global harness install:

```bash
npx impeccable install --providers=grok,claude --scope=global
```

Grok plugin alternative (upstream docs):

```bash
grok plugin install pbakaus/impeccable#plugin --trust
```

Then reload skills if needed. Refresh with `npx impeccable update`.

**Coexistence note:** Upstream install writes an `impeccable` skill directory. If this T3 integration skill occupies the same path, prefer **project-scoped** official install (`--scope=project`) so playbooks live under the project, or run `npx impeccable update` / install with awareness that `--force` replaces an existing skill dir. Never `git submodule` the whole monorepo into T3 unless the user explicitly asks.

### Session bootstrap (official skill)

When the full skill is loaded, upstream Setup says: run once per session:

```bash
node <skill-base-dir>/scripts/context.mjs --target <path-or-route>
```

Keep cwd at the user project. Follow its directives. Then load **one** command playbook from `<skill-base-dir>/reference/<command>.md` before acting.

Also honor project artifacts when present: `PRODUCT.md`, `DESIGN.md`, `.impeccable/config.json`, `.impeccable/design.json`, `.impeccable/critique/*.md`.

## What Impeccable can do (honest capability map)

| Kind | What it does | How |
|------|----------------|-----|
| **Analyze** | UX critique (hierarchy, clarity, heuristics); technical audit (a11y, perf, responsive, theming, integrity); deterministic anti-pattern scan | `/impeccable critique`, `/impeccable audit`, `npx impeccable detect` |
| **Recommend** | Prioritized fixes mapped to follow-up commands; design direction; next-step menus | Critique/audit reports; `/impeccable` with no args (routing menu — **never auto-run**) |
| **Generate** | Design context (`PRODUCT.md` / `DESIGN.md`); design-system extraction; UX plans before code; optional comps when image gen available | `init`, `document`, `extract`, `shape`, `craft` (deprecated alias for new-work) |
| **Implement** | Agent applies UI edits under a command playbook (typography, layout, color, motion, polish, etc.) | Mutating commands below — **the agent** implements; Impeccable provides the playbook + detectors |

**Cannot:** replace product requirements, safely rewrite backend/APIs, guarantee “secure” or “done” from a green detect alone, or delete/rebuild large app surfaces without user intent.

## Commands (upstream — do not invent others)

Invoke as `/impeccable <command> [target]` (or natural language that clearly implies one command).

| Command | Category | Role |
|---------|----------|------|
| `init` | Build | Capture product/design context → `PRODUCT.md` (+ `DESIGN.md`) |
| `document` | Build | Generate `DESIGN.md` from existing code |
| `extract` | Build | Pull tokens/components into design system |
| `shape` | Build | Plan UX/UI **before** writing code |
| `craft` | Build | Deprecated alias for ordinary new-work |
| `critique` | Evaluate | UX design review (read-heavy; persists critique snapshot) |
| `audit` | Evaluate | Technical quality checks — **do not fix; document** |
| `polish` | Refine | Final pass / shipping readiness (often implements fixes) |
| `bolder` / `quieter` | Refine | Amplify or tone down visual intensity |
| `distill` | Refine | Strip to essence |
| `harden` | Refine | Errors, i18n, overflow, edge cases |
| `onboard` | Refine | First-run / empty states / activation |
| `animate` | Enhance | Purposeful motion |
| `colorize` | Enhance | Strategic color |
| `typeset` | Enhance | Fonts / type hierarchy |
| `layout` | Enhance | Spacing / rhythm / hierarchy |
| `delight` / `overdrive` | Enhance | Personality / ambitious effects |
| `clarify` | Fix | UX copy / labels / errors |
| `adapt` | Fix | Responsive / device adaptation |
| `optimize` | Fix | UI performance |
| `live` | Iterate | Browser visual variants (web) |
| `pin` / `unpin` | Meta | Standalone `/<command>` shortcuts via upstream `pin.mjs` |
| `hooks` | Meta | Design detector hook on/off/status/ignores |
| `doctor` | Meta | Repair/report Impeccable artifact drift |

No-argument `/impeccable` → show context-aware **menu** (upstream `routing.md`); **do not auto-run** a command.

## CLI (no LLM required for detect)

```bash
npx impeccable detect src/
npx impeccable detect index.html
npx impeccable detect --json .
npx impeccable ignores list
npx impeccable install | update | check | help
```

Use `detect` for cheap deterministic scans / CI-style signals. It is **not** a full substitute for `critique` or `audit`.

## When to invoke

**Yes:** dashboard UX review; make a settings page more professional; improve visual hierarchy; frontend a11y/responsive audit; redesign a component without changing functionality; better typography/spacing; polish before ship; brand/product UI craft.

**No (default):** backend, database, API implementation, general non-UI debugging, game logic, infrastructure/devops.

## Workflow (T3-safe)

1. Confirm UI/UX scope; reject or redirect non-UI tasks.
2. Detect/install Impeccable as above.
3. Run `context.mjs` when full skill is available.
4. Map the request → **one** command (ask once if two fit).
5. **Inspect** current UI code / tokens / DESIGN.md / PRODUCT.md.
6. If Evaluate (`audit`/`critique`) or `detect`: produce the report; recommend follow-up commands; **do not silently implement** unless the user asks to apply fixes.
7. If Build/Refine/Enhance/Fix: load the official playbook; implement **targeted** UI changes; preserve functionality.
8. Verify (smoke UI, re-`detect` / re-`audit` when useful).
9. Report what changed, what was only recommended, and residual risks.

### Existing-project safety

- Prefer surgical edits over rewrites.
- Do not delete components, replace large frontend areas, change routing/behavior, globally rewrite design-system primitives, or remove functionality **without explicit user intent** (confirm when ambiguous).
- Do not delete files “because a redesign would be cleaner.”
- Do not apply every recommendation blindly — prioritize P0/P1 and user-chosen scope.

### Visual quality lenses (when the active command covers them)

Hierarchy · typography · spacing · contrast · a11y · responsive · interaction/loading/error/empty states · consistency · reuse · density · affordances — only to the depth of the chosen Impeccable command/playbook.

## Intent → command cheatsheet

| User ask | Start with |
|----------|------------|
| “Review this dashboard’s UX” | `critique` |
| “Audit a11y / responsive / perf of this UI” | `audit` (+ optional `npx impeccable detect`) |
| “Make this look more professional / ship-ready” | `polish` (after critique/audit if none yet) |
| “Improve hierarchy / spacing” | `layout` |
| “Fix typography” | `typeset` |
| “Make it responsive” | `adapt` |
| “Add motion” | `animate` |
| “Too bland / too loud” | `bolder` / `quieter` |
| “Empty states / first-run” | `onboard` |
| “Plan before coding a new surface” | `shape` then build |
| “Set up design context” | `init` |
| “Capture DESIGN.md from code” | `document` |

## Output

```markdown
# Impeccable
## Install / skill base used
## Command(s) run
## Analyzed vs changed
## Findings (if audit/critique/detect)
## UI changes (if any)
## Suggested next /impeccable commands
## Residual risks / confirmations needed
```

