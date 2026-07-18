---
id: POC-001-WO-003
status: completed
owner: data_analytics_engineer
created: 2026-07-17
review_date: 2026-08-07
---

# Work Order: Evidence Sprint 001

## Objective

Run one bounded public-evidence stop-or-continue test for each of the eight shortlisted opportunities from Opportunity Scan 001 and record a reproducible disposition without making an operational recommendation.

## Context

### Facts

- Opportunity Scan 001 contains 29 opportunities and eight shortlist candidates.
- The Founder authorized the evidence sprint on 2026-07-17.
- The assessment method requires current administrative counterpositions and explicit evidence gaps.

### Assumptions

- A public desk test can determine whether an opportunity is sufficiently testable to continue.
- Some useful next tests will require controlled aggregates and therefore cannot be executed in this work order.

## Accountable Owner

`data_analytics_engineer` is the sole writing owner.

## Constraints

- Public, read-only evidence only.
- No external contact, restricted data, live-procurement intervention, publication, service change, or governance change.
- Separate facts, attributed positions, inferences, and research decisions.
- `continue` means authorize a more specific evidence test, not validate the hypothesis.
- `hold` means preserve the opportunity until a named dependency is met.
- `stop` means the current hypothesis should not consume further research capacity unless new evidence appears.

## Deliverables

- [x] Versioned sprint source ledger.
- [x] Eight machine-readable sprint decisions.
- [x] Human-readable evidence and decision portfolio.
- [x] Updated opportunity lifecycle states.
- [x] Dependency-free sprint validation.

## Acceptance Criteria

- [x] Exactly the eight shortlisted opportunities receive one disposition each.
- [x] Each decision records tested question, supporting evidence, counterevidence, limitations, and next action.
- [x] Every material factual claim points to a source-ledger entry.
- [x] No disposition is represented as an efficiency finding, savings estimate, or implementation approval.
- [x] Controlled-data and external-action dependencies remain explicit approval gates.

## Dependencies

- [Opportunity Scan 001](../../opportunity-scans/scan-001/opportunity-register.md)
- [Assessment method](../../assessment-method.md)

## Ownership Boundaries

| Path or system | Writer | Read-only contributors |
| --- | --- | --- |
| `initiatives/cologne-tax-improvements/evidence-sprints/sprint-001/` | `data_analytics_engineer` | research, finance, product, technology, legal-risk, and assurance roles |
| Opportunity Scan 001 lifecycle fields | `data_analytics_engineer` | none |
| Public websites and documents | none | public read-only access |

## Approval Level

`founder-approval-required`

Founder approval remains required before external contact, publication, controlled-data access, governance or service changes, or interference with a live procurement.

## Evidence and Closure

- [Sprint results](sprint-results.md)
- [Decision register](decisions.json)
- [Source ledger](sources.md)
- [Validator](validate_sprint.py)

The sprint is complete when validation passes. Every `continue` item still requires a new scoped work order before its next test.

