# Multi-Phase Code Hygiene Initiative

## Goal

Establish a fully enforced, zero-warning quality toolchain (linting, formatting,
type checking, markdown validation, and test infrastructure) across the codebase,
with zero behavior changes to runtime code.

## Scope

All work is organized into three sequential phases, each delivered as its own
branch and pull request. All changes are non-functional — no runtime behavior
may change.

### Phase 1: Environment bootstrap + Python linting

- Install all Python development dependencies into the virtual environment,
  including `black`, `flake8`, `mypy`, and `pytest` (uncommented/added in
  `requirements.txt` or an equivalent dev requirements file).
- Add TOML linting via `taplo` (installed as `@taplo/cli` via `npm`) — validate
  all `.toml` files in the repository.
- Add PowerShell linting via `PSScriptAnalyzer` — validate all `.ps1` scripts
  under `bin/windows/` regardless of the developer's host platform.
- Add shell script linting via `shellcheck` — validate all `.sh` scripts under
  `bin/unix/` and the repo root.
- Run `black` to auto-format all Python files under `src/` and `install/`.
- Fix all `flake8` warnings in `src/` and `install/` (zero warnings required).
- Confirm `mypy src/ install/` passes (zero errors required).
- Fix all `taplo`, `PSScriptAnalyzer`, and `shellcheck` warnings found in
  existing files.
- Update `.vscode/tasks.json`: add a Linux-compatible "Activate .venv" task
  (using Unix paths) alongside the existing Windows task.
- Confirm all pre-commit hooks pass with real enforcement, including the new
  linters.

### Phase 2: Markdown linting

- Fix all 39 markdownlint errors in the following pre-existing files:
  - `README.md`
  - `PLAN.MD`
  - `THANKS.md`
  - `examples/DDR.md`
  - `examples/LAPTOP.md`
  - `src/arcade_station/core/windows/README_ICLOUD.md`
  - `src/pegasus-fe/themes/micro/README.md`
- Remove all temporary ignore entries from `.markdownlint-cli2.jsonc` that
  were added to suppress pre-existing errors.
- Confirm `npx markdownlint-cli2 '**/*.md'` passes with zero errors.

### Phase 3: Test scaffolding

- Create the `tests/` directory structure following pytest conventions.
- Add pytest configuration (`pyproject.toml` or `pytest.ini`).
- Write unit tests for all stable pure functions in
  `src/arcade_station/core/common/core_functions.py`.
- Confirm `python -m pytest` passes with zero failures.
- Confirm the pre-push hook runs real pytest (not a no-op) and passes.
- Set up test coverage reporting (e.g., `pytest-cov`) so coverage can be
  measured and reported on demand.

## Out of scope

- Changes to any runtime behavior, configuration values, or application logic.
- Adding docstrings to existing public functions that currently lack them
  (this is a separate ongoing effort; only new code written in Phase 3 must
  follow the Google-style docstring standard from `docs/CONTRIBUTING.md`).
- Full test coverage of all public methods across the entire codebase —
  Phase 3 establishes the test infrastructure and seeds one module
  (`core_functions.py`); remaining coverage is a follow-on effort.
- Adding `mypy` or new linters to the git pre-commit hook (beyond confirming
  they pass) — hook configuration changes are limited to what is explicitly
  described in Phase 1.
- CI/CD pipeline setup (no automated CI exists; quality gates remain local).
- Upgrading or replacing any runtime dependency (`PyQt5`, `keyboard`, `psutil`,
  `tomli_w`, `Pillow`).
- Changes to `config/` TOML values or game configuration.

## Constraints

- Every change must be non-functional — zero runtime behavior differences.
- Each phase must be its own branch and PR. Branch naming: `feature/<description>`.
- Python 3.12.9 required; no other Python version supported.
- Runtime dependencies are fixed: `PyQt5`, `keyboard`, `psutil`, `tomli_w`,
  `Pillow` — no additions or removals.
- No hardcoded paths or credentials — all paths come from TOML config files in
  `config/`.
