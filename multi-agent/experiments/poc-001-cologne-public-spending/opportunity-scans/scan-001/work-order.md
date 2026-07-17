---
id: POC-001-WO-002
status: completed
owner: data_analytics_engineer
created: 2026-07-17
review_date: 2026-08-07
---

# Work Order: Opportunity Scan 001

## Objective

Produce between 10 and 30 distinct, traceable Cologne public-value opportunities by joining complementary public data sources, with every opportunity framed as a testable hypothesis rather than a finding.

## Context

### Facts

- POC-001 has five assessed calibration cases and a governed assessment method.
- The intended mechanism must later support hundreds or thousands of candidates.
- The source inventory covers financial plans and actuals, assurance, procurement, operations, assets, spatial context, decisions, and investigative leads.
- The Founder authorized the first scaled search wave on 2026-07-17.

### Assumptions

- A structured register plus human-readable portfolio view is sufficient for the first scalability test.
- Public metadata and reports can generate useful hypotheses without person-level data or external contact.
- Full case dossiers would be premature for most candidates in this wave.

## Accountable Owner

`data_analytics_engineer` is the sole writing owner.

## Constraints

- Artifacts use English and neutral language.
- Produce opportunities, not waste findings, allegations, rankings, or promised savings.
- Exclude the five existing calibration cases as primary outputs.
- Every opportunity must join at least two materially distinct evidence objects and identify a cheap next test.
- Preserve source dates, counterpositions, limitations, and uncertainty.
- Do not contact external parties, access restricted records, influence live procurement, or publish results.
- No composite opportunity score or hidden weighting is allowed.

## Deliverables

- [x] A versioned source ledger for the scan.
- [x] A machine-readable opportunity register with a stable schema.
- [x] A human-readable portfolio view containing 10 to 30 opportunity cards.
- [x] A transparent shortlist for later evidence sprints.
- [x] Dependency-free validation for count, identifiers, required fields, source joins, and guardrails.

## Acceptance Criteria

- [x] The register contains between 10 and 30 unique opportunities.
- [x] Every opportunity has at least two source references, a hypothesis, a caveat, and a next test.
- [x] Every referenced source exists in the scan source ledger.
- [x] Existing cases are linked when adjacent, not silently duplicated.
- [x] Shortlisting uses separate observable dimensions rather than a composite score.
- [x] No opportunity is represented as an established inefficiency or operational recommendation.

## Dependencies

- [Assessment method](../../assessment-method.md)
- [Company source inventory](../../../../company/data-source-inventory.md)
- Public source availability and stable source URLs

## Ownership Boundaries

| Path or system | Writer | Read-only contributors |
| --- | --- | --- |
| `experiments/poc-001-cologne-public-spending/opportunity-scans/scan-001/` | `data_analytics_engineer` | research, finance, product, technology, legal-risk, and assurance roles |
| Existing case dossiers and source contracts | existing owners | `data_analytics_engineer` |
| External systems and publications | none | public read-only access only |

## Approval Level

`founder-approval-required`

Founder approval is required before external contact, publication, restricted-data access, intervention in a live procurement, or advancing a candidate into an operational decision.

## Evidence and Closure

- [Source ledger](sources.md)
- [Machine-readable register](opportunities.json)
- [Portfolio view](opportunity-register.md)
- [Validation script](validate_scan.py)

The scan closes when the artifacts validate. Selection of evidence sprints remains a separate Founder decision.

