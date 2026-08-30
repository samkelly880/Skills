---
name: setup-error-monitoring
description: Wire a project up to Zeald's self-hosted GlitchTip (Sentry-compatible) error monitoring at https://errors.12z.ai. Detects the project's platform and confirms a Sentry-protocol SDK exists (notifies and gives up if not), ensures the GlitchTip MCP is connected, walks the user through creating a GlitchTip project + supplying the DSN, hands the SDK integration to /implement, then verifies events flow end-to-end via the MCP. Trigger when the user says "set up error monitoring", "add Sentry", "add GlitchTip", "wire up error tracking", "/setup-error-monitoring", or asks to connect this app to errors.12z.ai.
---

# setup-error-monitoring

Connect the current project to Zeald's self-hosted **GlitchTip** instance at
**https://errors.12z.ai**. GlitchTip is Sentry-API-compatible, so any Sentry-protocol
SDK works against it — this skill detects the stack, gets a project + DSN set up, hands
the code integration to `/implement`, and proves errors arrive end-to-end.

## What this skill does and doesn't do

- It **does** detect the platform, ensure the GlitchTip MCP is connected, guide GlitchTip
  project creation, collect the DSN, delegate the SDK integration to `/implement`, and
  verify a test event lands.
- It **does not** write GlitchTip via the MCP (the MCP is read/triage-only — it cannot
  create a project or mint a DSN, which is why those two steps are manual), enable
  performance tracing by default, or change the GlitchTip server.

## Prerequisites

- The Claude Code CLI (`claude mcp ...` available) and `gh`/git for the eventual PR.
- Access to https://errors.12z.ai (you must be a member of the GlitchTip organization).

## Steps

### 1. Detect the platform and guard

Inspect the repo's manifests to determine the platform and framework:

| Platform | Detect from | Framework signals |
| --- | --- | --- |
| PHP | `composer.json` | `laravel/framework` → Laravel; `symfony/*` → Symfony; else vanilla |
| JS/Node | `package.json` | `next` → Next.js; `express`/server entry → Node; `react`/`vue`/`@angular/*` → browser SPA |
| Python | `requirements.txt`, `pyproject.toml`, `Pipfile` | `django` → Django; `flask` → Flask; `fastapi` → FastAPI; else plain |
| Perl | `cpanfile`, `Makefile.PL`, `dist.ini`, `*.pl`/`*.pm` | mod_perl / plain script |
| other | `go.mod`, `Gemfile`, `*.csproj`, … | use the dynamic fallback (step 5) |

Then apply the guards **before doing anything else**:

- **No Sentry-protocol SDK for this platform** → tell the user the detected platform and
  that no Sentry SDK exists for it, then **stop**. Do not proceed.
- **Already wired up** — the SDK dependency is already in the manifest **and** an
  `init`/handler call is present **and** a DSN is configured → report that error monitoring
  is already configured (name the file) and **stop**. This skill does not re-configure or
  "repair" an existing setup.
- **Multiple app targets** (e.g. a PHP backend + a JS frontend in one repo) → ask the user
  which target to instrument before continuing.

### 2. Ensure the GlitchTip MCP is connected

The MCP gives Claude read/triage access to GlitchTip (and powers step 6's verification).
Check whether a `glitchtip` server is configured for this project (`claude mcp list`, or a
`glitchtip` entry in `./.mcp.json`). If it's missing, add it at **project scope** so it's
committed and shared with the team:

```bash
claude mcp add --transport http -s project glitchtip https://errors.12z.ai/mcp
```

This writes a `glitchtip` HTTP server entry to `./.mcp.json`. The server uses OAuth
auto-discovery, so the user must authenticate on first use:

> Run `/mcp`, select **glitchtip**, and complete the browser authentication. You may need
> to start a new Claude Code session before the GlitchTip MCP tools become available.

The MCP auth isn't required to proceed — the verification in step 6 (and the optional
existing-project check below) needs it, but project creation and DSN entry do not — so
don't block on it.

### 3. Guide GlitchTip project creation

The Zeald organization slug is always **`zeald`** — don't ask for it. If the MCP is
authenticated, optionally call `list_projects` to check whether a project for this repo
already exists (offer to reuse it if so). Then hand the user the **exact** create-project
URL and the values to enter — GlitchTip's new-project form is a client-side Angular page
with no query-param prefill, so "pre-fill" means telling them precisely what to type:

