# Task: P3-T2 -- Write unit tests for core_functions.py pure/config functions

## Environment setup (MUST DO FIRST)

Activate the virtual environment before running ANY Python commands:

```bash
source /home/coder/projects/arcade_station/.venv/bin/activate
```

Run this at the start of every new terminal/bash session. Verify with `which python` -- it must point to `/home/coder/projects/arcade_station/.venv/bin/python`.

## Context

- **Feature:** Multi-phase code hygiene initiative
- **State file:** `/home/coder/projects/arcade_station/.state/feature-state.json`
- **Exec plan:** `/home/coder/projects/arcade_station/docs/exec-plans/active/2026-03-27-code-hygiene-initiative.md`
- **Coding standards:** `/home/coder/projects/arcade_station/docs/CONTRIBUTING.md`
- **Source under test:** `/home/coder/projects/arcade_station/src/arcade_station/core/common/core_functions.py`
- **Existing test infra:** `/home/coder/projects/arcade_station/tests/conftest.py`, `/home/coder/projects/arcade_station/tests/__init__.py`, `/home/coder/projects/arcade_station/tests/unit/__init__.py`
- **pyproject.toml:** `/home/coder/projects/arcade_station/pyproject.toml`

This task was previously attempted but the changes were reverted. You are redoing it from scratch. The file `tests/unit/test_core_functions.py` does NOT exist yet -- create it fresh.

## What to implement

Create `/home/coder/projects/arcade_station/tests/unit/test_core_functions.py` with unit tests for the pure/config functions in `core_functions.py`. Read the source file carefully before writing tests.

### Functions to test and required test cases

1. **`determine_operating_system()`** -- Mock `platform.system()` for three cases: `"Windows"`, `"Linux"`, `"Darwin"`. Verify return value matches the mocked value.

2. **`convert_path_for_platform(path)`** -- Use `@pytest.mark.parametrize`. Required cases:
   - Forward-slash path on Windows -> backslashes (`"path/to/file"` on Windows -> `"path\\to\\file"`)
   - Backslash path on Linux -> forward slashes (`"path\\to\\file"` on Linux -> `"path/to/file"`)
   - `None` input -> returns `None`
   - Empty string input -> returns empty string (falsy, same branch as None)
   - **Windows input with backslashes only** (`"path\\to\\file"` on Windows -> `"path\\to\\file"` unchanged)
   - **Darwin input with forward slashes only** (`"path/to/file"` on Darwin -> `"path/to/file"` unchanged)

3. **`load_toml_config(file_name)`** -- Use `tmp_path` fixture and patch `builtins.open` or the path computation so it reads from a temp directory:
   - Valid TOML file: write a valid TOML to tmp_path, verify returned dict matches
   - Missing file: verify `FileNotFoundError` is raised
   - Invalid TOML: write garbage content, verify `tomllib.TOMLDecodeError` is raised

4. **`load_key_mappings_from_toml(toml_file_path)`** -- Mock `load_toml_config` to return controlled data:
   - Config with `key_mappings` dict containing entries -> returns those entries
   - Config with NO `key_mappings` key (e.g., `{"other": "data"}`) -> returns empty dict
   - **Do NOT include a test for empty key_mappings** (`{"key_mappings": {}}`) -- this exercises the same `if not key_mappings:` code path as the no-key case. CONTRIBUTING.md requires every test to exercise a distinct code path. Only include the `no_key_mappings_key` test.

5. **`load_installed_games()` / `load_game_config()` / `load_mame_config()`** -- Mock `load_toml_config` and verify each calls it with the correct TOML filename (`"pegasus_binaries.toml"`, `"installed_games.toml"`, `"mame_config.toml"` respectively).

6. **`log_message(message, prefix)`** -- Capture logging output or patch the logging/file-writing:
   - With prefix: verify output contains `[prefix]` and the message
   - Without prefix: verify output contains the message but not `[] ` pattern
   - Verify timestamp format `[YYYY-MM-DD HH:MM:SS]` is present

### Coding standards (MUST follow)

- All test functions must have Google-style docstrings explaining what they test
- Use `unittest.mock.patch` for IO-dependent functions
- Use `str | None` union syntax -- do NOT use `from typing import Optional` (project targets Python 3.12 exclusively)
- Use absolute imports: `from arcade_station.core.common.core_functions import ...`
- Every test exercises a distinct code path -- no tautological tests

### Infrastructure fixes (do these BEFORE writing tests)

1. **Add `pythonpath` to pytest config:** In `/home/coder/projects/arcade_station/pyproject.toml`, add `pythonpath = ["src"]` to the `[tool.pytest.ini_options]` section. This is needed so pytest can resolve `from arcade_station.core.common.core_functions import ...` imports.

2. **Fix conftest.py fixture:** In `/home/coder/projects/arcade_station/tests/conftest.py`, the `toml_config_dir` fixture calls `monkeypatch.setenv("ARCADE_STATION_CONFIG_DIR", ...)` but `load_toml_config` never reads that env var -- it computes the config path from `__file__`. Remove the `monkeypatch.setenv` call and update the docstring to document that tests needing to redirect config lookups should patch `builtins.open` directly. Keep the `tmp_path` parameter and the config dir creation (those are still useful). Remove the `monkeypatch` parameter entirely since it is no longer used.

3. **Check for erroneous root-level `__init__.py`:** If `/home/coder/projects/arcade_station/__init__.py` exists, delete it -- it is not a valid package marker at the repo root. (It likely does not exist, but verify.)

### Quality gates (MUST all pass before reporting done)

Run these commands (after activating the venv) and fix any failures:

```bash
cd /home/coder/projects/arcade_station
python -m pytest tests/unit/test_core_functions.py -v
python -m pytest --cov=src/arcade_station --cov-report=term-missing
python -m black --check src/ install/ tests/
python -m flake8 src/ install/ tests/
python -m mypy src/ install/ tests/
```

All must exit 0. Do NOT use `--no-verify` on anything. Fix root causes.

### What NOT to do

- Do NOT modify `core_functions.py` -- this task is tests only
- Do NOT write integration tests or tests that require real processes, real filesystem config files, or network access
- Do NOT add any new runtime dependencies
- Do NOT create any `__init__.py` at the repo root

### Report when done

Summarize:
- Files created/modified
- Number of tests written
- All quality gate results (pass/fail with command output)
- Coverage report output