- Platform-specific code must remain in `src/arcade_station/core/{windows,linux,macos}/`.
- Test suite must complete in under 30 seconds (from `docs/RELIABILITY.md`).
- All changes must satisfy every coding standard in `docs/CONTRIBUTING.md`
  with no exceptions (black, flake8, mypy, markdownlint, no bare `except:`,
  no mutable defaults, Google-style docstrings on new public functions, etc.).
- `pre-commit` hook must enforce: `black --check`, `flake8`, `markdownlint-cli2`.
- `pre-push` hook must enforce: `python -m pytest`.
- Never use `--no-verify` — fix the root cause.

## Acceptance criteria

### Phase 1

- [x] `python -m black --check src/ install/` exits 0 with no reformatting needed.
- [x] `python -m flake8 src/ install/` exits 0 with zero warnings.
- [x] `python -m mypy src/ install/` exits 0 with zero errors.
- [x] `npx @taplo/cli check **/*.toml` (or equivalent invocation) exits 0 with zero errors on all `.toml` files in the repo.
- [x] `Invoke-ScriptAnalyzer` run against all `.ps1` files under `bin/windows/` reports zero warnings or errors.
- [x] `shellcheck` run against all `.sh` files under `bin/unix/` and the repo root exits 0 with zero warnings.
- [x] `.vscode/tasks.json` contains both a Windows "Activate .venv" task (existing) and a new Linux-compatible "Activate .venv" task using Unix paths.
- [x] Running `git commit` on a staged change triggers the pre-commit hook and all checks pass without `--no-verify`.
- [x] `requirements.txt` (or equivalent dev requirements file) includes `black`, `flake8`, `mypy`, and `pytest` as uncommented entries.

### Phase 2

- [x] `npx markdownlint-cli2 '**/*.md'` exits 0 with zero errors across all markdown files.
- [x] `.markdownlint-cli2.jsonc` contains no temporary ignore entries for pre-existing files (`README.md`, `PLAN.MD`, `THANKS.md`, `examples/DDR.md`, `examples/LAPTOP.md`, `src/arcade_station/core/windows/README_ICLOUD.md`, `src/pegasus-fe/themes/micro/README.md`).
- [x] All 7 previously-failing markdown files parse and render without lint errors.

### Phase 3

- [x] A `tests/` directory exists at the repo root with at least one subdirectory or `conftest.py` following pytest conventions.
- [x] Pytest configuration exists (`pyproject.toml` `[tool.pytest.ini_options]` section or `pytest.ini`) and `python -m pytest --collect-only` discovers at least one test.
- [x] Unit tests exist for every stable pure function in `src/arcade_station/core/common/core_functions.py` (one test per distinct code path, not tautological).
- [x] `python -m pytest` exits 0 with zero failures and zero errors.
- [x] `python -m pytest` completes in under 30 seconds.
- [x] Running `git push` triggers the pre-push hook and `python -m pytest` runs for real (not skipped) and passes.
- [x] `pytest-cov` (or equivalent) is installed and `python -m pytest --cov=src/arcade_station` produces a coverage report without error.

## Design

### Approach

This initiative installs a comprehensive local quality toolchain in three
sequential phases: Python linting/formatting (Phase 1), markdown linting
(Phase 2), and test infrastructure (Phase 3). Each phase is a standalone
branch/PR because each builds on the clean baseline established by the
previous phase — Phase 2 depends on Phase 1's formatting being stable so
markdown-only changes are reviewable in isolation, and Phase 3 depends on
both phases so that new test files are born clean under all linters.

The strategy is toolchain-first: configure each tool, auto-fix what can be
auto-fixed (black formatting), then manually resolve remaining warnings.
No runtime code changes are permitted — only whitespace, imports, type
annotations, and lint pragmas. A new `pyproject.toml` at the repo root
becomes the single source of truth for all Python tool configuration (black,
flake8, mypy, pytest), replacing scattered or missing config files.

### Phase 1: Environment bootstrap + Python linting

#### Tool configuration

