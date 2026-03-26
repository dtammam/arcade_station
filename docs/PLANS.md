# Plans

Plans are first-class artifacts. The product-manager agent creates them during
Discovery. The principal-engineer agent fills in the Design section. The
engineering-manager agent manages their lifecycle.

## Execution plan template

Create: `docs/exec-plans/active/<yyyy-mm-dd>-<short-title>.md`

Skeleton:

```markdown
# [Feature Name]

## Goal

[One sentence]

## Scope

[What's in]

## Out of scope

[What's explicitly out]

## Constraints

[Non-negotiable boundaries]

## Acceptance criteria

- [ ] [Criterion 1 — must be testable]
- [ ] [Criterion 2]

## Design

(Filled by principal-engineer agent)

### Approach

### Component changes

### Data model changes

### API changes

### Alternatives considered

### Risks and mitigations

### Performance impact

## Task breakdown

(Filled by engineering-manager agent)

## Progress log

(Append-only, dated entries)

## Decision log

(Append-only, dated entries)
```

## Plan lifecycle

1. Created in `active/` by the product-manager agent during Discovery
2. Design section filled by the principal-engineer agent
3. Task breakdown added by the engineering-manager agent
4. Progress log updated during Implementation
5. Acceptance criteria checked by the product-manager agent during Acceptance
6. Moved to `completed/` by the engineering-manager agent when Done
