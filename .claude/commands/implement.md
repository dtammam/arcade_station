# Implement the next incomplete task.

Routes to the Software Developer agent, who writes code and tests for ONE task, runs quality checks, and reports what changed.

## Input

$ARGUMENTS can specify which task to implement if you want to override
the default order (e.g., "implement task 3"). If empty, picks the next
incomplete task in order.

## Procedure

1. Invoke the engineering-manager agent with this instruction:

   "Run the Implementation stage for ONE task only. Read `.state/feature-state.json`
   to identify the next incomplete task (or user-specified task: [$ARGUMENTS]).
   Write the exact prompt for the software-developer agent to
   `.state/inbox/software-developer.md` so I can run it via the VS Code task.
   Do NOT invoke the software-developer yourself."

2. Relay the engineering-manager's routing instruction to the user verbatim.
   The EM will tell the user which VS Code task to run.

---

## Next step

Run the VS Code task **"Run Software Developer"** via **Terminal -> Run Task...**

## When done

- If **more tasks remain** -> run **`/implement`** again for the next task
- If **all tasks are complete** -> run **`/verify`** to validate the build
- Optional: run **`/review`** for a code review at any point

---

## Rules

- ONE task per invocation.
- The EM outputs instructions — it does not run the SDE itself.
- If all tasks are already complete, the EM should tell the user to run `/verify`.
