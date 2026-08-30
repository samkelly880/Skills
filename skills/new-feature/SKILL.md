---
name: new-feature
description: >
  Orchestrate a feature from idea to verified implementation: /grill-me first, then only relevant skills (/scope, /architect, /backend-architect, /database-engineer, game-design specialists as needed), then /implement, /test, /code-review, /reality-checker. Do not invoke irrelevant skills. Do not modify code during discovery/planning unless explicitly instructed. Use when the user runs /new-feature, or wants end-to-end feature delivery from idea through verification.
argument-hint: <feature, bug, project, or brief>
metadata:
  short-description: "Idea → verified feature orchestration"
---

# /new-feature — Feature Delivery Orchestration

Take a feature from idea to **verified** implementation by chaining only the skills that matter.

## Hard rules

1. **Discovery before code.** Do not modify the project during grill/scope/architecture unless the user explicitly allows it.
2. **Invoke specialists only when relevant** — never because they exist.
3. Treat `$ARGUMENTS` / the user brief as the starting claim; refine via `/grill-me`.
4. Stop and confirm the plan with the user after discovery/design if major ambiguity remains — then implement.
5. "Done" requires `/test` + `/code-review` + `/reality-checker`, not just commits.

## Pipeline

### 1. Clarify — always
- Run **`/grill-me`** on the feature until behavior, non-goals, and edge cases are clear.

### 2. Select specialists (conditional)
| Condition | Skill |
|-----------|-------|
| Feature may be too large / needs MVP cut | `/scope` |
| Touches system structure, module boundaries, cross-cutting design | `/architect` |
| APIs, auth, services, queues, backend shape | `/backend-architect` |
| Schema, persistence, migrations, queries | `/database-engineer` |
| Core gameplay rules | `/mechanic` |
| Numbers / fairness / progression tuning | `/balance` |
| Enemy behavior | `/enemy` |
| Boss encounter | `/boss` |
| Resources / sinks / shops | `/economy` |
| Spaces / arenas / flow | `/level-designer` |
| Worldbuilding | `/lore` |
| Story/quests/dialogue systems | `/narrative-designer` |

Skip any row that does not apply. Do not run the whole game-design suite for a pure API tweak.

### 3. Build
- **`/implement`** the approved feature (smallest vertical slice that matches the grilled spec).

### 4. Verify
- **`/test`** — failing-test-first or solid regression coverage for the behavior.
- **`/code-review`** — implementation quality on the change.
- **`/reality-checker`** — challenge "it's done"; require evidence.

## Output

Track a short run log:

```markdown
# New feature: <name>
## Grilled requirements
## Skills invoked (and why)
## Skills skipped (and why)
## Implementation summary
## Verification
## Reality-check verdict
```

