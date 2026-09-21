<!-- harness:region:start id=doc -->
# /seed — onboard this repo (one-shot)

Detect the project's stack and fill the harness's `{{PLACEHOLDER}}` tokens with
real values, so a fresh install becomes specific to this repo. One-shot: it does
NOT open a plan or enter the flow. Safe to re-run — on an already-seeded repo it
reports and changes nothing.

## What it fills

The project-owned docs the harness installs as templates (all `once` / `keep`
-owned, so seeding never fights a harness update):

- `docs/CONTRIBUTING.md` — language, frameworks, package manager, build / test /
  lint / format commands, testing methodology.
- `docs/ARCHITECTURE.md` — system purpose, shape, components, data & state,
  dependencies, invariants.
- `docs/RELIABILITY.md` — what "reliable" means here, how it's measured, failure modes.
- `AGENTS.md` — the `keep` region: the project's attack surfaces and any lessons.

## Procedure

1. **Detect the stack**, citing what each value came from. Read the manifest and
   config files present: `package.json`, `Cargo.toml`, `pyproject.toml` /
   `requirements*.txt`, `go.mod`, `Gemfile`, `pom.xml`, `Makefile`, a task runner,
   and the CI workflow. Infer language, frameworks, package manager, and the
   build / test / lint / format commands from them; infer architecture from the
   top-level layout and entry points.
2. **Find the tokens.** For each seedable file, locate the remaining `{{TOKENS}}`.
   A file with none is already seeded — leave it untouched.
3. **Fill only the tokens.** Replace each `{{TOKEN}}` with the detected value,
   preserving all surrounding content. Do not rewrite prose a human wrote, and do
   not touch harness-owned regions.
4. **Flag what you couldn't detect.** Any token you cannot fill from evidence is
   reported as "needs manual attention" — never guessed, never left as a silent
   `{{TOKEN}}`.
5. **Report.** Present a seed report: the detected stack with its sources, the
   tokens filled per file, and anything needing manual attention. State plainly
   that no plan was created.

## Rules

- One-shot: never create a `docs/exec-plans/` plan or advance a phase.
- Fill from evidence only; a value you cannot source is flagged, not invented.
- Preserve human-written content and harness-owned regions; touch only the tokens
  in project-owned space.
- Idempotent: re-running on a seeded repo is a no-op report, not an overwrite.
<!-- harness:region:end id=doc -->
