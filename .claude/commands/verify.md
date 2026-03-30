# Run the build and test suite.

Routes to the Build Specialist agent, who runs all quality gates and reports pass/fail — without fixing anything.

## Input

$ARGUMENTS is not typically needed. Can include "verbose" for full output.

## Procedure

1. Invoke the engineering-manager agent with this instruction:

   "Run the Verification stage ONLY. Read `.state/feature-state.json` and
   write the exact prompt for the build-specialist agent to
   `.state/inbox/build-specialist.md` so I can run it via the VS Code task.
   Do NOT invoke the build-specialist yourself."

2. Relay the engineering-manager's routing instruction to the user verbatim.
   The EM will tell the user which VS Code task to run.

---

## Next step

Run the VS Code task **"Run Build Specialist"** via **Terminal -> Run Task...**

## When done

- If all checks **pass** and tasks remain -> run **`/implement`** for the next task
- If all checks **pass** and all tasks complete -> run **`/accept`**
- If any checks **fail** -> run **`/implement`** to fix, or handle manually
- Optional: run **`/review`** for a code review before acceptance

---

## Rules

- The build-specialist reports only — it does not fix code.
