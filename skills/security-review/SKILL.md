---
name: security-review
description: >
  Security-focused review workflow: identify attack surface; /security-engineer primary; /threat-detection, /dependency-auditor, /api-tester when relevant; /code-review for implementation; /reality-checker against unsupported security claims. Separate confirmed vulns, plausible risks, info, false positives. Do not make security changes unless explicitly instructed. Use when the user runs /security-review, or wants a structured security assessment.
argument-hint: <feature, bug, project, or brief>
metadata:
  short-description: "Security review workflow (read-only unless asked)"
---

# /security-review — Security Review Orchestration

Structured defensive security assessment. **No security changes unless explicitly instructed.**

## Hard rules

1. Read-only by default (no "quick harden" commits unless asked).
2. Map attack surface first.
3. Separate **Confirmed vulnerability** · **Plausible risk** · **Informational** · **False positive**.
4. Specialists only when relevant to the surface.
5. Challenge marketing/"we're secure" claims with `/reality-checker`.

## Pipeline

1. Attack-surface inventory (auth, inputs, data stores, admin, APIs, deps, deploy config).
2. **`/security-engineer`** — primary review.
3. Conditional: `/threat-detection`, `/dependency-auditor`, `/api-tester`, `/code-review`.
4. **`/reality-checker`** on unsupported security claims.
5. Synthesize prioritized findings.

## Output

```markdown
# Security review: <target>
## Attack surface
## Confirmed vulnerabilities
## Plausible risks
## Informational
## False positives dismissed
## Recommended remediations (priority order)
```

