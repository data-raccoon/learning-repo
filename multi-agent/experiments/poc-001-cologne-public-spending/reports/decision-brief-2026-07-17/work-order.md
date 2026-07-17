---
id: POC-001-WO-004
status: completed
owner: operations_knowledge
created: 2026-07-17
review_date: 2026-08-07
---

# Work Order: German Decision Brief

## Objective

Create one internally distributable German PDF that presents all five assessed cases and all 29 opportunity-scan candidates to a human decision-maker, with evidence maturity, uncertainty, decisions, and approval boundaries visible.

## Context

### Facts

- POC-001 contains five case dossiers, 29 opportunity records, and eight completed evidence-sprint decisions.
- The Founder requested a German PDF for a human decision-maker on 2026-07-17.
- Repository source artifacts remain canonical; the PDF is a dated synthesis.

### Assumptions

- The recipient needs a concise portfolio view plus enough case detail to choose the next research work.
- Internal presentation does not authorize external publication.

## Accountable Owner

`operations_knowledge` is the sole writing owner for the report directory.

## Constraints

- German presentation language as explicitly requested by the Founder.
- Label facts, attributed positions, inferences, open hypotheses, and recommendations distinctly.
- Do not introduce savings estimates, blame, waste rankings, or operational approvals.
- Preserve the approval gates for external communication, controlled data, procurement, spend, governance, and service changes.
- Use only existing repository evidence and current official sources already captured in the source ledgers.

## Deliverables

- [x] German LaTeX source suitable for deterministic local rendering.
- [x] German PDF decision brief.
- [x] Quality-gate record with integrity and content checks.

## Acceptance Criteria

- [x] All five assessed cases are represented.
- [x] All 29 opportunities are represented exactly once in the portfolio sections.
- [x] All eight evidence-sprint dispositions are represented.
- [x] The PDF is non-empty, opens as a valid PDF, and has a plausible page count.
- [x] Internal-only and approval boundaries are visible.
- [x] Material claims retain links or source references.

## Dependencies

- [Case index](../../cases/README.md)
- [Opportunity Scan 001](../../opportunity-scans/scan-001/opportunity-register.md)
- [Evidence Sprint 001](../../evidence-sprints/sprint-001/sprint-results.md)

## Ownership Boundaries

| Path or system | Writer | Read-only contributors |
| --- | --- | --- |
| `experiments/poc-001-cologne-public-spending/reports/decision-brief-2026-07-17/` | `operations_knowledge` | finance, data, legal-risk, and assurance roles |
| Canonical cases, opportunities, and evidence decisions | existing owners | `operations_knowledge` |
| External sources | none | public read-only use |

## Approval Level

`founder-approval-required`

The PDF is approved for internal review only. External distribution or publication requires explicit Founder approval and legal-risk review.

## Evidence and Closure

- [LaTeX source](entscheidungsvorlage-koeln.tex)
- [PDF](entscheidungsvorlage-koeln.pdf)
- [Quality gate](quality-gate.md)
