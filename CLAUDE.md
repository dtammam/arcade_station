# CLAUDE.md

This file is the Claude Code entry point for this repo.

## What YOU (the main session) do

You are NOT any of the agents listed below. You are the user's interface.
Your only job is to:

1. Receive the user's request
2. Invoke the engineering-manager agent via the Agent tool
3. Relay the engineering-manager's output — including its routing instructions — verbatim to the user

Do NOT roleplay as the engineering-manager. Do NOT directly invoke
product-manager, principal-engineer, software-developer, or any other
agent. Always go through engineering-manager.

If you catch yourself coordinating the pipeline, reading state files,
or delegating to specialist agents directly — STOP. Invoke the EM instead.

## Agent architecture

The engineering-manager is an **advisor and state manager**, not a delegator.
It writes the specialist prompt to `.state/inbox/<agent-name>.md` and tells the
user which VS Code task to run. The user launches each specialist via
**Terminal → Run Task…** in VS Code, which spawns a fresh Claude Code session
that reads the inbox file automatically. This keeps every agent's output directly
visible to the user — no intermediary summaries, no copy-paste.

### Agents (`.claude/agents/`)

| Agent | What it does | How to run it |
|-------|-------------|---------------|
| `engineering-manager` | Tracks feature state, routes work to specialists, manages stage transitions | Invoked automatically by `/commands` |
| `product-manager` | Gathers requirements + acceptance criteria (Discovery), validates delivered work (Acceptance) | VS Code task **"Run Product Manager"** |
| `principal-engineer` | Reads requirements and codebase, produces technical design with approach, risks, alternatives | VS Code task **"Run Principal Engineer"** |
| `software-developer` | Implements ONE task at a time — writes code, tests, runs quality checks | VS Code task **"Run Software Developer"** |
| `build-specialist` | Runs build + test + lint + format checks, reports pass/fail (never fixes code) | VS Code task **"Run Build Specialist"** |
| `quality-assurance` | Reviews code for correctness, security, performance, standards compliance (never fixes code) | VS Code task **"Run Quality Assurance"** |

### Commands (`.claude/commands/`)

Each command moves the feature one stage forward. Run them in order.

| Command | What it does | Then you do |
|---------|-------------|-------------|
| **`/kickoff`** | Initializes state, reads project context, summarizes starting point | Review summary → **`/discover`** |
| **`/discover`** | Routes to PM to gather requirements and write exec plan | Run task **"Run Product Manager"** → **`/design`** |
| **`/design`** | Routes to PE to produce technical design in exec plan | Run task **"Run Principal Engineer"** → **`/tasks`** |
| **`/tasks`** | EM breaks design into small, testable tasks with definitions of done | Review tasks → **`/implement`** |
| **`/implement`** | Routes ONE task to SDE for implementation | Run task **"Run Software Developer"** → repeat or **`/verify`** |
| **`/verify`** | Routes to build specialist to run all quality gates | Run task **"Run Build Specialist"** → **`/accept`** |
| **`/review`** | Routes to QA for code review (optional, recommended for non-trivial changes) | Run task **"Run Quality Assurance"** → fix or proceed |
| **`/accept`** | Routes to PM to validate every acceptance criterion | Run task **"Run Product Manager"** → **`/done`** |
| **`/done`** | Archives plan, commits, pushes, creates PR, offers release tagging | Merge PR → **`/kickoff`** for next feature |
| **`/commit-only`** | Stages and commits (no push) | — |
| **`/commit-and-push`** | Stages, commits, pushes | — |

### VS Code tasks (`.vscode/tasks.json`)

Each specialist agent has a corresponding VS Code task that spawns a fresh
Claude Code session reading from `.state/inbox/<agent-name>.md`. Run via
**Terminal → Run Task…** in VS Code.

### Shared state

`.state/feature-state.json` tracks the current feature lifecycle. The
engineering-manager reads and updates it at every stage transition.

`.state/inbox/` holds ephemeral prompt files written by the EM for specialist
agents. These are `.gitignore`d — only `.gitkeep` is tracked.

### Workflow

```text
/kickoff → /discover → /design → /tasks → /implement → /verify → /accept → /done
                                              ↑            |
                                              └── (next) ──┘

Optional at any point: /review (code review)
```

Every stage transition requires explicit user approval. No auto-progression.
The user runs each command manually. The engineering-manager runs ONE stage
per invocation and stops.

## Reference docs

Read these before touching any code:

1. `docs/index.md` — knowledge map
2. `docs/ARCHITECTURE.md` — system design, repo layout
3. `docs/RELIABILITY.md` — performance budgets (non-negotiable)
4. `docs/CONTRIBUTING.md` — design principles and coding standards

For active work: `docs/exec-plans/active/`
For tech debt: `docs/exec-plans/tech-debt-tracker.md`

## Non-negotiables

- Performance budgets in `docs/RELIABILITY.md` — flag regressions before proceeding
- Python 3.12.9 required; no other Python version supported
- Runtime dependencies limited to: PyQt5, keyboard, psutil, tomli_w, Pillow
- No hardcoded paths or credentials — all paths come from TOML config files in `config/`
- Platform-specific code must live in `src/arcade_station/core/{windows,linux,macos}/`

## Coding standards

See `docs/CONTRIBUTING.md` for design principles, coding standards, and the three-pillar code quality framework.

## Quality gates

- `pre-commit`: `black --check src/ install/` && `flake8 src/ install/` && `npx markdownlint-cli2 '**/*.md'`
- `pre-push`: `python -m pytest`
- Never use `--no-verify`. Fix the root cause.

## Commands

```text
black --check src/ install/
flake8 src/ install/
mypy src/ install/
python -m pytest
npx markdownlint-cli2 '**/*.md'
```

## Active work

Active exec plans: (none)
Completed plans: (none yet)
