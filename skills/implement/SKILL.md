---
name: implement
description: Implement a plan end-to-end — create a branch, write the code, commit, then hand off to /pullrequest for review. Use when the user says "/implement", "implement this", "ship it", or "implement and PR it". Accepts an optional plan as argument (e.g. a path to a spec under .plans/); otherwise uses the plan from the current conversation. Supports --fast, --parallel, --persist, --base <branch>, and --no-notification (forwarded to /pullrequest).
argument-hint: "[plan description or path to spec] [--fast] [--parallel] [--persist] [--base <branch>] [--no-notification]"
---

# implement — branch, code, commit, PR

## Steps

1. **Resolve the plan & flags.** If a path arg is given, that's the plan; otherwise use the thread plan. If neither exists, stop and ask. Parse `--fast`, `--parallel`, `--persist`, `--base <branch>`, `--no-notification`. If `--parallel` is set without a clean tree, ask the user to commit or stash before proceeding.

2. **If `--parallel`:**
   - Capture `MAIN_ROOT=$(git rev-parse --show-toplevel)` and `CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)`.
   - Derive a `<slug>` from the plan/feature name (short kebab-case).
   - **Determine the base branch:**
     - If `--base <branch>` given: run `git fetch origin --quiet`, set `BASE_BRANCH=<branch>`.
     - Otherwise: set `BASE_BRANCH=$CURRENT_BRANCH`.
   - Ensure `.claude/worktrees/` is in `.gitignore` (add if missing).
   - Create and enter the worktree:
     - With `--base`: `git worktree add .claude/worktrees/<slug> -b feature/<slug> origin/$BASE_BRANCH`
     - Without `--base`: `git worktree add .claude/worktrees/<slug> -b feature/<slug>` (creates from local HEAD)
   - **Install dependencies:** after entering the worktree, copy env files (`cp -a "$MAIN_ROOT"/.env* . 2>/dev/null`), then install deps by lockfile (pnpm-lock.yaml → `pnpm install --frozen-lockfile`, package-lock.json → `npm ci`, yarn.lock → `yarn install --immutable`, bun.lockb → `bun install`, else `npm install`).
   - Continue work in the worktree in-session (no `cd` back to MAIN_ROOT until cleanup).

3. **If NOT `--parallel`:**
   - Check the tree is clean. If there are uncommitted changes, stop and ask the user how to handle them. Do not auto-stash.
   - **Determine the base.** If `--base <branch>` was given, run `git fetch origin --quiet` and branch off `origin/<branch>` (the remote tip, not local HEAD). Otherwise branch off the current base (usually `main`).
   - **Create a branch.** Prefix with `feature/` for new functionality or `fix/` for bug fixes — pick based on the plan; if genuinely ambiguous, ask. Then a short kebab-case slug from the plan (e.g. `feature/add-rate-limiter`, `fix/null-deref-in-login`). With `--base`: `git checkout -b feature/<slug> origin/<branch>`.

4. **Implement.** Make the changes. Run tests/typecheck/lint if the project has them. Keep iterating until green before moving on — do not open a PR on broken code.

5. **Commit.** One commit per logical unit; don't bundle unrelated changes. Commit messages must be **code-only** (what changed in the tree). Never put personal/operator data in messages (Atlas memory, todos, open threads, chat, model/provider, settings, secrets). Don't push — `/pullrequest` handles that.

