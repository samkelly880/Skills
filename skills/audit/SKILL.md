---
name: audit
description: >
  Comprehensive project-audit orchestration: inspect first, then only relevant auditors (/review, /security-engineer, /dependency-auditor, /performance-benchmarker, /accessibility-auditor, /api-tester, /reality-checker). Combine findings, dedupe, prioritize by severity/impact; separate confirmed vs recommendations vs N/A. Do not modify the project. Use when the user runs /audit, or wants a multi-area project audit / health check.
argument-hint: <feature, bug, project, or brief>
metadata:
  short-description: "Selective multi-area project audit (read-only)"
---

# /audit — Project Audit Orchestration

Read-only multi-specialist audit. **Selective**, not "run everything."

## Hard rules

1. **Do not modify the project.**
2. Inspect the project; decide which audit areas apply.
3. Do **not** invoke every auditor automatically.
4. Merge findings: dedupe, prioritize by severity × practical impact.
5. Label each item: **Confirmed** · **Recommendation** · **Not applicable / not reviewed**.

## Pipeline

### 1. Triage
Identify project type (web, API, game, library, infra) and attack/risk surfaces.

### 2. Conditional auditors
| If relevant… | Skill |
|--------------|-------|
| Implementation quality | `/review` |
| App security | `/security-engineer` |
| Dependencies / supply chain | `/dependency-auditor` |
| Measurable perf concerns | `/performance-benchmarker` |
| UI / web a11y | `/accessibility-auditor` |
| HTTP/API surfaces | `/api-tester` |
| "Are we production-ready?" claim | `/reality-checker` |

### 3. Synthesize
Single prioritized report — no duplicate walls of text from each specialist.

## Output

```markdown
# Audit: <project>
## Scope & what was reviewed
## Skipped auditors (why)
## Prioritized findings
| Sev | Area | Finding | Status |
|-----|------|---------|--------|
| … | … | … | confirmed/recommendation |

## Strengths
## Not reviewed / residual risk
```

