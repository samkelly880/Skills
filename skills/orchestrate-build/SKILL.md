---
name: orchestrate-build
description: Orchestrate an entire numbered .plans/ workstream to completion, unattended. Reads a set of plan files (e.g. .plans/<prefix>-*.md) whose frontmatter declares prerequisites, creates one feature branch, then drives a prerequisite-gated build — launching each unblocked plan as its own background subagent that runs /implement and the full /pullrequest review loop in its own resident context (reviewers are nested subagents), self-merges its converged PR down to the feature branch with rebase-retry on conflict, and marks itself complete by ✓-renaming its own plan file. Newly-unblocked plans launch as their prerequisites finish. Use when the user says "/orchestrate-build", "orchestrate this build", "build out this workstream", "run all the plans", or points at a numbered plan series and wants it executed end-to-end without manual orchestration. Defaults to UNATTENDED mode — it never stops for input, decides every question itself from its own recommendation, and reports all decisions in the final report. Supports --base <branch> (feature-branch base), --attended (surface ambiguous decisions instead of auto-deciding), --max-parallel <n> (throttle concurrent plans; default uncapped — the prerequisite graph governs width), and --fast / --focused (forwarded to each /pullrequest).
argument-hint: "<overview-path-or-prefix> [--base <branch>] [--attended] [--max-parallel <n>] [--fast] [--focused]"
---

# orchestrate-build — drive a whole plan workstream to completion, unattended

## Purpose

Take a numbered series of plan files under `.plans/` (e.g. `customer-knowledge-00-overview.md`,
`customer-knowledge-01-…`, …) whose frontmatter declares `prerequisites:`, and execute the whole
workstream automatically:

1. Create **one feature branch** that every plan's PR merges into.
2. Loop: launch each plan whose prerequisites are all met as its **own background subagent**.
   Each subagent runs `/implement` → the full `/pullrequest` fresh-eyes review loop **in its own
   resident context**, then **squash-merges its converged PR** down to the feature branch and
   marks its plan complete.
3. As prerequisites finish, newly-unblocked plans launch — until everything reachable is done.
4. Report what was built, every decision made autonomously, and anything needing your attention.

**This runs UNATTENDED by default. No one is at the keyboard. NEVER stop for user input.** When a
question arises, decide it yourself from your own recommendation and record the decision for the
final report. The only exception is `--attended` (below), which re-enables three specific prompts.

## Why this architecture (load-bearing facts)

- **Nested subagents.** A subagent runs `/implement`, which chains into `/pullrequest`, which
  spawns **fresh-eyes reviewer subagents of its own** (nested). The agent that triages review
  findings **is** the agent that wrote the code — implementation rationale is preserved for free,
  with no handoff document and no context transfer. Requires Claude Code ≥ **v2.1.172**.
- **Resident context = the author self-merges.** Because the implementing subagent stays resident
  through its whole review loop, it still holds full context when it merges — so most merge conflicts
  are **resolved by the agent that wrote the code**. Only genuinely semantically ambiguous conflicts
  escalate to `needs-human` (blocking that plan's dependents, not the whole build).
- **The orchestrator (this skill) is read-only on shared branches.** It never edits code, never
  commits to `main` or the feature branch. It only: schedules plans, launches subagents, reads
  their structured results, and writes the final report. All code + completion-marking happens
  inside the per-plan subagents and lands via their PR merges.

## Usage
```
/orchestrate-build <overview-path-or-prefix> [--base <branch>] [--attended] [--max-parallel <n>] [--fast] [--focused]
```

## Arguments
- `<overview-path-or-prefix>` — **required**. Either a path to the workstream's overview plan
  (`.plans/<prefix>-00-overview.md`) or the bare `<prefix>`. Used to glob `.plans/<prefix>-*.md`.
- `--base <branch>` — base branch for the feature branch. Default `main`; if absent, fall back to
  the overview's `base:` frontmatter. (Some workstreams build off an integration branch.)
- `--attended` — opt back into surfacing the **three** genuinely-ambiguous decisions to the user
  (critical-finding cap, implementation-appears-wrong, semantically-ambiguous conflict). Everything
  else is still decided automatically.
- `--max-parallel <n>` — cap the number of concurrently-running plan subagents. **Default:
  uncapped** — the prerequisite graph already bounds width. Use only to protect local resources
  (parallel dep-installs / test runs) or API rate limits.
- `--fast` / `--focused` — forwarded verbatim to every `/pullrequest` (review-round caps / scope).

If `<prefix>` is missing, ask the user **before** the loop starts — never guess. Once the loop is
running, never ask (unless `--attended`, and then only the three decision points).

## Step 0 — Preflight (fail fast, before any branch is created)

- **Version gate.** Run `claude --version`. If `< 2.1.172`, **abort** with a clear message: nested
  subagents are unavailable, so a plan subagent cannot run its own `/pullrequest` review loop and
  the whole model collapses. Do not attempt a degraded fallback.
- **Forge + auth.** Detect the forge from `origin` (github.com → `gh`, else Forgejo `fgj`). Confirm
  it is authenticated; if not, stop and tell the user how to log in.
- **Clean tree.** The main working tree must be clean. If not, stop and ask the user to commit/stash.

## Step 1 — Load the plan set

- Glob `.plans/<prefix>-*.md`. Parse YAML frontmatter for each.
- **Overview** = the plan with **no `build:` field** (typically `*-00-overview.md`). Read it
  **in full** — it is injected verbatim as shared context into every plan subagent.
- **Buildable plans** = every plan **with** a `build:` field (e.g. `build: /implement`). Honor that
  field as the build command (default `/implement` if a buildable plan omits it but is clearly a
  stage). Skip any plan whose `status:` is not ready/blank if a status convention is present.
- Build the **dependency graph** from each plan's `prerequisites:` list (bare basenames, no `.md`,
  no `✓`). A plan is **unblocked** when every prerequisite is `complete`.