**`pyproject.toml`** (new file at repo root) — central config for all Python
tooling:

```toml
[tool.black]
line-length = 88
target-version = ["py312"]

[tool.flake8]
max-line-length = 88
extend-ignore = ["E203", "W503"]
per-file-ignores = [
    "__init__.py:F401",
]

[tool.mypy]
python_version = "3.12"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = false
check_untyped_defs = true
ignore_missing_imports = true

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "-v --tb=short"
```

Rationale for key choices:

- **black line-length 88**: black's default; avoids conflicts with flake8
  when `E203` and `W503` are ignored (these rules conflict with black's
  formatting of slice notation and line breaks before binary operators).
- **flake8 `extend-ignore`**: `E203` (whitespace before `:`) and `W503`
  (line break before binary operator) conflict with black. The
  `per-file-ignores` for `__init__.py:F401` allows re-export imports.
- **mypy `ignore_missing_imports`**: Required because runtime dependencies
  (`keyboard`, `psutil`, `PyQt5`) lack complete type stubs. Starting with
  `check_untyped_defs = true` but not `disallow_untyped_defs` — this checks
  the bodies of untyped functions without requiring every existing function to
  have annotations. This is pragmatic for an existing codebase.
- **flake8 config note**: flake8 does not read `pyproject.toml` natively.
  Configuration must go in a `.flake8` file or `setup.cfg`. Create a
  `.flake8` file at repo root with the settings above.

**`requirements-dev.txt`** (new file) — development dependencies kept
separate from runtime `requirements.txt`:

```text
# Development and quality tools — not needed at runtime
black>=23.0.0
flake8>=6.0.0
mypy>=1.0.0
pytest>=7.0.0
pytest-cov>=4.0.0
```

Rationale: Separating dev dependencies avoids bloating the runtime install.
The existing `requirements.txt` keeps its commented-out entries removed (they
become redundant). A comment in `requirements.txt` should reference
`requirements-dev.txt` for development tools.

**taplo**: Installed via `npm install -g @taplo/cli` (or `npx @taplo/cli`).
No config file needed — taplo validates against the TOML spec by default.
Run as `npx @taplo/cli check **/*.toml` or `taplo check` if installed
globally. The 9 `.toml` files under `config/` are the primary targets.

**PSScriptAnalyzer**: This is a PowerShell module, not a standalone binary.
On Linux (the dev environment), it requires `pwsh` (PowerShell Core). The
linting command is:
`pwsh -Command "Import-Module PSScriptAnalyzer; Invoke-ScriptAnalyzer -Path bin/windows/ -Recurse"`.
Target files: 4 `.ps1` files (repo root `install_logic.ps1` and 4 under
`src/arcade_station/core/windows/`) plus 1 `.psm1` module. Note:
`install_logic.ps1` is at repo root, not under `bin/windows/` — the
analyzer invocation must cover both locations.

**shellcheck**: Validate `.sh` files. Target files:
`bin/unix/take_screenshot.sh`, `setup.sh`,
`src/arcade_station/core/linux/arcade_station_start.sh`,
`src/arcade_station/core/macos/arcade_station_start.sh`,
`.claude/hooks/session-start.sh`. Run as
`shellcheck bin/unix/*.sh setup.sh src/arcade_station/core/linux/*.sh src/arcade_station/core/macos/*.sh`.
Exclude `.claude/hooks/session-start.sh` from shellcheck scope as it is
agent infrastructure, not application code.

#### Components to change (Phase 1)

