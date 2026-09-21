---
plan: land-harness-v2
harness: v2 · lean
branch: chore/land-harness-v2
anchor: outcome
status: Shipped 2026-09-21
next: Shipped to main. Swing B (test foundation) cuts from the post-merge main.
gate: APPROVED
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
3. **The suite is green on this Linux box, and the gate approves.** The pre-push
   hook runs the suite, and it blocked landing from Linux because two
   `test_launch_arguments.py` argv cases fail off-Windows without the
   `CREATE_NO_WINDOW` fixture stub. `--no-verify` is a non-negotiable-prohibited
   escape, so the guard (`fbd7ff4`, Dean-authored, tests-only, 7 lines) was folded
   into this branch (see Deviations). Measured after reinstalling the tk runtime
   libs (`tk-dev tcl-dev`, wiped by a container recreate) and cherry-picking the
   guard: **46 passed / 3 skipped** — green, matching the Windows baseline. The
   review gate runs against the committed sha (seats per `.harness/scrutiny.toml`;
   this diff — docs + harness + one tests fixture — still sizes to **slim —
   adversary only**) and the required seat is APPROVED at the final sha before
   merge. Never self-merge.

## Branch plan

The pile is uncommitted, so it moves cleanly: cut `chore/land-harness-v2` from
`origin/main`, carrying the working-tree changes with it. Originally the argv
guard (`fbd7ff4`) was to stay on `feature/linux-test-guards` for Swing B — but
the pre-push hook forced it in here (see Deviations), so it is cherry-picked onto
this branch. Swing B (the test-foundation branch) now cuts from the post-merge
`main` that already carries the guard.

## Deviations

- **`.vscode/tasks.json` was clobbered by the install** (not a manifest-tracked
  file). The harness replaced the four project tasks (Activate .venv, Run Tests,
  Lint, Kill Python) with a single auto-run "Claude session" task pointing at the
  personal path `$HOME/.claude/bin/claude-here.sh`. Surfaced to the user; decision
  = **keep both** — the four project tasks are restored and the Claude session
  task is retained alongside them. (The `$HOME/.claude` path is personal and will
  not resolve on other clones; accepted knowingly.)
- **The Linux argv guard (`fbd7ff4`) was folded into this branch.** The plan
  originally scoped it to Swing B, but the `pre-push` hook runs the suite and
  blocked the push from this Linux box (2 argv failures without the stub), and
  `--no-verify` is prohibited. Surfaced to the user; decision = **fold guard into
  Swing A**. Cherry-picked as `ba6519e` (Dean's authorship preserved), suite now
  46 passed / 3 skipped. This changed the reviewed surface, so the earlier r1
  verdict (bound to sha 81adf51) was voided and the piece re-gated at the new sha;
  the two premature bookkeeping commits (verdict + close) were reset off
  (unpushed) so history carries a single valid sign-off bound to the final sha.
  (Prose here deliberately avoids the `<VERB> @<sha>` shape so `check-markers.sh`
  does not read a narrative sentence as a live approval marker — an r2 finding.)

Gate: CHANGES r2 @06645f6 — adversary (see findings)

Gate: APPROVED r3 @73ca402 — adversary
