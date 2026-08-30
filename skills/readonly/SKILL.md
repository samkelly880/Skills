---
name: readonly
description: Switch into read-only mode — observe and analyze only, make no changes to anything. Triggers when the user says "/readonly", "read only mode", "look but don't touch", "don't change anything", "investigate but make no modifications", or otherwise signals you must not mutate anything while you work. Applies for the remainder of the task.
---

# readonly

You are operating in **READ ONLY mode**.

## Rules

- Do **NOT** attempt to make any modifications to the filesystem.
- Do **NOT** execute any applications that may result in modifications to the host.
- Do **NOT** attempt to modify any databases in any way.

The intent is a bright line: **change nothing, anywhere, by any means** — not the local host, not a remote system, not any data store. This covers indirect routes too: version control writes, network calls that alter remote state, and any skill, subagent, or tool you might invoke. If a task cannot proceed without a modification, stop and report it rather than working around this.
