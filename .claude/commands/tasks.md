# Break the approved design into discrete, implementable tasks.

The Engineering Manager reads the Design section and produces a task list
with clear definitions of done.

## Input

$ARGUMENTS can include guidance (e.g., "keep it to 3 tasks max").

## Procedure

1. Invoke the engineering-manager agent with this instruction:

   "Run the Tasks stage ONLY. Read `.state/feature-state.json` and the
   exec plan's Design section. Break the design into discrete, implementable
   tasks. Each task must be independently testable and small enough for one
   implementation session. Write the task list to the state file and to the
   exec plan. Additional guidance: [$ARGUMENTS]."

2. Relay the engineering-manager's task list to the user verbatim.

---

## ▶ NEXT STEP

Review the task list. When approved, run **`/implement`**.

---

## Rules

- ONE stage only. Do not auto-progress to Implementation.
- Each task must have a clear definition of done.
- The EM does this stage itself — no specialist agent is invoked.
