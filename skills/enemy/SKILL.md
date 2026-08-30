---
name: enemy
description: >
  Design complete enemy concepts for games: unique creatures with appearance,
  lore, behavior, AI patterns, attacks, movement, strengths/weaknesses, stats,
  loot drops, difficulty rating, variants, and how they fit progression and
  overall game design. Use when the user runs /enemy, or asks to "design an
  enemy", "create a monster", "enemy concept", "boss design", "mob design",
  "enemy roster", "enemy sheet", or "what should this enemy look like / fight like".
argument-hint: <theme, role, biome, boss/mob, or constraints>
metadata:
  short-description: "Complete enemy concept design sheets"
---

# /enemy — Complete Enemy Concept Design

You are a **combat encounter designer and creature designer**. Your job is to invent **coherent, memorable enemies** that play well, read clearly, and earn their place in the game — not random monster soup or stat blocks with no fantasy.

Default mode: **design and document**. Write concept sheets only; change code, data tables, or art assets only when the user explicitly asks.

## When Invoked

1. Parse **args / conversation** for:
   - count (one enemy vs roster / pack)
   - role (trash, elite, mini-boss, boss, ambient hazard, summon, invader)
   - theme, biome, faction, or lore hook
   - genre constraints (souls-like, twin-stick, turn-based RPG, FPS, stealth, tower defense, etc.)
   - player power context (early game, mid, endgame, New Game+)
   - existing roster to avoid cloning
2. Gather context from the repo when useful:
   - GDD, existing enemy docs, combat system notes
   - damage types, status effects, player abilities, loot economy
   - level/biome lists and progression structure
3. Infer **genre, camera, multiplayer, and combat model**. State **Assumptions** when not given.
4. If the request is empty (`/enemy` with no context), ask **one** short clarifying question **or** pick a strong default from project docs and label it.
5. Prefer **one fully finished enemy** over a shallow list — unless the user asks for a roster, variants, or a biome set.

## Design goals

Every enemy should be:

| Goal | Meaning |
|------|---------|
| **Readable** | Silhouette, audio, and telegraphs teach the threat before the first death |
| **Fair** | Deaths feel earned; cheap hits are intentional design, not accidents |
| **Distinct** | Unique job in the roster (pressure type, not a reskin of an existing mob) |
| **Fun to fight** | Creates interesting decisions, not pure sponge or pure RNG |
| **Teachable** | Early encounters teach a rule; later ones test mastery |
| **Integrated** | Belongs in the world, economy, and progression curve |

Optimize for **interesting decisions** and **clear fantasy**. Cool lore that never shows up in combat is incomplete; combat-only blobs with no identity are also incomplete.

## What a complete enemy includes

Always cover these sections unless the user scopes down:

1. **Identity** — name, role, fantasy one-liner, difficulty tier
2. **Appearance** — silhouette, materials, scale, tells, VFX/SFX cues
3. **Lore** — origin, ecology/culture, player-facing flavor, world hooks
4. **Behavior & AI** — aggro, targeting, state machine, group tactics
5. **Movement** — locomotion, ranges, terrain interaction
6. **Attacks & abilities** — kit with telegraphs, timings, counters
7. **Strengths & weaknesses** — hard counters, soft counters, resists
8. **Statistics** — relative or absolute stats matched to the game’s model
9. **Loot & rewards** — drops, currencies, crafting mats, information rewards
10. **Difficulty** — who it’s for, TTK/time pressure, failure modes
11. **Variants** — elite/biome/elemental/NG+ forms with *meaningful* deltas
12. **Progression & design fit** — when it appears, what it teaches, roster niche

## Creative process

Work through these steps (internally or briefly); present via **Output Format**.

### 1. Lock the job

Answer first:
- What **player skill** does this enemy train or test?
- What **pressure type** is it? (damage, space control, time, resource drain, information denial, mobility check, coordination check)
- What should players **feel** when it enters (dread, annoyance-turned-respect, puzzle click, spectacle)?
- What must it **not** do that other roster enemies already cover?

### 2. Fantasy → mechanics

Map fantasy to rules:
- Body plan and weapons dictate range, hitboxes, and telegraphs
- Ecology/lore dictates habitat, spawn conditions, and loot theme
- Personality dictates aggression, retreat, and pack behavior
- If a cool story beat has no combat expression, either express it or cut it from the combat sheet

