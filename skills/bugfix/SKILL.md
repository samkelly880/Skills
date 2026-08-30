---
name: bugfix
description: >
  Fix a bug the user has found. Reproduce and confirm the failure, trace it to the
  true root cause (not just the symptom), apply a minimal targeted fix, then verify
  the fix by exercising the actual flow. Use when the user runs /bugfix, or says
  "there's a bug", "this is broken", "found a bug", "X isn't working", "fix this
  bug", or reports incorrect behavior.
argument-hint: <describe the bug, paste the error, or point at the failing behavior>
---

# Bugfix

The user has found a bug and wants it fixed. Work the loop below in order. Do not
skip to a patch before you understand the root cause, and do not declare victory
before you have verified the fix actually holds.

## 1. Understand the report

- Read the user's description / error / stack trace carefully. If `$ARGUMENTS`
  is empty, ask the user for the exact symptom, how to trigger it, and what they
  expected instead.
- Identify the smallest concrete failing case: the input, action, or flow that
  produces the wrong behavior.
- Note what "correct" looks like so you know when the bug is gone.

## 2. Reproduce

- Actually trigger the failure before changing anything — run the command, hit the
  endpoint, drive the flow, or write a quick failing test that captures it.
- Confirm you see the SAME symptom the user reported. If you can't reproduce it,
  say so and gather more detail rather than guessing at a fix.
- Keep the reproduction handy — it's what you'll re-run in step 5 to prove the fix.

## 3. Find the root cause

- Trace from the symptom back to the origin: read the relevant code, follow the
  data, add logging or a debugger where useful.
- Distinguish the root cause from the symptom. A crash three frames deep is usually
  not where the bug lives. Ask "why" until you reach the real defect.
- State the root cause in one sentence before writing any fix. If you can't, keep
  investigating.

## 4. Fix

- Apply the smallest change that corrects the root cause. Match the surrounding
  code's style and idioms.
- Do not refactor unrelated code, rename things, or "improve" beyond the bug unless
  it's necessary to fix it. Keep the diff reviewable.
- Consider adjacent cases the same root cause could break, and whether a regression
  test belongs alongside the fix.

## 5. Verify

- Re-run the exact reproduction from step 2 and confirm the symptom is gone.
- Run the relevant tests / build / typecheck for the area you touched.
- If you added a regression test, confirm it fails without the fix and passes with
  it.
- Report faithfully: what the bug was, the root cause, what you changed, and the
  evidence it's fixed. If anything is still failing or unverified, say so plainly.
