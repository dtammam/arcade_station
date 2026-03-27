---
name: Always activate venv in SDE prompts
description: Software developer agent must activate the .venv before any pip/python commands
type: feedback
---

Every software-developer inbox prompt must include explicit venv activation instructions at the top, before any pip install or Python tool commands.

**Why:** Each VS Code task spawns a fresh shell with no venv active. The SDE agent tried to install packages globally and hit permission/path issues.

**How to apply:** When the engineering-manager writes `.state/inbox/software-developer.md`, always include a "## Environment setup (MUST DO FIRST)" section with `source /home/coder/projects/arcade_station/.venv/bin/activate` (and venv creation if it doesn't exist).
