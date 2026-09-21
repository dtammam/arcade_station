<!-- harness:region:start id=doc -->
# /gate — run the review gate (Phase 4)

Run the gate protocol against the current diff. This is Phase 4 of `.harness/flow.md` and
it implements `.harness/lib/gate-protocol.md` exactly. Independent seats review the work
and write bound verdicts into the plan doc; you fix and re-engage until every
required seat is APPROVED at the same final sha. **You never merge your own
work** — the gate is the independence.

## Input

`$ARGUMENTS` = optional base ref to diff against. Default the base to
`git merge-base HEAD <default-branch>` (the branch point).

## Precondition — commit first

The work must be committed before gating: verdicts bind to a commit sha and the
seats mutate against a committed tree. If the tree is dirty, commit it (a WIP
commit is fine) — the reviewed sha is `HEAD`. Never gate a staged-but-uncommitted
diff, and never rewrite the approved commit afterward; a fix is a new commit,
re-gated.

## Procedure

1. **Select the seats from the table, not from judgment.** Compute the diff and
   its change class, then evaluate `.harness/scrutiny.toml`:
   - `git diff --name-only <base>` for the touched paths.
   - Classify the change (e.g. `deletes-data`, `alters-schema`) from the diff.
   - Match rows top to bottom: the first non-floor rule sets the baseline seat
     set, then every `force = true` rule that also matches unions in and cannot
     be dropped. The **Adversary is always in the set**.
   - **Destructive or data-losing changes force the FULL gate** — no discretion
     to dial it down.
   - You may ESCALATE (add seats); you may NEVER de-escalate. If you think a seat
     is unnecessary, you still run it.

2. **Build the brief.** For each selected seat, assemble: `{branch, base sha,
   path to the plan/acceptance doc, named attack surfaces}`. The plan doc is the
   contract the diff is judged against — and it may itself be wrong; a diff that
   faithfully implements a wrong plan is still a finding.

3. **Spawn the seats fresh, in independent context.** Fork the seat agents from
   `.claude/agents/` — `adversary`, and `qa` / `security-brief` as the table
   selected them — via the Agent tool, one message with all of them so they run
   concurrently, each with its brief. A seat that runs in your own head is not a
   seat; the independent context is the whole value.

4. **Collect verdicts.** Each seat appends one bound line to the plan doc:

   ```
   Gate: <APPROVED|CHANGES> r<n> @<sha> — <seat>
   ```

   `@<sha>` is the exact reviewed commit; the verdict binds to it.

5. **The fix loop.** On any `CHANGES`:
   - Fix the findings (a deviation that changes a public interface, data model,
     acceptance criterion, or user-visible behavior halts and returns to the
     user first — the approval covered the design as written).
   - Commit the fix, then **re-engage the SAME seat instances** (re-message them,
     do not spawn new ones) for a delta re-review against the new sha: they
     re-verify each finding, re-verify their own prescriptions, catch anything
     the fix introduced, and re-verdict at `r<n+1> @<new sha>`.
   - Repeat until every required seat is `APPROVED`.

6. **Close condition.** Every required seat (per `.harness/scrutiny.toml`) is `APPROVED`,
   each bound to the SAME final sha. Update the status block's `gate:` marker to
   reflect it. Only then is Phase 5 (`/release`) allowed.

## Rules

- **Never self-merge and never approve on your own say-so.** All required seats
  APPROVE, or the gate is not satisfied.
- Seats are set by `.harness/scrutiny.toml`, not by your judgment — you may only escalate.
- If this tool cannot give a seat genuinely independent context, the gate CANNOT
  be satisfied — report it unavailable and the change unreviewed. Do not fake it
  by self-reviewing.
- Do not fabricate a verdict line — only the seat that reviewed writes its own.
- An approval bound to an old sha is stale the moment the tree moves — re-engage.
<!-- harness:region:end id=doc -->
