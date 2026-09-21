<!-- harness:region:start id=doc -->
# Architecture

*Schema template, seeded 2026-09-21. `/seed` fills the placeholder tokens by
scanning the codebase; every `## ` heading is fixed — a section may read
"N/A — none" but is never renamed or reordered. The `keep` region at the bottom
is yours and survives every harness update.*

What kind of system this is and how it's shaped. Referenced from `AGENTS.md` for
"what kind of system this is and how it's shaped." Read it before touching a part
you don't own end-to-end.

## System purpose

*What this system is for, in one or two sentences — the problem it exists to
solve, not how.*

A Python front-end for launching rhythm games and arcade software (ITGMania,
DDR, MAME) on a dedicated cabinet or a regular PC. It wraps the Pegasus
frontend, launches games from TOML configuration, drives a secondary marquee
display, and handles kiosk-mode concerns — the cabinet turns on and works with
no desktop, taskbar, or manual step.

## Shape / topology

*The overall form: monolith, service set, CLI, library, batch job — and how the
pieces are deployed and talk to each other.*

A local desktop application (monolith), not a networked service — no network
APIs. Pegasus Frontend (`src/pegasus-fe`, QML) is the display layer; Python
(`src/arcade_station`) orchestrates launching, process management, input
listening, image display, and peripheral control. `start_frontend_apps.py` is
the main entry point; the root batch files (`launch_/install_/kill_arcade_station.bat`)
are the operator-facing entry points. A separate Tkinter installer
(`install/`) configures the system on first run. Integration is via process
management (`subprocess`/`psutil`), file-based TOML config, keyboard event hooks,
and image display (PyQt5).

## Key components

*The parts that carry real responsibility, each with a one-line charter.*

- **Pegasus Frontend** (`src/pegasus-fe`) — the user-facing display; arcade_station
  launches it and manages its lifecycle.
- **Core common** (`src/arcade_station/core/common`) — cross-platform utilities
  (process management, display, launch, screenshots) consumed everywhere;
  `core_functions.py` is the canonical home to reuse before inventing.
- **Platform cores** (`core/windows`, `core/linux`, `core/macos`) — OS-specific
  implementations; Windows is the working target.
- **Launchers** (`launchers/`) — game-specific launch logic on top of core.
- **Listeners** (`listeners/`) — background keyboard/event listeners that trigger
  actions (screenshots, launches, kills).
- **Installer** (`install/`) — Tkinter UI + `installer/config/installation.py`,
  which owns and regenerates the TOML config schema on every run.

## Data & state

*What data the system owns, where state lives, and what is authoritative vs.
derived.*

All runtime behavior is driven by TOML config under `config/` (parsed with
`tomllib`, written with `tomli_w`): `installed_games.toml` (game names, paths,
launch parameters), `key_listener.toml` (key→action bindings), display/marquee
config, and others. Config is authoritative; process state is runtime-only via
`psutil` (nothing persisted to disk). **The installer owns the config schema** —
a setting it does not know about is silently dropped on reconfigure — and every
tracked `config/*.toml` carries `skip-worktree` so personal values are never
committed (a fresh clone sees near-empty defaults).

## External dependencies & boundaries

*Systems, services, and APIs this depends on, and the line where this system's
responsibility ends and theirs begins.*

No network services or remote APIs. External surfaces are the OS process table
(launching/killing executables the user installed — ITGMania, MAME, etc.), the
filesystem (TOML config, screenshots, assets), keyboard input (via the
`keyboard` library), and the display (PyQt5). Third-party runtime deps:
PyQt5, keyboard, psutil, tomli_w, Pillow (see `requirements.txt`). The launched
games themselves are outside this system's responsibility — arcade_station owns
starting, monitoring, and killing them, not their internals.

## Invariants

*Things that must always hold — the properties a change is never allowed to
break. Violating one is a correctness bug, not a preference.*

*Inherited from the pre-v2 reliability notes and not each individually
re-verified against the code — treat as intent to uphold.*
- TOML config files in `config/` must always be valid TOML — never write partial
  or corrupted config. A malformed `installed_games.toml` takes down *every*
  game, not one.
- Platform-specific code never imports from another platform's module (no
  `windows` imports in `linux/`).
- `kill_all` must terminate every process it manages — a partial kill leaves the
  system broken.
- Key listeners must not block the main thread — they run in background threads.
- `core_functions.open_header` must set the global environment before any script
  runs.
- The installer must never overwrite existing user configuration without explicit
  confirmation.
<!-- harness:region:end id=doc -->

<!-- harness:region:start id=project keep -->
## Architectural decisions

*This region is yours. The harness never regenerates it on update. Migrated from
the pre-v2 docs and `CLAUDE.md` (2026-09-21).*

- **No `pyproject.toml`** — a deliberate non-choice (`PLAN.MD`). Dependencies are
  `venv` + `requirements.txt` (+ `requirements-dev.txt`); pytest is configured in
  `pytest.ini` and pylint in `.pylintrc` because there is no `pyproject.toml`.
- **The installer owns the config schema.** `install/installer/config/installation.py`
  regenerates configuration on every run, so a new config key must be added there
  too or it is silently dropped on the next reconfigure.
- **Personalized files carry `skip-worktree`** (12 files: `config/*.toml` and three
  Pegasus files). To change what a *fresh clone* receives, change the installer,
  not the file. An empty `git diff` does not prove the working tree is restored.
- **Windows-first.** Linux and macOS support is Phase 2 intent (`PLAN.MD`); the
  platform-core split (`core/{windows,linux,macos}`) exists for it but only
  Windows is exercised.
- **There is no CI.** Nothing runs the checks except a developer and the git hooks
  (`pre-commit`, `pre-push`), enabled per clone with
  `git config core.hooksPath hooks`.
<!-- harness:region:end id=project -->
