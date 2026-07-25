# ADR-0001: Record architecture decisions

- **Status:** Accepted
- **Date:** YYYY-MM-DD
- **Owners:** <team or individual>

## Context

We need a durable record of important architectural decisions, including
their context, trade-offs and consequences. Commit history alone does not
explain why an option was selected.

## Decision

We will record significant architectural decisions as Markdown files under
`docs/decisions/`.

A decision requires an ADR when it affects one or more of:

- public interfaces
- component boundaries
- data ownership or retention
- security and trust boundaries
- model, tool or orchestration strategy
- operational responsibilities
- major dependencies
- evaluation or release policy

## Alternatives considered

### Rely only on pull requests

Rejected because pull requests contain implementation discussion but do not
provide a stable, concise architecture record.

### Maintain decisions in an external wiki

Rejected because the records could drift from the source revision they
describe.

## Consequences

### Positive

- Decisions are versioned with the code.
- Agents and humans can discover relevant constraints.
- Superseded decisions remain traceable.

### Negative

- Engineers must maintain the records.
- Outdated ADRs can mislead readers if their status is not updated.

## Validation

During review, verify that architectural changes add or update an ADR.
