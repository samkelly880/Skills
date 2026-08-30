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
