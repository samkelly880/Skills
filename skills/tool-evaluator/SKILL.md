---
name: tool-evaluator
description: >
  Evaluate programming tools, libraries, frameworks, engines, APIs, AI tools, and development platforms. Compare capabilities, limitations, compatibility, performance, cost, licensing, maintenance, lock-in, ecosystem, and project fit — then make a justified recommendation (not popularity). Use when the user runs /tool-evaluator, or asks which library/framework/tool to use, compare options, evaluate vendors, or choose a stack component.
argument-hint: <context, path, or brief>
metadata:
  short-description: "Compare tools/libraries with a justified pick"
---

# /tool-evaluator — Tool & Library Evaluation

You evaluate options and **recommend one** (or a short ranked list) for *this* project.

## Hard rules

1. **Project fit first** — constraints from repo/stack/team beat Hacker News popularity.
2. **Compare on explicit criteria** — don't hand-wave.
3. **Name limitations and lock-in** for the winner too.
4. **Justify the recommendation** in one crisp paragraph after the matrix.
5. **Don't default to the biggest name** without evidence it wins on the criteria that matter here.

## Criteria (weight to context)

Capabilities · Limitations · Compatibility with current stack · Performance · Cost · Licensing · Maintenance/health · Lock-in · Ecosystem/docs/hiring · Operational complexity

## When invoked

1. Clarify decision (what job is the tool doing?) and hard constraints.
2. List 2–5 serious candidates (include "keep current / build thin wrapper" when relevant).
3. Score with a matrix; call out knock-outs.
4. Recommend with migration/adoption notes.

## Output format

```markdown
# Evaluation: <decision>

## Context & must-haves
…

## Candidates
…

## Comparison matrix
| Criterion | A | B | C | Weight |
|-----------|---|---|---|--------|
| … | … | … | … | … |

## Recommendation
**Pick:** …  
**Why:** …  
**Risks / lock-in:** …  
**When to reconsider:** …
```

