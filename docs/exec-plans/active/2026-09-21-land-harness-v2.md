---
plan: land-harness-v2
harness: v2 · lean
branch: chore/land-harness-v2
anchor: outcome
status: Building
next: Run the review gate against the committed sha; seats per .harness/scrutiny.toml.
gate: pending
---

# Land the v2 harness

## Context

The entire handoff-harness v2 install is sitting **uncommitted** in the working
tree and has never been committed anywhere: `.harness/`, `AGENTS.md`, the new
`.claude/` agents/commands/hooks/settings, the doc rewrites
(`CLAUDE.md`, `docs/ARCHITECTURE.md`, `docs/RELIABILITY.md`,
`docs/CONTRIBUTING.md`), the deletion of the pre-v2 agents
(`.claude/agents/adversarial-reviewer.md`, `quality-assurance.md`), and the
`docs/exec-plans/` + `.state/` scaffolding. This is exactly the kind of harness
reconciliation `AGENTS.md` warns has hidden changes from review before.

Nothing can rest on a clean foundation while this floats, so it lands first as
its own PR — before any test-foundation work.

**Anchor: outcome.** This is committing already-installed infrastructure whose
design is embodied in the files; there is no new design to approve. The care goes
into the *diff being coherent and complete*, not into inventing anything.

## Acceptance

1. **Every harness file is committed, coherent, and nothing else changed.** The
   working tree is clean afterward except for intentionally-ignored paths; the
   pre-v2 agents are deleted, the v2 agents/commands/hooks/protocol are present,
   and the doc rewrites are included. Files staged **by name** — no `git add .`.
2. **No `skip-worktree` config file is touched.** The 12 personalized files named
   in `AGENTS.md` (`config/*.toml`, the three `src/pegasus-fe/config/metafiles/*`)
   show no edits; verified by reading them back, not by trusting an empty diff.
3. **The suite does not regress vs `origin/main`, and the gate approves.** This
   branch is cut from `origin/main`, which does **not** carry the Linux argv guard
   (`fbd7ff4`, still on `feature/linux-test-guards` — that is Swing B). So the
   honest bar here is *parity with the baseline*, not 46/3. Measured on this box
   after reinstalling the tk runtime libs (`tk-dev tcl-dev`, wiped by a container
   recreate): **HEAD == origin/main == 2 failed / 44 passed / 3 skipped.** The two
   failures are the pre-existing `test_launch_arguments.py` argv cases Swing B
   fixes; this docs/harness-only commit touches no `.py` and moves nothing. The
   review gate runs against the committed sha (seats per `.harness/scrutiny.toml`;
   this diff sizes to **slim — adversary only**) and every required seat is
   APPROVED at the final sha before merge. Never self-merge.

## Branch plan

The pile is uncommitted, so it moves cleanly: cut `chore/land-harness-v2` from
`origin/main`, carrying the working-tree changes with it. The one commit already
on `feature/linux-test-guards` (`fbd7ff4`, a 7-line off-Windows test stub) stays
on that branch and folds naturally into the later test-foundation work — it is a
linux test guard, same theme.

## Deviations

- **`.vscode/tasks.json` was clobbered by the install** (not a manifest-tracked
  file). The harness replaced the four project tasks (Activate .venv, Run Tests,
  Lint, Kill Python) with a single auto-run "Claude session" task pointing at the
  personal path `$HOME/.claude/bin/claude-here.sh`. Surfaced to the user; decision
  = **keep both** — the four project tasks are restored and the Claude session
  task is retained alongside them. (The `$HOME/.claude` path is personal and will
  not resolve on other clones; accepted knowingly.)
