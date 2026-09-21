<!-- harness:region:start id=doc -->
# Reliability

*Schema template, seeded 2026-09-21. `/seed` fills the placeholder tokens from
the detected project; every `## ` heading is fixed — a section may read
"N/A — none" but is never renamed or reordered. The `keep` region at the bottom
is yours and survives every harness update.*

How reliability is defined and measured here — so a change can be judged against
it, not against a vibe. Referenced from `AGENTS.md` for "how reliability is
defined and measured here."

## What "reliable" means here

*The concrete definition for this system: the behavior it must uphold, and the
bar it is held to. Not a platitude — something a change can be checked against.*

Plug-and-play, not plug-and-tinker: the cabinet boots straight to a working
frontend and games launch with no manual step. Concretely, a change must not (a)
corrupt config or write partial/invalid TOML, (b) drop or destroy a user's game
list or settings on reconfigure, or (c) leave processes running after a kill.
These are checkable against a change; "should work" is not enough.

## How it's measured

*The signals and thresholds that say whether the bar is being met — tests,
metrics, SLOs, error budgets, or the manual checks that stand in for them.*

There is **no CI**, no metrics/SLOs, and **no measured performance budgets** —
nothing here has been timed on a cabinet, so no budget is asserted. The only
automated signal is the pytest **characterization baseline** (`python -m pytest`,
also run by the pre-push hook): five files covering config loading, the
installer's TOML writer, what a reconfigure preserves vs. discards, the
install-location page's cleanup path, and the launch-argument contract. The
documented dev-box baseline is **46 passed / 3 skipped**. A green run means the
pinned behavior did not move — not that the change is safe; large areas
(notably `start_frontend_apps.py` and the boot-to-game path) have no coverage.

## Failure modes & blast radius

*The ways this system fails, and how far each failure spreads — what breaks,
who's affected, and what stays contained.*

- **Malformed `installed_games.toml`** → *every* game fails to launch, not one.
  Blast radius: whole cabinet.
- **Reconfigure drops an unknown config key** → the feature silently dies at the
  next install (the installer owns the schema).
- **Partial kill** (`kill_all` misses a process) → the system is left in a broken
  state between sessions.
- **A `skip-worktree` config file is mutated or accidentally committed** → a
  user's personal game list/settings are silently destroyed; the damage does not
  show in `git status`/`git diff`.

## Startup / smoke checks

*The fast checks that confirm the system is up and sane after a start or deploy —
what to run, and what a healthy result looks like.*

There is no cabinet-independent smoke harness. The practical checks:
- `python -m pytest` — healthy result is the documented baseline (46 passed / 3
  skipped on the Linux dev box).
- `python -m py_compile <file>` on changed Python (the pre-commit hook does this
  for staged files).
- After any TOML edit, parse it back with `tomllib`.
- For launch-path changes, a dry run that echoes rather than launches, to prove
  argument and quoting behavior when a real launch is not possible.
- Cabinet behavior is only claimable if actually run — otherwise say it was not.

## Degradation & recovery

*How the system degrades under stress rather than falling over, and the steps to
bring it back — retries, fallbacks, rollback, and the recovery runbook pointer.*

Kiosk mode is designed to recover gracefully from game crashes — arcade_station
owns the start/monitor/kill lifecycle and returns to the frontend rather than
falling over. There is no automated rollback. Config recovery: the installer
regenerates config on every run, and non-`skip-worktree` files can be restored
from git; a `skip-worktree` config file mutated during testing must be restored
explicitly and read back to confirm (an empty `git diff` does not prove it).
<!-- harness:region:end id=doc -->

<!-- harness:region:start id=project keep -->
## Reliability notes

*This region is yours. The harness never regenerates it on update. Record here
the hard-won operational lessons: incidents and their rulings, known-fragile
areas, environment quirks, and the checks that exist because something once
broke.*

- If a build breaks on the main line, fix it before any new feature work.
- **2026 — first review-gate run** found three CRITICALs in work already described
  as "verified," two of which were destroying config on reconfigure. Ruthless
  honesty and the review gate exist because of this.
- **No performance budgets.** An earlier revision of this file listed six, none
  measured; they were removed rather than be mistaken for observations. If you
  need a budget, measure first and record the measurement alongside it.
- **Linux dev box:** pyenv Python; a tk runtime fix is required for the installer
  tests; expected suite result is 46 passed / 3 skipped.
- When an invariant (see `ARCHITECTURE.md`) is at risk, flag it before proceeding
  and let the review gate weigh it — never silently ship a regression against one.
<!-- harness:region:end id=project -->
