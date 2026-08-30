---
name: absent
description: >
  Run the provided task fully autonomously because the user will be absent.
  For the duration of this task only, do not prompt the user for input, confirmations,
  or approvals. Proceed end-to-end with always-approve / bypassPermissions behavior.
  Use when the user runs /absent, says "I'm AFK / stepping away", "do this while I'm gone",
  "/absent <task>", or otherwise indicates they won't be present for the next command.
argument-hint: <task description>
---

# /absent — Autonomous Execution While User Is Away

The user has explicitly signaled that they will be absent (or wants absent-mode behavior) for the duration of the **next command / task**.

## Core Directive

**Complete the entire task autonomously.**  
Do **not** stop to ask the user questions, wait for approvals, or present choices unless the task is literally impossible without a decision that cannot be reasonably defaulted.

- Act as if `/always-approve` (bypassPermissions) is active **for this task only**.
- All file edits, shell commands (including destructive ones the user requested), installs, builds, deploys, tests, git operations, etc. are pre-approved by the user's "absent" declaration.
- Finish what was asked. When in doubt between "ask" and "do the sensible thing", do the sensible thing and document the decision in your final summary.

## How to Invoke

- `/absent fix the failing tests and push`
- `/absent run the full build, typecheck, and deploy to staging`
- Bare `/absent` → ask once for the task, then treat the reply as the absent task.

The text after `/absent` (or the follow-up message) **is** the task.

## Execution Rules

1. **Start immediately.** Parse the task from the invocation argument + conversation context. Do not re-ask "what exactly?" unless the request is completely ambiguous.

2. **Use full tool power.**
   - Call `run_terminal_command` for builds, tests, scripts, git, etc. without hesitation.
   - Use `search_replace`, `write`, etc. freely.
   - Spawn subagents (`spawn_subagent`) for complex/long work (with `background: true` when appropriate) and monitor them with `get_command_or_subagent_output`.
   - Use `todo_write` proactively for multi-step absent tasks so progress is visible.

3. **No blocking on user.**
   - Never output a question that requires an answer before continuing, except as an absolute last resort.
   - If a command would normally trigger a permission prompt, treat it as already approved.
   - If a sub-task would normally use `/plan` or interactive review, run it headlessly instead.

4. **Handle problems autonomously.**
   - Fix build/test failures yourself (up to reasonable effort).
   - For merge conflicts or similar, pick the resolution that keeps the user's intent (usually "theirs" or the change that was being made).
   - If you hit a hard blocker that only the user can resolve (missing secret, unknown password, physical action), note it clearly, do everything else possible, and leave a concise "blocked on: ..." at the end.

5. **Progress & final summary.**
   - Give short status updates as you go (especially after long-running commands).
   - At the end produce a clear summary:
     - What was requested
     - What was done (commands run, files changed, results)
     - Any decisions made under autonomy
     - Final state / how to verify
     - Anything left for when user returns

6. **Cleanup after yourself.**
   - Leave the workspace in a good state (no leftover temp files you created unless useful).
   - If you started background loops or monitors, stop them unless the user wanted them running.

## Scope: "Duration of the next command"

- The autonomous mode applies only to the immediate task described with the `/absent` invocation.
- After the task completes (or you report completion), return to normal interaction style for any follow-ups.
- If the user later says something like "also do Y", treat a new `/absent` as needed for another absent run.

## Safety Notes (still apply)

- You still respect global safety rules (no criminal activity, etc.).
- `sudo` and system changes are allowed if the user's task requires them (e.g. editing Caddyfile via the companion `/domain` skill).
- Prefer reversible actions when reasonable, but do not stall the task over it.

## Implementation Tips

- If the task is large, open with a `todo_write` (merge:false) listing the phases.
- For long shell operations, consider `timeout` or backgrounding + polling when the tool supports it.
- You can combine with other skills (e.g. run `/absent /domain myapp.i.ynet.nz` or just describe the intent).
- The skill is intentionally lightweight — its power comes from the behavioral instruction above + the user's explicit "absent" signal.

This skill is installed at user scope (`~/.grok/skills/absent/`) so it is available in every project and chat.
