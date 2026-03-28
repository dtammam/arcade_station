---
name: Pre-commit hooks must use venv binaries
description: Git hooks run in bare shells without venv — must use .venv/bin/tool paths directly
type: feedback
---

The pre-commit hook skips black/flake8 because they're only installed in the venv, and git hooks run in a bare shell without venv activation. Fix by using `.venv/bin/black` and `.venv/bin/flake8` directly in `hooks/pre-commit`, or sourcing the venv at the top.

**Why:** User flagged that pre-commit hooks have been showing "SKIP" messages throughout the entire initiative despite the tools being installed. The hooks need real enforcement.

**How to apply:** When updating hooks/pre-commit, reference tools via `.venv/bin/` path rather than expecting them on PATH. This was folded into the current code hygiene work after P2-T2.
