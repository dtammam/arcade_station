# CLAUDE.md - Arcade Station

Arcade Station is a front-end for launching rhythm games and arcade software on a dedicated cabinet or a regular PC. It wraps the Pegasus frontend, launches games from TOML configuration, drives a secondary marquee display, and handles kiosk-mode concerns. Python 3.12, with PowerShell reserved for low-level Windows work.

`PLAN.MD` holds project direction and phasing. This file holds how the work gets done.

## Product Intent

The bar is **plug-and-play, not plug-and-tinker**. A user turns the cabinet on and it works - no desktop, no taskbar, no config file, no manual step they have to remember. When a change introduces something the user must do by hand, that is a cost to be justified rather than a neutral trade-off.

This is the standard the installer and any post-install configuration flow are held to.

## Core Working Principles

Lean mode: a single agent owns the whole lifecycle, with no role hand-offs. Two pillars are non-negotiable.

1. **The two-reviewer gate.** Non-trivial work does not merge without passing both codified reviewers in `.claude/agents/` - the QA seat, then the adversarial seat. Both must return APPROVE.
2. **Ruthless honesty.** Report failures verbatim, including the actual error text. Never downplay a regression. State plainly what was verified and what was not - "not launch-tested on the cabinet" is a complete and acceptable sentence.

## Reviewer Structure

| Seat | Agent | Focus |
|------|-------|-------|
| QA | `quality-assurance` | Correctness, regressions, security, standards, comment accuracy |
| Adversarial | `adversarial-reviewer` | Assumes the implementer *and* QA both missed something; breaks claims by measurement |

CRITICAL findings block the merge. WARNINGs block unless explicitly declared safe to ship and disclosed in the summary. Trivial changes - typo fixes, documentation wording - may skip the gate, but say so when you skip it rather than letting it pass silently.

## Testing and Verification

**There is no test suite and no CI in this repository today.** The pytest and GitHub Actions plan in `PLAN.MD` is aspirational and not yet built. Do not claim a test run. Do not write "tests pass."

Building a **characterization baseline** is the current priority: tests that capture what the code actually does today, so that later changes can be made with confidence. When writing them:

- Assert observed behavior, not intended behavior. The point is to pin down the current contract before it moves.
- If you discover a bug while writing a baseline test, **report it and encode the buggy behavior as-is**. Fixing it in the same change destroys the baseline's value as a before/after reference.
- Prefer tests that need no cabinet hardware. Config parsing, path resolution, argument construction, and TOML round-tripping are all testable in isolation.

Until that baseline exists, verification means:

- **Python changes:** `python -m py_compile <file>` at minimum.
- **Any TOML edit:** parse it back with `tomllib` before declaring done. A malformed `installed_games.toml` takes down *every* game, not one.
- **Launch-path changes:** prove argument and quoting behavior with a dry run that echoes rather than launches, when a real launch is not possible.
- **Cabinet behavior:** only claimable if actually run. Otherwise say it was not.

Update this section when the baseline lands.

## Repository Constraints

These are non-obvious and have caused real problems. Read before touching configuration.

### Personalized files carry skip-worktree

Twelve tracked files are flagged `skip-worktree` so that personal values are never committed:

```
config/*.toml                                    (all 9)
src/pegasus-fe/config/metafiles/metadata.pegasus.txt
src/pegasus-fe/config/settings.txt
src/pegasus-fe/config/stats.db
```

Consequences that matter:

- **Edits to these files never appear in `git status` or `git diff`.** That is intended. Do not try to "fix" it.
- **An empty `git diff` does not prove you restored the tree.** If you mutate a config file while testing, restore it explicitly and verify by reading the file back. This is the single easiest way to silently destroy someone's game list.
- To change what a *fresh clone* receives, change the installer, not the file. See below.
- Never run `git update-index --no-skip-worktree` on these without asking first.

### The installer owns config schema

`install/installer/config/installation.py` regenerates configuration on every run. **Any setting it does not know about is silently dropped when a user reconfigures.** When adding a config key, add it to the installer too, or the feature quietly dies at the next install.

### Config format

TOML, parsed with `tomllib`. Use literal strings - single quotes - for values that contain double quotes. Validate after writing.

## Project Specifics

- **Language:** Python 3.12.9. PowerShell only for low-level Windows work (`core_functions.psm1`, `*.ps1`).
- **Dependencies:** `venv` plus `requirements.txt`. `pyproject.toml` is a deliberate non-choice - do not introduce it.
- **Frontend:** Pegasus (`src/pegasus-fe`), Micro theme written in QML.
- **Entry points:** `launch_arcade_station.bat`, `install_arcade_station.bat`, `kill_arcade_station.bat`.
- **Logging:** `log_message(message, prefix)` from `core_functions`. Match the existing prefix vocabulary - `GAME_LAUNCH`, `PS`, `STARTUP`.
- **Docstrings:** Google style, per `PLAN.MD`.
- **Platforms:** Windows is the working target. Linux and macOS are Phase 2 intent - do not claim cross-platform support that has not been run.
- **Reuse before inventing.** When you hit a problem this codebase already solves, use the existing solution rather than writing a second one alongside it. `core_functions.py` is the first place to look. Parallel implementations of the same idea are how this project accumulates drift, and a new helper that duplicates an old one is a defect even when it works.

## Git Norms

- Branch, gate, then merge. Do not commit to `main` directly.
- **Commit messages are plain sentence case**, not Conventional Commits. Match the existing log: "Logic for a default game launching on system boot".
- Stage explicitly by path. Never `git add -A` or `git add .` - untracked personal assets live in this tree.
- Confirm a commit landed by inspecting `git log`, not by assuming.
- Push only when asked.
