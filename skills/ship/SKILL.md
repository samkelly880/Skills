---
name: ship
description: >
  Release-readiness orchestration: baseline /test; add /security-engineer, /dependency-auditor, /performance-benchmarker, /accessibility-auditor, etc. when relevant; /reality-checker then /release-manager for checklist, versioning, changelog, known issues, rollback. Do not release/deploy unless explicitly instructed. Final result states blockers, warnings, completed checks, remaining work. Use when the user runs /ship, or asks if ready to release / ship checklist.
argument-hint: <feature, bug, project, or brief>
metadata:
  short-description: "Release-readiness checks (no deploy unless asked)"
---

# /ship — Release Readiness Orchestration

Prove (or refute) release readiness. **Do not deploy/publish/tag unless explicitly told.**

## Hard rules

1. No release actions (npm publish, store upload, prod deploy, git tag) without explicit instruction.
2. Always baseline with **`/test`** (or document why tests cannot run).
3. Add specialists only when the project type warrants them.
4. Final answer must separate **blockers** · **warnings** · **completed checks** · **remaining work**.
5. End with `/release-manager` checklist synthesis.

## Pipeline

### 1. Context
What is shipping (app/game/library), channel, version target.

### 2. Baseline
- **`/test`**

### 3. Conditional checks
| Relevant when… | Skill |
|----------------|-------|
| Auth, user data, network exposure | `/security-engineer` |
| Non-trivial dependency tree | `/dependency-auditor` |
| Perf SLOs / known slowness | `/performance-benchmarker` |
| Web UI users | `/accessibility-auditor` |
| Public APIs | `/api-tester` |

### 4. Challenge & package
- **`/reality-checker`** — challenge "ready to ship."
- **`/release-manager`** — final checklist, notes outline, rollback, known issues.

## Output

```markdown
# Ship readiness: <version>
## Verdict: READY | READY WITH CONDITIONS | NOT READY
## Blockers
## Warnings
## Completed checks
## Remaining work
## Rollback (summary)
```

