<!-- harness:region:start id=doc -->
# /status — read the current state (read-only)

Report where the work stands by reading the active plan doc's markers and
running the marker checker. This command is a mirror: it reflects the
state-as-document spine, it does not change it.

## Rules — read these first

- This command is STRICTLY READ-ONLY. Do NOT write, move, or edit any file —
  not the plan doc, not the status block, not a marker.
- Do NOT spawn any agent or seat. `/status` never runs the gate.
- Do NOT advance a phase or "fix" a flagged marker — only report it.

## Procedure

1. **Find the active plan.** List `docs/exec-plans/active/*/plan.md` (a piece of
   work is a directory), plus any legacy flat `docs/exec-plans/active/*.md`. If
   none exists, report "No active plan." and stop.

2. **Read the status block** of each active plan and report, from its markers:
   - `plan` (the id / branch name)
   - `anchor` (`outcome | spec | tdd`)
   - `status` (from the closed vocabulary in `.harness/lib/harness-markers.md`)
   - `next` (the one-line resume point — the very next concrete action; lead with it)
   - `gate` and every `Gate: <verdict> r<n> @<sha> — <seat>` line, i.e. which
     required seats have APPROVED and at which sha, and which are still
     outstanding.

3. **Run the marker checker.** Run `.harness/lib/check-markers.sh` (read-only) and report
   its output verbatim — a clean result, or each stale/misfiled marker it flags
   (unknown sha, approval predating a file change, terminal status still under
   `active/`).

4. **Show the uncommitted diff** for context: `git status` and
   `git diff --stat` (read-only). Note if the tree has moved since the last
   `Gate: APPROVED` sha — that approval is stale until re-confirmed.

5. **Present a short summary** — plan, anchor, status, gate standing, checker
   result, working-tree state — and, as a suggestion only, which phase command
   would come next (`/start`, `/gate`, `/release`). Recommend; do not act.
<!-- harness:region:end id=doc -->