| Action | File/directory | What changes |
|--------|---------------|-------------|
| Create | `pyproject.toml` | Python tool config (black, mypy, pytest) |
| Create | `.flake8` | flake8 config (cannot use pyproject.toml) |
| Create | `requirements-dev.txt` | Dev-only Python dependencies |
| Modify | `requirements.txt` | Remove commented dev deps, add reference to `requirements-dev.txt` |
| Modify | `src/**/*.py` (22 files) | black auto-format, flake8 fixes, type annotation fixes |
| Modify | `install/**/*.py` (21 files) | black auto-format, flake8 fixes, type annotation fixes |
| Modify | `config/*.toml` (9 files) | taplo format fixes (if any) |
| Modify | `install_logic.ps1` | PSScriptAnalyzer fixes |
| Modify | `src/arcade_station/core/windows/*.ps1` (4 files) | PSScriptAnalyzer fixes |
| Modify | `src/arcade_station/core/windows/core_functions.psm1` | PSScriptAnalyzer fixes |
| Modify | `bin/unix/take_screenshot.sh` | shellcheck fixes |
| Modify | `setup.sh` | shellcheck fixes |
| Modify | `src/arcade_station/core/linux/arcade_station_start.sh` | shellcheck fixes |
| Modify | `src/arcade_station/core/macos/arcade_station_start.sh` | shellcheck fixes |
| Modify | `.vscode/tasks.json` | Add Linux-compatible "Activate .venv" task |
| Modify | `hooks/pre-commit` | Ensure linters run with real enforcement (review skip logic) |

#### VS Code task addition

Add a new task to `.vscode/tasks.json`:

```json
{
  "label": "Activate .venv (Linux)",
  "type": "shell",
  "command": "source ${workspaceFolder}/.venv/bin/activate",
  "presentation": {
    "reveal": "always",
    "panel": "shared"
  },
  "detail": "Activates the virtual environment on Linux/macOS"
}
```

### Phase 2: Markdown linting

#### Approach

Fix all 39 markdownlint errors across 7 files. The existing
`.markdownlint.json` disables 13 rules globally — some of these may need to
be re-evaluated, but changes to the rule config are out of scope unless a
rule must be re-enabled to satisfy the acceptance criteria. The primary work
is fixing the 7 files listed in `.markdownlint-cli2.jsonc` ignore entries.

#### Components to change (Phase 2)

| Action | File | What changes |
|--------|------|-------------|
| Modify | `README.md` | Fix markdownlint errors |
| Modify | `PLAN.MD` | Fix markdownlint errors |
| Modify | `THANKS.md` | Fix markdownlint errors |
| Modify | `examples/DDR.md` | Fix markdownlint errors |
| Modify | `examples/LAPTOP.md` | Fix markdownlint errors |
| Modify | `src/arcade_station/core/windows/README_ICLOUD.md` | Fix markdownlint errors |
| Modify | `src/pegasus-fe/themes/micro/README.md` | Fix markdownlint errors |
| Modify | `.markdownlint-cli2.jsonc` | Remove all temporary file ignores (keep `.state/inbox/*.md`) |

### Phase 3: Test scaffolding

#### Directory structure

```text
tests/
├── conftest.py              # Shared fixtures (e.g., temp dirs, mock config)
├── unit/
│   ├── __init__.py
│   └── test_core_functions.py   # Tests for core_functions.py
└── __init__.py
```

The `tests/unit/` subdirectory follows pytest conventions and leaves room for
future `tests/integration/` when integration tests are needed.

#### Functions to test in `core_functions.py`

Classify each public function as semantic (pure/testable) or pragmatic
(IO/side-effects):

