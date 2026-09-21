<!-- harness:region:start id=wrapper -->
# CLAUDE.md

This project is configured through **`AGENTS.md`**. Read it first — it is the
entry point, and it points to everything else.

`AGENTS.md` is canonical so the same configuration works across Claude Code,
Cursor, Codex, and any other agent. This file is only a thin wrapper for the
tools that load `CLAUDE.md` by name.

## Non-negotiables (the short version — `AGENTS.md` has the rest)

- **Never self-merge.** The review gate runs before anything lands; the
  Adversary seat is its floor.
- **Destructive / data-losing changes force the full gate** — never dialed down.
- **Stage files by name.** No `git add .`, no force-push, no `--no-verify`.
- **Report failures verbatim.** "Verified" is not "should work."

If you read nothing else, read `AGENTS.md` before acting.
<!-- harness:region:end id=wrapper -->
