---
name: optimize-feature
description: >
  Performance-improvement orchestration: measure/reproduce first; /performance-benchmarker for baseline and bottleneck; /optimize for improvements; re-benchmark; /test for regressions; /review for significant changes; /technical-artist for rendering/assets/shaders/VFX. Require measured evidence — never accept 'looks faster'. Use when the user runs /optimize-feature, or wants a disciplined performance improvement workflow.
argument-hint: <feature, bug, project, or brief>
metadata:
  short-description: "Measure → optimize → re-measure"
---

# /optimize-feature — Performance Improvement Orchestration

**Measure → change → measure.** No vibes-only speedups.

## Hard rules

1. Reproduce / measure before optimizing.
2. Baseline with **`/performance-benchmarker`**.
3. Reject "looks faster" without numbers.
4. Re-run benchmarks after changes; watch regressions via **`/test`**.
5. Use **`/technical-artist`** when the bottleneck is rendering/assets/shaders/VFX/graphics pipeline.

## Pipeline

1. Define the slow behavior / workload.
2. `/performance-benchmarker` — baseline + bottleneck hypothesis.
3. `/optimize` — appropriate improvements.
4. `/performance-benchmarker` again — before/after.
5. `/test` — correctness regressions.
6. `/review` if the change is non-trivial.
7. `/technical-artist` when graphics-pipeline related.

## Output

```markdown
# Optimize: <target>
## Baseline
## Changes
## After metrics
## Verdict: improved / unchanged / regressed
## Tests / review
```

