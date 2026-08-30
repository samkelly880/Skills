# Skills

User-level agent skills for Grok Build and Claude Code (dual-write).

## Layout

```text
skills/<skill-name>/SKILL.md
skills/<skill-name>/scripts/     # optional
skills/<skill-name>/references/  # optional
skills/shared/                  # personas + host helpers for design/review/execute-plan/pr-babysit
```

## Install

Copy or symlink into both harnesses (same content):

```bash
# from this repo root — exclude impeccable so a full upstream Impeccable
# install (npx impeccable install) is not overwritten by this thin stub
rsync -a --exclude 'impeccable/' skills/ ~/.grok/skills/
rsync -a --exclude 'impeccable/' skills/ ~/.claude/skills/

# Optional: install the thin Impeccable integration stub only if you do not
# already have the official Impeccable skill/playbooks:
#   rsync -a skills/impeccable/ ~/.grok/skills/impeccable/
# Prefer project-scoped official Impeccable: npx impeccable install --providers=grok,claude --scope=project
```

Or link individual skills (also link `shared/` whenever you use
`design`, `review`, `execute-plan`, or `pr-babysit`):

```bash
ln -s "$(pwd)/skills/shared" ~/.grok/skills/shared
ln -s "$(pwd)/skills/shared" ~/.claude/skills/shared
ln -s "$(pwd)/skills/workflow" ~/.grok/skills/workflow
ln -s "$(pwd)/skills/workflow" ~/.claude/skills/workflow
```

Some project-specific skills (e.g. Gardenbound content authors) stay in their
repos under `.grok/skills/` / `.claude/skills/` and are not duplicated here.

## Included skills

`absent`, `accessibility-auditor`, `api-tester`, `architect`, `audit`, `backend-architect`, `balance`, `boss`, `brainstorm`, `bugfix`, `build`, `check-work`, `clean-branches`, `create-skill`, `database-engineer`, `dependency-auditor`, `design`, `devops`, `domain`, `domains-used`, `economy`, `enemy`, `evidence-collector`, `execute-plan`, `exploit`, `fix`, `game-audio`, `game-design`, `game-feature`, `grill-me`, `handoff`, `impeccable`, `implement`, `investor`, `level-designer`, `lore`, `mechanic`, `monitor`, `narrative-designer`, `new-feature`, `notify-when-done`, `optimize`, `optimize-feature`, `orchestrate-build`, `patchnotes`, `performance-benchmarker`, `playtest`, `pr-babysit`, `project-manager`, `promptfoo`, `pullrequest`, `pullrequest-rereview`, `pullrequest-review`, `read-arxiv-paper`, `readonly`, `reality-checker`, `release-manager`, `research`, `research-feature`, `researcher`, `review`, `review-project`, `roadmap`, `scope`, `security-engineer`, `security-review`, `setup-error-monitoring`, `ship`, `skill-design-principles`, `technical-artist`, `technical-writer`, `test`, `threat-detection`, `tool-evaluator`, `unattended`, `web-feature`, `what-if`, `workflow`
