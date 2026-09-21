<!-- harness:region:start id=doc -->
# The gate protocol

The gate is a **protocol, not a fork**. Defining it as an interaction — not as a
Claude Code feature — is what lets it survive across tools and never silently
degrade into the builder reviewing itself.

## The contract

**Precondition — the work is committed.** The verdict binds to a commit sha and
the seats mutate against a committed tree, so commit the work (a WIP commit is
fine) before gating; the reviewed `<sha>` is `HEAD`. A fix in the loop is a *new*
commit, re-gated — never rewrite the approved commit, which would void the bound
verdict.

1. **Seat selection.** Evaluate `.harness/scrutiny.toml` against `git diff --name-only`
   (+ change class). The Adversary is always in the set. QA and Security-brief
   are added by the table; `force` rows union in and cannot be dropped. The
   builder may add seats (escalate); it may never remove one.
2. **The brief.** Each seat is engaged fresh with: `{branch, base sha, path to
   the plan/acceptance doc, named attack surfaces}`. The plan doc is the contract
   the diff is judged against — and may itself be wrong.
3. **Independent context.** Each seat reasons in a context the builder does not
   share. This is the whole value; a seat that runs in the builder's own head is
   not a seat.
4. **Verdict to the doc.** Each seat appends one line to the plan:
   `Gate: <APPROVED|CHANGES> r<n> @<sha> — <seat>`, approval bound to the sha.
5. **The fix loop.** On `CHANGES`, the builder fixes, then re-engages the **same
   seat instances** for a delta re-review (verify each finding against the fix
   commit, re-run distrusted checks, catch anything the fix introduced), and each
   re-verdicts at `r<n+1> @<new sha>`. Repeat until all required seats `APPROVED`.
6. **Close condition.** Every required seat `APPROVED`, each bound to the *same
   final sha*. Never self-merge; never approve on the builder's say-so.

## Tool implementations

The protocol is fixed; only step 2–3's mechanism varies per tool:

- **Claude Code** (native): the builder forks the seat agents in
  `.claude/agents/` (`adversary`, `qa`, `security-brief`) with the brief, and
  re-messages the same instances for the fix loop. Full fidelity.
- **Portable** (any tool): open a **second session**, run `/gate` with the
  brief; it plays the seats and writes the same verdict lines. Fidelity depends
  on the second session being genuinely independent (fresh context).
- **Degraded** (a tool with no independent context available): the gate
  **cannot be satisfied** — do not fake it by self-reviewing. Report that the
  gate is unavailable in this tool and that the change is unreviewed. "The
  builder reviewed its own work" is the one outcome the harness forbids.

## Why this and not a hard-coded fork

Generating `.cursor/` and `.codex/` files "from one source" projects the seats'
*prose* but not the *fork mechanism* — those tools have no forkable, context-
isolated subagents. Without this protocol boundary, the gate there would
silently collapse to self-review. With it, the multi-tool claim is honest: every
tool gets a real gate via a second session, and only Claude Code gets the
one-session convenience.
<!-- harness:region:end id=doc -->
