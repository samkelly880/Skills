---
name: build
description: Full pipeline — grill the user on the design, write a spec, confirm, then implement and PR. Use when the user says "/build", "build this", or wants to go from rough idea to shipped PR in one shot. Accepts the same primary argument as /grill-me (the topic/plan to interview about). Supports --fast, --parallel, --persist, and --base <branch> (forwarded to /implement → /pullrequest).
argument-hint: "[topic or plan to grill on] [--fast] [--parallel] [--persist] [--base <branch>]"
---

# build — grill → spec → confirm → implement → notify

Orchestrates `/grill-me`, `/implement`, and `/notify-when-done` into one pipeline. Do not implement code yourself in this skill — delegate to `/implement`.

## Steps

1. **Parse args.** Extract flags: `--fast`, `--parallel`, `--persist`, and `--base <branch>` (remember all). Everything else is the primary argument — forward verbatim to `/grill-me`.

2. **Grill.** Invoke the `grill-me` skill with the primary argument. Let it run to completion — one question at a time, branch by branch, until shared understanding is reached.

3. **Write a spec.** Once grilling is done, distill the resolved decisions into a concise spec at `.plans/<kebab-slug>.md`. Create the `.plans/` directory if missing. The spec should be tight: goal, scope (in/out), key decisions with rationale, acceptance criteria. No padding, no restating the grill transcript.

4. **Present & confirm.** Show the user:
   - The spec path.
   - A brief summary of the grill outcome (key decisions made).
   Then use `AskUserQuestion` with a yes/no question: "Ready to proceed with implementation?" Options: "Yes, implement" / "No, stop here".

5. **Implement.** If yes, invoke the `implement` skill with the spec path as the argument. Forward all parsed flags (`--fast`, `--parallel`, `--persist`, `--base <branch>`) if they were passed to `/build`. **Always pass `--no-notification`** to `/implement` (which forwards it to `/pullrequest`) — `/build` owns the final notification and the inner skill must not duplicate it. If no, stop — leave the spec in place for later (and do NOT notify).

6. **Notify.** As the very last stage — only if step 5 actually ran to completion — invoke the `notify-when-done` skill with `--optional` and a short summary message (PR URL, branch name, and termination status from `/pullrequest` if available; otherwise a brief "build complete" line). `--optional` silently no-ops if the webhook isn't configured. Skip this step entirely if the user answered "No, stop here" in step 4 or the grill was abandoned.

## Flags
- `--fast` — forwarded to `/implement` (which forwards to `/pullrequest`).
- `--parallel` — create a worktree for isolated, parallel builds. Stack on the current branch unless `--base` is given.
- `--persist` — keep the worktree after the PR is merged (only meaningful with `--parallel`). Without this, the worktree is removed after a successful push and PR creation.
- `--base <branch>` — when used with `--parallel`, build from a clean remote tip of `<branch>` instead of stacking on the current branch. PR targets `<branch>`.

## Notes
- This skill is glue only — `/grill-me` does the interviewing, `/implement` does the code-writing, `/notify-when-done` sends the ping. Don't duplicate their work.
- If the user aborts mid-grill, stop the pipeline; do not write a spec from an incomplete interview, and do not notify.
- `--no-notification` is always passed to `/implement` to suppress the inner `/pullrequest` notification — `/build`'s own final notification is the single ping the user gets, preventing a double-notify.
- Without `--parallel`, behavior is unchanged: standard feature branch off the current base, PR targets `main` (or the base branch specified in the current workflow).
- `--parallel` requires a clean working tree; if the tree is dirty, commit first or the step will fail.