| Function | Classification | Testable? | Notes |
|----------|---------------|-----------|-------|
| `determine_operating_system()` | Semantic | Yes | Thin wrapper; mock `platform.system()` |
| `convert_path_for_platform(path)` | Semantic | Yes | Pure logic; mock `platform.system()` for both branches |
| `load_toml_config(file_name)` | Pragmatic | Yes (with fixture) | Needs temp TOML file fixture |
| `load_key_mappings_from_toml(...)` | Pragmatic | Yes (with fixture) | Depends on `load_toml_config`; mock or fixture |
| `log_message(message, prefix)` | Pragmatic | Yes | Test formatting output; mock file/logging |
| `open_header(script_name)` | Pragmatic | Integration | Sets globals, creates dirs — integration test candidate |
| `kill_processes_from_toml(...)` | Pragmatic | No (Phase 3) | Requires psutil mocking; defer to follow-on |
| `start_listening_to_keybinds_from_toml(...)` | Pragmatic | No (Phase 3) | Blocks forever; skip |
| `kill_process_by_identifier(...)` | Pragmatic | No (Phase 3) | Heavy psutil dependency |
| `launch_script(...)` | Pragmatic | No (Phase 3) | Subprocess launching |
| `start_app(...)` | Pragmatic | No (Phase 3) | Platform-specific subprocess |
| `kill_pegasus()` | Pragmatic | No (Phase 3) | psutil process iteration |
| `start_pegasus()` | Pragmatic | No (Phase 3) | Complex subprocess + file search |
| `start_process(...)` | Pragmatic | No (Phase 3) | Platform-specific subprocess |
| `load_installed_games()` | Pragmatic | Yes (with fixture) | Thin wrapper on `load_toml_config` |
| `load_game_config()` | Pragmatic | Yes (with fixture) | Thin wrapper on `load_toml_config` |
| `load_mame_config()` | Pragmatic | Yes (with fixture) | Thin wrapper on `load_toml_config` |
| `run_powershell_script(...)` | Pragmatic | No (Phase 3) | Subprocess |
| `start_process_with_powershell(...)` | Pragmatic | No (Phase 3) | Windows-only subprocess |

Phase 3 unit tests target the **stable pure functions** and the thin
config-loading wrappers:

1. `determine_operating_system` — mock `platform.system()` to return each OS
   string; verify return value matches.
2. `convert_path_for_platform` — parametrize: Windows converts `/` to `\`,
   Unix converts `\` to `/`, `None` input returns `None`, empty string
   returns empty string.
3. `load_toml_config` — use `tmp_path` fixture with a valid TOML file; test
   successful parse. Test `FileNotFoundError` for missing file. Test
   `TOMLDecodeError` for invalid TOML.
4. `load_key_mappings_from_toml` — fixture with TOML containing
   `[key_mappings]`; verify dict returned. Test empty mappings case.
5. `load_installed_games`, `load_game_config`, `load_mame_config` — mock
   `load_toml_config` to verify each calls the correct TOML filename.
6. `log_message` — capture output; verify timestamp format and prefix
   inclusion/exclusion.

#### `conftest.py` fixtures

```python
@pytest.fixture
def toml_config_dir(tmp_path, monkeypatch):
    """Create a temporary config directory and patch core_functions to use it."""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    # Monkeypatch the base_path calculation in load_toml_config
    return config_dir
```

The key challenge is that `load_toml_config` computes `base_path` relative
to `__file__`. The fixture must either monkeypatch the path calculation or
create a temp TOML file and patch `os.path.abspath` / `os.path.dirname`
within the function's scope. The cleanest approach is to monkeypatch
`os.path.abspath` for the specific call inside `load_toml_config`, or to
extract the config directory resolution into a helper function that can be
patched. However, since this is a non-functional initiative, we should NOT
refactor `core_functions.py` — instead, use `unittest.mock.patch` to mock
the `open` call or the computed `config_path`.

#### Coverage reporting

`pytest-cov` is included in `requirements-dev.txt`. Configuration in
`pyproject.toml`:

```toml
[tool.coverage.run]
source = ["src/arcade_station"]

