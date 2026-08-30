# Skills

User-level agent skills for Grok Build and Claude Code (dual-write).

## Layout

```text
skills/<skill-name>/SKILL.md
skills/<skill-name>/scripts/     # optional
skills/<skill-name>/references/  # optional
```

## Install

Copy or symlink into both harnesses (same content):

```bash
# from this repo root
rsync -a skills/ ~/.grok/skills/
rsync -a skills/ ~/.claude/skills/
```

Or link individual skills:

```bash
ln -s "$(pwd)/skills/workflow" ~/.grok/skills/workflow
ln -s "$(pwd)/skills/workflow" ~/.claude/skills/workflow
```

Project-scoped skills (e.g. MiroFish, Nanochat) live in their own repos under `.grok/skills/` / `.claude/skills/` and are not duplicated here unless promoted.

## Included skills

`absent`, `accessibility-auditor`, `api-tester`, `architect`, `audit`, `backend-architect`, `balance`, `boss`, `brainstorm`, `bugfix`, `build`, `check-work`, `clean-branches`, `create-skill`, `database-engineer`, `dependency-auditor`, `design`, `devops`, `domain`, `domains-used`, `economy`, `enemy`, `evidence-collector`, `execute-plan`, `exploit`, `fix`, `game-audio`, `game-design`, `game-feature`, `grill-me`, `handoff`, `impeccable`, `implement`, `investor`, `level-designer`, `lore`, `mechanic`, `monitor`, `narrative-designer`, `new-feature`, `notify-when-done`, `optimize`, `optimize-feature`, `orchestrate-build`, `patchnotes`, `performance-benchmarker`, `playtest`, `pr-babysit`, `project-manager`, `promptfoo`, `pullrequest`, `pullrequest-rereview`, `pullrequest-review`, `readonly`, `reality-checker`, `release-manager`, `research`, `research-feature`, `researcher`, `review`, `review-project`, `roadmap`, `scope`, `security-engineer`, `security-review`, `setup-error-monitoring`, `ship`, `skill-design-principles`, `technical-artist`, `technical-writer`, `test`, `threat-detection`, `tool-evaluator`, `unattended`, `web-feature`, `what-if`, `workflow`
