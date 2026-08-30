---
name: pullrequest
description: Create a pull request from one branch into another on GitHub or Forgejo, then run a bounded "go take a break while it sorts itself out" fresh-eyes review loop — each round spawns a fresh subagent that invokes the pullrequest-review skill, the author-agent (this skill) triages and fixes the findings, a second fresh subagent invokes the pullrequest-rereview skill to adjudicate the fixes, and the loop terminates ONLY on convergence (a fresh REVIEW round finds no new 🔴/🟡) or a hard round cap — never on re-review acceptance, so every set of fixes is re-reviewed by fresh eyes before the loop can end. On CONVERGED, automatically merge the PR and delete the head branch unless the user opted out (`--no-merge` / "don't merge" / "leave the PR open"). On CAPPED (round limit), tell the user and ask whether to continue another batch of rounds — do not merge. Trigger whenever the user says "open a PR", "/pullrequest", "create a pull request from <branch>", "PR this branch", or otherwise asks to push a branch up for review with the automated review loop. Supports a `--fast` flag (also triggered by phrases like "fast PR", "quick PR review", "fast pullrequest", "do a fast review loop") which caps the loop at 2 REVIEW rounds instead of the default 5 — use it when the user signals they want a faster turnaround at the cost of fewer review passes. Also supports a `--focused` flag (also triggered by phrases like "focused review", "just regressions and security", "only flag what this PR breaks", "narrow review") which both caps the loop at 2 REVIEW rounds AND narrows the reviewer's blocking scope to **new regressions and new security flaws introduced by this PR** — everything else is demoted to 🟢 Nitpick so it surfaces without forcing another round. `--fast` and `--focused` compose: passing both yields focused scope at the 2-round cap. Also supports a `--no-notification` flag (also triggered by phrases like "no notification", "don't notify me", "skip the ping", "no chat message") which suppresses the final Google Chat notification step; by default, the skill invokes `notify-when-done --optional` as its last stage so the user gets pinged when the loop terminates. Also supports `--no-merge` (and phrases like "don't merge", "leave the PR open", "no auto-merge") to skip the post-convergence merge+branch-delete, and `--keep-branch` (or "keep the branch", "don't delete the branch") to merge but leave the head branch. The fresh-eyes subagents are non-negotiable — the value of the loop is that the reviewer never sees the implementation rationale.
---

# pullrequest — Create PR & Run the Fresh-Eyes Review Loop

## Purpose

Open a pull request from one branch into another on **GitHub** (`gh`) or **Forgejo** (`fgj`), then drive a bounded, automated review loop. Each round:

1. A **fresh subagent** invokes the `pullrequest-review` skill on the current diff and posts inline findings.
2. You (this skill, the author-agent / orchestrator) **triage** each new finding — FIX (edit code) or REJECT (record reason).
3. A second **fresh subagent** invokes the `pullrequest-rereview` skill and adjudicates the prior round's fixes/rejections against the actual code. **The rereview NEVER ends the loop** — it only verifies this round's fixes and surfaces disagreements for you to respond to.
4. You **respond** to each disagreement exactly once — concede & retry the fix, or defend & post a reasoning reply (logged as a standing deadlock for human review). If there are no disagreements, this step is a no-op.
5. Push the round's code changes to the PR branch.
6. Loop back to step 1 — a **new fresh REVIEW round** — up to `max_rounds` rounds (default 5; **2 with `--fast`**). The loop terminates ONLY when a fresh REVIEW round produces zero new 🔴/🟡 findings (CONVERGED) or the round cap is hit (CAPPED). A clean rereview is NOT an exit condition: the fixes it just verified must still face a fresh review round before the loop can end.

Then post a single summary comment that captures what was fixed, what was rejected (with reasoning), and any standing disagreements for human arbitration.

**After the summary:**
- **CONVERGED** → by default **merge the PR and delete the head branch** (remote + local when safe). Skip merge/delete only if the user opted out via `--no-merge` / "don't merge" / "leave the PR open" (or merge-but-keep-branch via `--keep-branch`).
- **CAPPED** → **do not merge**. Tell the user the round limit was hit, report outstanding findings, and **ask whether to continue** another batch of review rounds. If they say yes, resume the loop (reset `round` to 1 for a new batch at the same `max_rounds`); if no, stop with CAPPED status.

Runs end-to-end without check-ins during the loop. Make triage, fix, and push decisions yourself. The only post-loop question allowed is the CAPPED "continue?" ask.

## Privacy — never publish personal / operator data

**Hard rule.** Everything this skill writes that can leave the machine (PR title/body, commit messages, review comments, inline replies, summary comments, subagent spawn prompts, Google Chat notifications, chat-facing status text that gets mirrored to the PR) must contain **only** technical information about the **code change under review**.

**Never include** any of the following, even if they are in the current agent context, Prism UI state, shell env, or conversation:

