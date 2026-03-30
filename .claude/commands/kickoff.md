# Start here. Bootstraps a new feature into the agent pipeline.

Tell the system what you want to build — it initializes state, reads project context, and prepares for requirements gathering.

## Input

$ARGUMENTS should be a brief description of the feature or change.
If empty, ask the user what they want to build.

## Procedure

1. Invoke the engineering-manager agent with this instruction:

   "The user wants to start a new feature: [$ARGUMENTS]. Run the Bootstrap
   stage ONLY. Initialize the state file, read existing context, summarize
   the starting state, and stop. Do NOT proceed to Discovery or any other
   stage. Output what you did and ask if the user is ready to move to
   Discovery."

2. Relay the engineering-manager's output to the user.

---

## Next step

Review the summary. When ready, run **`/discover`** to start requirements gathering.

---

## Rules

- ONE stage only. Do not chain into Discovery.
- If `.state/feature-state.json` already has an active feature, the EM should
  warn about this and ask whether to archive it or continue it.
