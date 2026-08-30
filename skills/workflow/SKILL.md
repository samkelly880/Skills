---
name: workflow
description: >
  Master workflow orchestration skill: intelligent task dispatcher. Classify the request, inspect project state and available skills, choose the smallest sensible workflow, and invoke appropriate existing skills (prefer high-level workflows like /new-feature, /fix, /game-feature, /ship, etc. over recreating sequences). For AI/LLM/agent/RAG/prompt systems, intelligently invoke /promptfoo when evaluation would provide meaningful quality, correctness, reliability, or security evidence — not merely because AI is present. Conditionally route clear MiroFish, Nanochat, or Impeccable (UI/design) work to /mirofish, /nanochat, or /impeccable — never merely because those skills exist. Context-aware — minimum skills for a reliable result; no checklist bloat. Ends with a summary of workflow, skills invoked, changes, verification, and remaining uncertainty. Use when the user runs /workflow, or wants automatic routing of a task through the right skill pipeline.
argument-hint: <task or goal>
metadata:
  short-description: "Intelligent skill dispatcher / master workflow"
---

# /workflow — Master Task Dispatcher

You are the project's **intelligent workflow dispatcher**. Understand the task, inspect the project and available skills, pick the **smallest reliable workflow**, and invoke the right existing skills. Prefer high-level orchestration skills over reinventing their sequences.

## Hard rules

1. **Minimum viable skill set.** Never invoke a skill just because it exists or to satisfy a mental checklist.
2. Prefer **existing workflow skills** (`/new-feature`, `/fix`, `/game-feature`, `/game-design`, `/research`, `/research-feature`, `/audit`, `/review-project`, `/security-review`, `/optimize-feature`, `/ship`, `/web-feature`) when they already cover the task.
3. **No duplicate work** — if a workflow already includes `/test`, `/grill-me`, or `/promptfoo` for the same purpose, don't re-run them unless new evidence requires it.
4. Before each skill: state **why** it is relevant (briefly). After each major stage: decide if another skill is actually needed.
5. **Never** delete, overwrite, migrate, deploy, release, merge, or take other destructive actions without sufficient evidence and authorization (respect `/pullrequest` / `/ship` opt-outs and user constraints).
6. Never modify files merely because a specialist *recommends* it — only when the chosen workflow stage and user intent require it.
7. Respect project conventions and constraints.
8. **`/promptfoo` is evidence, not a rubber stamp.** Meaningful failures must be triaged and addressed (or explicitly accepted with rationale) before declaring AI work complete. Passing Promptfoo alone does not prove the system is secure or done.

## Step 0 — Classify

Classify the task as one or more of:

`discovery` · `research` · `planning` · `design` · `implementation` · `bug fixing` · `refactoring` · `review` · `testing` · `security` · `performance` · `game development` · `web development` · `deployment` · `release` · `AI evaluation`

Also note: **trivial vs substantial**, whether requirements are already clear, and whether the work touches an **AI surface** (LLM app, agent, RAG, AI-powered API, prompt-based feature, AI code-analysis tool, agent skill, evaluator, model/prompt pipeline).

Inspect: repo state, `$ARGUMENTS`, conversation context, and which skills exist. For AI work, also note existing Promptfoo configs/evals if present.

## Routing — prefer high-level workflows

| Situation | Prefer |
|-----------|--------|
| New/underspecified feature (general) | `/new-feature` |
| Web feature | `/web-feature` |
| Game feature (design→build→verify) | `/game-feature` |
| Game design only (no code) | `/game-design` |
| Bug | `/fix` (or `/debugger` if available and appropriate) |
| Pre-impl research Q | `/research` or `/research-feature` |
| Multi-area project audit (code/security/deps/a11y/API readiness — not UI-design-only) | `/audit` |
| UI/design audit, polish, visual hierarchy, layout/type/color/motion | `/impeccable` |
| Independent project assessment | `/review-project` |
| Security assessment | `/security-review` |
| Performance improvement | `/optimize-feature` |
| Release readiness | `/ship` |
| Direct AI eval / Promptfoo / red-team ask | `/promptfoo` |
| Explicit MiroFish / MiroFish project simulation·report·graph | `/mirofish` |
| Explicit Nanochat train·tok·eval·checkpoint·doctor·prepare | `/nanochat` |

Only manually chain leaf skills when no workflow fits or the user asked for a custom path.