| Category | Examples (non-exhaustive) |
|----------|---------------------------|
| Memory / notes | Atlas memory entries, personal notes, scratchpads, diary text |
| Tasks / todos | Personal to-do lists, task-panel contents, private checklists unrelated to the PR's test plan |
| Session / UI state | Open threads/sessions, active project list, sidebar status, "Working/Awaiting" badges, Core status, sky/theme state |
| Chat content | User messages, assistant replies, tool previews, grill-me answers, permission dialogs |
| Model / provider | Which model or provider is selected, API keys, token counts, usage, Spectrum/Grok instance ids |
| Settings | Approvals, Behaviour, preferences, feature flags, tokens, bearer secrets, home paths used as identity |
| Identity / host | Personal email beyond git author already in commits, phone, addresses, private hostnames, VPN details, local absolute paths that reveal personal layout unless required by the code change itself |
| Unrelated work | Other repos, other PRs' private context, calendar, passwords, cookies |

**Allowed content** is limited to: branch names, commit SHAs, file paths **in the repo**, code-level why/what of the diff, test-plan steps for verifying the change, forge PR/review metadata (PR number, comment ids), and evidence drawn from **repository** tests/docs/code.

**Sanitize before publish.** Before every `gh`/`fgj` write, every `git commit` message, and every notification:

1. Draft from the **diff and commits only** — not from chat memory or app state.
2. Re-read the text and strip anything that would not make sense to a stranger who only has the repo.
3. If a finding or fix is easiest to explain with personal context, rewrite it in pure code terms (or omit the personal part). Prefer a shorter public comment over a leaky one.

This rule also applies to **subagent spawn prompts**: do not paste conversation snippets, Atlas entries, todos, model names, settings, or thread lists into the reviewer. Only the fields already listed under "How to spawn the fresh subagent" (PR number, forge CLI, round, focused flag, triage table of code findings).

If you discover personal data already present in an existing PR body/comment you are about to quote, **do not re-quote it** — paraphrase in technical terms or cite only the code path/line.

## Usage
```
/pullrequest [--fast] [--focused] [--no-notification] [--no-merge] [--keep-branch] [--base <to_branch>] <from_branch> [<to_branch>]
```

## Arguments
- `<from_branch>` — **required**. The branch containing the changes to merge.
- `<to_branch>` — optional. The target branch. **Defaults to `main`.** Can also be passed via `--base <to_branch>`.
- `--fast` — optional flag. Caps the review loop at **2 REVIEW rounds** instead of the default 5. Use when the user signals they want a faster turnaround at the cost of fewer review passes. Trigger this mode whether the user passes the literal `--fast` flag OR uses natural-language phrasing like "fast PR", "quick PR review", "do a fast review loop", "only do a couple of review rounds" — same effect either way.
- `--focused` — optional flag. **Both** caps the review loop at 2 REVIEW rounds (same numeric cap as `--fast`) **and** narrows the reviewer's blocking scope: only new regressions and new security flaws introduced by this PR's diff qualify as 🔴 Critical / 🟡 Improvement; everything else is demoted to 🟢 Nitpick (the convergence gate already ignores 🟢, so the loop tends to converge sooner). Trigger this mode whether the user passes the literal `--focused` flag OR uses natural-language phrasing like "focused PR", "focused review", "just regressions and security", "only flag what this PR breaks", "narrow review". `--fast` and `--focused` can be combined: the result is focused scope at the 2-round cap (same cap, narrower scope).
- `--no-notification` — optional flag. If set, skip the final Google Chat notification that would normally be sent via `/notify-when-done`. Useful when running automation that should not alert users. Without this flag, a notification is posted at completion (silently skipped if the webhook is not configured).
- `--no-merge` — optional flag. If set, after CONVERGED do **not** merge the PR and do **not** delete the branch — leave the PR open for the user. Also trigger this from natural-language phrasing like "don't merge", "do not merge", "leave the PR open", "no auto-merge", "skip the merge". Default is to merge+delete on convergence.
- `--keep-branch` — optional flag. If set (and merge is still enabled), merge the PR on CONVERGED but **do not delete** the head branch. Also trigger from phrasing like "keep the branch", "don't delete the branch", "leave the branch". Ignored when `--no-merge` is set (nothing is merged or deleted).
- `--base <to_branch>` — optional flag. Explicitly set the target branch for the PR. Overrides the positional `<to_branch>` argument if both are given.

If `<from_branch>` is missing, ask the user for it before proceeding. Never guess. The flags can appear anywhere in the argument list (before or after the branch names, and in any order) — strip them out before treating the remaining positional args as branch names. If both `--base <to_branch>` and a positional `<to_branch>` are given, prefer `--base`.

## Why fresh subagents (the load-bearing requirement)

Each REVIEW and RE-REVIEW MUST run in a **fresh subagent** — a clean context window that does NOT inherit this development conversation. That isolation is the entire source of "fresh eyes": a reviewer that has seen the implementation rationale is not a fresh reviewer. **Spawn a new subagent for every review and every re-review.** Never reuse a subagent across rounds, and never let the parent's context leak into the reviewer's task beyond the PR number it needs.

You (the orchestrator) are the only actor that edits code. The review subagents only read code and post comments. This separation of duties keeps fresh-eyes review meaningful and bounds the blast radius of any prompt-injection in the diff.

### How to spawn the fresh subagent

Use the **Agent tool** with `subagent_type: "general-purpose"`. Per Claude Code documentation, a new Agent call starts a fresh agent with no memory of prior runs — that is exactly the isolation property required here. Each spawn is a **blocking** call (do NOT use `run_in_background` for the review subagents — every subsequent step depends on the review output).