6. **Push and create PR.** 
   - If `--parallel`:
     - Ensure `BASE_BRANCH` exists on origin (if it's the current branch and unpushed, run `git push origin "$BASE_BRANCH"`).
     - Push the worktree branch: `git push -u origin HEAD`.
     - Create the PR targeting `BASE_BRANCH` with an explicit title/body derived from the **git range only** (not chat/Atlas/todos/status). Prefer `gh pr create --base "$BASE_BRANCH" --title "…" --body "…"`. Avoid bare `--fill` if commit messages might contain non-code context; if you use `--fill`, re-read the created PR body and edit out any personal data.
   - If NOT `--parallel`:
     - Hand off to `/pullrequest` skill with the new branch as `<from_branch>`. If `--base <branch>` was given, pass it as `<to_branch>` so the PR targets that branch; otherwise `/pullrequest` targets `main` by default. `/pullrequest` enforces the same **Privacy** rule (no personal data on the PR).
   - Forward `--fast` to `/pullrequest` if set. Forward `--no-notification` to `/pullrequest` if it was passed to `/implement` (e.g. `/build` always passes it so the outer skill can own the single final notification — avoids a double ping).

7. **Cleanup (if `--parallel`).**
   - Only proceed after push AND PR creation both succeed.
   - If `--persist` was NOT passed:
     - `cd "$MAIN_ROOT"` (must cd back — a session can't remove the worktree it's in).
     - `git worktree remove --force .claude/worktrees/<slug>`.
     - Keep the local branch (do not delete it).
   - If `--persist` was passed:
     - Print the worktree path and the command to test it locally (e.g. `cd .claude/worktrees/<slug> && npm test`).
     - Leave the worktree in place with deps pre-installed.

8. **Report.** Final summary with these sections — keep each tight, no padding:
   - **Branch & PR:** branch name, PR URL, commit count, files changed count.
   - **Changes implemented:** bullet list of features/fixes shipped (one bullet per logical change).
   - **PR review outcome:** short overview of issues raised — what was addressed vs. rejected (with the rejection reason in one line each).
   - **Unresolved disagreements:** any standing deadlocks from the review loop flagged for human arbitration. Say "none" if there are none.
   - **(If `--persist`) Worktree info:** path and test command.

## Flags
- `--fast` — forwarded to `/pullrequest`.
- `--parallel` — create a worktree for isolated builds. Stack on the current branch unless `--base` is given. Requires a clean tree.
- `--persist` — keep the worktree after success (only with `--parallel`). Useful for local testing before merge.
- `--base <branch>` — build from `origin/<branch>` remote tip and PR into it. Works in both modes: with `--parallel` it governs the worktree base and PR target; without `--parallel` it branches off `origin/<branch>` and forwards `<branch>` to `/pullrequest` as the PR target (used by `/orchestrate-build` so each plan PRs into the workstream's feature branch).
- `--no-notification` — forwarded to `/pullrequest` to suppress its final Google Chat notification. Use when an outer orchestrator (e.g. `/build`) sends its own end-of-pipeline notification and a duplicate would be noisy.

## Notes
- If implementation reveals the plan is wrong, stop and surface it; don't silently improvise.
- This skill is the only code-writing actor in the chain; `/pullrequest`'s review subagents must stay fresh-eyes.
- **Privacy:** PR titles/bodies, commit messages, and notifications must never include personal/operator data (Atlas, todos, sessions, chat, model/provider, settings). Draft from the code change only — same rule as `/pullrequest`.
- `--parallel` improves CI/CD throughput by isolating builds — each worktree has independent deps, lockfiles, and build state.
- Without `--parallel`, behavior is unchanged: standard feature branch off current base, PR targets main (or current base if a custom flow is in place).
- If push or PR creation fails with `--parallel`, the worktree is left in place so work isn't lost (the user can retry manually).

## Step 6: Memory Flush

After the loop terminates with 0 open issues, update the workspace memory file with patterns from this run. The orchestrator performs this directly using its own tools — no subagent is needed for this step.

The write goes through `"${PYTHON}" "${MEMORY_HELPER}" update --file <spec>` so that:
- The path resolves to the **shared workspace-scoped file** (`$HOME/.grok/implement-memory/<workspace-id>.md`), not a per-worktree file.
- An exclusive lock (`fcntl.flock` on POSIX, `msvcrt.locking` on Windows; no `flock(1)` shell binary required) is held during the read-merge-write, so a /implement run in another worktree of the same repo can't clobber this update.
- Dedup against existing entries is enforced **deterministically** (case- and whitespace-insensitive match within each category).
- Compaction is enforced: each category is capped at 25 entries (lowest-count entries dropped first); Recent Runs is capped at 20 entries (oldest dropped).
- Strict input validation: malformed types (e.g., a non-list `key_patterns`, a string where a dict is required, a calendar-invalid `date`) fail fast with exit code 4 and a clear error message rather than silently corrupting the file.

### Step 6a: Collect & Categorize This Run's Patterns

1. Use the `issue_patterns` list accumulated during Step 3 across all rounds. This list contains a one-line description of every distinct issue that was open at any review checkpoint during the run.
2. **Generalize each pattern.** The memory file exists to help *future* runs on *different* tasks — patterns that reference this task's specific code, variable names, or domain objects are useless noise. Strip implementation-specific details (file names, variable names, type names, function names, domain-specific terms) and rewrite each pattern as a reusable principle that applies across different codebases and tasks:
   - Bad: "Missing error type `RetryableError` in retry handler list" → Good: "Missing entries in error-type or configuration allowlists"
   - Bad: "JWT token not validated for expiration" → Good: "Missing expiration/TTL validation on tokens or credentials"
   - Bad: "`calculateTotal` function exceeds 80 lines" → Good: "Functions exceeding reasonable length without decomposition"
   - Bad: "No test for `handleUserAuth` error path" → Good: "Missing tests for error/edge case paths"
   - Bad: "Missing null check on `userId` parameter" → Good: "Missing null/undefined checks on function inputs"
   If a pattern is *already* general (e.g., "Missing null checks on function inputs"), keep it as-is. If multiple task-specific patterns generalize to the same reusable principle, collapse them into one entry.
3. Categorize each generalized pattern into one of: Error Handling, Testing, Security, Code Quality, Naming, Documentation, Performance, or another short category name as appropriate. Reuse existing category names from `existing_patterns_snapshot` (captured in Step 0) whenever the pattern fits — do not invent a near-duplicate category like "Error-Handling" or "Tests" when one already exists.
4. For each pattern, write a concise one-line description. Keep descriptions on a single line; the helper collapses any embedded newlines but it's cleaner to write them without.

### Step 6b: Harmonize Phrasing Against Existing Entries

Before handing generalized patterns to the helper, dedup at the *phrasing* level using `existing_patterns_snapshot`:

1. For each of this run's patterns, scan `existing_patterns_snapshot` for an entry in the same (or semantically equivalent) category whose description means the same thing — even if worded differently. Examples of matches:
   - "missing null check on input" ≈ "No null validation for function parameters"
   - "functions over 50 lines" ≈ "Long functions without decomposition"
   - "no tests for error path" ≈ "Missing tests for failure cases"
2. **If a semantic match exists:** replace this run's description with the **exact existing description string** (so the helper's normalised match will collapse them onto the same entry).
3. **If no match exists:** keep your concise description as-is. It will be added as a new entry.
4. **Within this run's own list:** also dedup by phrasing — if you have two patterns that mean the same thing, collapse them to a single entry (the helper would otherwise count them as two distinct hits, which is fine but slightly inflates new-pattern stats).

The helper will also do a final case/whitespace/punctuation normalisation, but it cannot infer semantic equivalence — that's the orchestrator's job here. Skipping this step leads to the file accumulating near-duplicates over time.

### Step 6c: Build the Update Spec

Construct a JSON object with this shape (omit `run` only if you want to record patterns without logging a run; in normal flow, always include both):

```json
{
  "patterns": [
    {"category": "Error Handling", "description": "Missing null/undefined checks on function inputs"},
    {"category": "Testing", "description": "Missing tests for error/edge case paths"}
  ],
  "run": {
    "date": "2026-04-23",
    "description": "Add retry logic to blackbox client",
    "rounds": 2,
    "issues_by_severity": {"bug": 1, "suggestion": 1, "nit": 5},
    "key_patterns": ["Missing entries in error-type allowlists", "Incomplete configuration validation"],
    "specializations": ["general"]
  }
}
```

Field notes (the helper rejects wrong-typed input with exit code 4 and a clear error message identifying the offending field; empty-or-null input falls back to defaults or is silently skipped per the per-field rules below):
- `patterns[]`: each entry must be an object. `category` must be a string (defaults to `"Other"` if empty/null). `description` must be a string; **null and omitted are treated identically** (both result in a silent skip with no error).
- `patterns[].description`: one-line, harmonised in Step 6b. Newlines/tabs are collapsed to single spaces; internal multi-space runs are preserved.
- `run` must be an object (not a list, not a string). Send `null` or omit it entirely to skip the Recent Runs entry.
- `run.date`: a string in `YYYY-MM-DD` format. Calendar-invalid dates like `2026-13-99` are rejected. Pass `null`, empty string, or whitespace-only string and the helper fills in today's UTC date.
- `run.description`: the user's implementation request, trimmed to a short label. Must be a string (or `null`/omitted to fall back to `"(no description)"`). The helper strips ALL double-quote characters from the description and then wraps it in exactly one outer pair, so internal quotes never produce broken nested-quote markup. (`Add retry "logic" to client` becomes `"Add retry logic to client"`.) If you need to preserve quotes verbatim, escape them yourself before submission — the helper assumes the description is a free-form label, not a structured string.
- `run.rounds`: `round_count` as an integer. Booleans, floats, strings, and lists are rejected. Zero is accepted as-is (structurally unreachable in the actual /implement loop, but not enforced).
- `run.issues_by_severity`: derived from `total_issues_by_severity`. Must be an object with string keys and integer values (or `null`/omitted to skip the `**Issues**` body line entirely). Zero-count severities are silently dropped from the rendered summary; if all severities are zero (or the object is empty) the helper omits the `**Issues**` body line entirely.
- `run.key_patterns`: must be a list of strings (or `null`/omitted to skip the `**Key patterns**` body line). Pick the 2-3 most-significant patterns from this run. **Apply the same generalization rules as Step 6a** — strip task-specific names and rewrite as reusable principles. Two implementable options, pick consistently across runs:
  - **Option A (recommended): severity-ranked.** Re-read the latest merged review_file (still on disk at this point in the loop). Each issue has a `Severity:` tag. Take 1-2 of the highest-severity issues first (bugs > suggestions > nits), then top up with the next-highest severity until you have 3 entries. This sees only **final-round survivors** (issues that the implementer actually had to address) which is the natural "most-significant" reading.
  - **Option B (lower-effort): recency-ranked.** Take the **last 2-3 entries** of `issue_patterns` (the list grows by appending per round in Step 3, so the tail is the most-recent round's issues). This sees **cross-round accumulation** including issues that were introduced and fixed mid-loop. Use this only if re-reading the review_file is impractical — the resulting `key_patterns` will sometimes include issues that ended up wontfix or were ephemeral.
  - **Pick one option and stick with it for the run.** The two options return semantically different sets, so mixing them across runs makes the Recent Runs log inconsistent.
- `run.specializations`: must be a list of strings (or `null`/omitted to skip the `**Specializations used**` body line). Strip the `-N` suffix from `general-2`/`general-3` first so the list is the set of distinct specialization classes (e.g., `["general", "security"]`, not `["general", "general-2", "security"]`); deduplicate.

### Step 6d: Invoke the Helper

Use the `write` tool to create `${scratch_dir}/grok-mem-${IMPL_ID}.json` with the JSON spec above (using a temp file avoids quoting issues that heredocs introduce), then invoke the helper via `run_terminal_command`:

```
<PYTHON> <MEMORY_HELPER> update --file <scratch_dir>/grok-mem-<IMPL_ID>.json
```

The helper acquires the lock, parses the existing file, merges, compacts, writes atomically, and prints a JSON stats summary on stdout (pretty-printed with `indent=2`):

```json
{
  "file": "/Users/.../implement-memory/proj-d5016f47e5cb.md",
  "existed_before": false,
  "stats": {
    "new_patterns": 2,
    "merged_patterns": 5,
    "categories_touched": ["Error Handling", "Testing"],
    "categories_capped": {},
    "recent_runs_dropped": 0
  },
  "total_categories": 4,
  "total_patterns": 17,
  "total_recent_runs": 12
}
```

Key fields:
- `existed_before`: `true` if the file existed before this update, `false` if the helper just created it. Use this for the report wording.
- `stats.categories_capped`: dict of `{category: dropped_count}` for any category that exceeded `MAX_PATTERNS_PER_CATEGORY` and had its lowest-count entries dropped. Empty dict in the typical case.

Use these stats to report to the user:
> "Memory updated: 2 new patterns, 5 merged into existing entries (file at <file>)."

Or if `existed_before` is `false`:
> "Memory file created at <file> with N patterns."

### Memory File Format

The helper writes a markdown file with this structure:

<!-- mirror-of: scripts/memory.py DEFAULT_HEADER -->
<!-- The 5-line block immediately following this comment must match -->
<!-- '\n'.join(memory.DEFAULT_HEADER) verbatim. The drift-check unit -->
<!-- test TestDocsConsistency.test_skill_md_default_header_matches -->
<!-- asserts this on every test run. -->
```markdown
# Implementation Review Patterns

> This file is maintained by the /implement skill.
> It records common issues found during implementation reviews to help avoid them in future runs.
> Shared across all working directories that resolve to the same workspace id.

