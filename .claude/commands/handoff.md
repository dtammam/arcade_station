<!-- harness:region:start id=doc -->
# /handoff — a capsule for a fresh session

Produce a self-contained handoff so the **next** session cold-starts with zero
bleed from this one. Its whole job is to make a clean break *safe*: capture what
the next session needs, persist the resume point in the plan, and then tell you to
actually stop and start fresh.

## When to use it

When this session is running long, context is drifting, or you're about to stop.
The point is to **end this session** — not to keep working here. If you find
yourself continuing in a session that's already drifted, that's the signal to run
`/handoff` and cut over.

## Procedure

1. **Read the real state — don't reconstruct it from memory.** The active plan
   (`docs/exec-plans/active/…` — its status block: `plan`, `branch`, `anchor`,
   `status`, `gate`, `next`), `git branch --show-current`, `git log --oneline -5`,
   and `git status` for uncommitted work.

2. **Persist the resume point.** Update the plan's `next:` line to the true, single
   next concrete action — the file/function/command to touch next. This is the
   durable anchor: it survives even if the capsule below is never pasted, and it's
   the first thing the next session's SessionStart hook surfaces.

3. **Emit the capsule** — a self-contained block the next session can act on with
   NONE of this session's memory. Keep it tight, and point at the **minimum** docs,
   never the whole tree (context is the budget):

   > **Objective** — the one-line goal of this piece of work.
   > **Where it stands** — branch, status, gate verdict; what's committed vs not.
   > **Decisions that constrain the next step** — only the few that would be
   >   expensive to relitigate; cite the plan/design section, don't restate it.
   > **Done** — what's finished and verified (not "should work").
   > **Next** — the single concrete next action (matches the plan's `next:`).
   > **Gotchas / do NOT** — traps, dead ends, environment quirks that bit you.
   > **Read only these** — the active plan doc, `AGENTS.md`, and at most the one or
   >   two files the next step touches. Not the whole repo.

4. **Nudge the cut-over.** End your output with, literally:
   *"Start a new session and paste the capsule above. Don't continue in this one —
   a fresh context is the point."*

## Rules

- The capsule MUST be self-contained: a cold agent acts from it alone, with no
  access to this conversation.
- Point at the **minimum** set of docs; never "read everything."
- Read-only except for updating the plan's `next:` line.
- `/handoff` hands off — it does not do the work. Don't slip into building here.
<!-- harness:region:end id=doc -->
