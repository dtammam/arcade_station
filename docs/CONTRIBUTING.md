# Contributing

## Software design principles

These apply to every change, no exceptions.

- **Single responsibility** — every function, module, and file does one thing well.
- **Small, clean functions** — short, focused, readable top-to-bottom.
- **Modularity and cohesion** — composable pieces with clear inputs/outputs; related code lives together.
- **Explicit over implicit** — named parameters, clear return types, obvious control flow.
- **Minimal coupling** — depend on traits, not concrete types; follow layer boundaries.
- **DRY — but not prematurely** — extract after three genuine repetitions, not two.
- **Fail fast and visibly** — validate at boundaries; surface errors early.
- **Naming is documentation** — if a name needs a comment, rename it.
- **Type safety** — strict mode; validate at system boundaries.
- **Test coverage** — every public method has explicit tests.
- **Keep state minimal and local** — prefer derived values over stored duplicates.
- **Delete freely** — dead code is a liability; version control remembers.

## Coding standards

- Format: `black --check src/ install/` must pass
- Lint: `flake8 src/ install/` must pass (zero warnings)
- Type check: `mypy src/ install/` must pass
- Markdown lint: `npx markdownlint-cli2 '**/*.md'` must pass (all markdown files)
- No bare `except:` — always catch specific exceptions
- No mutable default arguments in function signatures
- Google-style docstrings on all public functions and classes
- Configuration via TOML files in `config/` — never hardcode paths or credentials
- Platform-specific code isolated in `src/arcade_station/core/{windows,linux,macos}/`
- Cross-platform code in `src/arcade_station/core/common/`
- Tests: `python -m pytest` must pass, every public behavior has a test
- Setup: run `./setup.sh` after cloning to install git hooks

## Three-pillar code quality framework

Every function and type must be classifiable as semantic, pragmatic, or a model.
If something straddles two categories, refactor until it doesn't.

### Semantic functions

- No boolean parameters that switch behavior — use enums or string literals (e.g., `Enum('upper', 'lower')` not `lowercase: bool`).
- Return types must encode invariants. If a function always returns exactly N items, use a tuple or dataclass, never a list.
- Accept the narrowest type that expresses the domain: prefer dataclasses over generic dicts.
- Pure functions must not transform data they don't own.

### Pragmatic functions

- Only `main()` and CLI/IO boundary code should be pragmatic. Everything else should be semantic and pure.
- Pragmatic functions must not leak into test expectations — test semantic functions directly, integration-test pragmatic ones via subprocess or entry points.

### Models

- Eliminate `Optional` fields when a default value exists — use `dataclasses.field(default=...)` at the parsing boundary instead.
- Represent multi-field domain objects as dataclasses, not tuples or dicts. Field names are documentation.
- If two values have different domain meanings, they must be distinguishable by type or dataclass field — never two bare strings in a list.

### Testing

- Every test must exercise a distinct code path. Tautological tests (same inputs, same function, different variable names) must be removed.
- Semantic functions get unit tests. Pragmatic/CLI behavior gets integration tests that invoke the entry point via subprocess.
- Edge cases must have explicit tests.

### Documentation

- Only include design principles that apply to this codebase. Remove generic principles.
- `RELIABILITY.md` invariants must be populated — if the type system doesn't enforce it, the docs must state it.
- `ARCHITECTURE.md` data model section must match actual types in code.
