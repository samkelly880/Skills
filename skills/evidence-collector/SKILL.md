---
name: evidence-collector
description: >
  Collect concrete evidence that a feature or fix works: determine what must be demonstrated; inspect tests, logs, output, and screenshots where appropriate; identify insufficient evidence; produce a concise evidence report. Never treat an untested assumption as proof. Use when the user runs /evidence-collector, or asks for proof it works, evidence pack, verification artifacts, or to gather demo evidence before calling something done.
argument-hint: <context, path, or brief>
metadata:
  short-description: "Concrete proof a feature/fix works"
---

# /evidence-collector — Evidence Pack

Collect **proof**, not narratives.

## Hard rules

1. **Assumptions are not evidence.**
2. Define the claim, then list required demonstrations.
3. Prefer reproducible commands and their output.
4. Mark each item: **strong** / **weak** / **missing**.
5. Hand off to `/reality-checker` for the pass/fail judgment when asked for readiness.

## When invoked

1. State the claim to prove.
2. Decide evidence types needed (unit/integration tests, manual script, HTTP transcript, UI screenshot, log excerpt).
3. Run or locate artifacts; store/report paths.
4. Produce the evidence report with gaps called out.

## Output format

```markdown
# Evidence report: <claim>

## Required demonstrations
1. …

## Collected evidence
| Item | Artifact | Strength | Notes |
|------|----------|----------|-------|
| … | path/command | strong/weak/missing | … |

## Insufficient / missing
…

## Commands to reproduce
```

