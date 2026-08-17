# Architecture

How the repository is laid out and how its pieces fit together. Maintained by
hand - when the layout moves, move this with it.

## High-level design

arcade_station is a Python-based frontend interface for managing and playing arcade and rhythm games (ITGMania, DDR, MAME) on dedicated arcade cabinets. It uses Pegasus Frontend as its display layer, with Python orchestrating game launching, process management, input listening, image display, and peripheral control (litboard lights, streaming, screenshots).

The system is designed for kiosk-mode operation — it starts automatically, manages the full lifecycle of game sessions, and recovers gracefully from crashes.

## Repo layout

```text
arcade_station/
├── src/arcade_station/
│   ├── core/
│   │   ├── common/           # Cross-platform utilities (process mgmt, display, launch, screenshots)
│   │   ├── windows/          # Windows-specific implementations
│   │   ├── linux/            # Linux-specific implementations
│   │   └── macos/            # macOS-specific implementations
│   ├── launchers/            # Game-specific launch logic
│   ├── listeners/            # Keyboard/event listeners
│   ├── start_frontend_apps.py  # Main entry point
│   └── debug_pegasus_launch.py
├── install/
│   ├── main.py               # Installer entry point
│   ├── installer/
│   │   ├── config/           # Installation configuration
│   │   ├── ui/               # Tkinter installer pages
│   │   └── resources/        # Installation assets
│   └── logs/
├── bin/
│   ├── windows/              # Windows batch/PowerShell scripts
│   └── unix/                 # Unix shell scripts
├── config/                   # TOML configuration files
│   ├── default_config.toml
│   ├── installed_games.toml
│   ├── key_listener.toml
│   ├── mame_config.toml
│   └── ...
├── assets/                   # Game icons, logos, images
├── examples/                 # Setup walkthroughs (DDR, laptop)
├── tests/                    # pytest characterization baseline
├── docs/                     # Architecture and reliability notes
├── .claude/agents/           # The two reviewer seats (QA, adversarial)
└── hooks/                    # Git hooks (pre-commit, pre-push)
```

## Component relationships

- **Pegasus Frontend** is the user-facing display — arcade_station launches it and manages its lifecycle
- **Core common** provides shared utilities consumed by launchers, listeners, and the installer
- **Launchers** use core functions to start specific games (ITGMania, MAME, etc.) and manage their processes
- **Listeners** monitor keyboard events (via `keyboard` library) and trigger actions (screenshots, game launches, kills)
- **Config** (TOML files) drives all runtime behavior — paths, key bindings, game lists, display settings
- **Installer** (Tkinter UI) configures the system for first-time setup, writing TOML config files

## Data model

- **Configuration**: TOML files parsed via `tomllib` (Python 3.11+ built-in), written via `tomli_w`
- **Game metadata**: Defined in `installed_games.toml` — game names, paths, launch parameters
- **Key bindings**: Defined in `key_listener.toml` — maps physical keys to actions
- **Display config**: Controls image viewer behavior (marquees, screenshots) via `display_config.toml`
- **Process state**: Managed at runtime via `psutil` — no persistent process state on disk

## CI/CD

**There is no CI.** Nothing runs these checks except a developer and the git
hooks, which are enabled per clone with `git config core.hooksPath hooks`:

- `pre-commit`: blocks staged personalized config, Python that will not
  compile, malformed TOML, and pylint errors on staged files
- `pre-push`: runs the pytest suite

Linting is `pylint`, configured in `.pylintrc`. `black` and `mypy` are not used
here - `requirements.txt` lists both under a "Not currently used" block.
`flake8` is neither a dependency nor run anywhere.

## Key protocols / APIs

None. This is a local application with no network APIs. All integration is via:

- Process management (launching/killing executables via `subprocess` and `psutil`)
- File-based configuration (TOML)
- Keyboard event hooks (via `keyboard` library)
- Image display (via `PyQt5`)