- Treat a plan as already `complete` if its file is already `✓`-prefixed on disk (resumability).

## Step 2 — Create the feature branch

- `git fetch origin --quiet`.
- Resolve `BASE` = `--base` value, else overview `base:`, else `main`.
- If `feature/<prefix>` already exists on `origin` (a prior run created it), check it out and
  fast-forward to the remote tip. Otherwise create it off `origin/$BASE` and push:
  `git push -u origin feature/<prefix>`.
- This is the integration branch. Every plan PR targets it. **The orchestrator never commits to it.**
- Record `state.json` under `.claude/orchestrate-build/<prefix>/` (optional, for resumability /
  mid-run visibility): the plan graph and each plan's status. The on-disk `✓` files remain the
  source of truth.

## Step 3 — Scheduling loop (event-driven)

```
in_flight = {}                      # plan -> running subagent task
loop:
  ready = { p in buildable | p not started, not complete, not blocked,
            and every prereq of p is complete }
  if --max-parallel: ready = take(ready, max_parallel - len(in_flight))
  for p in ready:
      launch L1 subagent for p   (Agent tool, isolation:"worktree", run_in_background:true)
      in_flight[p] = task
  if in_flight is empty and ready is empty:
      break                        # nothing running, nothing launchable -> done
  wait for ANY in_flight subagent to return        # event-driven, not polling
  record its structured result; remove from in_flight
  on  status == merged       -> mark p complete
  on  status in {failed, needs-human} -> mark p that status; CASCADE-BLOCK all
                                          transitive dependents as skipped-blocked
  # recompute on next loop iteration
```

- **Launch mechanics:** use the **Agent tool** with `isolation: "worktree"` (each plan gets its own
  isolated checkout so parallel builds never collide) and `run_in_background: true` (so the
  orchestrator is re-invoked on each completion and can launch newly-unblocked plans immediately).
- **Cascade-block** is transitive: if A fails and B requires A and C requires B, both B and C
  become `skipped-blocked`. Keep building everything still reachable.
- **Never** halt the whole loop because one plan failed. Isolate the failure to its dependents.

## Step 4 — The per-plan subagent (prompt template)

The subagent prompt is **self-contained** — it carries the overview context and everything the
subagent needs; it must not depend on the orchestrator's conversation. Template:

