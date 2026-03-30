# Validate the implementation against acceptance criteria.

Routes to the Product Manager agent, who checks every criterion explicitly and reports pass/fail — without fixing anything.

## Input

$ARGUMENTS is not typically needed.

## Procedure

1. Invoke the engineering-manager agent with this instruction:

   "Run the Acceptance stage ONLY. Read `.state/feature-state.json`, confirm
   all tasks are in completed_tasks, update state to 'acceptance', and write
   the exact prompt for the product-manager agent to
   `.state/inbox/product-manager.md` so I can run it via the VS Code task.
   Do NOT invoke the product-manager yourself."

2. Relay the engineering-manager's routing instruction to the user verbatim.
   The EM will tell the user which VS Code task to run.

---

## Next step

Run the VS Code task **"Run Product Manager"** via **Terminal -> Run Task...**

## When done

- If all criteria **pass** -> run **`/done`** to close the feature
- If any criteria **fail** -> run **`/implement`** to fix, or defer to tech debt

---

## Rules

- All tasks must be complete before running acceptance.
- The PM verifies — it does not implement fixes.
- All criteria must be explicitly checked — "looks good" is not acceptance.
