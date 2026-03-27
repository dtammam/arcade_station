---
name: Claude binary requires absolute path in tasks.json
description: claude is not on PATH in this dev environment - must use absolute path /home/coder/.local/bin/claude
type: feedback
---

The `claude` binary is installed at `/home/coder/.local/bin/claude`. VS Code tasks use non-login, non-interactive shells that don't source `~/.profile` or `~/.bashrc`, so PATH-relative `claude` does not resolve.

**Why:** Tried adding to `~/.profile` and reloading VS Code — still fails because VS Code task shells don't source login profiles.

**How to apply:** Use the absolute path `/home/coder/.local/bin/claude` in `.vscode/tasks.json`. This is an environment-specific file and the hardcoded path is acceptable here. The QA "no hardcoded paths" rule applies to application config, not dev tooling.
