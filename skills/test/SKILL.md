---
name: test
description: >
  Reproduce a reported bug with a purposefully failing test that fails only
  because of that bug, then fix the bug and iterate until the test passes.
  Only tell the user the bug is fixed after the test passes.
  Use when the user runs /test, or says "write a failing test then fix",
  "TDD fix", "red-green this bug", "prove it with a test then fix", or wants
  a failing regression test before applying a fix.
---

# Test (red → green bug fix)

Drive a bug fix with a failing regression test. Do **not** claim the bug is fixed until the new test passes.

## Arguments

`$ARGUMENTS` is the bug report / reproduction notes. Treat it as the source of truth for expected vs actual behavior.

## Hard rules

1. **Write the test first.** Do not change production code until the new test exists and has been run.
2. **The first run must fail for the right reason.** Failure must be caused by the reported bug — not missing imports, wrong paths, bad assertions, or flaky setup.
3. **Only then fix the bug.** Keep the fix minimal and targeted at the failing assertion.
4. **Re-run the same test** (or the smallest suite that includes it) after each fix attempt.
5. **If it still fails, keep iterating** on the fix (or the test, only if the test was wrong) until it passes.
6. **Silence until green.** Do not tell the user the bug is fixed — and do not imply success — until the regression test passes. Status updates like "wrote the failing test" / "still failing, adjusting fix" are fine.

## Workflow

### 1. Understand the bug

- Parse `$ARGUMENTS` (and any linked files, stack traces, or repro steps).
- Identify: expected behavior, actual behavior, and the smallest surface that demonstrates it.
- If the bug is ambiguous enough that you cannot write a correct assertion, ask one clarifying question — then continue.

### 2. Write a purposefully failing test

- Add or extend a test in the project's existing test framework and layout.
- Assert the **correct** (desired) behavior — not the current broken behavior.
- Keep the test focused: it should fail because of this bug and nothing else.
- Prefer a regression test name that describes the bug (e.g. `handles empty input without throwing`).

### 3. Run the test — confirm red

- Run only the new/related test if the toolchain allows it; otherwise the smallest relevant suite.
- Confirm it **fails**.
- Confirm the failure mode matches the bug (assertion mismatch, exception, wrong output, etc.).
- If it fails for a setup/harness reason, fix the test harness first and re-run until the failure is purely the bug.
- If it **passes** unexpectedly, the test is not reproducing the bug — revise the test until it fails for the right reason (or confirm the bug is already gone and report that instead of "fixed").

### 4. Fix the bug

- Change production code only as needed to make the failing test pass.
- Avoid drive-by refactors unrelated to the failure.

### 5. Run the test — confirm green

- Re-run the same test/suite.
- If it fails: diagnose, update the fix, re-run. Repeat until it passes.
- Optionally run a slightly wider related suite to catch obvious breakage — but the gate for "fixed" is the new regression test passing.

### 6. Reply to the user (only after green)

When — and only when — the regression test passes, reply that the bug is fixed. Include briefly:

- What the test covers (file + test name)
- What the root cause was
- What you changed to fix it
- The command used to verify, and that it passed

If you stop before green (blocked, need input, out of scope), say the bug is **not** fixed yet and what remains.
