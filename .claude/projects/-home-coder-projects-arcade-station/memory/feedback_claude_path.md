---
name: Claude binary requires absolute path in tasks.json
description: claude is not on PATH in this dev environment - must use absolute path /home/coder/.local/bin/claude
type: feedback
---

The `claude` binary is installed at `/home/coder/.local/bin/claude`. This path was added to `~/.profile` so it's available in all shell environments including VS Code tasks.

**Why:** VS Code tasks use non-interactive shells that don't source `.bashrc`. Adding to `~/.profile` ensures PATH resolution works everywhere.

**How to apply:** Use `claude` (PATH-relative) in `.vscode/tasks.json` — do not hardcode absolute paths. The PATH is permanently configured in the remote dev environment.