```
You are implementing ONE plan in an automated, UNATTENDED workstream build. No one is available
to answer questions — make every decision yourself and report it in your final summary.

You are in an isolated git worktree. The integration branch is `feature/<prefix>` on origin.

## Shared workstream context (read first)
<full text of the overview plan>

## Your plan
Path: <plan-path>
<you will read this file in full before starting>

## Do exactly this
1. Read your plan file end-to-end. Honor the locked decisions in the shared context above.
2. Create your branch off the integration branch:
       git fetch origin feature/<prefix> --quiet
       git checkout -b feature/<plan-slug> origin/feature/<prefix>
3. Run:  <build-command, default /implement> <plan-path> --base feature/<prefix> \
            [--fast|--focused as forwarded] --no-notification
   This implements the plan, commits, opens a PR into feature/<prefix>, and drives the
   /pullrequest fresh-eyes review loop to termination using your OWN nested review subagents.
4. Read the /pullrequest termination signal — the last line of its reply is a machine-readable
   token: `PR-STATUS: <CONVERGED|CAPPED>@round=<K> outstanding=<crit>/<impr>/<nit> deadlocks=<n>`.
   - CONVERGED, or CAPPED with crit==0 (only 🟡/🟢 outstanding) -> go to step 5 (merge).
   - CAPPED with crit ≥ 1 (🔴 Critical still outstanding)        -> do NOT merge. Stop and return
     status=needs-human with the outstanding criticals.   [--attended: ask the user instead]
   - Implementation could not be completed / the plan appears wrong -> do NOT merge. Return
     status=failed with the reason.                        [--attended: ask the user instead]
5. Mark complete + merge (the proceed path):
   a. git mv .plans/<name>.md .plans/✓<name>.md
      git commit -m "mark <name> complete"
      git push
   b. <CLI> pr merge <num> --squash --delete-branch
   c. If the merge reports "not mergeable" (a sibling merged first and touched shared files):
        git fetch origin feature/<prefix> --quiet
        rebase your branch onto origin/feature/<prefix>, resolve conflicts using your full
        implementation context, push, and retry `<CLI> pr merge`. Repeat until merged.
      Only if a conflict is genuinely semantically ambiguous (you cannot confidently resolve it)
      -> return status=needs-human describing the conflict. This blocks only THIS plan.
6. Return ONLY a structured summary (this is the sole thing the orchestrator sees):
   {
     plan: "<name>",
     status: "merged" | "failed" | "needs-human",
     pr_url: "<url or empty>",
     rounds_to_converge: <int or null>,
     autonomous_decisions: ["<one line each — any judgement call you made>"],
     standing_deadlocks: ["<finding the reviewer and author disagreed on, for human review>"],
     conflicts_resolved: ["<file: one-line how you resolved it>"],
     notes: "<anything the build owner should know>"
   }

Do not reference any conversation outside this prompt.
```

- The `<plan-slug>` is a short kebab-case slug derived from the plan name.
- `--no-notification` is always passed so individual plans don't each ping; the orchestrator owns
  the single end-of-build report.

## Step 5 — Final report (chat reply)

When the loop drains, post one concise report:

**Per plan** (a row each): status (`merged` / `failed` / `needs-human` / `skipped-blocked`), PR
link, rounds-to-converge, autonomous decisions made, standing review deadlocks, conflicts
auto-resolved.

**Build summary:** counts by status; the feature branch name; and a one-line next step —
"Merge `feature/<prefix>` → `<base>` when satisfied" (the orchestrator does **not** do the final
merge to the base branch; that stays with you).

**⚠️ For your attention:** collect everything that needs a human — every `needs-human` and `failed`
plan with its reason, every `skipped-blocked` plan and what blocked it, every standing review
deadlock, and any non-trivial decision a subagent made autonomously that you might want to revisit.

If `--attended` was set, also note which (if any) decisions you escalated to the user and how they
were resolved.

## Guardrails

- **Unattended by default — never stop for input.** Decide from your own recommendation, record it,
  move on. `--attended` re-enables exactly three prompts (critical-cap, impl-appears-wrong,
  ambiguous-conflict); nothing else.
- **The orchestrator is read-only on shared branches.** Never edit code; never commit to `main` or
  `feature/<prefix>`. All code + completion-marking lands through per-plan PR merges.
- **One plan's failure never halts the build.** Cascade-block its dependents; keep building the rest.
- **Version gate is mandatory.** If `claude --version < 2.1.172`, abort at step 0 — there is no safe
  degraded mode (a non-nesting subagent cannot run its own review loop).
- **Don't re-derive completion from stale memory.** A plan is complete iff its subagent returned
  `merged` (or its file is already `✓`-prefixed). Recompute the unblocked set after every return.
- **Launch every plan subagent fresh** via the Agent tool (`isolation:"worktree"`,
  `run_in_background:true`). Never reuse a subagent across plans.
