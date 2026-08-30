---
name: research-feature
description: >
  Investigate a feature before implementation: /grill-me for behavior/constraints; /researcher for approaches; /tool-evaluator for tech choices; /architect /backend-architect /database-engineer when design/data involved. Finish with implementation recommendation, risks, deps, tradeoffs, unanswered questions. Do not implement. Use when the user runs /research-feature, or wants pre-implementation feature research.
argument-hint: <feature, bug, project, or brief>
metadata:
  short-description: "Clarify + research a feature (no implement)"
---

# /research-feature — Pre-Implementation Feature Research

Clarify and research a feature. **Do not implement.**

## Hard rules

1. No feature code / schema migrations / dependency adds unless explicitly asked.
2. **`/grill-me` first.**
3. Specialists only when needed for the decision.
4. End with a concrete recommendation and open questions.

## Pipeline

1. `/grill-me` — behavior & constraints.
2. `/researcher` — approaches.
3. Conditional: `/tool-evaluator`, `/architect`, `/backend-architect`, `/database-engineer`.
4. Synthesize recommendation.

## Output

```markdown
# Feature research: <name>
## Desired behavior (grilled)
## Recommended approach
## Alternatives
## Tradeoffs / risks / dependencies
## Unanswered questions
## Suggested next skill (/new-feature, /implement, …)
```

