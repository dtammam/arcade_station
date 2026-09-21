<!-- harness:region:start id=doc -->
# /release — verify & close (Phase 5)

Verify the work against its anchor and close it out in **one pull request**. This
is Phase 5 of `.harness/flow.md`. The close-out bookkeeping is committed to the
FEATURE branch *before* the PR merges, so the plan ships `Shipped` in the same PR
as the code — no separate docs-PR. After the merge, it cleans up the branch.

## Input

`$ARGUMENTS` = optional version/tag for the `Shipped <version>` marker.

## Precondition — the gate must be closed

Refuse to proceed unless every required seat (per `.harness/scrutiny.toml`) has an
`APPROVED` verdict in the plan, each bound to the CURRENT sha. If the tree moved
after the last approval, those markers are stale — re-run `/gate` first. **Never
self-merge**; a change reaches release only through the gate.

## Procedure — on the feature branch, before the PR merges

1. **Verify against the anchor** (from the plan's status block):
   - **outcome:** verify the result yourself against the acceptance bullets.
   - **spec / tdd:** verify against the acceptance criteria / the named tests.
   Report any failure VERBATIM, with counts, before any framing.

2. **Close the plan out.** Set `status: Shipped <version>` in the plan and move it
   from `docs/exec-plans/active/` to `docs/exec-plans/completed/` (a flat
   `<slug>.md`, or the whole `<slug>/` directory if the piece uses one).

3. **Guard the move (renames-only trap).** After moving and editing, VERIFY the
   file at its new `completed/` path actually contains the status —
   `grep -q '^status: Shipped' <completed-path>`. A `git mv` plus a frontmatter
   edit can silently no-op the edit when the path was already moved; do not
   proceed on an unverified move.

4. **Commit the close-out to the feature branch, staged by name.** Stage the moved
   plan explicitly (never `git add .` / `git add -A`), commit with an imperative
   message + co-author trailer, never `--no-verify`. It touches only the plan, so
   the gated code approval stays valid. The branch now holds code + Shipped plan
   together.

5. **Marker check, then push the ONE PR.** Run `.harness/lib/check-markers.sh`; on
   non-zero, STOP and fix. On clean, push the feature branch and ensure a single
   PR (feature → default) carries both the code and the close-out — this is the
   whole change, there is no trailing docs-PR. The merge is the human's (protected
   `main`) or the agent's only where policy allows; never a self-merge of
   unreviewed code.

## After the merge — clean up

6. Return to the default branch and prune, then drop the merged branch:
   `git checkout <default> && git pull --prune`. If `.harness/harness.toml` sets
   `[cleanup] delete_merged_branch = true`, delete the local branch
   (`git branch -d <branch>`) and the remote (`git push origin --delete <branch>`
   — a harmless no-op if the host auto-deletes on merge). The plan's `branch:`
   field names it.

## Rules

- Never self-merge; the gate is the gate.
- **One PR per piece:** the Shipped plan ships with the code, not in a trailing docs-PR.
- Stage files by name; no `git add .`, no force-push, no `--no-verify`.
- `.harness/lib/check-markers.sh` must pass before push — no exceptions.
- Status is a bound marker in the plan, not a prose line or a state file.
<!-- harness:region:end id=doc -->