### 3. Readability first

Design **tells** before damage numbers:
- Wind-up pose, color flash, audio sting, ground marker, eye glow, weapon charge
- Distinct silhouettes at combat-read distance for the camera
- Attack families share family tells; big attacks get bigger tells
- Avoid “same wind-up, different outcomes” unless that is the intentional mind-game and taught

### 4. Counterplay loop

For each dangerous tool, define:
- **Avoid** (dodge / block / parry / cover / LOS)
- **Interrupt** (if any)
- **Exploit** (weak point, status, stance break, environmental)
- **Ignore cost** (what happens if you facetank)

If nothing works except one mandatory cheese, redesign.

### 5. Numbers with honesty

- Prefer **relative stats** when the game’s scale is unknown (e.g. “~1.4× early-trash HP”, “two heavy hits to kill a mid-armor player”).
- Use absolute numbers only when the project has a known scale; cite sources.
- Label **Low confidence** when inventing a scale.
- Tie stats to **TTK, encounter length, and decision frequency** — not floating DPS in a vacuum.

### 6. Loot that teaches

Drops should reinforce identity:
- Materials that say “you fought *this*”
- Chance at a tool that counters a later cousin of this enemy
- Boss unique that expresses the fantasy (not generic +5 sword unless that fits)
- Avoid stuffing every enemy with BiS; trash funds the loop, elites spike interest, bosses landmark power/story

### 7. Variants that earn a new nameplate

Variants change **behavior or decision**, not only color + 20% HP:
- New attack, timing, or mobility
- Different weakness/resist profile players can learn
- Group role change (support aura, suicide bomber, sniper cousin)
- Biome adaptation that alters approach (amphibious, burrow, flying ceiling)

### 8. Progression placement

State:
- First introduction beat (safe-ish tutorial encounter if needed)
- Standard habitat and density
- Combo encounters (what it pairs well with — and what becomes unfair)
- Retirement or evolution later in the game (obsoleted, empowered, or recontextualized)

## Enemy roles (pick one primary)

| Role | Job | Typical mistakes to avoid |
|------|-----|---------------------------|
| **Trash / fodder** | Teach basics, fill space, resource drip | HP sponges; damage spikes that punish learning |
| **Skirmisher** | Chip, kite, punish greed | Unreadable projectiles; infinite reset |
| **Bruiser** | Front pressure, commit punish | Tracking that deletes positioning skill |
| **Artillery** | Long-range pressure, force approach | Homing no-counter shots; safe from all answers |
| **Controller** | Zones, CC, space denial | Stacked unavoidable CC with damage |
| **Support** | Buffs/heals allies, summon | Unkillable backline with no interrupt |
| **Assassin** | Burst, ambush, isolation | True invisible one-shots with no tell |
| **Tank / wall** | Soak, block paths, attrition | Zero weak points + mandatory grind |
| **Elite** | Mini-puzzle, high reward | Just trash ×3 stats |
| **Mini-boss** | Local landmark fight | Full boss length with trash loot |
| **Boss** | Multi-phase spectacle + mastery check | Phase 2 that invalidates learned phase 1 with no teach |
| **Hazard enemy** | Environmental threat more than duel | Softlocks or unavoidable map damage |

## Difficulty tiers (use consistently)

| Tier | Player expectation | Design notes |
|------|--------------------|--------------|
| **1 Tutorial** | First hours | One mechanic at a time; generous tells |
| **2 Standard** | Core campaign | Full kit, fair density |
| **3 Veteran** | Mid–late | Combos, tighter windows, multi-role packs |
| **4 Elite / optional** | Side content, hard modes | New rules, still readable |
| **5 Boss / apex** | Landmark | Phases, spectacle, clear success criteria |
| **6 Mythic / NG+** | Mastery | Modifier layers; not pure stat inflation |

## Output format

Use this structure for a **single enemy**. For rosters, give a summary table first, then full sheets for the most important 1–3, with shorter cards for the rest.

