# Acceptance Validation: Multi-Phase Code Hygiene Initiative

You are the product-manager agent performing acceptance validation for the
"Multi-phase code hygiene initiative" feature.

## Your task

Validate every acceptance criterion from the exec plan. You must run actual
commands to verify each criterion -- do not just review code or trust previous
output. Every criterion must receive an explicit PASS or FAIL verdict.

## Setup -- REQUIRED FIRST STEP

Before running any Python commands, activate the virtual environment:

```bash
source /home/coder/projects/arcade_station/.venv/bin/activate
```

You MUST run this activation command before every bash invocation that uses
Python tools (black, flake8, mypy, pytest), because each bash call starts a
fresh shell.

## Working directory

All commands must be run from: `/home/coder/projects/arcade_station`

## Exec plan location

`/home/coder/projects/arcade_station/docs/exec-plans/active/2026-03-27-code-hygiene-initiative.md`

## Acceptance criteria to validate

Validate each criterion below by running the specified command and checking the
exit code. Report PASS or FAIL for each one with the actual command output.

### Phase 1

1. **black formatting**: Run `source /home/coder/projects/arcade_station/.venv/bin/activate && cd /home/coder/projects/arcade_station && python -m black --check src/ install/` -- must exit 0 with no reformatting needed.

2. **flake8 warnings**: Run `source /home/coder/projects/arcade_station/.venv/bin/activate && cd /home/coder/projects/arcade_station && python -m flake8 src/ install/` -- must exit 0 with zero warnings.

3. **mypy errors**: Run `source /home/coder/projects/arcade_station/.venv/bin/activate && cd /home/coder/projects/arcade_station && python -m mypy src/ install/` -- must exit 0 with zero errors.

4. **TOML validation**: Run `cd /home/coder/projects/arcade_station && npx @taplo/cli check config/*.toml pyproject.toml` -- must exit 0 with zero errors on all .toml files.

5. **PSScriptAnalyzer**: Check if `pwsh` is available. If so, run `cd /home/coder/projects/arcade_station && pwsh -Command "Import-Module PSScriptAnalyzer; Invoke-ScriptAnalyzer -Path install_logic.ps1; Invoke-ScriptAnalyzer -Path src/arcade_station/core/windows/ -Recurse"` -- must report zero warnings/errors. If pwsh is unavailable, check for a documented skip note in the exec plan or task history (PASS if documented).

6. **shellcheck**: Run `cd /home/coder/projects/arcade_station && shellcheck bin/unix/take_screenshot.sh setup.sh src/arcade_station/core/linux/arcade_station_start.sh src/arcade_station/core/macos/arcade_station_start.sh` -- must exit 0.

7. **VS Code tasks**: Read `/home/coder/projects/arcade_station/.vscode/tasks.json` and verify it contains BOTH a Windows "Activate .venv" task AND a Linux-compatible "Activate .venv (Linux)" task. Report PASS/FAIL based on file contents.

8. **Pre-commit hook**: Verify the pre-commit hook exists at `/home/coder/projects/arcade_station/.git/hooks/pre-commit` and contains commands for `black --check`, `flake8`, and `markdownlint-cli2`. Read the file and check. Do NOT actually run a git commit.

9. **Dev requirements**: Read `/home/coder/projects/arcade_station/requirements-dev.txt` and verify it includes `black`, `flake8`, `mypy`, and `pytest` as uncommented entries.

### Phase 2

10. **markdownlint**: Run `cd /home/coder/projects/arcade_station && npx markdownlint-cli2 '**/*.md'` -- must exit 0 with zero errors.

11. **No temporary ignores**: Read `/home/coder/projects/arcade_station/.markdownlint-cli2.jsonc` and verify it contains NO ignore entries for: README.md, PLAN.MD, THANKS.md, examples/DDR.md, examples/LAPTOP.md, src/arcade_station/core/windows/README_ICLOUD.md, src/pegasus-fe/themes/micro/README.md. The only allowed ignore is `.state/inbox/*.md`.

12. **7 markdown files clean**: Run markdownlint explicitly on each of the 7 previously-failing files: `cd /home/coder/projects/arcade_station && npx markdownlint-cli2 README.md PLAN.MD THANKS.md examples/DDR.md examples/LAPTOP.md src/arcade_station/core/windows/README_ICLOUD.md src/pegasus-fe/themes/micro/README.md` -- must exit 0.

### Phase 3

13. **Test directory exists**: Check that `/home/coder/projects/arcade_station/tests/` exists with `conftest.py` and `unit/` subdirectory: `ls -la /home/coder/projects/arcade_station/tests/ /home/coder/projects/arcade_station/tests/unit/`

14. **Pytest discovers tests**: Run `source /home/coder/projects/arcade_station/.venv/bin/activate && cd /home/coder/projects/arcade_station && python -m pytest --collect-only` -- must discover at least one test.

15. **Unit tests for core_functions.py**: Verify `/home/coder/projects/arcade_station/tests/unit/test_core_functions.py` exists and contains tests for: `determine_operating_system`, `convert_path_for_platform`, `load_toml_config`, `load_key_mappings_from_toml`, `load_installed_games`, `load_game_config`, `load_mame_config`, `log_message`. Read the file and check.

16. **All tests pass**: Run `source /home/coder/projects/arcade_station/.venv/bin/activate && cd /home/coder/projects/arcade_station && python -m pytest -v` -- must exit 0 with zero failures and zero errors.

17. **Test suite under 30 seconds**: Check the timing output from the pytest run above -- must complete in under 30 seconds.

18. **Pre-push hook**: Read `/home/coder/projects/arcade_station/.git/hooks/pre-push` and verify it contains `python -m pytest` (or equivalent). It must run real tests, not a no-op skip. Do NOT actually run a git push.

19. **Coverage report**: Run `source /home/coder/projects/arcade_station/.venv/bin/activate && cd /home/coder/projects/arcade_station && python -m pytest --cov=src/arcade_station` -- must produce a coverage report without error.

## Output format

Present your findings as a checklist:

```
## Acceptance Validation Results

### Phase 1
- [ ] or [x] Criterion 1: black formatting -- PASS/FAIL (brief evidence)
- [ ] or [x] Criterion 2: flake8 -- PASS/FAIL (brief evidence)
... etc.

### Phase 2
... etc.

### Phase 3
... etc.

## Overall Verdict
ACCEPT / REJECT (with explanation if rejecting)
```

For any FAIL, include the exact error output so the team can diagnose.

## Rules

- Do NOT implement any fixes. Report only.
- Do NOT skip any criterion. Every single one must be checked.
- "Looks good" is not acceptance. Run the command. Check the exit code. Report the output.
- Always activate the venv before Python commands: `source /home/coder/projects/arcade_station/.venv/bin/activate`