When delegating to a high-level workflow that already covers AI eval, **do not** also invoke `/promptfoo` yourself for the same purpose unless that workflow skipped it and new evidence says it is still needed.

**Specialist priority (conservative):** (1) user explicitly names the skill → use it; (2) clear domain match → use it; (3) ambiguous/general → do **not** force it; (4) combine specialists only when the task genuinely crosses domains.

## Automatic rules (when not fully covered by a delegated workflow)

### Discovery & planning
- **Unclear / underspecified** → `/grill-me` first. **Do not implement** until requirements are clear enough.
- **Already clearly specified by the user** → do **not** re-run `/grill-me` unnecessarily.
- **Too large / ambiguous scope / complexity risk** → `/scope` before implementation.
- **System structure, major abstractions, significant tech decisions** → `/architect`.
- **Backend shape** → `/backend-architect`; **persistent data** → `/database-engineer`.

### Domain specialists (only if actually related)
`/mechanic` · `/balance` · `/enemy` · `/boss` · `/economy` · `/level-designer` · `/lore` · `/narrative-designer` · `/technical-artist` · `/game-audio`

### Research & tools
- Unfamiliar tech / APIs / approaches → `/researcher` or `/research`.
- Choosing among tools/libs/frameworks → `/tool-evaluator`.

