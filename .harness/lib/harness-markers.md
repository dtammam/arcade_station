<!-- harness:region:start id=doc -->
# Harness markers — the state-as-document spine

State lives in the working documents under `docs/exec-plans/`, never in an
external state file. For that to be trustworthy — and not rot the way a stale
`feature-state.json` or an unmoved "SHIPPED" plan does — every marker obeys a
**closed vocabulary** and **binds to the git ref it describes**. A checker
(`.harness/lib/check-markers.sh`) mechanically flags any marker that no longer matches.

## The status block (machine-readable spine)

Every working doc opens with YAML frontmatter:

```yaml
---
plan: <kebab-name>          # stable id; matches the branch name
harness: v2 · <flavor>      # which harness style produced this plan (from .harness/harness.toml)
branch: <branch>            # the branch this work lives on — /release cleans it up on close
anchor: outcome|spec|tdd    # the acceptance dial for this work
status: <lifecycle-state>   # from the closed set below
next: <one line>            # resume point — the very next concrete action (a cold session reads this first)
design: Approved <date> @<sha>     # present once design is approved (spec/tdd)
gate: <verdict>                    # see gate line below; "pending" until gated
---
```

## Location, naming, and shape

A piece of work is a **flat `docs/exec-plans/active/YYYY-MM-DD-<slug>.md`** by
default — the status block + acceptance + inline `## Research` / `## Design`
sections + `next:`. Same parent dirs as always, for unbroken history; it moves to
`docs/exec-plans/completed/` when `Shipped`.

- Only a genuinely large piece promotes to a `<slug>/` directory: `plan.md` (the
  spine that keeps the bound markers) plus `research/*.md` and `design.md`
  siblings. The tooling reads flat files and `<slug>/plan.md` alike, so the shape
  is a free choice per piece — most stay flat.
- `docs/exec-plans/tech-debt-tracker.md` is unchanged.

The `harness:` header tells a mixed repo which style produced each plan; `next:`
is the one-line resume point a cold session reads first. v1 plans have neither.

## Closed lifecycle vocabulary

A `status:` is exactly one of:

| State | Meaning | Lives in |
|-------|---------|----------|
| `Draft` | intake underway; nothing approved | `active/` |
| `Approved @<sha>` | plan/design approved at `<sha>` | `active/` |
| `Building` | implementation in progress | `active/` |
| `Gate:<verdict> r<n> @<sha>` | under or through review | `active/` |
| `Shipped <version>` | merged/released | **`completed/`** |
| `Parked(revisit: <why>)` | paused deliberately | `active/` (allowed) |
| `Abandoned(<why>)` | will not ship | **`completed/`** |

Prose status lines (`Status: ACTIVE. "pivot to sync."`) are forbidden — they are
exactly what rotted in the reference repos. If a state isn't in the table, it
doesn't exist; add to the table, don't freehand.

## The gate line

The gate writes its verdict INTO the plan, bound to the reviewed sha:

```
Gate: APPROVED r2 @7f3a2c1 — adversary, qa, security-brief
Gate: CHANGES r1 @a19c4d0 — adversary (see findings below)
```

- `r<n>` is the review round (the fix loop increments it).
- `@<sha>` is the commit reviewed. **Approval binds to that sha.** If the tree
  changes after it, the approval is stale until re-confirmed at the new sha.
- Close requires every *required* seat (per `.harness/scrutiny.toml`) APPROVED at the
  current sha. Never self-merge.

## What the checker enforces

`.harness/lib/check-markers.sh` scans each plan's SPINE (flat `active/*.md` and
`<slug>/plan.md` — never `research/*.md` or `design.md`) and flags, exiting
non-zero, on:

1. A terminal `status:` (`Shipped`/`Abandoned`) still under `active/` — read from
   the **frontmatter field only**, never prose that happens to start with the word.
2. An approval marker (`@<sha>`) whose `<sha>` is not in history, or that carries
   no `@<sha>` at all.
3. An `Approved` / `Gate: APPROVED @<sha>` where the reviewed CODE changed since
   `<sha>` (the plans dir is excluded, so a plan's own bookkeeping never counts;
   `Gate: CHANGES` lines are history and are not checked).
4. **Merged but not released** — an active plan whose latest `Gate: APPROVED @<sha>`
   is already an ancestor of the default branch while its status isn't terminal:
   the work shipped and `/release` never ran.
5. In `completed/` (checked for consistency, not staleness): a non-terminal
   status, or a frontmatter `gate:` that contradicts the body's last `Gate:` verdict.

Run it from the SessionStart hook (so a resumed session sees the true state) and
from `pre-push` (so stale approvals never leave the machine).

## Conventions that keep this honest

- **Commit before gating.** A bound verdict needs a real commit sha, so gate the
  committed work (a WIP commit is fine); the fix loop adds new commits rather
  than rewriting the approved one.
- **One piece, one plan directory.** A piece of work carries its bound markers in
  its own `plan.md`. An umbrella / roadmap doc holds status *pointers* — prose and
  links to the per-piece plans — never its own bound `Gate:` / `Approved`
  markers, so one piece's edits never touch another's approval.
- **Research is cited and can invalidate.** Findings live in `research/*.md` with
  their sources; a finding that contradicts an approved decision is surfaced to
  the user, never silently resolved. Write an artifact only for a decision-
  changing finding you can't cheaply re-derive — not a log of everything read.
<!-- harness:region:end id=doc -->
