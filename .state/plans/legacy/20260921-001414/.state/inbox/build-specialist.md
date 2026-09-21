# Build Specialist -- Full Verification Run

## Context

Feature: **Multi-phase code hygiene initiative** (code-hygiene-initiative)
All 13 tasks (P1-T1 through P1-T9, P2-T1, P2-T2, P3-T1, P3-T2) are marked
complete. This is the final verification pass before acceptance.

State file: `/home/coder/projects/arcade_station/.state/feature-state.json`
Exec plan: `/home/coder/projects/arcade_station/docs/exec-plans/active/2026-03-27-code-hygiene-initiative.md`

## Instructions

You are the build specialist. Your job is to run every quality gate listed below,
report **PASS** or **FAIL** for each one, and include full output for any failures.
Do **NOT** fix anything -- report only.

### Environment setup

Before running any Python commands, activate the virtual environment:

```bash
source /home/coder/projects/arcade_station/.venv/bin/activate
```

All commands must be run from the project root: `/home/coder/projects/arcade_station`

### Quality gates to run (in order)

1. **Black (format check)**
   ```bash
   cd /home/coder/projects/arcade_station && source .venv/bin/activate && python -m black --check src/ install/ tests/
   ```

2. **Flake8 (lint)**
   ```bash
   cd /home/coder/projects/arcade_station && source .venv/bin/activate && python -m flake8 src/ install/ tests/
   ```

3. **Mypy (type check)**
   ```bash
   cd /home/coder/projects/arcade_station && source .venv/bin/activate && python -m mypy src/ install/ tests/
   ```

4. **Pytest (test suite)**
   ```bash
   cd /home/coder/projects/arcade_station && source .venv/bin/activate && python -m pytest -v
   ```

5. **Pytest with coverage**
   ```bash
   cd /home/coder/projects/arcade_station && source .venv/bin/activate && python -m pytest --cov=src/arcade_station
   ```

6. **Markdownlint (markdown files)**
   ```bash
   cd /home/coder/projects/arcade_station && npx markdownlint-cli2 '**/*.md'
   ```

7. **Taplo (TOML validation)**
   ```bash
   cd /home/coder/projects/arcade_station && npx @taplo/cli check config/*.toml pyproject.toml
   ```

8. **Shellcheck (shell scripts)**
   ```bash
   cd /home/coder/projects/arcade_station && shellcheck bin/unix/*.sh setup.sh src/arcade_station/core/linux/*.sh src/arcade_station/core/macos/*.sh
   ```

9. **PSScriptAnalyzer (PowerShell scripts) -- if pwsh is available**
   Check if `pwsh` is on PATH. If yes, run PSScriptAnalyzer on all `.ps1` and
   `.psm1` files:
   ```bash
   pwsh -Command "Import-Module PSScriptAnalyzer; \
     Get-ChildItem -Path /home/coder/projects/arcade_station -Recurse -Include '*.ps1','*.psm1' | \
     ForEach-Object { Invoke-ScriptAnalyzer -Path \$_.FullName -Severity Warning,Error } | \
     Format-Table -AutoSize"
   ```
   If `pwsh` is not available, report **SKIP** with a note.

### Output format

Produce a summary table at the end:

```
| # | Gate              | Result |
|---|-------------------|--------|
| 1 | Black             | PASS/FAIL |
| 2 | Flake8            | PASS/FAIL |
| 3 | Mypy              | PASS/FAIL |
| 4 | Pytest            | PASS/FAIL |
| 5 | Pytest + coverage | PASS/FAIL |
| 6 | Markdownlint      | PASS/FAIL |
| 7 | Taplo             | PASS/FAIL |
| 8 | Shellcheck        | PASS/FAIL |
| 9 | PSScriptAnalyzer  | PASS/FAIL/SKIP |
```

For any FAIL, include the full command output immediately above the summary table.

Do NOT fix any issues. Report only.