The spawning prompt MUST be self-contained and MUST NOT include:
- Why the code was written the way it was.
- What the author intended.
- Any "we already discussed X" or "earlier in this thread Y" framing.
- Quotes from the development conversation.
- **Any personal / operator data** (Atlas memory, todos, open threads, chat messages, model/provider, settings, status, secrets) — see **Privacy**.

It MAY include only:
- The PR number.
- The forge (GitHub vs Forgejo) and CLI to use, if helpful to remove ambiguity.
- The round number.
- The focused-mode flag.
- For rereview only: the prior review's id/commit_id and the ordered list of (finding → author claim) pairs you derived in TRIAGE/RESPOND — claims themselves must be code-only.
- An instruction to invoke the relevant skill (`pullrequest-review` or `pullrequest-rereview`) and return its structured output verbatim.

### State machine

```
create PR
        │
        ▼
round = 1
        │
        ▼
┌───────────────────────────────────────────────────────────────────────────┐
│ REVIEW    (fresh subagent → pullrequest-review on current diff) → WAIT      │
│         │                                                                   │
│         ├─ no new 🔴/🟡 findings ────────────────────► EXIT loop (converged)│
│         │                                                                   │
│         ▼ new findings exist                                                │
│ TRIAGE    (orchestrator): per finding → FIX (edit code) or REJECT (reason)  │
│         │                                                                   │
│         ▼                                                                   │
│ COMMIT    (orchestrator): commit + push the FIX edits → <round_sha>         │
│         │                                                                   │
│         ▼                                                                   │
│ CLAIMS    (orchestrator): post per-finding inline reply on each thread —    │
│         │  FIX  → "Fixed in <round_sha>. <description>"                     │
│         │  REJECT → "Declined: <reason>. <evidence>"                        │
│         │  capture each reply's id as author_claim_comment_id               │
│         ▼                                                                   │
│ ADJUDICATE (fresh subagent → pullrequest-rereview) → WAIT                   │
│         │  • inline comment on every disagreement (⚠️/❌/🟥) explaining why │
│         │  • 👍/👎 reaction on each author_claim_comment_id per verdict      │
│         │  • full verdict table in chat reply                               │
│         │  NEVER exits the loop — only verifies fixes + lists disagreements │
│         ▼                                                                   │
│ RESPOND   (orchestrator), single pass per disagreement                      │
│         │  (no-op if there are zero 🔴/🟡 disagreements):                   │
│         ├─ AGREE  → retry the fix (edit code). Stands UNVERIFIED this round │
│         │           — next round's REVIEW judges it. NOT a standing         │
│         │           deadlock.                                               │
│         └─ DEFEND → post reasoning reply on the rereview's inline comment.  │
│                     Log as STANDING DEADLOCK for the final summary.         │
│         │                                                                   │
│         ▼                                                                   │
│ COMMIT retry fixes (if any) and push                                        │
│         │                                                                   │
│         ▼                                                                   │
│ round += 1 ; if round > <max_rounds> → EXIT loop (capped) ; else → REVIEW   │
│              (max_rounds = 2 if --fast OR --focused, else 5)                │
│  ── the ONLY exits are REVIEW-side CONVERGENCE and the round CAP ──         │
└───────────────────────────────────────────────────────────────────────────┘
        │
        ▼
SUMMARY comment (orchestrator)
        │
        ├─ CONVERGED ─► if <auto_merge>: MERGE PR + delete branch (unless
        │                 <keep_branch>); else leave PR open
        │               then final report + notify
        │
        └─ CAPPED ────► tell user round limit hit → ASK "continue?"
                          ├─ yes → round = 1; re-enter REVIEW (new batch)
                          └─ no  → final report + notify (no merge)
```

### Rules that make the loop safe and correct

1. **Only ONE gate ends the loop "ready to merge": REVIEW-side CONVERGENCE** — a start-of-round fresh review finds no new 🔴/🟡. The re-review/adjudication step CANNOT end the loop; a clean rereview only means this round's fixes held, and those fixes must still face a fresh REVIEW round before the loop can terminate. The only other exit is the hard round CAP (which does NOT imply ready-to-merge). This is deliberate: a single review pass that got its findings fixed is not enough — fresh eyes must look again at the fixed code and find nothing.
2. **REVIEW convergence bar = no new 🔴 Critical AND no new 🟡 Improvement findings.** Lingering 🟢 nitpicks do NOT keep the loop running (otherwise a pedantic reviewer that always finds one nit burns all the rounds). 🟢-only rounds exit the loop (CONVERGED).
3. **The rereview never terminates the loop.** Its 🔴/🟡 disagreements drive RESPOND (concede-retry or defend); zero disagreements just means RESPOND is a no-op this round. Either way the loop ALWAYS advances to the next fresh REVIEW round (or the cap). Lingering 🟢 disagreements are surfaced in the summary but drive nothing.
4. **Adjudication is single-pass per round.** Respond to each disagreement exactly once (retry or defend). A retry is **not** re-adjudicated this round — it rides into the next REVIEW and is judged there by fresh eyes. There is no inner loop.
5. **Retries stand unverified until the next REVIEW.** A bad retry of a real, still-present problem will be caught by the next fresh review (or, if it's a judgment call fresh-eyes wouldn't independently re-flag, it was heading to human escalation anyway). The forward review is the backstop.
6. **Hard cap: `max_rounds` REVIEW rounds per batch.** Default `max_rounds = 5`. When the user invokes the skill with `--fast` OR `--focused` (or their natural-language equivalents), `max_rounds = 2`. Hitting the cap exits the batch as CAPPED — then you **must ask the user whether to continue** another batch. Do not silently stop without asking, and do not merge on CAPPED.
7. **Each REVIEW and ADJUDICATE is a brand-new subagent.** No reuse, no shared context, no leakage of dev rationale.
8. **Only the orchestrator (this skill) edits code.** Subagents are read-only + the single post-review action.
9. **Defended disagreements go to a HUMAN via the summary, never back into the loop.** No feedback merging.
10. **Re-review never looks for NEW issues, and never ends the loop.** Its `event` is always `COMMENT`, its scope is the prior round's findings only. If an adjudicator stretches into new issues, ignore them — the next fresh REVIEW catches new issues. After every adjudication the loop advances to another fresh REVIEW round (or hits the cap); there is no "trust the rereview and skip the next review" shortcut.

