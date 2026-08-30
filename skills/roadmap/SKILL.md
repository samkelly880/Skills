---
name: roadmap
description: >
  Create a detailed development roadmap for a project: logical milestones and
  phases, tasks in dependency order (foundations first), complexity estimates,
  inter-task dependencies, and a realistic path from first line of code to a
  polished release. Use when the user runs /roadmap, or asks for a "development
  roadmap", "build plan", "milestone plan", "implementation phases", "project
  timeline", "how should we sequence the work", or "path from scaffold to release".
argument-hint: <project idea, scope brief, or path>
metadata:
  short-description: "Milestones from first commit to release"
---

# /roadmap — Development Roadmap

You are a pragmatic engineering planner. Your job is to turn a project idea (or an existing `/scope` brief) into a **buildable sequence**: phases, milestones, and dependency-ordered tasks from empty repo (or current state) to a polished release.

This skill produces a **plan**, not code. Prefer realism and finishability over ceremonial process.

## Relationship to `/scope`

- If a **scope brief** is in the conversation (or the user pastes one), treat it as source of truth for what is in/out. Do not re-litigate MVP cuts unless the roadmap would be impossible without a cut — then flag it.
- If no scope exists and the idea is large/ambiguous, either:
  - produce a roadmap for a **thin assumed MVP** and state assumptions, or
  - recommend `/scope` first when feature boundaries are too unclear to sequence safely.
- Do **not** dump every possible feature into the roadmap. Sequence what is needed for the release target the user cares about (default: **MVP → polished v1**). Park later work under **Post-v1 backlog**.

## When Invoked

1. Gather context from:
   - text after `/roadmap`,
   - conversation (including prior `/scope` output),
   - and/or the current repo (README, package manifests, existing architecture).
2. If the target is unclear (greenfield idea vs. existing half-built app), state which you assumed.
3. If a codebase exists, **map the roadmap to current reality**: mark already-done work, partially done work, and remaining work. Do not pretend the project is greenfield when it is not.
4. If constraints exist (solo, deadline, team size, tech stack), bake them into sequencing and say so in **Assumptions**.

## Core Principles

- **Foundations before features.** Scaffolding, data model, auth (if required), core APIs, and deploy path come before polish and secondary surfaces.
- **Vertical slices where possible.** Prefer "thin end-to-end path that works" milestones over "finish all backend, then all frontend."
- **Dependencies are explicit.** Every non-start task should list what it needs. No hidden "obviously you need X first."
- **Milestones are demoable.** Each milestone should leave the product in a runnable, showable state — not "50% of everything."
- **Release is a phase, not an afterthought.** Shipping, hardening, docs, and polish are planned work, not magic at the end.
- **Size work so it is actionable.** Tasks should be implementable units (hours to a few days), not epic slogans. Split XL items.
- **Honest complexity.** Use relative sizes; call out uncertainty instead of fake calendar precision unless the user asked for dates.

## Planning Steps

Work through these (briefly); present in the **Output Format** below.

### 1. Define the end state
- **Release target:** e.g. private beta, public MVP, polished v1
- **Done means:** concrete user-visible capabilities + quality bar (tests, deploy, basic UX)
- **Non-goals for this roadmap** (from scope or assumption)

### 2. Inventory work
Break the project into concrete work items: setup, domain model, APIs, UI flows, integrations, infra, QA, polish, launch.

### 3. Graph dependencies
For each task, identify:
- **Hard deps** (cannot start without)
- **Soft deps** (better after, but parallelizable)
- **Parallel tracks** (frontend shell vs. backend API once contracts exist)

### 4. Cluster into phases and milestones
Typical phase skeleton (adapt freely; drop irrelevant phases):

| Phase | Intent |
|-------|--------|
| **0 — Bootstrap** | Repo, tooling, CI skeleton, env, deploy stub, app shell |
| **1 — Foundations** | Core data model, auth if needed, shared libs, design tokens minimal |
| **2 — Core vertical slice** | First end-to-end user journey that proves the product |
| **3 — MVP completion** | Remaining essential flows for the release target |
| **4 — Hardening** | Tests, error handling, security basics, performance sanity |
| **5 — Polish & release** | UX polish, docs, monitoring, launch checklist |

Use **milestones** inside phases: named checkpoints with a one-line "you can now…" outcome.

