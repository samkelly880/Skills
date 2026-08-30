---
name: level-designer
description: >
  Game level design for arenas, levels, encounters, traversal, pacing, sightlines, player flow, cover, enemy placement, exploration, difficulty curves, and environmental storytelling. Consider existing mechanics and constraints; explain why major layout decisions support gameplay. Use when the user runs /level-designer, or asks for level/arena design, encounter layout, pacing, sightlines, cover, or difficulty curve in a space.
argument-hint: <context, path, or brief>
metadata:
  short-description: "Game levels, arenas, pacing, flow"
---

# /level-designer — Level & Arena Design

Design playable spaces that serve **this game's mechanics**.

## Hard rules

1. Read existing mechanics, camera, movement, and enemy kit before designing.
2. Every major layout choice explains **what gameplay it creates**.
3. Respect engine/performance constraints (streaming, draw distance, budget).
4. Complement `/mechanic`, `/enemy`, `/boss`, `/lore` — don't reinvent systems.
5. Deliver buildable briefs (maps, beats, encounter scripts), not vague mood boards only.

## Cover

Arenas · traversal · pacing beats · sightlines · cover · spawns · exploration rewards · difficulty curve · environmental storytelling hooks

## Output format

```markdown
# Level: <name>

## Fantasy & role in campaign
…

## Constraints (mechanics / tech)
…

## Layout overview
- Flow diagram / beat map

## Encounter & spawn plan
…

## Pacing & difficulty
…

## Why this layout
…

## Metrics / smoke checks (playtest)
…
```

