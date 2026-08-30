---
name: research
description: >
  Research orchestration for technical/project questions before implementation: clarify needed info; /researcher; /tool-evaluator for comparisons; /architect when design is affected; other specialists only if directly relevant. Concise conclusion with recommendation, alternatives, tradeoffs, risks, uncertainties. Do not modify the project. Use when the user runs /research, or wants a pre-implementation research answer.
argument-hint: <feature, bug, project, or brief>
metadata:
  short-description: "Research orchestration before implementation"
---

# /research — Research Orchestration

Answer technical questions **before** implementation. Read-only.

## Hard rules

1. **Do not modify the project.**
2. Clarify exactly what information is needed for the decision.
3. Specialists only when directly relevant.
4. Finish with a concise conclusion usable by implementers.

## Pipeline

### 1. Frame the question
Decision to unlock, constraints, success criteria for the research.

### 2. Core investigation
- **`/researcher`** — facts, sources, options.

### 3. Conditional
| Need… | Skill |
|-------|-------|
| Compare tools/libs/engines/services | `/tool-evaluator` |
| Impacts system structure | `/architect` |
| Backend/data specifics | `/backend-architect` / `/database-engineer` |

### 4. Conclude

## Output

```markdown
# Research conclusion: <topic>
## Recommended approach
## Alternatives considered
## Tradeoffs
## Risks
## Still uncertain
## Sources / confidence
```

