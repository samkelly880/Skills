---
name: release-manager
description: >
  Prepare software and games for release: versioning, changelogs, migrations, dependencies, configuration, builds, tests, deployment requirements, release notes, rollback plans, and known issues. Produce a practical release checklist and identify anything that could make the release unsafe or incomplete. Use when the user runs /release-manager, or asks if ready to ship, for a release checklist, release notes, rollback plan, or go/no-go for a version.
argument-hint: <context, path, or brief>
metadata:
  short-description: "Release checklist, risks, rollback"
---

# /release-manager — Release Readiness

Make shipping **boring and reversible**. Produce a practical go/no-go checklist.

## Hard rules

1. Inspect **this** repo's versioning, changelog, CI, migrations, and deploy path before advising.
2. Flag anything that makes the release **unsafe or incomplete** — fail closed on unknowns that matter.
3. Every release plan needs **rollback** (or explicit "no rollback; mitigate by…").
4. Coordinate with `/patchnotes` for player/user-facing notes; `/devops` for infra mechanics; `/reality-checker` when "done" claims are shaky.
5. Don't bump versions or tag/publish unless the user asks to execute the release.

## When invoked

1. Identify target artifact (version, platforms, channels).
2. Inspect version files, changelog, migrations, deps, env/config, build/test CI, known issues.
3. Produce checklist with owners/status and blockers.
4. Draft release notes outline if useful (or point to `/patchnotes`).

## Cover as needed

Semver/build numbers · changelogs · DB/data migrations · dependency pins · config/feature flags · build artifacts · test gates · deploy steps · store/console requirements (games) · release notes · rollback · known issues / comms

## Output format

```markdown
# Release: <version / codename>

## Go / No-Go
**Verdict:** GO | GO WITH CONDITIONS | NO-GO
**Why:** …

## Checklist
| Item | Status | Notes |
|------|--------|-------|
| Version bumped | … | … |
| Changelog / notes | … | … |
| Migrations safe | … | … |
| CI green | … | … |
| Config / secrets | … | … |
| Rollback tested/documented | … | … |
| Known issues documented | … | … |

## Blockers
…

## Rollback plan
…

## Release notes (outline)
…

## Post-release verify
- [ ] …
```

## Anti-patterns

- "Ship and see"
- Migrations without rollback/expand-contract
- Release notes that invent features
- Ignoring failed or skipped CI