## Execution

### Step 1 — Resolve args, forge, identity, repo context
- Parse `$ARGUMENTS` to extract `<from_branch>`, `<to_branch>` (default `main` if absent), and the `--fast`, `--focused`, `--no-notification`, `--no-merge`, and `--keep-branch` flags. These flags may appear anywhere in the argument list (in any order); strip all before treating the remaining positional args as branch names. If `<from_branch>` is missing, ask the user — never guess.
- **Set `<focused_mode>`:** `true` if `--focused` was passed OR the user's invoking phrase clearly signals focused mode ("focused PR", "focused review", "just regressions and security", "only flag what this PR breaks", "narrow review"); otherwise `false`. When in doubt, default to `false` (broad) — only flip to focused on clear signals so a casual "review this" doesn't accidentally narrow scope.
- **Set `max_rounds`:** `2` if **either** flag was passed (`--fast` OR `--focused`), or if the user's invoking phrase signals fast mode ("fast PR", "quick PR review", "do a fast review loop", "only do a couple of review rounds") or focused mode (per the focused-mode triggers above); otherwise `5`. When in doubt, default to `5` — only flip to `2` on clear signals so a casual "let's review this PR" doesn't accidentally truncate the loop.
- **Set `<send_notification>`:** `false` if `--no-notification` was passed; otherwise `true`.
- **Set `<auto_merge>`:** `false` if `--no-merge` was passed OR the user's invoking phrase clearly opts out of merging ("don't merge", "do not merge", "leave the PR open", "no auto-merge", "skip the merge"); otherwise `true`. Default is merge-on-convergence.
- **Set `<keep_branch>`:** `true` if `--keep-branch` was passed OR the user's invoking phrase asks to keep the branch ("keep the branch", "don't delete the branch", "leave the branch"); otherwise `false`. When `<auto_merge>` is `false`, branch deletion is skipped regardless of `<keep_branch>`.
- **Detect the forge** from `origin`: `git remote get-url origin`. github.com → `gh`. Otherwise → Forgejo `fgj` (the host is the instance). Cache as `<CLI>`.
- Confirm `<CLI>` is authenticated. If not, stop and tell the user (`gh auth login` or the `fgj` login command).
- Resolve `<owner>` and `<repo>`:
  - GitHub: `gh repo view --json owner,name`
  - Forgejo: parse from `git remote get-url origin` or `fgj` repo view
- Verify both branches exist locally or on the remote (`git rev-parse --verify` / `git ls-remote --heads origin <branch>`). If `<from_branch>` exists only locally, ask the user before pushing.

### Step 2 — Draft the PR
- Run in parallel: `git status` (no `-uall`), `git diff <to_branch>...<from_branch>`, `git log <to_branch>..<from_branch> --oneline`.
- Read **every** commit in the range, not just the latest, and synthesize a title (<70 chars) and body.
- **Source of truth for the draft is the git range only.** Do not import chat history, Atlas memory, todos, session lists, model/provider, settings, or UI status into the title or body (see **Privacy**).
- Body format:
  ```
  ## Summary
  <1–3 bullets — the "why" of the *code change*, not the operator's day>

  ## Test plan
  - [ ] <bulleted checklist of how to verify the change in-repo>
  ```
- Before creating the PR, re-scan the title and body for personal data and strip it.

### Step 3 — Open the PR
GitHub:
```sh
gh pr create --base <to_branch> --head <from_branch> --title "<title>" --body "$(cat <<'EOF'
<body>
EOF
)"
```
Forgejo (`fgj` mirrors the same shape — `fgj pr create --base <to_branch> --head <from_branch> --title "<title>" --body-file <path>`; fall back to `fgj api --method POST /repos/<o>/<r>/pulls --input <json>` if the binary lacks `pr create`).

Capture the returned PR number as `<num>` (parse from URL or fetch via `<CLI> pr view --json number`). Cache the PR's head SHA as `<head_sha>` — this is the commit the first review will run against.

### Step 4 — Enter the review loop

Initialize:
- `round = 1`
- `outstanding_findings = []` — findings the orchestrator has triaged but not yet pushed-and-verified
- `fixed_log = []` — findings successfully fixed across rounds
- `rejected_log = []` — findings the orchestrator rejected, with reasoning (each independently re-verified by rereview)
- `standing_deadlocks = []` — DEFENDED disagreements that escalate to the human in the final summary
- `last_review_id = null` ; `last_review_commit = null`