> Create the project here: **https://errors.12z.ai/zeald/settings/projects/new**
> - **Name:** `<repo name>` (suggest the repository's name)
> - **Platform:** `<detected platform>` (e.g. *PHP · Laravel*, *Node.js*, *Python · Django*)

### 4. Collect the DSN

Ask the user to paste the DSN shown on the new project's setup page. Validate it looks
like `https://<key>@errors.12z.ai/<project-id>` — GlitchTip uses the modern secret-less DSN
format (a single public key, no `:<secret>` segment). If it points at a different host, stop
and ask them to re-copy it from this GlitchTip instance.

### 5. Integrate the SDK via `/implement`

Hand a precise brief to the `/implement` skill (it creates the branch, writes the code,
commits, and opens the PR). The brief must specify the **platform + framework**, the
**package** to add, **where the DSN lives** (per-framework convention — see below), the
**instrumentation scope** (capture unhandled errors/exceptions + tag `environment` and
`release`; tracing off / `tracesSampleRate` 0), and the **production-enablement
instructions** to surface in the PR description.

**DSN handling (all stacks):** never commit the DSN value. Store it via the framework's
env convention, read it at init, and add a placeholder to `.env.example`
(`SENTRY_DSN=` or the framework-specific key).

#### Curated recipes

**PHP**
- *Laravel* — `composer require sentry/sentry-laravel`; `php artisan sentry:publish --dsn=<DSN>`
  (creates `config/sentry.php`, adds `SENTRY_LARAVEL_DSN` to `.env`). Set
  `'environment' => env('APP_ENV')`, `'release' => env('SENTRY_RELEASE')`,
  `'traces_sample_rate' => 0` in `config/sentry.php`. On Laravel ≤10 the package captures
  unhandled exceptions automatically; on Laravel 11+ add `Integration::handles($exceptions)`
  inside `bootstrap/app.php`'s `->withExceptions(...)` closure. Convention: DSN in `.env` as
  `SENTRY_LARAVEL_DSN`.
- *Symfony* — `composer require sentry/sentry-symfony`; configure
  `config/packages/sentry.yaml` with `dsn: '%env(SENTRY_DSN)%'`. Convention: `SENTRY_DSN`.
- *Vanilla* — `composer require sentry/sentry`; `\Sentry\init([...])` with
  `'dsn' => $_ENV['SENTRY_DSN']` early in the bootstrap, before app code runs.

**JavaScript / Node**
- *Node/Express* — `npm i @sentry/node`; `Sentry.init({ dsn: process.env.SENTRY_DSN,
  environment: process.env.NODE_ENV, release: process.env.SENTRY_RELEASE,
  tracesSampleRate: 0 })` at the very top of the entry file (before other imports). For
  Express, register the SDK's error handler (`Sentry.setupExpressErrorHandler(app)` on v8).
- *Next.js* — `npx @sentry/wizard@latest -i nextjs` then set the DSN; the wizard scaffolds
  client/server/edge configs.
- *Browser SPA* — `@sentry/browser` (or the framework package). The DSN is a publishable
  key, but still source it from build-time env (`VITE_SENTRY_DSN`, `NEXT_PUBLIC_SENTRY_DSN`,
  etc.), never hardcode.

**Python**
- `sentry-sdk` (add to `requirements.txt`/`pyproject.toml`).
  `sentry_sdk.init(dsn=os.environ["SENTRY_DSN"], environment=..., release=...,
  traces_sample_rate=0, integrations=[...])`. *Django* → `DjangoIntegration()` in
  `settings.py`; *Flask*/*FastAPI* → the matching integration (often auto). Convention:
  `SENTRY_DSN` env var.

**Perl** *(community SDK — best-effort; verify especially carefully in step 6)*
- `Sentry::SDK` (preferred where available) — `Sentry::SDK::init({ dsn => $ENV{SENTRY_DSN},
  environment => ..., release => ..., traces_sample_rate => 0 })`, then
  `Sentry::SDK::capture_exception($err)` in error handling; or
- `Sentry::Raven` (widely used but archived in 2023) — `Sentry::Raven->new(sentry_dsn =>
  $ENV{SENTRY_DSN}, ...)` and wrap the app in `capture_errors`. Note `Sentry::Raven` may
  need attention for GlitchTip's modern (secret-less) DSN format. Convention: `SENTRY_DSN`.

#### Dynamic fallback (any other platform)

Confirm a Sentry-protocol SDK exists for the platform (check
https://glitchtip.com/sdkdocs/ and https://docs.sentry.io/platforms/). If none exists,
**give up** per step 1. Otherwise fetch the matching SDK's install + init docs and follow
them, sourcing the DSN from an env var, tagging `environment`/`release`, and keeping
tracing off.

#### Production-enablement instructions (always emit these in the PR)

Tell the user exactly how to turn it on outside local dev, matched to the DSN path chosen:
- Set the DSN env var (`SENTRY_LARAVEL_DSN`/`SENTRY_DSN`/the build-time key) in the
  production environment — hosting env vars, the container/`systemd` definition, or the CI
  secret store — not in committed files.
- For browser builds, set the build-time DSN var in the CI/build pipeline.
- Optionally set `SENTRY_RELEASE` (e.g. to the deploy's git SHA) in the deploy pipeline so
  errors are grouped by release.
- For Laravel, re-run `php artisan config:cache` after setting prod env.

### 6. Verify end-to-end

After `/implement` has integrated the SDK, prove the pipeline works:

1. Emit a deliberate **test error** using the stack's mechanism (e.g. Laravel
   `php artisan sentry:test`; Node a thrown error in a throwaway script; Python a captured
   `1/0`; Perl `capture_message`/`capture_exception`).
2. Poll the GlitchTip MCP (`list_issues` for the project, found via `list_projects`) for a
   few seconds — events take a moment to ingest.
3. On success, report the issue and link it. If nothing arrives, surface the likely cause
   (DSN wrong/host mismatch, SDK init not reached, network egress blocked) rather than
   claiming success.

## Notes / guardrails

- The GlitchTip MCP is **read/triage-only** — never assume it can create projects or DSNs.
- Treat the DSN as configuration, not a committed secret; `.env.example` gets a placeholder
  only.
- This skill gathers context and delegates code-writing to `/implement` — it does not write
  the integration itself, so the PR goes through the normal review loop.
- If detection is ambiguous or a stack has no env convention for the DSN, ask the user
  rather than guessing.
