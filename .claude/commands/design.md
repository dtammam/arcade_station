# Produce a technical design.

Routes to the Principal Engineer agent, who reads the exec plan and codebase,
then writes the Design section of the exec plan.

## Input

$ARGUMENTS can include design hints (e.g., "prefer composition over inheritance").

## Procedure

1. Invoke the engineering-manager agent with this instruction:

   "Run the Design stage ONLY. Read `.state/feature-state.json` and
   write the exact prompt for the principal-engineer agent to
   `.state/inbox/principal-engineer.md` so I can run it via the VS Code task.
   Additional guidance: [$ARGUMENTS].
   Do NOT invoke the principal-engineer yourself."

2. Relay the engineering-manager's routing instruction to the user verbatim.
   The EM will tell the user which VS Code task to run.

---

## ▶ NEXT STEP

Run the VS Code task **"Run Principal Engineer"** via **Terminal → Run Task…**

## ✅ WHEN DONE

- Review the Design section in the exec plan
- Run **`/tasks`** to break the design into implementable tasks

---

## Rules

- The exec plan must exist with requirements before running Design.
- The EM outputs instructions — it does not run the PE itself.