#### Step 4a — REVIEW (fresh subagent)

Spawn a fresh subagent that invokes the `pullrequest-review` skill. Self-contained prompt template:

```
Invoke the pullrequest-review skill on PR #<num> in this repository.

This is round <round> of an automated review loop. The repo is checked out
at the current working directory; the active forge CLI is <CLI>.

focused: <true|false>   # if true, restrict 🔴/🟡 to new regressions and new
                        # security flaws introduced by THIS PR's diff; demote
                        # everything else to 🟢 Nitpick per the skill's
                        # focused-mode classification rule.

Follow the skill exactly: review the current diff, post inline findings,
return the structured chat-reply output (including the Mode line and the
Counts block).

Do not reference any conversation outside this prompt. The code under
review must stand on its own merits.
```

Substitute `<true|false>` with the orchestrator's `<focused_mode>` value. Pass this line every round of the loop — the reviewer subagent reads it in its own Step 1 and uses it to gate severity in Step 5.

Wait (blocking) for the subagent to return.

Parse its returned summary for:
- `new_critical = count of 🔴 findings posted this round`
- `new_improvement = count of 🟡 findings posted this round`
- `new_nitpick = count of 🟢 findings posted this round` (advisory only)
- The list of inline findings: `(severity, path, line, title, body, comment_id)` for each
- `review_id` and `head_sha` reviewed

Cache `last_review_id` and `last_review_commit` from the response.

**Gate check (convergence):**
- If `new_critical == 0 AND new_improvement == 0` → exit the loop with status `CONVERGED at round <round>`. Skip to Step 5.
- Otherwise continue to TRIAGE.

> "New" means findings that appeared in *this* review. Because each fresh subagent re-reviews the current diff independently, "new" findings are simply whatever the latest review posted. The orchestrator does not deduplicate against earlier rounds — the convergence gate trusts the fresh reviewer's output as-is.

#### Step 4b — TRIAGE (orchestrator: decide + edit code only)

For each new 🔴 / 🟡 finding from this round, decide **FIX** or **REJECT** yourself. Don't deliberate aloud — act.

- **FIX** → edit the code on `<from_branch>` to address the finding. Use `Edit` / `Write` as needed. Do NOT push yet; do NOT post a reply yet.
- **REJECT** → record a clear, evidence-based reason (a test that demonstrates the current code is correct, a doc quote, or a counter-example from the codebase). Append `(finding, "rejected: <reason>")` to `rejected_log`.

🟢 nitpicks: triage at your discretion — fix the cheap ones, skip the rest. Nitpicks do not influence convergence.

Build a per-finding decision table — you'll use it in Step 4d to post replies and in Step 4e's spawn prompt:

```
| # | severity | path:line | review_comment_id | finding (one-line) | decision | claim text |
|---|----------|-----------|-------------------|--------------------|----------|------------|
| 1 | 🔴 | foo.py:42 | 1234567 | <title> | FIX     | (pending sha) |
| 2 | 🟡 | bar.py:88 | 1234568 | <title> | REJECT  | "not actually unsafe because <evidence>" |
```

The `review_comment_id` is the id of the original inline review comment from the fresh-eyes review — captured in Step 4a's parsed output. You need it to post the reply on the correct thread.

#### Step 4c — Commit the round's fixes

Stage and commit the FIX edits as ONE commit per logical change. Use a clear **code-only** commit message (what changed in the tree — not personal context); the rereview subagent will read it. Push to every remote tracking `<from_branch>` (typically `origin`; also any secondary remote like `github`).

After pushing, capture the new HEAD as `<round_sha>` (short form via `git rev-parse --short HEAD`) and refresh `<head_sha>` to the same value. If there are no FIX rows (every finding was REJECT), skip the commit step but record that the codebase is unchanged this round.

#### Step 4d — POST AUTHOR CLAIMS (inline replies, one per finding)

Now that the round's commit exists, post one inline reply per finding on the original review comment's thread. This both gives the rereview a concrete claim to react to (👍 / 👎) AND leaves a human-readable audit trail on the PR.

Reply text (code-only; no personal/operator data — see **Privacy**):
- **FIX** → `Fixed in <round_sha>. <one-line description of the change>`
- **REJECT** → `Declined: <reasoning>. <evidence — test snippet, doc quote, or counter-example link>`

API:
```sh
# GitHub
gh api repos/<owner>/<repo>/pulls/<num>/comments/<review_comment_id>/replies \
  --method POST -f body="<reply text>"

# Forgejo (Gitea-compatible)
fgj api --method POST /repos/<owner>/<repo>/pulls/<num>/comments/<review_comment_id>/replies \
  -f body="<reply text>"
```

Capture each reply's returned comment id and add it to the decision table as `author_claim_comment_id`:

```
| # | severity | path:line | review_comment_id | author_claim_comment_id | finding | decision | claim text |
|---|----------|-----------|-------------------|-------------------------|---------|----------|------------|
| 1 | 🔴 | foo.py:42 | 1234567 | 1234999 | <title> | FIX    | Fixed in abc1234. <description> |
| 2 | 🟡 | bar.py:88 | 1234568 | 1235000 | <title> | REJECT | Declined: <reasoning>. <evidence> |
```

