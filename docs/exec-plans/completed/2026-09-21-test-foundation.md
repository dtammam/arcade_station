---
plan: test-foundation
harness: v2 · lean
branch: feature/test-foundation
anchor: spec
status: Shipped 2026-09-21
next: Shipped to main. Foundation landed (CI + coverage baseline + boot-path characterization); the coverage ratchet and module-by-module iteration are future roadmap work, gated behind this.
design: Approved 2026-09-21 @c281d44
gate: APPROVED
---

# Test foundation (Swing B)

## Context

Swing A landed the v2 harness on `main` (merge `5fa1327`) and created
`docs/ROADMAP.md`. Its near-term-foundation item 2 is this piece: stand up the
test **floor** so `main` becomes something future work can't fall through —
**CI + coverage baseline**, with the existing git hooks mirrored so they're
enforced even when a clone hasn't set `core.hooksPath` — then cover the
highest-risk untested path (`start_frontend_apps.py`, the boot-to-game flow that
`AGENTS.md` flags at zero coverage). Module-by-module iteration beyond that stays
future (roadmap, not this plan).

**Anchor: spec** (project default is `outcome`). This is foundation work whose
value is in decisions made deliberately — which OS CI runs on, how coverage is
configured under a no-`pyproject` constraint, what "baseline" means this swing —
each wanting a recorded rationale the gate can measure against. A decision
register is the right Phase-1 artifact; `outcome`'s three-bullet inference would
under-serve it.

### Blind-spot findings (Phase-1 pass over the repo)

- **Git hooks already exist.** `hooks/pre-commit` and `hooks/pre-push` (enabled
  via `git config core.hooksPath hooks`) already enforce: no committing
  `skip-worktree` config, `py_compile` on staged `.py`, `tomllib` parse on staged
  `.toml`, `pylint --errors-only` on staged `.py`, and the **full suite on push**.
  So "pre-commit hooks" is largely already in the tree — this swing does **not**
  reinvent it. Decision (confirmed with user): keep the raw hooks as-is and
  **mirror** their CI-meaningful checks in the workflow, adding no new dependency.
- **No CI exists.** `.github/workflows/` is absent. The hooks only fire on the
  machine of a clone that opted in; nothing enforces the floor on the remote.
- **No coverage tooling.** `requirements-dev.txt` has `pytest` + `pylint` only;
  no `pytest-cov`, no coverage config. Baseline is currently unknown.
- **Suite is platform-sensitive.** Green is **46 passed / 3 skipped** on this
  Linux box, but only after `tk-dev tcl-dev` are installed and the Linux argv
  guard (on `main` since Swing A) is present. CI on Ubuntu must reproduce both.
- **`pyproject.toml` is forbidden** (standing decision). Coverage config must live
  in a dedicated file, matching the existing `pytest.ini` / `.pylintrc` pattern.
- **Committed coverage artifacts are off-limits.** Prior code-hygiene branch was
  killed; coverage is written fresh, never resurrected into the tree. CI keeps it
  ephemeral (job artifact / log), nothing committed.

### Decisions taken with the user this session (constrain the register)

