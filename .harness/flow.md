<!-- harness:region:start id=doc -->
# The flow — five phases, sized by the anchor

One flow, not two. "Lean" and "Standard" are the same five phases at different
depths; the **anchor** decides the depth and the **auto** flag decides how often
you stop to ask. Build, Gate, and Close always run. Nobody hand-authors a
per-flavor flow — the depth is derived from the anchor.

The anchor is one of `outcome | spec | tdd` and is recorded in the plan's status
block and in `.harness/harness.toml [defaults]`. `auto` is a flag whose halts
are *derived from the anchor*: a `spec` or `tdd` anchor still forces the
design/plan approval halt even under `auto`, because an anchor no human approved
is fiction.

## Phase 1 — Intake & anchor  *(always)*

Read the request; do a blind-spot pass over the repo (the unknowns the user
hasn't thought to raise, while they're cheap). Then form an opinion: state the
project **default anchor** (`.harness/harness.toml`) next to the anchor you
**recommend for this request**, and when they differ, flag it and argue the
change with reasons — the default is only a baseline; your read of the work wins,
the user decides. Propose the acceptance for this work, and confirm once.

- **outcome:** three-bullet inferred acceptance, written to a plan doc under
  `docs/exec-plans/active/`. Confirm, then step back.
- **spec / tdd:** a decision register — IDs, recommendation, rationale, ordered
  by blast radius (data models & interfaces first). Approve the batch or override
  individual IDs.

Either way a **plan doc** now exists — flat `docs/exec-plans/active/<date>-<slug>.md`
carrying the bound status block, the acceptance, and a `next:` line. Research and
design live as *inline sections* of it by default; only a genuinely large piece
promotes them to sibling files in a `<slug>/` directory (`plan.md` + `research/`
+ `design.md`). Most work is one flat file. There is always a written acceptance
the gate can measure against; a bullet the Adversary cannot measure is itself a
finding — send it back here.

## Phase 1.5 — Research  *(when the work warrants it)*

Run this when the piece turns on something you have not confirmed — an
unfamiliar API, a library's real behavior, prior art, how the existing code
actually works. The agent decides whether it is needed, the same way it proposes
the anchor; a trivial change skips it.

- Record findings **inline in the plan under a `## Research` heading**, and **cite
  the source** for anything you did not derive yourself — a file path, a repo, a
  URL, the dependency's own code (never "the docs say"). Research exists to change
  decisions; stop when more reading would not change one. Only a large piece with
  several independent topics promotes them to sibling `<slug>/research/*.md` files.
- **Don't manufacture noise.** Write an artifact only for a finding that (a)
  changed a decision AND (b) can't be cheaply re-derived from the code or git
  history — a verified third-party behavior, a constraint, a ruled-out approach,
  the *why* behind a non-obvious choice. A trivial lookup, something obvious from
  the code, or a fact git already records does NOT get a file. Research captures
  what you had to find out, not a log of everything you read.
- **Invalidation rule (non-negotiable):** if research contradicts a decision the
  user already accepted, you MUST surface it and let them re-decide — never
  quietly resolve the contradiction yourself. They accepted that decision on
  different information.
- The research artifacts are referenced by the design and available to the gate,
  so the Adversary can check a claim against its cited source.

## Phase 2 — Design & plan  *(depth = anchor)*

- **outcome:** a short approach note in `plan.md`, or nothing. No formal gate.
- **spec:** write a **`## Design` section inline in the plan** — self-contained,
  with the sections the work needs (Overview, Requirements, Architecture,
  Components & Interfaces, Data Models, Error Handling, Testing Strategy). Approve
  it → `design: Approved <date> @<sha>`. Then `Step N:` items, **each with a Demo**
  (the observable behavior available once the step is done) → `status: Approved
  @<sha>`. Only a large design promotes to a self-contained `<slug>/design.md`.
- **tdd:** as spec, and each acceptance criterion names the test that will bind
  it before any code exists.

## Phase 3 — Build  *(always)*

You implement it. `tdd` writes the failing test first. Record progress in the
plan; log deviations under a `Deviations` heading. **A deviation that changes a
public interface, a data model, an acceptance criterion, or user-visible
behavior halts and returns to the user, whatever the involvement setting** — the
approval covered the design as written.

**Commit the work before gating** (staged by name; a WIP/checkpoint commit is
fine). The gate binds its verdict to a commit sha, and the reviewers mutate
against a committed tree — so a real commit must exist before Phase 4. This
commit is what ships; do not rewrite it after approval (that would void the
bound verdict). A fix in the gate's fix loop is a *new* commit, re-gated.

## Phase 4 — Gate  *(always)*

Run the gate protocol (`.harness/lib/gate-protocol.md`) against the committed
work — `<sha>` is `HEAD`. Seats are set by `.harness/scrutiny.toml` against the
diff — never by your judgment; you may only escalate. Each seat writes
`Gate: <verdict> r<n> @<sha> — <seat>`.

**The fix loop:** on `CHANGES`, fix, then re-engage the **same seat instances**
for a delta re-review; they re-verify their findings (and their own
prescriptions) against the new sha and re-verdict at `r<n+1>`. Repeat until every
required seat is `APPROVED` at the same final sha. Never self-merge.

## Phase 5 — Verify & close  *(always)*

**Passing the gate and merging is not shipping.** Until `/release` runs, the plan
still reads `Gate: APPROVED` in `active/` — wrong the moment the code lands on the
default branch. Do not stop after the merge; close it out. (The checker flags a
merged plan left in `active/`, but the point is to not create the drift at all.)

- **outcome:** you verify the result yourself.
- **spec / tdd:** verify against the acceptance criteria / the tests.

The work is already committed and gated (Phase 3/4). Now close it out: set the
plan's status to `Shipped <version>`, move the doc to `completed/`, and commit
that **as its own bookkeeping commit** — it touches only the plan doc, so it
does not change the reviewed code and the approval stays valid. Then run any
release ceremony and push. Run `.harness/lib/check-markers.sh` before push — a
stale approval never leaves the machine.

## The shape, at a glance

```
1 Intake&anchor ─▶ 2 Design&plan ─▶ 3 Build ─▶ 4 Gate ─▶ 5 Verify&close
                     (anchor)                    │  ▲
                                                 └──┘  fix loop: same seats
```
<!-- harness:region:end id=doc -->
