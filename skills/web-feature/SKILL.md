---
name: web-feature
description: >
  Web-development feature orchestration: /grill-me; then selective /scope, /architect or /backend-architect, /database-engineer, /implement, /api-tester, /accessibility-auditor, /security-engineer, /test, /code-review, /reality-checker. Skip irrelevant specialists. Do not make architectural changes without establishing necessity. Use when the user runs /web-feature, or wants a full web feature workflow from clarification through verification.
argument-hint: <feature, bug, project, or brief>
metadata:
  short-description: "Web feature delivery orchestration"
---

# /web-feature — Web Feature Orchestration

Deliver a web feature with selective architecture and quality gates.

## Hard rules

1. **`/grill-me` first.**
2. No architectural rewrites without a demonstrated need.
3. Skip irrelevant specialists (e.g. no `/database-engineer` for pure CSS).
4. Discovery/planning are read-only unless the user allows otherwise.
5. Finish with `/test`, `/code-review`, `/reality-checker`.

## Pipeline

1. `/grill-me`
2. Conditional planning: `/scope`, `/architect` or `/backend-architect`, `/database-engineer`
3. `/implement`
4. Conditional quality: `/api-tester`, `/accessibility-auditor`, `/security-engineer` (security-sensitive only)
5. `/test` → `/code-review` → `/reality-checker`

## Output

Run log with requirements, skills invoked/skipped, implementation summary, verification, reality verdict.