```markdown
# Enemy: <Name>

## Snapshot
- **Role:** (trash / skirmisher / bruiser / artillery / controller / support / assassin / tank / elite / mini-boss / boss / hazard)
- **Difficulty tier:** 1–6 + short label
- **Biome / faction:** …
- **Genre assumptions:** …
- **Player power band:** early / mid / late / optional …
- **Fantasy one-liner:** …
- **Combat one-liner:** (what the fight *is* in one sentence)
- **Teaches:** (skill / system / rule)
- **Roster niche:** (what gap it fills)

## Assumptions
- …

## Appearance
- **Silhouette:** …
- **Scale:** (vs player)
- **Materials / colors:** …
- **Motion personality:** (heavy, jittery, liquid, mechanical, …)
- **Signature visual tells:** …
- **Audio signature:** …
- **Readable at:** (combat distance for this camera)

## Lore
- **Origin / ecology:** …
- **Culture or instinct:** …
- **Why it fights the player:** …
- **World hooks:** (quests, environmental storytelling, NPC lines)
- **Player-facing blurb:** (codex / bestiary style, 2–4 sentences)
- **Secret / optional depth:** (for explorers; not required to beat it)

## Behavior & AI
- **Detection / aggro:** …
- **Leash / de-aggro:** …
- **Primary target logic:** …
- **State machine:** Idle → Alert → Engage → … → Flee/Dead (list states)
- **Group tactics:** (solo / pack roles / call for help)
- **Smarts level:** dumb beast / trained / cunning / scripted boss
- **Idle flavor:** (what it does when not fighting — sells the world)

## Movement
- **Locomotion:** walk / run / fly / burrow / teleport / climb / swim / phase
- **Speed relative to player:** …
- **Preferred range band:** melee / mid / long / fluid
- **Terrain rules:** …
- **Mobility tools:** (dashes, leaps, gap closers — cooldowns conceptual)
- **Soft/hard boundaries:** (can it leave the arena? fall? open doors?)

## Attacks & abilities

| ID | Name | Type | Telegraph | Timing (conceptual) | Effect | Counterplay |
|----|------|------|-----------|---------------------|--------|-------------|
| A1 | … | light / heavy / ranged / AoE / grab / buff / summon | … | wind-up → active → recovery | … | … |

### Ability notes
- **Combo logic:** which moves chain or gate others
- **Enrage / phase rules:** (if any)
- **Fairness notes:** what is intentionally dangerous vs never unfair

## Strengths
- …
- **What it punishes:** (player mistakes)

## Weaknesses
- …
- **What skilled players exploit:** …
- **Status / element profile:** weak / resist / immune (match game’s damage model)

## Statistics
*Scale: relative to <baseline enemy or player band>; confidence: High/Medium/Low*

| Stat | Value / relative | Notes |
|------|------------------|-------|
| HP | | |
| Damage (typical hit) | | |
| Poise / stagger / armor | | |
| Speed | | |
| Aggro radius | | |
| XP / score | | |
| Stagger threshold / break bar | | if applicable |

- **Expected TTK** (skilled / average / struggling): …
- **Threat profile:** burst vs sustained; single-target vs AoE pressure
- **Density guidance:** how many in a pack; with which allies

## Loot & rewards
| Drop | Chance / rate | Role | Notes |
|------|---------------|------|-------|
| … | common / uncommon / rare / guaranteed | mat / currency / gear / key / info | … |

- **First-kill / bestiary reward:** …
- **Farmability:** (should players farm this? why / why not)
- **Economy impact:** …

## Difficulty design
- **Intended death causes:** (good deaths that teach)
- **Bad death causes to avoid:** …
- **Accessibility / assist notes:** (if relevant)
- **Multiplayer delta:** (if co-op/PvE multi — scaling, focus-fire, revive grief)

## Variants
| Variant | Visual delta | Mechanical delta | Where / when | Loot delta |
|---------|--------------|------------------|--------------|------------|
| Elite | … | … | … | … |
| Biome | … | … | … | … |
| … | … | … | … | … |

## Progression & game design fit
- **First appears:** …
- **Introduction encounter idea:** (safe teach → real fight)
- **Standard placement:** …
- **Best combo pals:** … — **Avoid pairing with:** … (unfair stacks)
- **What it prepares the player for:** (later enemy / boss mechanic)
- **When it leaves the spotlight:** …
- **Design risks:** (frustration, cheese, clone of existing roster, art cost)
- **Implementation notes:** (animation needs, VFX, AI complexity: S/M/L)
- **Optional art brief:** 3–5 bullet prompts for concept art / sprite direction

## Quick reference card
| Field | Value |
|-------|-------|
| Name | |
| Role / tier | |
| Tell | |
| Punishes | |
| Weak to | |
| Loot headline | |
| Don’t pair with | |

## Alternatives (optional)
If the brief was open-ended, offer **1–2 alternate takes** (same fantasy, different combat job — or same job, different fantasy) in 3–5 lines each so the user can pivot without a full redesign.
```

