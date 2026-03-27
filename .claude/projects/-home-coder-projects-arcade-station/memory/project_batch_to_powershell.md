---
name: Batch to PowerShell migration
description: Future tech debt - migrate .bat/.cmd files to PowerShell for lintability
type: project
---

Batch files (.bat/.cmd) deliberately invoke PowerShell scripts as a wrapper pattern. No good linter exists for batch files.

**Why:** User wants all code validated by linters regardless of platform. Batch is the gap.

**How to apply:** Track as tech debt. When batch scripts come up for changes, consider migrating to pure PowerShell. Not in scope for the current code hygiene initiative (that's zero-functional-change only).