[tool.coverage.report]
show_missing = true
skip_empty = true
```

Run with: `python -m pytest --cov=src/arcade_station`

#### Components to change (Phase 3)

| Action | File/directory | What changes |
|--------|---------------|-------------|
| Create | `tests/__init__.py` | Empty init for test package |
| Create | `tests/conftest.py` | Shared fixtures |
| Create | `tests/unit/__init__.py` | Empty init for unit test subpackage |
| Create | `tests/unit/test_core_functions.py` | Unit tests for pure/config functions |
| Modify | `pyproject.toml` | Add `[tool.pytest.ini_options]` and `[tool.coverage.*]` sections (already specified in Phase 1 config above) |
| Modify | `requirements-dev.txt` | Already includes `pytest` and `pytest-cov` from Phase 1 |
| Verify | `hooks/pre-push` | Confirm `python -m pytest` runs real tests (currently skips if pytest not installed — after Phase 1 it will be installed) |

### Data model changes

None. This initiative is entirely non-functional — no data models, schemas,
or configuration values change.

### API changes

None. No endpoints, entry points, or public interfaces change.

### Phase sequencing rationale

The three phases must be sequential:

1. **Phase 1 before Phase 2**: black reformatting will touch every Python
   file. If markdown fixes were done first, the Phase 1 PR would contain
   irrelevant markdown diffs mixed with Python changes, making review
   difficult. More importantly, the pre-commit hook must pass after Phase 1
   — and it runs markdownlint, which will fail until Phase 2. The
   `.markdownlint-cli2.jsonc` ignores must remain during Phase 1.

2. **Phase 2 before Phase 3**: Phase 3 creates new `.py` and `.md` files
   (test files, potentially a `conftest.py` with docstrings). These files
   must be born clean under all linters. If Phase 2 is not done first, the
   pre-commit hook with markdownlint would need ignore entries for any new
   markdown files. Completing Phase 2 first means the entire markdown
   toolchain is clean and any new file is validated immediately.

3. **No parallelization**: Each phase's PR should be small and reviewable.
   Merging Phase 1 first gives Phase 2 a clean Python baseline. Merging
   Phase 2 gives Phase 3 a clean markdown baseline. This minimizes merge
   conflicts and keeps PRs focused.

### Alternatives considered

#### Ruff instead of black + flake8

**Pros**: Single tool replaces both formatter and linter. Faster execution.
Simpler config (one `[tool.ruff]` section in `pyproject.toml`).

**Cons**: The project's `CONTRIBUTING.md` and `CLAUDE.md` explicitly specify
`black` and `flake8` as the quality gate tools. The git hooks already
reference them by name. Switching to ruff would require updating all
documentation, hooks, and CI references — scope creep for a hygiene
initiative. Ruff is also less mature for some flake8 plugin equivalents.

**Decision**: Rejected. Stay with black + flake8 to match existing standards.
Ruff migration can be a separate future initiative.

#### Single requirements file with extras instead of `requirements-dev.txt`

**Pros**: One file to manage. pip supports `pip install -r requirements.txt`
with optional groups via markers.

**Cons**: pip's `-r` flag does not support extras groups natively (that
requires `pyproject.toml` with `[project.optional-dependencies]`). A full
`pyproject.toml` packaging setup is scope creep. Two files is simple and
well-understood.

**Decision**: Rejected. Use separate `requirements-dev.txt`.

#### nox or tox for test orchestration instead of direct pytest

**Pros**: nox/tox can manage virtual environments and run multiple tool
invocations in sequence.

**Cons**: Adds a dependency and complexity for a project that only targets
one Python version and has no CI. The git hooks already orchestrate tool
runs. nox/tox is warranted when there are multiple Python versions or
complex test matrices — neither applies here.

**Decision**: Rejected. Direct tool invocation via hooks is sufficient.

#### `pytest-cov` vs standalone `coverage.py`

**Pros of `coverage.py`**: More granular control, no pytest dependency for
coverage.

**Cons**: Requires separate invocation (`coverage run -m pytest` then
`coverage report`). `pytest-cov` integrates seamlessly with `--cov` flag.

**Decision**: Use `pytest-cov` — simpler developer experience with a single
command.

### Risks and mitigations

- **Risk**: mypy may report errors in code that uses `keyboard`, `psutil`,
  or `PyQt5` due to missing or incomplete type stubs.
  **Mitigation**: `ignore_missing_imports = true` in mypy config. If
  specific function bodies cause errors, use targeted `# type: ignore[code]`
  comments with specific error codes, never bare `# type: ignore`.

- **Risk**: black reformatting may cause semantic changes in edge cases
  (e.g., trailing comma insertion changing tuple vs. expression).
  **Mitigation**: Run the test suite after black formatting. All tests must
  pass before committing. Review black's diff for any suspicious changes.

