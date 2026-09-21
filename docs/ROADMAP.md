# Roadmap

The forward-looking vision for arcade_station. This is an **umbrella doc**: it
holds *pointers* — intent and links to the per-piece plans under
`docs/exec-plans/` — and carries **no bound `Gate:`/`Approved` markers of its
own** (per `.harness/lib/harness-markers.md`). Each item ships as its own
spec-driven piece with its own plan doc; the status here is a signpost, not the
source of truth.

`PLAN.MD` is the *historical* origin plan (the PowerShell→Python migration). This
file is where the project is going next.

---

## Guiding principles

These constrain every item below.

- **Plug-and-play, not plug-and-tinker.** Turn the cabinet on and it works — no
  desktop, no taskbar, no config file, no manual step. Anything a user must do by
  hand is a cost to justify, not a neutral trade-off. (From `AGENTS.md`.)
- **Fewer dependencies.** Every external dependency is a liability to own or
  remove. The long arc is toward controllable, first-party binaries.
- **No `pyproject.toml`.** Deps stay `venv` + `requirements.txt` /
  `requirements-dev.txt` — a deliberate non-choice.
- **Windows is the working target.** Linux/macOS are Phase-2 intent; don't claim
  cross-platform support that hasn't actually been run.
- **The config schema has one owner.** The installer regenerates config on every
  run; any key it doesn't know is silently dropped. New config keys go into the
  installer too, or the feature quietly dies at the next install.

---

## Near-term foundation *(active focus)*

The prerequisite for everything below is a repo you can't fall through. Until
main is bound by tests, every roadmap item is built on sand.

1. **Land the v2 harness** — commit the installed harness reconciliation cleanly.
   → `docs/exec-plans/active/2026-09-21-land-harness-v2.md`
2. **Test foundation** — CI + pre-commit hooks + coverage baseline, then cover
   the highest-risk untested path (`start_frontend_apps.py`, the boot-to-game
   path, which currently has zero coverage), then iterate module by module.
   `spec`-anchored, foundation-first. → plan doc TBD (Swing B)

Every roadmap item after this is gated by the foundation being in place.

---

## The arching roadmap

Ordered roughly by dependency, not commitment. None are scoped yet; each earns a
spec-driven plan when it's picked up.

### 1. Replace the Pegasus dependency with a homegrown frontend
**Status:** Future — not started.
**Intent:** Retire the external Pegasus-FE dependency (`src/pegasus-fe`) in favor
of a first-party, fully controllable binary — Rust or Python, TBD — that does
exactly what arcade_station needs: the game picker/grid and, critically, the
**dynamic marquee** module.
**Why:** Fewer dependencies, full control over behavior and install, and the
marquee is a differentiator worth owning outright.
**Rough shape:** Start with a spike that pins the *minimal* frontend surface
arcade_station actually consumes from Pegasus today, so the replacement targets
real usage rather than reimplementing all of Pegasus. Largest item here; likely
runs long and parallel to smaller wins.

### 2. Standardized installer
**Status:** Future — not started.
**Intent:** Replace the current download-zip-then-script-copies-it-elsewhere flow
with a real, standardized installer.
**Why:** The current flow is self-contained but ad-hoc — built from not knowing
better at the time, not from a definitive direction. Held to the plug-and-play
standard.
**Rough shape:** Must remain the sole owner of the config schema and must never
disturb the `skip-worktree` personalized config files. Design language and error
handling are first-class, not afterthoughts.

### 3. Harden the settings menu
**Status:** Future — not started.
**Intent:** Make the PyInstaller-based settings UI robust and coherent — a real
design language, input validation, and no path that writes bad data back to a
config file.
**Why:** It works, but predates any design language, and has edge cases where a
user can repopulate a config with invalid data. A malformed `installed_games.toml`
takes down *every* game, not one.
**Rough shape:** Validate on the way in; round-trip every TOML write through
`tomllib` before persisting; single-quoted literals for values with quotes.

### 4. Standalone games updater
**Status:** Future — not started. First genuinely *new* user-facing feature.
**Intent:** A small standalone binary to add/update games without running the
whole installer or hand-editing a config file.
**Why:** Today updating your game list means the full installer or a manual config
edit — jank tolerated only on a dev cabinet.
**Rough shape:** Focused CRUD over `installed_games.toml` with the same validation
guarantees as the hardened settings menu; shares the config-schema-ownership
constraint with the installer.

### 5. Auto-updater
**Status:** Future — not started.
**Intent:** Let an installed cabinet update arcade_station itself.
**Why:** Ship fixes and features to cabinets in the field without a manual
reinstall.
**Rough shape:** Depends on the installer and release story being settled first;
sequence it after items 2–4.

---

## Sequencing notes

- **Foundation first, always.** Nothing above starts before the test foundation
  is landed on main.
- Items **2, 3, 4** share config-schema ownership and validation logic — worth
  designing that shared spine once rather than three times.
- Item **1 (Pegasus replacement)** is the big rock; it can progress as a spike in
  parallel while the smaller installer/settings/updater wins land.
- Item **5 (auto-updater)** is last: it rides on a settled installer + release
  story.
