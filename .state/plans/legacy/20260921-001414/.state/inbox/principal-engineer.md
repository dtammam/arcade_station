# Principal Engineer -- Design for "Multi-phase code hygiene initiative"

## Your task

Produce a detailed technical design for the multi-phase code hygiene initiative. Write the design into the `## Design` section of the exec plan.

## Steps

1. **Read the exec plan** at `/home/coder/projects/arcade_station/docs/exec-plans/active/2026-03-27-code-hygiene-initiative.md`. Understand the goal, scope (three phases), constraints, and acceptance criteria thoroughly.

2. **Read project reference docs:**
   - `/home/coder/projects/arcade_station/docs/ARCHITECTURE.md`
   - `/home/coder/projects/arcade_station/docs/CONTRIBUTING.md`
   - `/home/coder/projects/arcade_station/docs/RELIABILITY.md`

3. **Scan the codebase structure.** Understand the repo layout, existing tooling configuration, and files that will be affected. Key areas to examine:
   - `src/` and `install/` directories (Python code that black/flake8/mypy will touch)
   - `bin/windows/` (PowerShell scripts for PSScriptAnalyzer)
   - `bin/unix/` and repo root (shell scripts for shellcheck)
   - All `*.toml` files (for taplo validation)
   - All `*.md` files, especially the 7 files listed in Phase 2 scope
   - `src/arcade_station/core/common/core_functions.py` (target for Phase 3 unit tests)
   - `requirements.txt` or any dev requirements file
   - `.markdownlint-cli2.jsonc` (current ignore entries)
   - `.vscode/tasks.json` (existing task definitions)
   - Git hooks in `.githooks/` or `.git/hooks/` (pre-commit and pre-push)
   - `pyproject.toml` or `pytest.ini` if they exist
   - `package.json` if it exists

4. **Produce the design.** Replace the placeholder `(To be filled by principal-engineer)` under the `## Design` heading in the exec plan with a thorough design section covering:

   - **Approach:** How each phase will be executed, in what order, and why.
   - **Components to change:** List every file or directory that will be created, modified, or deleted, organized by phase.
   - **Data model impact:** Confirm there is none (this is a non-functional change), or flag any concerns.
   - **Risks:** What could go wrong? Consider: mypy strictness levels, flake8 rules that conflict with black, shell script portability, PSScriptAnalyzer availability on Linux, taplo formatting vs. validation, test isolation for functions that touch the filesystem or OS APIs, pre-commit hook ordering.
   - **Alternatives considered:** At least two alternatives for key decisions (e.g., ruff vs. black+flake8, nox vs. manual scripts, pytest-cov vs. coverage.py, etc.).
   - **Phase sequencing rationale:** Why the three phases must be done in order, or whether any can be parallelized.
   - **Tool configuration details:** Recommended configuration for each tool (black line length, flake8 rules to enable/disable, mypy strictness, pytest markers, etc.) with rationale.

5. **Update ARCHITECTURE.md** if the design introduces new components (e.g., a `tests/` directory, new config sections). Add them to the appropriate section.

6. **Update the state file** at `/home/coder/projects/arcade_station/.state/feature-state.json`:
   - Set `artifacts.design` to `"docs/exec-plans/active/2026-03-27-code-hygiene-initiative.md"`

## Constraints

- Do NOT implement any code, tests, or configuration changes. Design only.
- Do NOT change any runtime behavior or application logic.
- All design decisions must comply with `docs/CONTRIBUTING.md` standards.
- Python 3.12.9 is the only supported version.
- Runtime dependencies are fixed: PyQt5, keyboard, psutil, tomli_w, Pillow.
- Performance budget: test suite must complete in under 30 seconds.
- No hardcoded paths -- all paths from TOML config in `config/`.
- Platform-specific code stays in `src/arcade_station/core/{windows,linux,macos}/`.

## Output

When you are done, report:
- A summary of the design approach
- Any risks or open questions flagged
- Confirmation that the exec plan and state file have been updated
