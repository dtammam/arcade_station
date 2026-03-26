# Gather requirements and acceptance criteria.

Routes to the Product Manager agent, who writes a structured exec plan with
goals, scope, constraints, and testable acceptance criteria.

## Input

$ARGUMENTS can include context for the PM (e.g., "focus on API changes only").

## Procedure

1. Invoke the engineering-manager agent with this instruction:

   "Run the Discovery stage ONLY. Read `.state/feature-state.json` and
   write the exact prompt for the product-manager agent to
   `.state/inbox/product-manager.md` so I can run it via the VS Code task.
   Additional context: [$ARGUMENTS].
   Do NOT invoke the product-manager yourself."

2. Relay the engineering-manager's routing instruction to the user verbatim.
   The EM will tell the user which VS Code task to run.

---

## ▶ NEXT STEP

Run the VS Code task **"Run Product Manager"** via **Terminal → Run Task…**

## ✅ WHEN DONE

- Review the exec plan in `docs/exec-plans/active/`
- Run **`/design`** to produce the technical design

---

## Rules

- The exec plan file must exist before proceeding to Design.
- The EM outputs instructions — it does not run the PM itself.
