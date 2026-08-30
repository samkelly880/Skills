---
name: game-design
description: >
  Game-design orchestration before code: /brainstorm if open-ended; /grill-me for clarity; only relevant specialists from /mechanic, /balance, /enemy, /boss, /economy, /level-designer, /lore, /narrative-designer; /scope if too large. Finish with a coherent design spec (goals, rules, interactions, edge cases, deps, balance, unresolved). Do not implement code. Use when the user runs /game-design, or wants gameplay designed without coding.
argument-hint: <feature, bug, project, or brief>
metadata:
  short-description: "Gameplay design spec (no code)"
---

# /game-design — Design Orchestration (No Code)

Produce a coherent **design specification**. **Do not implement code.**

## Hard rules

1. No production code, scaffolds, or "quick prototypes" unless the user explicitly asks.
2. Start with **`/brainstorm`** only if the concept is still open-ended; otherwise skip.
3. Use **`/grill-me`** when requirements/ambiguity need locking.
4. Invoke only relevant specialists from the game-design set.
5. Use **`/scope`** if the design is ballooning.

## Pipeline

1. Optional `/brainstorm` → `/grill-me` as needed.
2. Selective: `/mechanic` `/balance` `/enemy` `/boss` `/economy` `/level-designer` `/lore` `/narrative-designer`.
3. `/scope` if needed.
4. Synthesize one design spec.

## Output

```markdown
# Game design spec: <feature/system>
## Goals / player fantasy
## Rules & interactions
## Edge cases
## Dependencies on other systems
## Balancing considerations
## Unresolved decisions
## Non-goals
```

