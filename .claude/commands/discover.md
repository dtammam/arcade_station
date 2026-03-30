# Gather requirements and acceptance criteria.

Routes to the Product Manager agent, who defines goal, scope, constraints, and writes the exec plan.

## Input

$ARGUMENTS can provide additional context for the PM (e.g., "focus on CLI UX").
If empty, the PM works from the state file.

## Procedure

1. Invoke the engineering-manager agent with this instruction:

   "Run the Discovery stage ONLY. Read `.state/feature-state.json`, update
   state to 'discovery', and write the exact prompt for the product-manager
   agent to `.state/inbox/product-manager.md` so I can run it via the VS Code
   task. Additional context for the PM: [$ARGUMENTS]. Do NOT invoke the
   product-manager yourself."

2. Relay the engineering-manager's routing instruction to the user verbatim.
   The EM will tell the user which VS Code task to run.

---

## Next step

Run the VS Code task **"Run Product Manager"** via **Terminal -> Run Task...**

## When done

Run **`/design`** to produce the technical design.

---

## Rules

- ONE stage only. Do not chain into Design.
- The EM outputs instructions — it does not run the PM itself.
- The exec plan file must exist at `docs/exec-plans/active/` before `/design`
  will proceed.
