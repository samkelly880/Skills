---
name: clean-branches
description: >
  Find and delete stale local git branches — those fully merged into the base
  branch (main by default, or a branch the user names) with no unique commits.
  Always lists what it would delete and confirms first; never touches the current
  branch or the base/protected branches. After local deletion, offers to delete
  matching remote branches. Use when the user runs /clean-branches, says "clean up
  branches", "delete merged branches", "prune stale branches", "remove old
  branches", or "tidy up git branches".
argument-hint: "[base branch to compare against — defaults to main]"
---

# Clean Branches

Delete stale local git branches that are **fully merged into the base branch** (no
unique commits left to lose). Be careful: this deletes branches. Always show the
list and get confirmation before deleting anything.

## 1. Determine the base branch

- If the user passed a branch name in `$ARGUMENTS`, use it as the base.
- Otherwise default to `main`. If `main` doesn't exist, fall back to `master`, then
  to the repo's default branch (`git symbolic-ref refs/remotes/origin/HEAD` stripped
  to its branch name).
- Confirm the base branch exists: `git rev-parse --verify <base>`. If it doesn't,
  stop and ask the user which branch to compare against.

## 2. Refresh state

Make the merged-check accurate before judging anything:

```bash
git fetch --prune        # update remote-tracking refs, drop deleted ones
```

Note the current branch: `git rev-parse --abbrev-ref HEAD`.

## 3. Find fully-merged branches

List local branches whose commits are all already in the base branch:

```bash
git branch --merged <base> --format='%(refname:short)'
```

From that list, **exclude** (never delete):
- the base branch itself
- the currently checked-out branch
- protected branches: `main`, `master`, `develop`, `release` (and anything the
  user names as protected)

What remains is the deletion candidate set. If it's empty, tell the user there are
no stale branches and stop.

## 4. Show the list and confirm

Present the candidate branches to the user, e.g.:

```
These local branches are fully merged into <base> and will be deleted:
  - feature/old-login
  - fix/typo-readme
Base: <base> · current branch (kept): <current>
```

**Wait for explicit confirmation** before deleting. Do not proceed on a maybe.

## 5. Delete local branches

Use the safe delete flag, which refuses to remove anything not actually merged:

```bash
git branch -d <branch>
```

Delete each confirmed branch. If `git branch -d` ever refuses (branch not fully
merged), do NOT force with `-D` — report it to the user and let them decide.

## 6. Offer to delete remote branches

After local deletion, check whether any deleted branches still exist on the remote:

```bash
git ls-remote --heads origin <branch>
```

For any that do, list them and ask the user whether to delete them remotely too.
Only if the user confirms:

```bash
git push origin --delete <branch>
```

Never delete remote branches without a separate explicit confirmation.

## 7. Report

Summarize what happened: base branch used, which local branches were deleted, which
remote branches were deleted (if any), and anything skipped (protected, current, or
refused-because-unmerged). Report faithfully — if git refused a deletion, say so.