- **Risk**: PSScriptAnalyzer requires `pwsh` (PowerShell Core) which may not
  be installed on the Linux dev environment.
  **Mitigation**: Document the `pwsh` installation requirement. If `pwsh` is
  unavailable, PSScriptAnalyzer checks can be run manually or skipped with a
  documented note. Do not add PSScriptAnalyzer to the pre-commit hook (out
  of scope per the exec plan).

- **Risk**: shellcheck may flag issues in shell scripts that are intentional
  (e.g., word splitting in `setup.sh`).
  **Mitigation**: Use targeted `# shellcheck disable=SCXXXX` directives with
  comments explaining why, rather than global suppressions.

- **Risk**: flake8's `E203` and `W503` rules conflict with black's
  formatting.
  **Mitigation**: Explicitly ignore these in `.flake8` config. This is a
  well-known and widely-accepted practice.

- **Risk**: Pre-commit hook currently uses soft-skip logic (`if command -v
  ... then ... else SKIP`). After Phase 1, tools will be installed, but a
  fresh clone without `pip install -r requirements-dev.txt` would still skip.
  **Mitigation**: This is acceptable — the hook is a convenience gate, not a
  CI replacement. Document the setup steps clearly.

- **Risk**: `load_toml_config` uses `__file__`-relative path resolution,
  making it hard to test without monkeypatching.
  **Mitigation**: Use `unittest.mock.patch` to mock the built-in `open` or
  to patch `os.path.abspath` within test scope. Do NOT refactor
  `core_functions.py` — this is a non-functional initiative.

- **Risk**: Test suite exceeds the 30-second budget.
  **Mitigation**: Phase 3 only tests pure functions and thin wrappers — no
  subprocess calls, no real file system operations (use `tmp_path`), no
  network. Expected execution time: under 2 seconds.

### Performance impact

No expected impact on runtime performance budgets. This initiative changes
only developer tooling, formatting, and test infrastructure. The test suite
budget (< 30 seconds) applies to Phase 3 — the planned unit tests are
lightweight pure-function tests that will execute in well under 1 second.

## Task breakdown

### Phase 1: Environment bootstrap + Python linting (8 tasks)

**P1-T1: Create Python tooling config files and dev requirements**
Create `pyproject.toml` (black, mypy, pytest, coverage config), `.flake8`
(max-line-length=88, extend-ignore E203/W503, per-file-ignores `__init__.py:F401`),
`requirements-dev.txt` (black, flake8, mypy, pytest, pytest-cov). Update
`requirements.txt` to remove commented dev deps and reference
`requirements-dev.txt`. Install dev deps.
Files: `pyproject.toml`, `.flake8`, `requirements-dev.txt`, `requirements.txt`
Done when: All files exist, `pip install -r requirements-dev.txt` succeeds.

**P1-T2: Run black auto-format on all Python files**
Run `black src/ install/` to auto-format. Only formatting -- no flake8/mypy fixes.
Files: `src/**/*.py`, `install/**/*.py`
Done when: `python -m black --check src/ install/` exits 0.

**P1-T3: Fix all flake8 warnings**
Fix all flake8 warnings in `src/` and `install/`. No runtime behavior changes.
Files: `src/**/*.py`, `install/**/*.py`
Done when: `python -m flake8 src/ install/` exits 0.

**P1-T4: Fix all mypy errors**
Fix all mypy errors in `src/` and `install/`. Use targeted
`# type: ignore[code]` with specific error codes where needed.
Files: `src/**/*.py`, `install/**/*.py`
Done when: `python -m mypy src/ install/` exits 0.

**P1-T5: Add TOML validation with taplo**
Validate and fix all `.toml` files using `npx @taplo/cli`.
Files: `config/*.toml`, `pyproject.toml`
Done when: `npx @taplo/cli check **/*.toml` exits 0.

