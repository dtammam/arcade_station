# Onboard the agent framework into this repository.

Reads existing repo documentation, build config, and codebase structure to fill in all TODO placeholders and configure the agent pipeline for this project. Designed for brownfield repos that already have code, docs, and conventions.

## Input

$ARGUMENTS can provide hints (e.g., "this is a Python FastAPI project" or "we use pnpm"). If empty, the agent discovers everything from the repo.

## Procedure

1. Invoke the engineering-manager agent with this instruction:

   "This is a SEED operation — onboarding the agent framework into an existing
   repository. Do NOT run the normal feature pipeline. Instead, act as a
   setup assistant and perform the following steps.

   Additional context from the user: [$ARGUMENTS]

   ### Step 1: Discover the project

   Read and catalog everything you can find about this project:
   - README.md, CONTRIBUTING.md, or any existing contributor docs
   - Build config files: package.json, Cargo.toml, pyproject.toml, Makefile,
     Dockerfile, docker-compose.yml, go.mod, build.gradle, CMakeLists.txt, etc.
   - CI config: .github/workflows/*.yml, .gitlab-ci.yml, Jenkinsfile, etc.
   - Existing lint/format config: .eslintrc*, .prettierrc*, rustfmt.toml,
     ruff.toml, .flake8, .golangci.yml, etc.
   - Test config: jest.config.*, pytest.ini, .mocharc.*, vitest.config.*, etc.
   - Source directory structure (top-level ls + one level deep in src/ or equivalent)
   - Any existing CLAUDE.md (preserve user customizations, merge with template)
   - docs/ directory contents if present

   From this, determine:
   - **Language/framework** (e.g., TypeScript + Next.js, Rust + clap, Python + FastAPI)
   - **Build command** (e.g., npm run build, cargo build, make)
   - **Test command** (e.g., npm test, cargo test, pytest)
   - **Lint command** (e.g., npm run lint, cargo clippy -- -D warnings, ruff check .)
   - **Format check command** (e.g., npm run format:check, cargo fmt -- --check, ruff format --check .)
   - **Main branch name** (check git remote or default)
   - **Package manager** (npm, pnpm, yarn, pip, cargo, go, etc.)
   - **Existing coding standards** (from any contributor docs or lint configs)
   - **Architecture patterns** (monorepo? microservices? MVC? layers?)
   - **Performance constraints** (any SLAs, budgets, or benchmarks mentioned anywhere)
   - **Existing non-negotiables** (e.g., no unsafe, 100% type coverage, required CI checks)

   ### Step 2: Fill in CLAUDE.md

   Read the current CLAUDE.md. Replace every TODO and placeholder:
   - Quality gates: fill in pre-commit and pre-push with actual commands
   - Commands section: list the real build/test/lint/format commands
   - Non-negotiables: carry over anything from existing docs + lint configs
   - Active work: note any in-progress branches or open PRs if discoverable

   Preserve the agent architecture sections unchanged. Only fill in the
   project-specific sections.

   ### Step 3: Fill in docs/CONTRIBUTING.md

   Read the current docs/CONTRIBUTING.md. Replace placeholders:
   - Coding standards: fill in format, lint, test commands
   - Add any project-specific standards discovered from existing docs or configs
   - Preserve the universal design principles already in the file
   - Add setup instructions (what to run after cloning)

   If the repo already had a CONTRIBUTING.md before agent-pack was installed,
   merge the agent-pack template's structure with the existing content —
   keep the user's original standards and add the missing sections.

   ### Step 4: Fill in docs/ARCHITECTURE.md

   Read the current docs/ARCHITECTURE.md. Replace the template with actual
   architecture based on what you discovered:
   - Overview of the system
   - Major components/modules and their responsibilities
   - How they interact (data flow, API boundaries, layer structure)
   - Key dependencies and why they exist

   If the repo already has architecture docs elsewhere, reference or consolidate them.

   ### Step 5: Fill in docs/RELIABILITY.md

   Read the current docs/RELIABILITY.md. Replace placeholders:
   - If the project has benchmarks, SLAs, or perf tests: document those budgets
   - If not: propose sensible defaults based on the project type and note they
     are provisional

   ### Step 6: Fill in hooks/

   Read hooks/pre-commit and hooks/pre-push. Replace the placeholder warnings
   with the actual commands discovered in Step 1.

   ### Step 7: Present a summary

   Output a structured report:

   ```
   Seed Report: [repo name]

   Language/framework: [detected]
   Package manager: [detected]
   Build: [command]
   Test: [command]
   Lint: [command]
   Format: [command]

   Files updated:
   - CLAUDE.md — [what was filled in]
   - docs/CONTRIBUTING.md — [what was filled in]
   - docs/ARCHITECTURE.md — [what was filled in]
   - docs/RELIABILITY.md — [what was filled in]
   - hooks/pre-commit — [commands configured]
   - hooks/pre-push — [commands configured]

   Warnings:
   - [anything that needs manual attention]

   Ready to use: /kickoff <your feature>
   ```

   Do NOT advance to any other stage. This is a one-shot setup operation."

2. Relay the engineering-manager's seed report to the user.

---

## When done

Review the changes, then run **`/kickoff <feature>`** to start your first feature.

---

## Rules

- This is a one-shot setup command, not part of the normal pipeline.
- Preserve any existing user content — merge, don't replace.
- If something can't be auto-detected, note it as needing manual attention.
- Do not start a feature lifecycle. Just configure the framework and stop.