### Implementation & verify
- Code/project changes with clear requirements → `/implement`.
- After code changes, when meaningful verification is possible → `/test`.
- Non-trivial changes / quality-architecture-security-maintainability risk → `/code-review`.
- Substantial work, important fixes, major features, or before "complete" → `/reality-checker` (challenge that it *works*, don't trust looks).

### AI evaluation — `/promptfoo` (conditional)
Invoke **`/promptfoo`** when the task involves an AI system **and** evaluation would provide meaningful evidence about quality, correctness, reliability, or security of the work. Examples of surfaces: LLM applications, AI agents, RAG systems, AI-powered APIs, prompt-based features, AI code-analysis tools, agent skills.

**Do invoke `/promptfoo` when:**
- AI behavior itself needs evaluation (outputs, tool use, grounding, refusal, policy adherence).
- Security-sensitive AI work warrants red-team (prompt injection, jailbreaks, data leakage, excessive agency, malicious inputs, other applicable LLM risks).
- A prompt, model, agent behavior, skill, evaluator, RAG pipeline, or other AI behavior changed in a way that could regress existing behavior (regression eval).
- You need a baseline before recommending AI changes, or a before/after comparison after changes.

**Do not invoke `/promptfoo` merely because the project contains AI**, or when there is nothing meaningful to evaluate (e.g. pure infra/docs/CSS with no AI behavior under change).

When `/promptfoo` is invoked, treat it as the operator of the configured **Promptfoo MCP server**: allow it to discover/use MCP tools to create tests, run evaluations, retrieve results, red-team, and analyze failures (per the `/promptfoo` skill).

**On meaningful Promptfoo failures:** do not ignore them or declare the feature complete. Classify whether the failure needs a code change, prompt change, configuration change, architecture change, or further investigation. Invoke `/fix`, `/implement`, `/security-engineer`, `/architect`, or another relevant specialist. After a meaningful change, invoke **`/promptfoo` again** to verify the problem was actually resolved. Avoid redundant re-runs when nothing relevant changed.

**Avoid double-eval:** if `/new-feature`, `/fix`, `/security-review`, `/research`, `/game-feature`, `/web-feature`, or another workflow already invoked `/promptfoo` for the same purpose, do not invoke it again unnecessarily.

### Specialized tools — `/mirofish`, `/nanochat`, `/impeccable` (conditional)

Route only on **explicit naming** or a **clear domain match**. Do not invoke these merely because they exist.

#### `/mirofish`
**Invoke when:** the user names MiroFish, or the work is clearly inside the MiroFish project **and** involves running simulations, social-reaction / policy–product “what if” simulations, analyzing MiroFish reports, inspecting runs, or searching the MiroFish/Zep graph.

**Do not invoke for:** generic simulation, data analysis, research, or ordinary “what if” brainstorming that does not need MiroFish’s pipeline.

#### `/nanochat`
**Invoke when:** the user names Nanochat, or the task clearly concerns Nanochat training, tokenizer/data prep, evaluation, checkpoints/artifacts, one-shot inference/chat, env/resource inspection (`doctor`), or preparing Nanochat experiments (including remote-GPU prepare-only).

**Do not invoke for:** ordinary LLM/Python/ML/coding questions, “add a chatbot to my app,” or using Nanochat as the default coding model.

#### `/impeccable`
**Invoke when:** UI/UX critique or design audit, visual design problems, polishing an interface, layout / typography / color / animation / responsive design / visual hierarchy, or detecting UI design issues (including `npx impeccable detect` via that skill).

**Do not invoke for:** backend, database, infrastructure, game logic, or ordinary non-UI programming.

**vs `/audit`:** `/audit` = multi-area project health (code, security, deps, etc.). `/impeccable` (and `/impeccable audit`) = **UI/design** surfaces. Prefer `/impeccable` for “audit this dashboard/settings page for UI issues”; prefer `/audit` for broad project audits. Deep a11y-only work may still use `/accessibility-auditor` when Impeccable is not the better fit.

### Security / deps / perf / a11y / play
- Authn/z, user data, networking, exposed APIs, secrets, untrusted input, multiplayer, payments, etc. → `/security-engineer` (and consider `/promptfoo` red-team when the sensitive surface is AI-mediated).
- Deps added/removed/upgraded or otherwise material → `/dependency-auditor`.
- Perf work → `/performance-benchmarker` **before and after** (never assume).
- UI design / visual polish / design-system UI audit → `/impeccable` when matched above; deep a11y-only → `/accessibility-auditor` when that is the better fit.
- Implemented gameplay feel → `/playtest`.

### Ship / docs / ops
- Coherent change ready for review/merge → `/pullrequest` (not for trivial local edits).
- Explicitly preparing to release/deploy → `/release-manager` and `/ship`.
- User-facing release / game update notes → `/patchnotes`.
- Docs create/update → `/technical-writer`.
- `/monitor`, `/notify-when-done`, `/unattended`, `/absent` — **only** when the request or workflow actually calls for them.

## Default lifecycle — implementation tasks

1. Understand request; inspect project.
2. `/grill-me` if unclear or important decisions unresolved.
3. Scope / architecture only when necessary.
4. Relevant specialists/design skills when needed.
5. `/implement`.
6. `/test`.
7. `/code-review` if non-trivial.
8. `/reality-checker` before claiming substantial completion.
9. `/pullrequest` if substantial enough to review/merge.

## Default lifecycle — AI feature implementation

When the feature is an AI system / LLM / agent / RAG / prompt-based / AI API / AI analysis / agent-skill surface:

1. Understand requirements; `/grill-me` when important requirements are unclear.
2. Scope and architecture when necessary.
3. Design via relevant specialists when appropriate.
4. `/implement`.
5. `/test` for conventional verification.
6. **`/promptfoo`** when the AI behavior itself needs evaluation (quality/correctness/reliability/security evidence).
7. `/code-review` for non-trivial changes.
8. `/reality-checker` before declaring substantial work complete (include Promptfoo evidence when it was run).
9. `/pullrequest` when the change is substantial enough.

If `/promptfoo` finds meaningful failures → triage → appropriate specialist → change → **`/promptfoo` again** → then continue.

For security-sensitive AI systems, prefer including Promptfoo **red-team** coverage as part of step 6 when attack classes apply.

## Default lifecycle — bugs

Investigate before modifying. Prefer `/fix` (or `/debugger` when available). Then `/test`, `/code-review`, `/reality-checker` as warranted. No speculative edits.

If the bug is in AI behavior (prompt/agent/RAG/etc.) and eval evidence would help, include `/promptfoo` (baseline → after fix) unless `/fix` already covered it.

## Default lifecycle — informational

Answer / research only. **Do not** invoke implementation, testing, PR, or release workflows. `/promptfoo` only if the question itself is about evaluating AI behavior and running evals is the right way to answer.

## Default lifecycle — trivial

Shortest path (e.g. tiny text/CSS). **No** architecture, security, database, performance, Promptfoo, MiroFish, Nanochat, or release workflows. Tiny CSS/text polish may use `/impeccable` only when the ask is clearly visual/UI design.

## Execution discipline

```text
classify → pick workflow or leaf set → for each skill:
  (why relevant?) → invoke → interpret result →
  (is another skill still necessary?) → continue or stop
```

Skip a skill when its purpose is already satisfied by available evidence.

## Final summary (required)

```markdown
# Workflow summary
## Classification
## Workflow selected
## Skills invoked (and why)
## Skills skipped (and why) — brief
## What changed
## What was verified
## Promptfoo (if used): evals run, key failures, re-runs after fixes
## Remaining issues / uncertainty
```
