# Run a code review on the current changes before merging.

## What this does

Invokes the engineering-manager agent to:
1. Read current state
2. Write the exact prompt for the **quality-assurance** agent to `.state/inbox/quality-assurance.md`

The quality-assurance engineer (run separately by you) will:
- Run `git diff main` to identify all changed files
- Review each file for correctness, security, performance, and standards compliance
- Report findings as CRITICAL / WARNING / SUGGESTION
- Give an overall verdict: APPROVE, REQUEST CHANGES, or NEEDS DISCUSSION
- **Does NOT fix code** — reports only

## Input

$ARGUMENTS is not typically needed. Can include "focus on security" or similar guidance.

## Procedure

1. Invoke the engineering-manager agent with this instruction:

   "Run the Review stage. Read `.state/feature-state.json` and write the exact
   prompt for the quality-assurance agent to `.state/inbox/quality-assurance.md`
   so I can run it via the VS Code task. Additional guidance: [$ARGUMENTS].
   Do NOT invoke the quality-assurance agent yourself."

2. Relay the engineering-manager's routing instruction to the user verbatim.
   The EM will tell the user which VS Code task to run.

---

## ▶ NEXT STEP

Run the VS Code task **"Run Quality Assurance"** via **Terminal → Run Task…**

## ✅ WHEN DONE

- If verdict is **APPROVE** → run `/done` to close the feature
- If verdict is **REQUEST CHANGES** → run `/implement` to fix the issues
- If verdict is **NEEDS DISCUSSION** → discuss with the team, then decide

---

## Rules

- The QA engineer reports only — it does not fix code.
- Can be run at any point, but most useful after `/verify` passes and before `/done`.
- Optional step — not required in the standard workflow, but recommended for non-trivial changes.
