<!-- harness:region:start id=doc -->
# Contributing

*Schema template, seeded 2026-09-21. `/seed` fills the placeholder tokens from
the detected project; every `## ` heading is fixed — a section may read
"N/A — none" but is never renamed or reordered. The `keep` region at the bottom
is yours and survives every harness update.*

How code is written here: the commands, the style, and the conventions every
seat is held to. Referenced from `AGENTS.md` for "code style, build/test/lint
commands, git conventions."

## Language & frameworks

- **Language:** Python 3.12.9 (pinned in `requirements.txt`). PowerShell only for
  low-level Windows work (`core_functions.psm1`, `*.ps1`).
- **Primary framework:** Pegasus Frontend — the user-facing display layer; Micro
  theme written in QML, under `src/pegasus-fe`.
- **Other frameworks / runtimes:** PyQt5 (image/marquee display), Tkinter
  (installer UI), `keyboard` (hotkey listeners), `psutil` (process management),
  `tomli_w` (TOML writing), Pillow (installer image processing).
- **Package manager:** pip into a `venv`, from `requirements.txt`
  (+ `requirements-dev.txt` for test tooling). No `pyproject.toml` — a
  deliberate non-choice; do not introduce it.

## Build / test / lint / format commands

*Seed fills each command; the exact string is what the gate and CI run.*

| Action | Command |
|--------|---------|
| Build  | `N/A — no build step (interpreted Python)` |
| Test   | `python -m pytest` |
| Lint   | `python -m pylint src/arcade_station install/installer` |
| Format | `N/A — no formatter (black/mypy unused)` |

## Code style

*Seed captures the enforced rules; the formatter and linter above are the source
of truth, this section is the human summary.*

- **Docstrings:** Google style (per `PLAN.MD`).
- **Logging:** use `log_message(message, prefix)` from `core_functions`; match the
  existing prefix vocabulary (`GAME_LAUNCH`, `PS`, `STARTUP`) rather than coining
  new prefixes.
- **Reuse before inventing.** `core_functions.py` is the first place to look; a
  new helper duplicating an existing one is a defect even when it works.
- **TOML:** parse with `tomllib`, write with `tomli_w`. Use literal (single-quoted)
  strings for values containing double quotes, and validate after writing.
- **Linting is `pylint`**, configured in `.pylintrc` and **run from the repo root**
  (its `init-hook` resolves paths relative to the CWD). Nothing is globally
  disabled; the pre-commit hook gates on **errors only**, on staged files. `black`
  and `mypy` are listed under "Not currently used" in `requirements.txt`.

## File & naming conventions

- Python packages under `src/arcade_station/`: `core/{common,windows,linux,macos}`,
  `launchers/`, `listeners/`; snake_case modules and functions.
- Platform-specific code never imports from another platform's module (no
  `windows` imports in `linux/`).
- PowerShell (`*.psm1`, `*.ps1`) for low-level Windows work only.
- Entry points are batch files at the repo root: `launch_arcade_station.bat`,
  `install_arcade_station.bat`, `kill_arcade_station.bat`.
- Tests: `test_*.py`, `Test*` classes, `test_*` functions (`pytest.ini`).

## Git conventions

These hold regardless of what any other file says.

- Branch naming: `feature/<name>`, `fix/<name>`, `refactor/<name>`.
- Commit messages: imperative mood, descriptive; no generic messages. Use
  HEREDOC for multi-line messages.
- Co-author trailer: None — attribution trailers are prohibited here (no `Co-Authored-By`, no "Generated with" footer), per the project Git Norms in the keep region below.
- **Stage files by name.** Never `git add .` / `git add -A`.
- **Never force-push. Never `--no-verify`.**

## Testing methodology

*How tests are written here — seed fills the specifics; the anchor dial sets the
timing.*