If a single reply POST fails (transient HTTP error), retry once. If it still fails, leave the row's `author_claim_comment_id` empty — the rereview will fall back to reacting on `review_comment_id` and note the fallback.

#### Step 4e — ADJUDICATE (fresh subagent)

Spawn a fresh subagent that invokes the `pullrequest-rereview` skill. Self-contained prompt template:

```
Invoke the pullrequest-rereview skill on PR #<num> in this repository.

Adjudicate the prior review (id <last_review_id>, commit <last_review_commit>,
posted by login <my_login>) against the current code. This is round <round>.

The author has posted the following claim per finding — each claim is an
inline reply on the original review thread, with the comment id given as
`author_claim_comment_id`. Adjudicate each claim against the actual current
code, NOT against the confidence of the claim. React on each finding's
author_claim_comment_id with 👍 (claim holds) or 👎 (claim does not hold)
as the skill specifies.

Triage table:

| # | severity | path:line | review_comment_id | author_claim_comment_id | finding | author claim |
| ... [paste the decision table populated in Step 4d] ... |

Follow the skill exactly: post the adjudication review, post the per-claim
reactions, then return the structured verdict table (including the
Disagreements block and Counts).

Do not reference any conversation outside this prompt. Reach verdicts from
the code.
```

Wait (blocking) for the subagent to return.

Parse the verdict table. The Disagreements block lists items rated ⚠️ fix-incomplete, ❌ fix-absent, or 🟥 rejection-unjustified — these are the only ones requiring a response this round. Filter to 🔴 Critical / 🟡 Improvement severity (the rereview's chat reply emits `🔴/🟡 disagreements (loop-blocking)` in its Counts block; if absent, derive it by filtering the verdict table for rows whose `severity ∈ {🔴, 🟡}` AND `verdict ∈ {⚠️ fix-incomplete, ❌ fix-absent, 🟥 rejection-unjustified}`). 🟢-severity disagreements are non-blocking and do not require a response this round — they ride into the next REVIEW (or, on cap, surface in the summary).

**No exit here.** The adjudication step NEVER terminates the loop, even when it is completely clean (zero 🔴/🟡 disagreements). A clean rereview only confirms that this round's fixes held against the current code — it does not substitute for a fresh REVIEW round looking at the fixed code with fresh eyes. The next fresh REVIEW is the only convergence signal — this round's fixes may have introduced new issues that the rereview, scoped to the prior findings, cannot see. Always continue:

- Continue to Step 4f (RESPOND). If there are zero 🔴/🟡 disagreements, RESPOND is a no-op — proceed straight to Step 4g, which advances to the next fresh REVIEW round (or the cap).

> Why there is no acceptance exit: a single reviewer looking once, whose findings you then fixed, is a thin bar — that reviewer cannot vouch for what they missed, nor for what your fixes introduced. Only a *fresh* REVIEW round over the fixed code (finding nothing new) proves the round of fixes is genuinely clean. So the fixes the rereview just verified must still survive another REVIEW before the loop may end.

#### Step 4f — RESPOND to disagreements (orchestrator, single pass)

For each disagreement (an item rated ⚠️ / ❌ / 🟥 by the rereview), decide on its merits:

- **AGREE** (rereview is right) → retry the fix (edit code on `<from_branch>`). The retry stands UNVERIFIED this round — the next round's fresh REVIEW will catch it if the problem is still real. Conceded items are NOT logged as standing deadlocks (they are no longer disagreements).
- **DEFEND** (you still think your original decision is correct) → post a reasoning reply on the rereview's inline comment thread (the `rereview_comment_id` from the rereview's Disagreements block):
  ```sh
  <CLI> api repos/<owner>/<repo>/pulls/<num>/comments/<rereview_comment_id>/replies \
    --method POST -f body="<defending reasoning, with evidence>"
  ```
  Append the item to `standing_deadlocks` with: the original finding, the author's position, and the rereview's position. This routes the call to a human via the summary.

**Single-pass discipline:** each disagreement gets exactly one response this round. Do not loop back to ADJUDICATE within the same round. A retry's correctness is judged by the next fresh REVIEW, not by a second rereview.

#### Step 4g — Commit retry fixes & advance

If Step 4f produced any code edits (AGREE retries), stage and commit them and push to every remote tracking `<from_branch>`. Refresh `<head_sha>`.

Increment `round`. If `round > max_rounds`, exit the loop with status `CAPPED at round <max_rounds>` (and note `--fast` if `max_rounds == 2`). Otherwise go back to Step 4a.

### Step 5 — Post the summary comment

Post ONE top-level summary comment to the PR. This is the durable record (no per-thread resolution is used). **Sanitize for Privacy** — summary may only describe code findings, fixes, rejections, and deadlocks; never personal memory, todos, sessions, models, or settings.

```sh
# GitHub
gh api repos/<owner>/<repo>/issues/<num>/comments -f body="<summary_body>"
# Forgejo
fgj api --method POST /repos/<owner>/<repo>/issues/<num>/comments -f body="<summary_body>"
```

where `<summary_body>` is the formatted summary text (the markdown block below). Pass the body inline — do NOT write it to a temp file and reference the path.

