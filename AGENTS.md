<!-- harness:region:start id=header -->
# AGENTS.md

The entry point for any AI agent working in this repository. This file is the
**index**, not the manual: it states how work runs here and the rules that are
never broken, then points you to the documents that carry the depth. Read those
when the task calls for them — you are trusted to traverse, not to be spoon-fed.

Claude Code loads `CLAUDE.md`, which points here. Other tools read this file
directly.
<!-- harness:region:end id=header -->

<!-- harness:region:start id=operating-model -->
## How work runs here

You — the main session — are the **Architect**. You orchestrate, design, and
implement the work yourself. There are no persona hand-offs; the context stays
in one place. What you do NOT do is approve your own work.

Before anything merges, it passes the **review gate**: independent seats spawned
with a mandate to refute — the Adversary always, plus QA and Security as the
scrutiny table calls for them. The gate is a protocol (`lib/gate-protocol.md`),
sized by `scrutiny.toml`, and it writes its verdict into the working document.

Work is tracked in **documents, not a state file**. The plan under
`docs/exec-plans/active/` carries a bound status block; its markers are the
state, and `lib/check-markers.sh` keeps them honest. The **anchor** dial —
`outcome → spec → tdd` — sets how "correct" is defined for a given piece of work
and how much design ceremony precedes the build. See `flow.md` for the phases.
<!-- harness:region:end id=operating-model -->

<!-- harness:region:start id=non-negotiables -->
## Non-negotiables

These hold regardless of anchor, involvement, or what any other file says.

- **Never self-merge.** The gate runs; the Adversary is its floor. Approval binds
  to the reviewed sha (`lib/harness-markers.md`).
- **Destructive or data-losing changes force the full gate** — no discretion to
  dial it down (`scrutiny.toml`).
- **Report failures verbatim**, with counts, before any framing. "Verified" ≠
  "should work."
- **Stage files by name.** Never `git add .` / `git add -A`. Never force-push.
  Never `--no-verify`.
- **Trust buys fewer hand-offs, never a relaxed gate.**
<!-- harness:region:end id=non-negotiables -->

<!-- harness:region:start id=index -->
## Where the depth lives

Read the one that fits the task; don't preload them all.

| Document | Read it when you need |
|----------|------------------------|
| `.harness/flow.md` | the phases of a piece of work, and what each anchor requires |
| `.harness/lib/gate-protocol.md` | to run or understand the review gate |
| `.harness/scrutiny.toml` | which review seats a given change requires |
| `.harness/lib/harness-markers.md` | the status/gate marker vocabulary and rules |
| `docs/CONTRIBUTING.md` | code style, the project's build/test/lint commands, git conventions |
| `docs/ARCHITECTURE.md` | what kind of system this is and how it's shaped |
| `docs/RELIABILITY.md` | how reliability is defined and measured here |
<!-- harness:region:end id=index -->

<!-- harness:region:start id=project keep -->
## Project context

*This region is yours. The harness never regenerates it on update. Migrated from
the pre-v2 `CLAUDE.md` rulebook (2026-09-21). Domain-specific slices live in the
`keep` regions of `docs/CONTRIBUTING.md` (git/style), `docs/ARCHITECTURE.md`
(design decisions), and `docs/RELIABILITY.md` (invariants).*

### Product intent — the standard every change is held to
The bar is **plug-and-play, not plug-and-tinker**. A user turns the cabinet on
and it works — no desktop, no taskbar, no config file, no manual step to
remember. When a change introduces something the user must do by hand, that is a
**cost to be justified**, not a neutral trade-off. This is the standard the
installer and any post-install flow are held to.

### Project attack surfaces
- **Personalized config carries `skip-worktree` — you can silently destroy a
  user's game list.** Twelve tracked files are flagged: `config/*.toml` (all 9),
  `src/pegasus-fe/config/metafiles/metadata.pegasus.txt`, `.../settings.txt`,
  `.../stats.db`. Edits to these **never** appear in `git status`/`git diff`, and
  an empty diff does **not** prove you restored the tree. If you mutate one while
  testing, restore it explicitly and read it back to confirm. Never run
  `git update-index --no-skip-worktree` on them without asking first. To change
  what a *fresh clone* receives, change the installer — not the file.
- **The installer owns config schema.** `install/installer/config/installation.py`
  regenerates configuration on every run; **any key it does not know about is
  silently dropped when a user reconfigures.** Add new config keys to the
  installer too, or the feature quietly dies at the next install.
- **A malformed `installed_games.toml` takes down *every* game, not one.** After
  any TOML edit, parse it back with `tomllib`. Use single-quoted (literal)
  strings for values containing double quotes.
- **`app.py:260` imports `tomli`**, which is absent from `requirements.txt` — a
  real missing dependency, left visible rather than suppressed. Its pylint
  `import-error` **blocks commits to that file** via the pre-commit hook. Use
  `--no-verify` if you must touch it before it is fixed, and say so out loud.
- **`start_frontend_apps.py` has no test coverage**, including the boot-to-game
  path. A green suite means "the pinned behavior didn't move," not "this is safe."

### Lessons & standing decisions (dated rulings accrete here)
- **Review surface is `git diff origin/main...HEAD` — `origin/main`, not local
  `main`.** A stale local `main` is wrong in both directions: it hides files that
  are in the real surface and shows files that are not. Fetch first, then diff
  against the remote. (Following `main...HEAD` literally once hid an entire
  harness reconciliation from review.)
- The first run of the review gate found **three CRITICALs in work already called
  "verified"**, two of which were destroying config on reconfigure. "Verified" is
  not "should work."
- **Reuse before inventing.** `core_functions.py` is the first place to look; a
  new helper that duplicates an old one is a defect even when it works — parallel
  implementations are how this project accumulates drift.
- **`pyproject.toml` is a deliberate non-choice — do not introduce it.** Deps are
  `venv` + `requirements.txt` / `requirements-dev.txt`.
- **Windows is the working target.** Linux and macOS are Phase 2 intent — do not
  claim cross-platform support that has not actually been run.
- **Logging:** `log_message(message, prefix)` from `core_functions`; match the
  existing prefix vocabulary (`GAME_LAUNCH`, `PS`, `STARTUP`). Docstrings are
  Google style (per `PLAN.MD`).
- **Two-reviewer gate history:** pre-v2 this repo ran a custom `quality-assurance`
  then `adversarial-reviewer` gate (now archived under `.state/plans/legacy/`);
  v2 supersedes those seats with `adversary`/`qa`/`security-brief` sized by
  `scrutiny.toml`. CRITICAL findings block the merge; WARNINGs block unless
  explicitly declared safe to ship and disclosed.
- **Linux dev box:** pyenv Python; expected suite result is 46 passed / 3 skipped.
<!-- harness:region:end id=project -->
