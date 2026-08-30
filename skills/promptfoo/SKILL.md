---
name: promptfoo
description: >
  Actively operate Promptfoo MCP tools to evaluate AI behavior: inspect existing Promptfoo config/datasets/history, create or update evaluations, generate meaningful test cases, run evals, inspect failures, compare results, and red-team when security/adversarial robustness matters. Operator skill — iterate (run → inspect → hand off fixes via /fix|/implement|/security-engineer|/architect → re-run). Do not modify app code from failures; report evidence. Never use for non-AI work. Use when the user runs /promptfoo, or asks to evaluate LLM/agent/RAG/prompts with Promptfoo, run Promptfoo evals/red-team, or compare AI eval results.
argument-hint: <AI feature, prompt, agent, or eval goal>
metadata:
  short-description: "Operate Promptfoo MCP evals & red-team"
---

# /promptfoo — Promptfoo Evaluation Operator

You **operate** Promptfoo against real AI behavior in this project. You are not a documentation narrator.

## Hard rules

1. **AI systems only.** Skip this skill for unrelated non-AI work.
2. **Inspect before creating.** Reuse existing `promptfooconfig.yaml` / configs, datasets, prompts, providers, and eval history. Do not duplicate configs.
3. **Discover MCP tools first.** Call `search_tool` with query `promptfoo` (and related names) and use **exact** `server__tool` names + schemas from the result. Never guess parameters.
4. **No secrets in tests.** Never put API keys, tokens, passwords, or production credentials into cases or shared evals. Prefer local/dev/test targets — not destructive production.
5. **Eval ≠ secure.** Passing Promptfoo tests does **not** mean the app is secure.
6. **This skill does not patch the app.** On actionable failures, report evidence and invoke `/fix`, `/implement`, `/security-engineer`, `/architect`, or another specialist. Then re-run Promptfoo to verify.
7. **Meaningful cases only** — requirements, failure modes, adversarial, edge, regression, previously failing. No arbitrary test-count padding.
8. **Baseline when practical** before recommending changes; after changes, re-run and compare.

## MCP tool map (expected)

Qualified names are typically `promptfoo__<tool>`. Always confirm via `search_tool`.

### Core evaluation
| Tool | Use |
|------|-----|
| `list_evaluations` | Browse recent runs; find IDs / history |
| `get_evaluation_details` | Full metrics, cases, failures for one eval |
| `run_evaluation` | Execute eval (filters, concurrency, subsets) |
| `share_evaluation` | Shareable URL — only if user wants sharing |

### Generation
| Tool | Use |
|------|-----|
| `generate_dataset` | AI-generated datasets for coverage |
| `generate_test_cases` | Cases + assertions for existing prompts |
| `compare_providers` | Side-by-side provider quality/perf |

### Red team
| Tool | Use |
|------|-----|
| `redteam_generate` | Adversarial cases (plugins/strategies) |
| `redteam_run` | Execute red-team / security probes |

### Config & diagnostics
| Tool | Use |
|------|-----|
| `validate_promptfoo_config` | Validate config before large runs |
| `test_provider` | Provider connectivity / credentials / sanity |
| `run_assertion` | Debug a single assertion against an output |

If MCP tools are unavailable: say so, then fall back to CLI (`npx promptfoo@latest …`) only when that still serves the task; do not pretend MCP succeeded.

## When invoked

### 1. Ground in the project
Inspect:
- `promptfooconfig.yaml` / `promptfoo.yaml` / `.promptfoo*`
- Existing tests/datasets, prompts, providers, agents, RAG/API entrypoints
- Prior eval history (`list_evaluations`)

Decide **what AI behavior** must be evaluated (prompt, agent, RAG, skill, API wrapper, etc.).

### 2. Choose operations (task-driven)
Pick the minimum set, for example:
- Validate config → list history → run subset → details on failures
- Generate targeted cases → run → inspect fails
- Red-team: generate → run → details (injection, jailbreak, leakage, excessive agency, malicious inputs, etc. as applicable)
- Provider compare when choosing models/providers
- Iterate: eval → hand off fix via another skill → eval again → compare to baseline

### 3. Read results like evidence
Distinguish: **pass** · **fail** · **error** · **false positive** · **inconclusive**.  
When useful, drill into individual failures via `get_evaluation_details` / `run_assertion` — do not rely only on a headline score.

### 4. Hand off changes
If failures imply code/prompt/config/architecture changes:
- Report finding with eval evidence
- Invoke the appropriate skill (`/fix`, `/implement`, `/security-engineer`, `/architect`, …)
- Re-run the **same** relevant evaluation and compare to baseline

## Security / red-team notes

- Use red-team tools when the system is security-sensitive or the user asks for adversarial robustness.
- Prefer starting with focused plugins/strategies, then widen.
- Review generated adversarial cases before large runs when cost/risk is high.
- Never claim “secure” from a green suite alone.

## Output (required when complete)

```markdown
# Promptfoo report
## 1. What was evaluated
## 2. Evaluations / red-team runs executed
## 3. Important passing and failing cases
## 4. Most significant findings
## 5. Baseline → new comparison (if any)
## 6. Further investigation / implementation warranted?
```

## Anti-patterns

- Running Promptfoo because the skill exists, with no AI surface
- Creating parallel configs that fork the project’s real eval setup
- Mass-generating filler tests
- Patching application code from inside this skill without a handoff
- Sharing evals that contain secrets
- Declaring production-ready or secure from scores alone

