# Tech Debt Tracker

## Active

### TD-001: Migrate .bat files to .ps1 for linting

- **Added:** 2026-03-27
- **Context:** Batch files are used to invoke PowerShell scripts. PSScriptAnalyzer can't lint `.bat` files. Migrating to `.ps1` would bring them under lint coverage.
- **Next action:** Evaluate which `.bat` files can be converted to `.ps1` without breaking existing workflows.
- **Owner:** Unassigned

### TD-002: Provision Python 3.12 in dev environment

- **Added:** 2026-03-27
- **Context:** Project requires Python 3.12.9 but the dev environment (Debian 12) ships 3.11. All tooling works on 3.11 but the version mismatch should be resolved. Requires pyenv, deadsnakes, or building from source.
- **Next action:** Install Python 3.12, recreate venv, confirm all tools pass under 3.12.
- **Owner:** Unassigned

### TD-003: Tighten mypy to require type annotations

- **Added:** 2026-03-27
- **Context:** `pyproject.toml` sets `disallow_untyped_defs = false` as a pragmatic baseline. Many `# type: ignore[code]` comments were added in P1-T4 to get a clean gate. Future work should enable `disallow_untyped_defs = true` and add proper type annotations file-by-file, removing ignores as types are added.
- **Next action:** Enable `disallow_untyped_defs = true` with per-file overrides for legacy files, then annotate files incrementally.
- **Owner:** Unassigned

## Closed

(none yet)

---

Rules:

- Every item must have a clear next action and owner (human or "unassigned").
- Close items by linking the PR that resolved them and moving to the Closed section.
