# Reliability

## Performance budgets

- Frontend launch (Pegasus start): < 5s from script invocation to visible UI
- Game launch: < 3s from key press to game process visible
- Screenshot capture: < 1s from key press to image saved
- Process kill (kill_all): < 2s to terminate all managed processes
- Installer page transitions: < 1s
- Test suite: < 30s

## Invariants

- `core_functions.open_header` must always set the global environment before any script runs
- TOML config files in `config/` must always be valid TOML — never write partial or corrupted config
- Platform-specific code never imports from another platform's module (no `windows` imports in `linux/`)
- `kill_all` must terminate every process it manages — partial kills leave the system in a broken state
- Key listeners must not block the main thread — they run in background threads
- The installer must never overwrite existing user configuration without explicit confirmation

## When a budget is at risk

Flag the regression before proceeding. Do not silently ship a performance
regression. The engineering-manager agent will decide how to handle it.
