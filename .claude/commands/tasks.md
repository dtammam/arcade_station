# Break the approved design into discrete, implementable tasks.

The engineering-manager reads the exec plan and splits the work into small, independently testable units with clear definitions of done.

## Input

$ARGUMENTS can refine how tasks are split (e.g., "keep it to one task,
this is trivial"). If empty, the EM decides based on the design.

## Procedure

1. Invoke the engineering-manager agent with this instruction:

   "Run the Tasks stage ONLY for the current feature. Read the design
   from the exec plan and break the work into discrete tasks. Write the
   tasks to the state file and the exec plan. Additional guidance from
   user: [$ARGUMENTS]. Present the task list and stop. Do NOT proceed
   to Implementation or any other stage."

2. Relay the engineering-manager's output to the user.

---

## Next step

Review the task breakdown above.

## When approved

Run **`/implement`** to start the first task.

---

## Rules

- ONE stage only. Do not chain into Implementation.
- Each task must have a clear definition of done.
- The EM does this itself — it does NOT delegate task breakdown to another agent.
