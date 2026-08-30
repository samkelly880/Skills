---
name: game-audio
description: >
  Game audio design: sound effects, footsteps, combat audio, ambience, music systems, spatial audio, adaptive music, audio feedback, mixing, variation, and performance. Design audio that reinforces gameplay, not decoration-only. Use when the user runs /game-audio, or asks for SFX systems, adaptive music, spatial audio, combat sound design, mix buses, or audio feedback for mechanics.
argument-hint: <context, path, or brief>
metadata:
  short-description: "Game audio systems that serve gameplay"
---

# /game-audio — Game Audio Design

Audio as **gameplay feedback and emotion**, not wallpaper.

## Hard rules

1. Tie sounds to mechanics (confirm, warn, punish, reward).
2. Plan variation + interruption + priority (don't stack into mush).
3. Respect performance (voice limits, memory, streaming).
4. Complementary to `/mechanic` / `/lore` — reinforce existing fantasy.
5. Specify mix buses and ducking where it matters.

## Cover

SFX · footsteps/surface · combat cues · ambience · music/adaptive · spatial · UI feedback · mix · variation · perf

## Output format

```markdown
# Audio design: <scope>

## Gameplay audio goals
…

## Event → sound map
| Game event | Sound / music | Priority | Notes |
|------------|---------------|----------|-------|
| … | … | … | … |

## Systems (adaptive, spatial, buses)
…

## Variation & anti-fatigue
…

## Performance budgets
…
```

