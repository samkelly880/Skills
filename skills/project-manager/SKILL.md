---
name: project-manager
description: >
  Project management that turns goals and roadmaps into concrete executable work: dependencies, milestones, risks, blockers, sequencing, scope creep, and priorities; keep tasks appropriately sized. Work with existing `/roadmap` and `/scope` — don't create redundant planning systems. Use when the user runs /project-manager, or asks to break down work, sequence tasks, find blockers/dependencies, cut scope creep, or turn a roadmap into an execution plan.
argument-hint: <context, path, or brief>
metadata:
  short-description: "Executable plans from goals & roadmaps"
---

# /project-manager — Execution Planning

Turn goals into **sequenced, sized work**. Honor `/scope` and `/roadmap`; don't fork a second plan of record.

## Hard rules

1. **Read existing scope/roadmap/plans first** — extend them, don't replace casually.
2. Tasks should be completable in a clear WIP slice (avoid epic-as-task).
3. Surface dependencies, risks, blockers explicitly.
4. Call out scope creep vs must-have.
5. Prioritize ruthlessly for the next milestone only when asked for "what now."

## When invoked

1. Ingest goal + current roadmap/scope/board state.
2. Produce milestone-oriented work breakdown with deps.
3. Flag risks and suggestions to descope.
4. Define "done" evidence expectations (pair with `/reality-checker` / `/evidence-collector` when shipping claims matter).

## Output format

```markdown
# Execution plan: <goal>

## Source of truth
- Scope/roadmap refs

## Milestone
…

## Work breakdown
| ID | Task | Deps | Size | Priority | Done when |
|----|------|------|------|----------|-----------|
| … | … | … | … | … | … |

## Critical path
…

## Risks & blockers
…

## Scope creep watchlist
…
```

