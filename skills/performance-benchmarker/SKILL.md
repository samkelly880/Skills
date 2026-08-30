---
name: performance-benchmarker
description: >
  Performance benchmarking: establish a baseline before optimization, identify meaningful metrics, design reproducible benchmarks, compare before/after, identify regressions, and distinguish meaningful improvements from noise. Measure first; recommend optimization second. Use when the user runs /performance-benchmarker, or asks to benchmark, baseline performance, before/after metrics, or verify an optimization helped.
argument-hint: <context, path, or brief>
metadata:
  short-description: "Measure first, optimize second"
---

# /performance-benchmarker — Benchmarking

**Measure first. Optimize second.**

## Hard rules

1. **Baseline before changes** whenever possible.
2. Metrics must map to user-visible or capacity-relevant outcomes.
3. Benchmarks must be **reproducible** (command, dataset, env notes, iteration count).
4. Report variance; don't celebrate noise.
5. Call regressions explicitly.

## Relationship

- `/optimize` proposes improvements — this skill **validates** them with numbers.
- Don't deep-dive algorithm rewrites here until baseline exists.

## When invoked

1. Define workload + metrics (p50/p95 latency, throughput, memory, FPS, etc.).
2. Establish baseline numbers.
3. After a change, re-run the same harness.
4. Conclude: improved / unchanged / regressed, with confidence notes.

## Output format

```markdown
# Benchmark: <target>

## Setup
- Env, command, dataset, iterations

## Metrics
|

## Baseline
|

## After
|

## Delta & interpretation
- Meaningful? noise?
- Regressions?

## Next measurements
…
```

