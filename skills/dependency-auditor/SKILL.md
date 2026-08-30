---
name: dependency-auditor
description: >
  Audit project dependencies for vulnerabilities, outdated packages, abandoned dependencies, unnecessary dependencies, licensing concerns, version conflicts, transitive dependencies, and supply-chain risks. Distinguish actionable problems from harmless outdated versions; prioritize by actual project risk. Use when the user runs /dependency-auditor, or asks to audit dependencies, check CVEs, find unused packages, review licenses, or assess supply-chain risk.
argument-hint: <context, path, or brief>
metadata:
  short-description: "Deps: vulns, abandonware, license, supply chain"
---

# /dependency-auditor — Dependency Audit

Review installed dependencies for **real risk**, not version-anxiety.

## Hard rules

1. Inspect the project's manifest lockfiles and, when available, advisory DB / audit CLI output.
2. **Actionable ≠ merely outdated.** Prioritize exploited/critical vulns, abandonware on critical path, license conflicts, and suspicious maintainers/typosquatting signals.
3. Separate direct vs transitive; say whether a fix is upgrade, replace, vendor, or accept-risk.
4. Don't mass-upgrade everything without a reason — churn is risk too.
5. Coordinate with `/security-engineer` for app-level fallout; `/tool-evaluator` if replacing a library.

## When invoked

1. Detect ecosystem (npm/pnpm/yarn, pip/uv/poetry, cargo, go.mod, composer, etc.).
2. Run or read audit/outdated outputs when tools exist.
3. Triage findings into prioritized recommendations.
4. Note scan coverage limits (private registries, pins, ignored advisories).

## Cover

CVEs/advisories · outdated vs vulnerable · abandoned/unmaintained · unused/unnecessary · licenses · version conflicts · transitive exposure · supply-chain (install scripts, maintainers, typosquat)

## Output format

```markdown
# Dependency audit: <project>

## Summary
- Risk posture
- Top actions

## Findings
### [SEV] <package>@<version>
- **Type:** vuln / abandonware / license / unused / conflict / supply-chain
- **Evidence:** …
- **Exposure:** direct/transitive; runtime/dev
- **Recommendation:** upgrade to … / replace with … / remove / accept risk
- **Effort / breakage risk:** …

## Harmless outdated (no action now)
…

## Suggested upgrade order
1. …
```

## Severity guide

- **Critical:** reachable critical vuln, compromised package signals, license that blocks distribution
- **High:** high vuln on runtime path, abandoned critical dependency
- **Medium:** moderate vulns, messy conflicts, questionable unused bloat on prod path
- **Low:** tidy-up outdated, unused dev tooling

