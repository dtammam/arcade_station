# Start here. Bootstraps a new feature into the agent pipeline.

## Input

$ARGUMENTS describes the feature or change.

## Procedure

1. Invoke the engineering-manager agent with this instruction:

   "Run the Bootstrap stage ONLY. Read `.state/feature-state.json` and
   project context (`docs/index.md`, `docs/ARCHITECTURE.md`, `docs/CONTRIBUTING.md`,
   `docs/RELIABILITY.md`, active exec plans). Initialize or resume state for
   the feature described below. Summarize the starting context.

   Feature: [$ARGUMENTS]"

2. Relay the engineering-manager's summary to the user verbatim.

---

## ▶ NEXT STEP

Run **`/discover`** to gather requirements.

---

## Rules

- ONE stage only. Do not auto-progress to Discovery.
- If a feature is already active, the EM should warn and ask the user how to proceed.
