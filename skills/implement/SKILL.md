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
