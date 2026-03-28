---
name: Never make code changes directly — always route through SDE
description: Main session and EM must not write/modify code — all code changes go through the software-developer agent
type: feedback
---

Do not make code changes directly in the main session, even for small QA review fixes. Always route code changes through the software-developer agent via the EM.

**Why:** User corrected this after I manually edited test files and conftest.py to address QA findings instead of routing to the SDE. Had to revert commits and redo the work. The main session is the EM interface, not a code editor.

**How to apply:** When QA findings need fixes, route them back through `/implement` with the QA findings included in the SDE prompt. Never use Edit/Write tools on source code or test files in the main session.
