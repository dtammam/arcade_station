# Reliability

## Performance budgets

None. Nothing here has been timed on a cabinet, so no budget is asserted.
An earlier revision of this file listed six, none of which were measured;
they were removed rather than left to be mistaken for observations. If you
need a budget, measure first and record the measurement alongside it.

## Invariants

Inherited from an earlier revision of this file and not individually
re-verified against the code. Treat them as intent to uphold rather than as
statements of proven fact.

- `core_functions.open_header` must always set the global environment before any script runs
- TOML config files in `config/` must always be valid TOML — never write partial or corrupted config
- Platform-specific code never imports from another platform's module (no `windows` imports in `linux/`)
- `kill_all` must terminate every process it manages — partial kills leave the system in a broken state
- Key listeners must not block the main thread — they run in background threads
- The installer must never overwrite existing user configuration without explicit confirmation

## When an invariant is at risk

Flag it before proceeding. Do not silently ship a regression against one of
these - say plainly what moved, and let the two-reviewer gate in
`.claude/agents/` weigh it.
