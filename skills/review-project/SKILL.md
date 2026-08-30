---
name: review-project
description: >
  Project-review orchestration: inspect first; selective /code-review, /architect or /backend-architect, /security-engineer, /performance-benchmarker, /accessibility-auditor, /dependency-auditor, /reality-checker. Prioritized report of confirmed issues, risks, recommendations, strengths. Do not modify anything. Use when the user runs /review-project, or wants an independent assessment of an existing project.
argument-hint: <feature, bug, project, or brief>
metadata:
  short-description: "Independent project assessment (read-only)"
---

# /review-project — Independent Project Review

Read-only assessment. Selective specialists. **Do not modify anything.**

## Hard rules

1. No edits, no dependency upgrades, no refactors "while reviewing."
2. Triage project type → choose reviewers.
3. Skip irrelevant specialists.
4. Prioritize confirmed issues over style nits.

## Pipeline

Triage, then conditional:

| Concern | Skill |
|---------|-------|
| Code quality | `/code-review` |
| Structure / boundaries | `/architect` or `/backend-architect` |
| Security | `/security-engineer` |
| Perf | `/performance-benchmarker` |
| A11y | `/accessibility-auditor` |
| Deps | `/dependency-auditor` |
| Readiness claims | `/reality-checker` |

## Output

```markdown
# Project review: <name>
## Strengths
## Confirmed issues (prioritized)
## Risks
## Recommendations
## Skipped areas (why)
```