**P1-T6: Add shellcheck validation and fix shell scripts**
Run shellcheck on all `.sh` files (excluding `.claude/hooks/`). Fix warnings.
Use targeted `# shellcheck disable=SCXXXX` with comments where needed.
Files: `bin/unix/take_screenshot.sh`, `setup.sh`,
`src/arcade_station/core/linux/arcade_station_start.sh`,
`src/arcade_station/core/macos/arcade_station_start.sh`
Done when: `shellcheck` exits 0 on all target files.

**P1-T7: Add PSScriptAnalyzer validation and fix PowerShell scripts**
Run PSScriptAnalyzer on all `.ps1`/`.psm1` files. Fix warnings. If `pwsh`
unavailable, document the skip.
Files: `install_logic.ps1`, `src/arcade_station/core/windows/*.ps1`,
`src/arcade_station/core/windows/core_functions.psm1`
Done when: PSScriptAnalyzer reports zero warnings, or documented skip note.

**P1-T8: Add Linux-compatible VS Code .venv activation task**
Add "Activate .venv (Linux)" task to `.vscode/tasks.json`.
Files: `.vscode/tasks.json`
Done when: Both Windows and Linux activation tasks exist in tasks.json.

**P1-T9: Provision Python 3.12 and recreate virtual environment**
Install Python 3.12.9 via pyenv. Recreate `.venv`. Reinstall all requirements.
Fix any new mypy errors from stricter py312 stubs. Confirm all tools pass.
Files: `.venv/`, `pyproject.toml`
Done when: Python 3.12.x in venv, all quality gates pass, no version warnings.

### Phase 2: Markdown linting (2 tasks)

**P2-T1: Fix markdownlint errors in all 7 failing files**
Fix all 39 errors across `README.md`, `PLAN.MD`, `THANKS.md`,
`examples/DDR.md`, `examples/LAPTOP.md`,
`src/arcade_station/core/windows/README_ICLOUD.md`,
`src/pegasus-fe/themes/micro/README.md`. No content/meaning changes.
Files: 7 markdown files listed above
Done when: `npx markdownlint-cli2` exits 0 on all 7 files.

**P2-T2: Remove temporary markdownlint ignore entries**
Remove all temporary file ignores from `.markdownlint-cli2.jsonc`. Keep
`.state/inbox/*.md` ignore.
Files: `.markdownlint-cli2.jsonc`
Done when: `npx markdownlint-cli2 '**/*.md'` exits 0. No ignores for the 7 files.

### Phase 3: Test scaffolding (2 tasks)

**P3-T1: Create test directory structure and pytest configuration**
Create `tests/__init__.py`, `tests/conftest.py` (with `toml_config_dir`
fixture), `tests/unit/__init__.py`. Verify pytest config in `pyproject.toml`.
Files: `tests/__init__.py`, `tests/conftest.py`, `tests/unit/__init__.py`
Done when: `python -m pytest --collect-only` runs without error.

**P3-T2: Write unit tests for core_functions.py**
Test all stable pure/config functions: `determine_operating_system`,
`convert_path_for_platform`, `load_toml_config`, `load_key_mappings_from_toml`,
`load_installed_games`, `load_game_config`, `load_mame_config`, `log_message`.
One test per distinct code path, Google-style docstrings, `unittest.mock.patch`
for IO. Do NOT refactor `core_functions.py`.
Files: `tests/unit/test_core_functions.py`
Done when: `python -m pytest -v` exits 0, all tests pass, suite under 30s,
`python -m pytest --cov=src/arcade_station` produces coverage report.

## Progress log

- 2026-03-27 — Exec plan created by product-manager agent (Discovery phase).

## Decision log

- 2026-03-27 — mypy validation added to Phase 1 scope. CONTRIBUTING.md requires
  `mypy src/ install/` to pass with no exceptions; the feature description
  installed mypy but did not explicitly mandate fixing errors. Corrected.
- 2026-03-27 — Full codebase test coverage marked out of scope. CONTRIBUTING.md
  requires every public method to have a test, but Phase 3 is establishing
  infrastructure and seeding one module. Full coverage is a follow-on effort.
  This gap is noted; the principle remains non-negotiable for all future changes.