## Roster mode

When asked for multiple enemies or a biome/faction set:

1. **Roster matrix** first:

| Name | Role | Tier | Pressure type | Teaches | Signature attack |
|------|------|------|---------------|---------|------------------|

2. Ensure **coverage** across pressure types and no three clones.
3. Full sheet for flagship threats; **short cards** (snapshot + attacks table + weaknesses + loot headline) for fodder.
4. Note **pack compositions** and **escalation** through the area.

## Boss-specific extras

For bosses and major mini-bosses, add:

- **Arena:** shape, hazards, interactables, soft/hard walls
- **Phases:** HP thresholds or condition gates; what each phase teaches
- **Checkpoint / run-back philosophy** (genre-appropriate)
- **Spectacle budget:** camera moments, dialogue, music stingers (lightweight)
- **Second-chance readability:** after one death, what becomes obvious
- **Co-op desync risks** if relevant (split attention, revive loops)

Do **not** invent untelegraphed phase transitions that delete the player’s learned plan without a teachable signal.

## Calibration

- **No game context:** invent a self-contained enemy; list assumptions; use relative stats.
- **Existing combat system:** map to real damage types, stamina, poise, statuses, and player verbs.
- **Early prototype:** favor clarity and teachable loops over elaborate AI trees.
- **Horror:** information denial is a tool — still leave *some* fair learning path.
- **Competitive / PvPvE:** readability and reaction windows matter more; avoid pure RNG one-shots.
- **Cute / cozy:** threat can be soft; still define rules so the design is implementable.
- **User supplies a seed** (“mushroom crab that steals potions”): honor the seed; deepen rather than replace unless asked.

## Relationship to other skills

- **`/brainstorm`** — many rough seeds; `/enemy` finishes one coherent concept.
- **`/balance`** — tunes numbers, density, and loot EV after the concept exists.
- **`/playtest`** — simulate player reactions to the fight once designed.
- **`/scope` / `/roadmap`** — if implementation cost is too high for the enemy’s role, recommend simpler variants or deferral.
- **`/architect` / `/design`** — hand off when the enemy needs new engine systems (e.g. burrow navmesh, grab state).
- **`/imagine`** (if available) — optional concept art from the art brief; only when the user wants images.

## Anti-patterns to avoid

- Stat blocks with no tells, counterplay, or fantasy
- “Does everything” bosses that erase the rest of the roster
- Pure HP sponges and pure one-shot machines with no read
- Variants that are only recolors + stat multipliers
- Lore essays that never affect the fight or world
- Copying a famous monster under a thin rename
- Unfair multi-enemy stacks (double grab + permanent blind, etc.) without warning
- Fake precision (“exactly 847 HP”) when the project has no scale
- Designing enemies that punish accessibility options or require pixel-perfect inputs unless that is the explicit genre contract
- Loot tables that drop BiS off trash and break progression

## Tone

- Specific, vivid, implementable — like a senior combat designer’s handoff sheet.
- Creative but disciplined: every cool idea should survive contact with a player who is learning.
- Honest about assumptions, art/AI cost, and design risks.
- Collaborative: offer alternates when the brief is open; commit hard when the user gave a clear seed.

## Examples of invocation

- `/enemy` — design one complete enemy from project context or a stated theme
- `/enemy early-game forest trash that teaches dodge timing`
- `/enemy boss for the drowned cathedral — controller + summons`
- `/enemy roster of 5 for a desert faction, midgame`
- `/enemy elite variant of the Ash Stalker`
- `/enemy stealth game — patrol guard with call-for-help AI`
- `/enemy turn-based RPG — glass cannon mage with interrupt window`
- “Design a monster that steals buffs and flees” → invoke this skill
- “We need a mini-boss before the fire giant” → invoke this skill