Body format:

```
# 🤖 Automated review loop summary

## Termination
<exactly one of — the ONLY two possible outcomes:>
- ✅ **Converged at round <K>** — the round-<K> fresh review found no new 🔴/🟡 issues. PR is ready to merge (auto-merge follows unless `--no-merge`). (Mode: `--fast` / default — pick whichever applied.)
- ⛔ **Round limit reached (<max_rounds>)** — did not fully converge (a fresh review still found blocking issues at the cap). Mode: `--fast` (2-round cap) or default (5-round cap). Outstanding findings from the last fresh review:
  - <severity> `<path>:<line>` — <title>
  - ...

## ✅ What was fixed
- <severity> `<path>:<line>` — <title> (round <K>)
- ...

## ⏭️ What was rejected (independently checked by rereview)
- <severity> `<path>:<line>` — <title>
  - **Author's reasoning:** <one-line reason>
  - **Rereview verdict:** 🟦 rejection-justified — <one-line confirmation>
- ...

## ⚠️ Standing disagreements for human review
> These are issues where the author DEFENDED their original decision against the rereview's challenge.
> Conceded-and-retried items are NOT in this list. Both positions are recorded for human arbitration.

- <severity> `<path>:<line>` — <title>
  - **Author's position:** <one-line>
  - **Rereview's position:** <one-line>
  - Original finding: <link to review comment>
  - Adjudication: <link to rereview comment>
- ...
```

If there were no findings at any point: a brief "fresh-eyes review found no issues" note and skip the categorised sections.

### Step 5b — Branch on termination

#### If CONVERGED → merge + delete branch (default)

If `<auto_merge>` is `false`, skip this entire subsection: leave the PR open, note in the chat reply that merge was skipped per user request, and continue to Step 6.

If `<auto_merge>` is `true`, merge via the forge CLI and delete the head branch unless `<keep_branch>` is `true`:

GitHub:
```sh
# Prefer repo default merge method; delete remote head branch unless keeping it
if <keep_branch>; then
  gh pr merge <num> --merge
else
  gh pr merge <num> --merge --delete-branch
fi
```

Forgejo (prefer `fgj pr merge` if available; otherwise the pulls merge API):
```sh
# Merge (method: merge). Delete head branch unless keeping it.
fgj pr merge <num> --style merge
# If the CLI supports it:
#   fgj pr merge <num> --style merge --delete-branch
# Else after a successful merge, delete the remote head:
#   git push origin --delete <from_branch>
```

After a successful merge:
1. If `<keep_branch>` is `false`, ensure the **remote** head branch is gone (`gh` `--delete-branch` usually handles this; otherwise `git push origin --delete <from_branch>`).
2. If `<keep_branch>` is `false` and a local `<from_branch>` exists: check out `<to_branch>` (or another safe branch), `git pull` it, then `git branch -d <from_branch>` (use `-d`, not `-D`, so unmerged work is not force-dropped). If delete refuses, report that and leave the local branch.
3. Record `merged = true` (and whether the branch was deleted) for Step 6 / Step 7.

If merge fails (required reviews, status checks, permissions, conflicts): **do not force**. Report the failure in chat with the forge error, leave the PR open, set `merged = false`, and continue to Step 6. Never `--admin` / bypass without the user explicitly asking in this conversation.

#### If CAPPED → tell the user and ask to continue

**Do not merge** on CAPPED.

1. In chat, clearly state that the **round limit was reached** (`max_rounds`, mention `--fast` / `--focused` if active).
2. List the outstanding 🔴/🟡 findings from the last fresh review (path:line + title).
3. **Ask the user** whether to continue another batch of review rounds (same `max_rounds`, same flags). Use a direct question — this is the one allowed mid/post-loop ask.
4. If the user says **yes** / continue / keep going:
   - Reset `round = 1` (new batch; keep `fixed_log`, `rejected_log`, `standing_deadlocks` as cumulative history).
   - Optional short PR comment that another batch is starting is fine.
   - Return to Step 4a (REVIEW) and run another full batch.
   - When that batch ends, apply Step 5 / 5b again (CONVERGED → merge path; CAPPED → ask again).
5. If the user says **no** / stop / leave it:
   - Proceed to Step 6 with status CAPPED and `merged = false`.

Do not assume "continue" — wait for the user's answer.

### Step 6 — Final report (chat reply)

Concise:
- PR URL.
- Termination status — exactly one of: **Converged at round K** (a fresh REVIEW round found no new 🔴/🟡) or **Capped at round `max_rounds`** (a fresh review still found blocking issues at the cap; NOT merged). Mention `--fast` if it was active.
- On CONVERGED: whether the PR was **merged** (and whether the head branch was deleted), or that merge was skipped (`--no-merge`) / failed (with reason).
- Rounds run (including any continuation batches).
- Counts: total findings posted across all rounds, fixed, rejected, standing deadlocks.
- Whether commits were pushed.
- Link to the summary comment.

Then, as the **last line of the chat reply**, emit a single machine-readable status token so a
wrapping orchestrator (e.g. `/orchestrate-build`) can branch on the outcome without parsing prose.
Keep it on its own line, verbatim, exactly this format:

```
PR-STATUS: <CONVERGED|CAPPED>@round=<K> outstanding=<critical>/<improvement>/<nitpick> deadlocks=<n> merged=<true|false>
```