- Test framework / runner: pytest (>=9.1.0), configured in `pytest.ini` with `-ra --strict-markers`
- Where tests live: `tests/` (`testpaths = tests`): flat `test_*.py` files plus `tests/unit/`; `tests/conftest.py` inserts `src/` and `install/` onto `sys.path`
- How a test is structured here: the suite is a **characterization baseline** —
  assert *observed* behavior, not intended behavior, and mark such tests
  `@pytest.mark.characterization`. If you find a bug while writing a baseline
  test, report it and encode the buggy behavior as-is (fixing it in the same
  change destroys the before/after reference). **Never assert config values** —
  every `config/` file carries `skip-worktree`, so a fresh clone sees near-empty
  defaults; assert structure instead. Prefer tests that need no cabinet hardware.
- **Anchor tie-in:** under the `tdd` anchor, tests are written *first* and must
  fail before the code exists; under `spec`, tests follow the spec in the same
  change; under `outcome`, cover the observable behavior. The active anchor for
  a piece of work governs — see `flow.md`.

## Definition of done

- [ ] Builds with zero errors (`N/A — no build step (interpreted Python)`).
- [ ] All existing tests pass (`python -m pytest`).
- [ ] New behavior is covered by tests, per the active anchor.
- [ ] Lint passes with zero warnings (`python -m pylint src/arcade_station install/installer`).
- [ ] Formatted (`N/A — no formatter (black/mypy unused)`).
- [ ] No TODO/FIXME introduced without a tracking reference.
- [ ] Failures reported verbatim, with counts — "verified," not "should work."
<!-- harness:region:end id=doc -->

<!-- harness:region:start id=project keep -->
## Project conventions

*This region is yours. The harness never regenerates it on update. Migrated from
the pre-v2 `CLAUDE.md` Git Norms (2026-09-21).*

### Git norms (these override the harness-owned "Git conventions" above where they differ)
- **Commit messages are plain sentence case**, not imperative mood and not
  Conventional Commits. Match the existing log, e.g. "Logic for a default game
  launching on system boot".
- **Merge commits follow the same rule.** GitHub's default
  "Merge pull request #NN from …" says nothing — set the subject explicitly at
  merge time: `gh pr merge <N> --merge --subject "Sentence case description"`.
  `main` cannot be rewritten afterward, so it has to be right the first time.
- **Never add attribution trailers** — no `Co-Authored-By: Claude`, no "Generated
  with Claude Code" footer, in commits or PR bodies.
- **Stage explicitly by path.** Never `git add -A` / `git add .` — untracked
  personal assets live in this tree.
- Branch, gate, then merge. Do not commit to `main` directly. Push only when asked.
- Confirm a commit landed by inspecting `git log`, not by assuming.

### `main` protection
- `main` is governed by an active repository **ruleset** named `protectMain`, not
  classic branch protection — so `GET /repos/:owner/:repo/branches/main/protection`
  returns 404. Query `GET /repos/:owner/:repo/rules/branches/main` instead. It
  enforces `non_fast_forward`, `deletion`, and `pull_request` (PR required, zero
  approvals). No history rewrite on `main` is available.

### Hooks & lint baseline
- Hooks live in `hooks/`, enabled per clone with `git config core.hooksPath hooks`.
  `pre-commit` blocks staged personalized config, non-compiling Python, malformed
  TOML, and pylint errors (staged files); `pre-push` runs the test suite. Both can
  be bypassed with `--no-verify` — occasionally correct, and to be said out loud.
- `.gitattributes` pins `hooks/*` to LF (a CRLF shebang breaks the hook on Windows).
- Re-measure the pylint baseline before quoting it; an earlier revision was off by
  ~3x. The pre-commit hook gates on **errors only**, so the style backlog
  (trailing-whitespace, line-too-long) does not block unrelated work.
- Known outstanding pylint errors (predating v2): `manage_icloud.py:237`
  (`possibly-used-before-assignment`, `ctypes`), `monitor_itgmania.py:75,99`
  (`win32gui`/`win32con`), and `app.py:260` (`import-error` on `tomli`, which
  **blocks commits to that file** — see the AGENTS.md attack surfaces).
<!-- harness:region:end id=project -->