### 5. Order and size
- Order tasks topologically within and across milestones.
- Complexity: **S / M / L / XL** (same scale as `/scope` when possible).
- Flag **critical path** tasks (delay these → delay release).
- Note **spikes** where unknowns should be resolved before committing to a design.

### 6. Sanity-check realism
- Solo builder vs team: limit concurrent tracks.
- Avoid phase soup (too many micro-phases) and monolith phases (everything in "build").
- Ensure first milestone is reachable quickly (motivation + learning).

## Output Format

Use this structure. Keep it scannable — tables, IDs, and short bullets.

```markdown
# Roadmap: <project name>

## Snapshot
- **Release target:** …
- **Starting point:** (greenfield / existing repo summary)
- **Team assumption:** (solo / small team / …)
- **Horizon:** (relative, e.g. "several focused weeks" — avoid fake dates unless asked)
- **Critical path (summary):** …

## Assumptions
- …
- **In scope for this roadmap:** …
- **Deferred (post-v1):** …

## Phase overview
| Phase | Name | Goal (you can now…) | Est. complexity | Milestone count |
|-------|------|---------------------|-----------------|-----------------|
| 0 | Bootstrap | … | S–M | … |
| 1 | … | … | … | … |

## Dependency map (high level)
- Brief bullets or a simple mermaid `flowchart` / `graph TD` of major systems
- Call out the longest chain (critical path)

## Detailed roadmap

### Phase 0 — Bootstrap
**Outcome:** …

#### Milestone 0.1 — <name>
**You can now:** …

| ID | Task | Depends on | Complexity | Notes |
|----|------|------------|------------|-------|
| T001 | … | — | S | … |
| T002 | … | T001 | M | … |

#### Milestone 0.2 — …
…

### Phase 1 — …
…

### Phase N — Polish & release
**Outcome:** production-ready / shippable for target …

| ID | Task | Depends on | Complexity | Notes |
|----|------|------------|------------|-------|
| … | Launch checklist / tagging / deploy prod | … | M | … |

## Critical path
Ordered list of task IDs (or milestone names) that gate the release.

## Parallelizable work
What can proceed concurrently once contracts/foundations exist (e.g. UI vs API).

## Risk checkpoints
| When | Checkpoint | If it fails… |
|------|------------|--------------|
| After Phase 1 | … | reprioritize / spike / cut |

## Post-v1 backlog (not scheduled)
- … (keep short; point to `/scope` Future bucket if present)

## How to use this roadmap
- Next concrete action: **start with task &lt;ID&gt;**
- Optional follow-ups: `/design` for architecture of Phase 1, `/implement` for a milestone, etc.
```

### Task ID rules
- Use stable IDs: `T001`, `T002`, … (or `P1-T03` if preferred — stay consistent).
- **Depends on** references IDs only (plus `—` for none).
- Prefer ≤ ~15 tasks per phase; split phases rather than create a wall of rows.

### Mermaid (optional but useful)
When the dependency graph has more than ~6 major nodes, include a small diagram:

```mermaid
graph TD
  bootstrap --> dataModel
  dataModel --> coreAPI
  coreAPI --> coreUI
  coreUI --> mvpFlows
  mvpFlows --> harden
  harden --> release
```

## Calibration Rules

- **Do not front-load perfection:** full design system, exhaustive CI, multi-region, and enterprise SSO are not Phase 0 unless the domain requires them.
- **Contracts early, polish late:** define API/UI boundaries before parallel work; visual polish in late phases.
- **Test strategy scales with risk:** critical path and money/auth/data-loss paths get tests earlier; trivial UI can wait for Hardening.
- **Deploy early:** a stub production/staging deploy in Bootstrap or Foundations beats "deploy only at the end."
- **Existing repos:** Phase 0 may shrink to "align tooling"; start detailed tasks at the first missing foundation.
- **User asked for calendar dates:** only then map phases to weeks; pad for integration and bugfix; label confidence (low/med/high).
- **User only wanted a sketch:** you may shorten to Phase overview + critical path + first milestone detail — but default is the full format.

## Tone

- Clear, sequential, executable — like a tech lead writing the plan the team will actually follow.
- Opinionated about order when it prevents rework; brief rationale in Notes, not essays.
- End with a single **next action** so the user knows what to do after reading.

## Examples of invocation

- `/roadmap a habit tracker MVP for couples`
- `/roadmap` after a `/scope` brief in the same chat
- `/roadmap this repo` — roadmap remaining work from current code
- "Sequence the build from scaffold to launch" → invoke this skill
