# Produce a technical design.

Routes to the Principal Engineer agent, who reads the exec plan and codebase, then writes an approach, component changes, risks, and alternatives into the exec plan.

## Input

$ARGUMENTS can provide design hints or constraints. If empty, the PE works
from the exec plan and codebase.

## Procedure

1. Invoke the engineering-manager agent with this instruction:

   "Run the Design stage ONLY. Read `.state/feature-state.json`, confirm the
   requirements artifact exists, update state to 'design', and write the exact
   prompt for the principal-engineer agent to `.state/inbox/principal-engineer.md`
   so I can run it via the VS Code task. Additional guidance for the PE:
   [$ARGUMENTS]. Do NOT invoke the principal-engineer yourself."

2. Relay the engineering-manager's routing instruction to the user verbatim.
   The EM will tell the user which VS Code task to run.

---

## Next step

Run the VS Code task **"Run Principal Engineer"** via **Terminal -> Run Task...**

## When done

Run **`/tasks`** to break the design into implementable tasks.

---

## Rules

- ONE stage only. Do not chain into Tasks.
- The EM outputs instructions — it does not run the PE itself.
- The Design section of the exec plan must be filled before `/tasks` will proceed.
