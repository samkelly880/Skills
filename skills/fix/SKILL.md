---
name: fix
description: >
  Bug-fixing orchestration: reproduce first; use /debugger if available for root cause; /test for failing reproduction; /bugfix for the smallest fix; then /test, /review, /reality-checker. Invoke security/performance/API/DB specialists only when evidence warrants. Never make speculative changes. Use when the user runs /fix, or wants a disciplined investigate-fix-verify bug workflow.
argument-hint: <feature, bug, project, or brief>
metadata:
  short-description: "Investigate → fix → verify bug orchestration"
---

# /fix — Bug Fix Orchestration

Fix bugs with **evidence**, not guess-and-thrash.

## Hard rules

1. **Reproduce before changing code.**
2. **No speculative edits** to "see if it goes away."
3. Prefer the **smallest correct fix** (`/bugfix`).
4. Specialists only when evidence points there.
5. Not fixed until re-test + review + reality-check pass the claim.

## Pipeline

### 1. Investigate
- Capture symptoms, repro steps, expected vs actual, environment.
- Reproduce (or document blocker if unreproducible).
- If **`/debugger`** (or equivalent debugger skill) exists, use it to trace likely root cause; otherwise do structured root-cause analysis yourself from stacks/logs/code.

### 2. Lock the bug
- **`/test`** — add or identify a failing test / reliable reproduction that fails **only** because of this bug.

### 3. Fix
- **`/bugfix`** — minimal targeted fix for the true root cause.

### 4. Verify
- **`/test`** again (must go green for the repro).
- **`/review`** on the fix diff.
- **`/reality-checker`** on the claim "bug is fixed."

### 5. Conditional specialists
| Evidence suggests… | Skill |
|--------------------|-------|
| Security issue | `/security-engineer` |
| Perf regression / hot path | `/performance-benchmarker` then maybe `/optimize` |
| API contract / authz | `/api-tester` |
| Data integrity / queries | `/database-engineer` |

## Output

```markdown
# Fix: <bug>
## Repro / evidence
## Root cause
## Fix summary
## Verification
## Reality-check verdict
```

Only tell the user the bug is fixed after verification is green (align with `/test` discipline).

