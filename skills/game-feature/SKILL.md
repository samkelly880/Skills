---
name: game-feature
description: >
  Game-development feature orchestration: /grill-me for player experience; only relevant design skills (/mechanic, /balance, /enemy, /boss, /economy, /level-designer, /lore, /narrative-designer, /technical-artist, /game-audio); then /implement, /test, /playtest when applicable, /code-review, /reality-checker. Do not force irrelevant design stages. Use when the user runs /game-feature, or wants a full game feature from design through verification.
argument-hint: <feature, bug, project, or brief>
metadata:
  short-description: "Game feature: grill → design → build → verify"
---

# /game-feature — Game Feature Orchestration

Deliver a game feature with **selective** design, then build and verify.

## Hard rules

1. **`/grill-me` first** — player fantasy, exact requirements, non-goals.
2. Invoke only relevant design specialists — not the whole roster.
3. No code during design unless explicitly allowed.
4. Simple features may skip most design skills.
5. Verify with `/test`, `/playtest` when feel/fun matters, `/code-review`, `/reality-checker`.

## Pipeline

### 1. Grill
Player experience + acceptance criteria.

### 2. Conditional design
| Concern | Skill |
|---------|-------|
| Rules / systems | `/mechanic` |
| Numbers / fairness | `/balance` |
| Enemy AI/kit | `/enemy` |
| Boss fight | `/boss` |
| Progression/resources | `/economy` |
| Space/layout | `/level-designer` |
| Canon/world | `/lore` |
| Story/quests | `/narrative-designer` |
| Rendering/VFX/assets tech | `/technical-artist` |
| SFX/music systems | `/game-audio` |

### 3. Build & verify
- `/implement` → `/test` → `/playtest` (if applicable) → `/code-review` → `/reality-checker`

## Output

Design summary + implementation + verification + reality verdict; list skipped specialists with why.

