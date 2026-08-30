---
name: create-skill
description: >
  Interactively create a new skill (SKILL.md + optional scripts/references)
  usable by both Claude and Grok. Defaults to user scope unless the user
  asks for a project-only skill. Use when the user wants to create a skill,
  scaffold a skill, or runs /create-skill.
---

# Create Skill

Interactively gather requirements from the user and create a fully working skill on disk that both Claude and Grok can read and use.

## Step 1: Gather information

Ask the user the following questions **one at a time as regular conversation questions** (do NOT use structured option prompts for free-text inputs):

1. **Skill name** - ask the user to type a name. Lowercase letters (a-z), digits (0-9), and hyphens (-) only. Must start and end with a letter or digit. Must be 2-64 characters long (e.g. `deploy-k8s`). Validate the name before proceeding.
2. **What it should do** - ask the user to describe the workflow, paste an example prompt they keep repeating, or explain the task the skill should automate.

### Scope (do not ask by default)

- **Default to User** for every new skill. Do **not** present a scope question unless the user already asked for project-only / repo-only / this-repo.
- **User** (default): write so both agents get it:
  - `~/.claude/skills/<name>/SKILL.md`
  - `~/.grok/skills/<name>/SKILL.md` (same content)
- **Project** (only when the user specifically requests a project-only skill):
  - `<repo-root>/.claude/skills/<name>/SKILL.md`
  - `<repo-root>/.grok/skills/<name>/SKILL.md` (same content)
- If `$ARGUMENTS` or the user's message already includes the name and/or what it should do, skip those questions and proceed.
- If the user later says they want it project-only, switch to project paths for that skill.

## Step 2: Draft the description

Write a `description` frontmatter value that includes:
- What the skill does (1-2 sentences)
- Trigger phrases and keywords so the agent knows when to auto-invoke it
- The slash command name (e.g. "Use when the user runs /deploy-k8s")

Show the drafted description to the user and let them approve or edit it.

## Step 3: Create the directories

Create **both** agent skill directories (same skill body in each):

```bash
mkdir -p <CLAUDE_SKILL_DIR> <GROK_SKILL_DIR>
```

Where the dirs are:

- User (default):
  - `<CLAUDE_SKILL_DIR>` = `~/.claude/skills/<name>`
  - `<GROK_SKILL_DIR>` = `~/.grok/skills/<name>`
- Project (only if requested):
  - `<CLAUDE_SKILL_DIR>` = `<repo-root>/.claude/skills/<name>`
  - `<GROK_SKILL_DIR>` = `<repo-root>/.grok/skills/<name>`

If the skill needs helper scripts, also create `scripts/` under both dirs (or create once and copy).
If the skill needs reference docs, also create `references/` under both dirs (or create once and copy).

Always use absolute paths when creating files.

## Step 4: Write SKILL.md

Write the **same** `SKILL.md` to both `<CLAUDE_SKILL_DIR>/SKILL.md` and `<GROK_SKILL_DIR>/SKILL.md`.

The file MUST follow this exact format:

```
---
name: <skill-name>
description: <the description from Step 2>
---

<markdown body with instructions, steps, code blocks>
```

Also write any supporting files (scripts, references) to both locations using the same content.

Keep wording agent-neutral ("the agent", not "Claude-only" or "Grok-only") unless the skill truly depends on one product's tools.

## Step 5: Verify and confirm

1. Verify both `SKILL.md` files were written correctly and match.
2. Tell the user the skill is ready and how to use it:
   - Slash command: `/<skill-name>`
   - TUI menu: `/skills <skill-name>`
   - Automatic: the agent will invoke it when the description matches user intent
3. Tell the user which scope was used (user by default, or project if they asked) and that copies exist for both Claude and Grok.
4. Tell the user the skill should appear in the slash menu within a few seconds (skills auto-reload when files change on disk).

## Guidelines

- Keep the SKILL.md body focused and actionable. It is a prompt for the agent, not documentation.
- The `description` field is critical. It controls auto-invocation. Be specific with trigger words.
- Prefer referencing existing CLI tools over writing custom scripts.
- Do NOT skip creating the directories. The file will fail to save without them.
- Always use absolute paths when creating files to avoid writing to the wrong location.
- **Never ask about scope** unless clarifying an ambiguous project-only request. User scope is the default.
- Always dual-write to Claude and Grok skill paths so both can use the skill.