- CI OS target: **Ubuntu only** (fast, matches what's proven green; the Windows
  working-target gap is recorded as a known limitation + future matrix item — we
  do not claim Windows CI coverage we haven't run).
- Pre-commit: **keep raw hooks, mirror in CI** (no `pre-commit` framework, no new
  dep).
- Coverage: **measure + report baseline only** this swing — no `--cov-fail-under`
  gate yet; a ratchet comes after `start_frontend_apps.py` is covered.

## Decision register

Ordered by blast radius: the dependency/interface/CI-contract decisions first
(they shape everything downstream), then the test target. Approve the batch, or
override individual IDs.

| ID | Decision | Recommendation | Rationale |
|----|----------|----------------|-----------|
| **D1** | Coverage dependency | Add `pytest-cov` (pinned, `>=`-style to match existing `requirements-dev.txt` entries) to **`requirements-dev.txt`** only — never `requirements.txt` (end users don't get test tooling). | Minimal, matches the file's stated purpose. `pytest-cov` pulls `coverage` transitively; no separate `coverage` pin needed. **Note:** editing `requirements*.txt` trips the `network-boundary-and-deps` force rule → **full gate (adversary + qa + security-brief)**, not slim. |
| **D2** | Coverage config location | New standalone **`.coveragerc`** — `source = src/arcade_station` (+ `install/` if it holds importable code), `omit` tests, `branch = true`. Do **not** add `--cov` to `pytest.ini` `addopts`. | No-`pyproject` constraint rules out `[tool.coverage]`; `.coveragerc` mirrors `pytest.ini`/`.pylintrc`. Keeping `--cov` out of `addopts` means a bare `pytest` (someone who installed only `requirements.txt`) still runs — coverage is opt-in via the CI invocation, so the local pre-push hook stays fast and dependency-light. |
| **D3** | CI workflow | New **`.github/workflows/ci.yml`**: `ubuntu-latest`, Python **3.12.9** (matches `REQUIRED_VERSION` so the version-mismatch warning stays silent), `apt-get install -y tk-dev tcl-dev`, `pip install -r requirements.txt -r requirements-dev.txt`, run `pytest --cov`. Triggers: `push` + `pull_request` targeting `main`. | Reproduces the exact conditions the suite needs to be green (tk libs + argv guard already on main). PR trigger makes it a real merge gate; push trigger catches direct-to-branch work. |
| **D4** | Which hook checks CI mirrors | CI re-runs the two checks that are meaningful on a remote: **`pylint --errors-only`** over the same scope the hook lints, and the **full `pytest` suite** (the pre-push check). It does **not** mirror the `skip-worktree` config-protection check. | The config-protection check is inherently local (it guards against clearing a local flag); it has no meaning on a fetched CI tree. The lint + suite are the checks that define "the floor didn't move." Run as steps in the same job (or a light second job). |
| **D5** | Baseline handling | Measure coverage in CI, **upload the report as a job artifact** (term + `coverage.xml`) and print the summary to the log. Record the measured baseline **number in this plan's Acceptance** once known. Commit **no** coverage file into the tree. | "Measure, don't gate" per the user's call. Recording the number in the plan (not a committed report) respects the standing "coverage is written fresh, never resurrected" rule and gives the future ratchet a documented starting point. |
| **D6** | First test target: `start_frontend_apps.py` | Add **characterization** tests (pytest `characterization` marker) that pin current behavior, mocking the side-effecting seams (`launch_script`, `display_image_from_config`, `launch_osd`, `load_toml_config`, `launch_game`, `time.sleep`). Cover, in blast-radius order: `setup_virtual_environment`, `prepare_system`, `start_conditional_scripts` (the config-driven branching), then `main()` orchestration. | This is the flagged zero-coverage boot path; characterization (not spec-of-desired-behavior) is correct because we're pinning what exists to protect future refactors — including current quirks (e.g. the fixed 5s Pegasus sleep with no readiness check, noted in the module). Import has side effects (version warning, `sys.path` insert); tests import via the `conftest` path setup already used by the suite. |

## Proposed acceptance (spec — measurable, gate-checkable)

1. **CI exists and is green on Ubuntu.** `.github/workflows/ci.yml` runs on
   push + PR to `main`, installs `tk-dev tcl-dev` + both requirements files on
   Python 3.12.9, and the suite passes at the known-green baseline
   (**46 passed / 3 skipped**, or the new count if D6 adds tests — stated
   explicitly, not "should pass").
2. **Coverage is measured and reported, not gated.** `pytest --cov` runs in CI,
   the report is uploaded as an artifact + printed, `.coveragerc` scopes it to
   the package, and **no** `--cov-fail-under` is set. The measured baseline
   number is recorded in this plan. No coverage file is committed.
3. **The hooks' floor is mirrored in CI.** CI re-runs `pylint --errors-only`
   (same scope as the hook) and the full suite; a red lint or a red suite fails
   the workflow. The raw hooks are unchanged; `core.hooksPath` behavior is
   untouched.
4. **`start_frontend_apps.py` has characterization coverage on its boot path.**
   New tests pin the current behavior of the functions named in D6 with the
   side-effecting seams mocked; they pass locally and in CI; coverage of that
   module rises measurably from zero (exact delta recorded once measured).
5. **No `skip-worktree` config file is touched, and no `pyproject.toml` is
   introduced.** The 12 personalized files show no edits (verified by reading
   back, not by trusting an empty diff); deps stay `venv` + `requirements*.txt`.
6. **The full gate approves.** Because D1 touches `requirements-dev.txt`, the
   change sizes to the **full gate** (adversary + qa + security-brief) per
   `scrutiny.toml`; every required seat is APPROVED at the final sha before
   merge. Never self-merge.

## Register decision

**Approved as a batch — D1 through D6 — with `start_frontend_apps.py` (D6)
in scope for this swing** (user directive, this session: "do everything").
Rationale for keeping D6 in: a coverage baseline that leaves the flagged
zero-coverage boot path at zero is not a floor. No IDs overridden.

## Research / baseline (measured)

Measured on this Linux box (pyenv 3.12.9, `.venv`, tk libs present), before and
after the D6 tests, cited from the `pytest --cov` runs:

- **Pre-existing baseline:** `src/arcade_station` at **20%** (909 statements
  measured; the boot path and two other scripts at 0%).
- **`start_frontend_apps.py`:** **0% → 88%** (139 stmts; the 15 uncovered lines
  are edge branches — the Python-version-mismatch warning (32-34), the Windows
  activate-missing branch (84-85), several exception/failure log lines (170,
  194-196, 234, 239, 281-283), and `__main__` (298)).
- **Whole-package figure after:** **27%**. The denominator grows to 1043 stmts
  because covering the boot path pulls `launch_binary.py` (134 stmts) into the
  imported-and-measured set for the first time — so the headline 20→27 understates
  the real gain on the target module (0→88).
- **Suite:** **46 → 65 passed, 3 skipped** — green. Bare `pytest` (no `--cov`,
  the pre-push hook path) still runs; `--cov` is CI-only.

These numbers are the recorded floor for the future coverage ratchet; no coverage
file is committed (CI keeps `coverage.xml` as an ephemeral artifact).

## Design

**Overview.** Three artifacts stand up the floor; a fourth raises the flagged
module off zero. Nothing changes runtime behavior — this is test/CI/config only.

**Components & interfaces.**

- **`.coveragerc`** (new) — coverage config in a dedicated file (no `pyproject`),
  `source = src/arcade_station`, `branch = true`, `show_missing`. **No
  `fail_under`** (measure, don't gate). Deliberately not referenced from
  `pytest.ini addopts`, so a bare `pytest` runs without `pytest-cov` installed.
- **`requirements-dev.txt`** (edit) — add `pytest-cov>=7.1.0` (dev-only; pulls
  `coverage` transitively). This is the line that trips the full gate (D1 note).
- **`.github/workflows/ci.yml`** (new) — `ubuntu-latest`, Python `3.12.9`, install
  `tk-dev tcl-dev` then both requirements files, then two steps that mirror the
  hooks: **(a)** `pylint --errors-only` over the branch's changed `.py` vs
  `origin/main` (the hook lints *staged* files; a remote has no staging area, so
  CI uses the `origin/main...HEAD` surface AGENTS.md mandates — this also dodges
  the known `app.py`/`tomli` import-error landmine unless a change actually
  touches `app.py`), and **(b)** `pytest --cov` (the pre-push suite) with the
  report uploaded as an artifact. Triggers: push on any branch, PR to `main`.
- **`tests/test_start_frontend_apps.py`** (new) — 19 characterization tests
  (pytest `characterization` marker) pinning current behavior of
  `setup_virtual_environment`, `prepare_system`, `start_conditional_scripts`, and
  `main`, with every side-effecting seam monkeypatched (no process launched, no
  marquee drawn, no real sleep, venv untouched). Follows the existing
  `test_launch_arguments.py` monkeypatch style.
- **`.gitignore`** (edit) — ignore `.coverage`, `.coverage.*`, `coverage.xml`,
  `htmlcov/` so a local `--cov` run never stages a coverage artifact.

**Error handling / behavior pinned.** The characterization tests assert what the
code *does today*, quirks included (e.g. the fixed 5 s Pegasus sleep is pinned as
a `time.sleep` call, not asserted to be a readiness check), so a refactor that
moves behavior fails here rather than silently shipping.

**Testing strategy.** Local: full suite green with and without `--cov`, and
`pylint --errors-only` clean on the changed file (both run before commit).
Remote: the same suite + lint + coverage on Ubuntu CI, verified via the Actions
run on the pushed branch — acceptance #1 is proven by that run, not asserted.

## Steps

Each step names the observable Demo available once it is done.

- **Step 1 — Coverage config + dev dep.** Add `.coveragerc` and `pytest-cov` to
  `requirements-dev.txt`; ignore coverage artifacts.
  *Demo:* `pytest --cov` prints a per-file table; bare `pytest` still runs.
- **Step 2 — CI workflow.** Add `.github/workflows/ci.yml`.
  *Demo:* pushing the branch triggers a green Actions run that installs tk libs,
  lints the changed `.py`, runs the suite, and uploads `coverage.xml`.
- **Step 3 — Boot-path characterization.** Add
  `tests/test_start_frontend_apps.py`.
  *Demo:* `pytest --cov` shows `start_frontend_apps.py` at 88% and the suite at
  65 passed / 3 skipped; `pylint --errors-only` on the file is clean.

## Gate

Full gate (adversary + qa + security-brief), sized by `scrutiny.toml`: the
`requirements-dev.txt` edit trips the non-overridable `network-boundary-and-deps`
rule. Seats ran fresh in independent context; the Architect transcribed verdicts
to avoid a concurrent write-race on this file.

**Round 1 (@c874b69).** The adversary returned CHANGES on one measurably-false
claim: mutation testing showed that no-op'ing the `time.sleep(5)` Pegasus warm-up
(`start_frontend_apps.py:273`) left the suite fully green, yet both the test
docstring and this plan's Design claimed that exact quirk was pinned "so a
refactor fails here." 9 of 10 other mutants were killed — the pin was otherwise
strong. qa and security-brief raised no blocking findings: qa flagged one
disclosed-safe WARNING (the CI lint step didn't exclude deletions, unlike the
hook it mirrors) plus a loose doc enumeration; security-brief flagged one LOW
(leading-dash filenames could be read as pylint flags in the lint step) plus INFO
advisories. All findings were folded into the r2 fix:

- Test now records call order and asserts the 5s warm-up sleep occurs *before*
  the default-game launch — the surviving mutant (MUT4) now fails.
- CI lint step: `--diff-filter=ACMR` (excludes deletions; matches the hook) and a
  trailing `--` (ends pylint option parsing) — closes qa's WARNING and
  security-brief's LOW in one step.
- Plan's uncovered-line enumeration corrected to the exact line numbers.

**Round 2 (@c281d44).** All three findings folded in and re-verified by the same
seat instances against the fix commit: the adversary re-ran the surviving mutant
(and a bonus `sleep(5)→sleep(3)` mutant) and confirmed both now fail; qa
confirmed the sleep pin is a real characterization assertion (not a tautology)
and its lint-step WARNING resolved; security-brief confirmed its LOW closed by the
`--` guard. Suite green at 65 passed / 3 skipped.

**Acceptance #1 verified (not asserted).** GitHub Actions run 35557861933 on
`c281d44` is green: Ubuntu / Python 3.12.9, Tk runtime installed, the lint step
scoped to the one changed `.py` and passed, `65 passed, 3 skipped`,
`start_frontend_apps.py` at 88%, TOTAL 27%, `coverage-xml` artifact uploaded. Two
non-blocking runner annotations (Node-20 action-runtime deprecation; the
`ubuntu-latest`→Ubuntu-26 migration notice) — advisory, tracked with
security-brief's action-pinning INFO.

Gate: CHANGES r1 @c874b69 — adversary (see round 1 above)

Gate: APPROVED r2 @c281d44 — adversary, qa, security-brief
