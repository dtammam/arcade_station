<!-- harness:region:start id=doc -->
# /start — intake & anchor (Phase 1)

Begin a piece of work. This is Phase 1 of `.harness/flow.md`: read the request, do the
blind-spot pass, propose the anchor and the acceptance, and write the plan doc
with a bound status block. It stops after one confirmation. It does NOT design,
build, or gate — those are later phases.

## Input

`$ARGUMENTS` = optional one-line description of the work. If empty, ask the user
for one before proceeding.

## Procedure

1. **Read the request.** Restate it in one line so the user can correct a
   misread before any doc exists.

2. **Blind-spot pass.** Read the repo enough to surface the unknowns the user
   has NOT thought to raise, while they are still cheap: existing plans under
   `docs/exec-plans/active/` that overlap this area, the attack surfaces and
   standing decisions in `AGENTS.md`, the code the change will touch. Name the
   assumptions the work rests on. This pass is the point of Phase 1 — do not
   skip it to get to a plan faster.

3. **Recommend the anchor — reconcile against the default.** Read the project
   default from `.harness/harness.toml` (`[defaults] anchor`), then form your OWN
   opinion for THIS request from the blind-spot pass. Always show both, and when
   they differ, say so plainly and argue the change:

   > Anchor — default: `outcome` · recommended: `spec`
   > This request changes a data model and a public interface, so "correct" has
   > to be pinned before code. Why: (X) it alters a schema other files parse;
   > (Y) it's multi-file with ordering that matters; (Z) a wrong read is
   > expensive to unwind. Recommend `spec` — confirm, or override.

   When they match, say so too ("default and recommended both `outcome` — you'll
   eyeball the result"). Choose by the work, not the default: `outcome` for a
   result you can eyeball, `spec` when interfaces or data models need deciding
   first, `tdd` when each acceptance criterion should name the test that binds it
   before any code. The default is only your opening baseline; your read of the
   request wins the argument, and the user makes the call. The anchor sets how
   deep Phase 2 goes.

4. **Propose the acceptance.** Every criterion must be something the gate can
   MEASURE against the tree — a bullet the Adversary cannot measure is itself a
   finding, so do not write one.
   - **outcome:** three inferred acceptance bullets, each measurable.
   - **spec / tdd:** a decision register — IDs with a recommendation and
     rationale, ordered by blast radius (data models & interfaces first).

5. **Write the plan doc** at `docs/exec-plans/active/<YYYY-MM-DD>-<slug>.md`,
   where `<slug>` matches the branch name — the same location and titling the old
   harness used, so a repo's plan history stays unbroken. Open it with the bound
   status block from `.harness/lib/harness-markers.md` (read `<flavor>` from
   `.harness/harness.toml`, `<branch>` from `git branch --show-current`):

   ```yaml
   ---
   plan: <kebab-slug>
   harness: v2 · <flavor>
   branch: <branch>
   anchor: outcome|spec|tdd
   status: Draft
   next: <one line — the very next concrete action>
   gate: pending
   ---
   ```

   Follow it with the restated request, the blind-spot findings, and the
   acceptance (the three bullets, or the decision register). `status: Draft`
   because nothing is approved yet. Research and design are *inline sections*
   (`## Research`, `## Design`) added by later phases; promote to a `<slug>/`
   directory with sibling files only if the piece grows genuinely large.

6. **Confirm once, then step back.** Show the user the anchor, the acceptance,
   and — if the work turns on something unconfirmed (an unfamiliar API, a
   library's real behavior, prior art, how the existing code works) — a proposed
   research pass (Phase 1.5: cited `research/*.md` before design). Ask for
   approval or an override (they may override individual decision-register IDs,
   the anchor, or whether to research). Do not proceed past intake in the same breath.

## Rules

- This command ONLY does intake. It does not produce a design, write code, or
  run the gate.
- Do not auto-progress to the next phase — a `spec`/`tdd` anchor no human
  approved is fiction, so wait for explicit approval even under `auto`.
- Every acceptance bullet must be measurable, or it does not go in the doc.
- Status and every verdict live as bound markers in the plan doc — never a prose
  status line, never an external state file.
<!-- harness:region:end id=doc -->