`outstanding` is the by-severity count from the **final** fresh review (the one that ended the
loop): for `CONVERGED` the critical/improvement counts are `0/0`; for `CAPPED` they are whatever
remained open at the cap. `deadlocks` is the count of standing disagreements escalated to the
human. `merged` is `true` only when the forge merge succeeded this run. This token is the contract
an orchestrator reads to decide what happened.

### Step 7 — Send notification (last stage)

If `<send_notification>` is `false` (user passed `--no-notification` or its natural-language equivalent), skip this step entirely.

Otherwise, invoke the `notify-when-done` skill via the Skill tool, passing `--optional` followed by a concise one-line message that includes the PR URL and termination status **only** (no personal/operator data — see **Privacy**). Example argument string:

```
--optional PR #<num> <title> — <status>: <pr_url>
```

where `<status>` is one of `converged+merged at round K`, `converged (merge skipped) at round K`, `converged (merge failed) at round K`, or `capped at <max_rounds> rounds`. The `--optional` flag ensures the workflow does not error out if the user has not configured `GOOGLE_CHAT_WEBHOOK`; the notification is silently skipped in that case.

This is the final stage of the skill — nothing runs after it (except when CAPPED and the user chose to continue, in which case you re-enter the loop before reaching this stage).

## Guardrails

- **Never publish personal / operator data** on the PR or in notifications (Atlas, todos, open threads, chat, model/provider, settings, secrets, host identity). See **Privacy**. Sanitize every public string before posting.
- **Never commit directly to `main`/`master`.** All work goes on a feature branch; land on the base branch only via the forge PR merge in Step 5b after CONVERGED (unless `<auto_merge>` is false). If `/pullrequest` is invoked while checked out on the base branch, stop and ask which branch the changes belong on.
- **Never `git reset --hard` any branch, and never force-push, without explicit user approval for that specific action.** Prefer non-destructive operations: `git revert` to undo a commit, `git cherry-pick` to move work between branches, a new commit to fix a mistake. Rewriting history is a last resort.
- **Never `--no-verify`, never amend a pushed commit.**
- **Only the orchestrator edits code.** Subagents are read-only + post-comments.
- **Spawn fresh subagents every round** — the isolation is non-negotiable. Never reuse an Agent invocation across rounds.
- **Rereview never exits the loop and never extends it.** Use the rereview's 🔴/🟡-disagreement count only to drive RESPOND (Step 4f) — never as an exit gate. A totally clean rereview does NOT end the loop; the loop always advances to another fresh REVIEW round (or the cap). Do not let rereview's other output (e.g. a passing remark about something unrelated) prompt new findings or new rounds — new issues are REVIEW's job; the next fresh REVIEW catches them. If a rereview output mentions a new unrelated issue, ignore it.
- **Defended disagreements go to humans, not back into the loop** — no feedback merging, no re-adjudication.
- **Always `event: "COMMENT"`** for any review posted by you or the subagents — never APPROVE / REQUEST_CHANGES.
- **Runs headless / non-interactively during the loop** — never ask the user a question while a REVIEW batch is in progress. If blocked mid-loop, record the limitation in the summary comment and proceed. **Exception:** after CAPPED, you MUST tell the user the round limit was hit and ask whether to continue (Step 5b). On CONVERGED, merge+delete without asking unless the user already opted out.
- **If `<CLI>` becomes unauthenticated mid-loop** (e.g. token expiry), stop and report it in the chat reply with the loop's state so the user can resume manually.

## Decision-making: act, don't ask

This flow is meant to run end-to-end without check-ins. Make the calls yourself:

- **Triage each finding yourself.** Don't present the triage to the user for approval. You read the code, you make the call.
- **Apply fixes and push without asking.** Routine forward progress on the feature branch the user just opened does not require a confirmation prompt.
- **Reject findings confidently** when you have evidence the finding is wrong. Cite the evidence (in `rejected_log` and inline if helpful) — the rereview will independently re-check it.
- **Defend disagreements confidently** when you still believe you're right after the rereview challenge. Defending is legitimate — it routes the call to a human, it does not mean you were wrong.
- **Pick one resolution** when a finding has multiple reasonable fixes. Choose the one most consistent with the surrounding code and the project's conventions; note the choice in the commit message.

Reserve `AskUserQuestion` for genuinely ambiguous situations the user must resolve — not for routine triage, push approval, in-loop disagreements, or the default post-convergence merge. Examples of when to actually ask:

- **After CAPPED:** always ask whether to continue another review batch (required — Step 5b).
- BEFORE the loop starts: the PR's target branch is unclear (no `main`, multiple plausible bases).
- BEFORE the loop starts: pushing a local-only branch for the first time (the user may not realize it's local-only).
- Anything destructive beyond the default merge+branch-delete on CONVERGED (force-push, closing/reopening PRs, touching unrelated branches, admin-bypass merge).

Once a REVIEW batch is running, never ask mid-batch — record any blocker in the summary and proceed. After the batch ends: on CONVERGED merge (unless opted out); on CAPPED ask to continue.

If you find yourself drafting a question that boils down to "is my plan OK?" or "should I merge now that we converged?" — don't. Execute the default (merge+delete), report what you did.
