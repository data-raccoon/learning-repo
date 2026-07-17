---
id: POC-001-SCAN-001-REGISTER
status: completed
owner: data_analytics_engineer
created: 2026-07-17
review_date: 2026-08-07
---

# Opportunity Scan 001

## Result

The first scaled search produced **29 testable opportunities** from 18 versioned public evidence objects. Eight entered Evidence Sprint 001; seven now have status `evidence_continue` and one has status `evidence_hold`. These are research hypotheses, not findings of inefficiency, savings estimates, recommendations, or a ranking of municipal functions.

The canonical records are in [the machine-readable register](opportunities.json), governed by the [schema](schema.md) and [source ledger](sources.md).

## Portfolio view

| ID | Opportunity | Domain | Evidence | Decision | Control | Test cost | Next test in one line |
| --- | --- | --- | --- | --- | --- | --- | --- |
| OPP-001 | Investment business-case thresholds | Finance | medium | high | high | low | Test documented option comparison across 30 planned investments |
| OPP-002 | Capital-plan delivery realism | Capital | medium | high | high | medium | Build a three-year plan-to-actual investment cohort |
| OPP-003 | Credit-portfolio risk visibility | Treasury | medium | medium | high | low | Map reports, recipients, sensitivities, and unresolved questions |
| OPP-004 | Evidence-led employee mobility | Workforce | medium | medium | high | low | Compare aggregate barriers at three service locations |
| OPP-005 | Employee parking portfolio | Assets | medium | medium | high | medium | Inventory cost, access, occupancy, exceptions, and alternative use |
| OPP-006 | Avoided service trips | Access | low | medium | high | medium | Compare completion and repeat contact for five services |
| OPP-007 | School IT harmonization | Education IT | medium | medium | medium | medium | Cluster software and support demand across a safe school sample |
| OPP-008 | Electronic-file realized benefits | Digitization | medium | high | high | medium | Compare three workflows before and after rollout |
| OPP-009 | Process-improvement portfolio | Operations | medium | high | high | low | Test ten project proposals against common evidence fields |
| OPP-010 | Risk-based IT audit capability | Assurance | medium | medium | high | low | Map digital risks against audit skills and coverage |
| OPP-011 | Major-construction governance | Construction | medium | high | high | medium | Compare governance evidence and outcomes for 15 projects |
| OPP-012 | Risk-to-continuity closure | Resilience | medium | medium | high | medium | Map ten essential services to hazards and dependencies |
| OPP-013 | Crisis on-call coverage | Resilience workforce | low | medium | high | medium | Compare alert demand, workload, response, and redundancy |
| OPP-014 | Youth-welfare reimbursement control | Youth finance | medium | high | high | medium | Build a privacy-safe closed-claim cohort |
| OPP-015 | Youth-welfare case-system interface | Youth process | medium | medium | medium | medium | Map one high-volume cross-system handoff |
| OPP-016 | District youth-welfare controlling | Youth management | medium | medium | medium | medium | Test comparability of an aggregate district cohort |
| OPP-017 | Embedded youth-welfare controls | Youth assurance | medium | medium | high | medium | Classify corrections and near misses by control point |
| OPP-018 | Public-health finance and service control | Health | medium | high | high | medium | Reconcile demand, service, workforce, and cost for three services |
| OPP-019 | Public-health provider outcomes | Health commissioning | low | medium | high | medium | Compare purpose, burden, reach, outcomes, and renewal use |
| OPP-020 | Public-health workforce planning | Health workforce | medium | high | medium | medium | Build workload scenarios for five critical role families |
| OPP-021 | Earlier permit consultation | Building control | medium | high | high | medium | Test milestone changes before and after the two-stage review |
| OPP-022 | Permit-backlog capacity allocation | Building control | medium | high | high | medium | Build an age-stage-complexity backlog funnel |
| OPP-023 | Small-area childcare matching | Childcare | medium | high | medium | medium | Pilot demand, staffed places, access, and future supply in three areas |
| OPP-024 | Heat-action targeting and reach | Climate health | medium | high | medium | medium | Map vulnerability, measures, reach, and access at safe geography |
| OPP-025 | Cycling-intervention evaluation | Mobility | medium | medium | medium | medium | Compare five interventions with normalized outcomes |
| OPP-026 | Transit compensation-to-quality | Public transport | medium | medium | medium | medium | Reconcile three annual reports into stable measures |
| OPP-027 | Municipal-holdings exposure map | Holdings | medium | high | medium | high | Create a scope bridge for the six largest exposures |
| OPP-028 | Integration-service outcome learning | Integration | low | medium | medium | medium | Map program purpose, reach definition, referrals, cost, and evidence |
| OPP-029 | Procurement-to-performance register | Procurement | low | high | high | medium | Reconstruct five closed contract lifecycles after award |

The dimensions remain separate. They are not added, weighted, or converted into a score.

## Recommended first evidence-sprint queue

The queue deliberately spans financial governance, administration, statutory services, spatial planning, and procurement. Selection means **investigate next**, not implement.

The queue was executed in [Evidence Sprint 001](../../evidence-sprints/sprint-001/sprint-results.md). The table below preserves the original selection rationale and stop conditions.

| Sequence | Opportunity | Why it enters the queue | Earliest stop condition |
| --- | --- | --- | --- |
| 1 | OPP-001 Investment business-case thresholds | High control, low test cost, current budget applicability | Existing binding thresholds and proportionate evidence already operate consistently |
| 2 | OPP-008 Electronic-file realized benefits | The city's December 2025 completion milestone is now testable | Comparable pre/post workflow data cannot be obtained without disproportionate monitoring |
| 3 | OPP-014 Youth-welfare reimbursement control | Directly joins service, finance, timeliness, and data quality | A current governed lifecycle already gives complete, timely reconciliation |
| 4 | OPP-018 Public-health finance and service control | The city response left finance integration unresolved | Service and finance scopes cannot be reconciled at a useful aggregate level |
| 5 | OPP-021 Earlier permit consultation | A stated process change supports before/after verification | Milestone capture is not comparable or the change has not reached stable operation |
| 6 | OPP-023 Small-area childcare matching | Strong positive citywide result creates a useful hidden-variation test | Staffed capacity and demand cannot be compared safely or consistently |
| 7 | OPP-002 Capital-plan delivery realism | Reusable across the investment portfolio and grounded in plan/actual data | Variance causes are not recoverable or readiness does not improve forecast error |
| 8 | OPP-029 Procurement-to-performance register | Foundational join for future scale across many purchased services | Stable identifiers cannot connect closed procurement, finance, and service records |

## Search-mechanism learning

### What worked

- Assurance findings generated specific control hypotheses quickly.
- The city's formal response prevented outdated recommendations from being treated as current facts.
- Financial, workforce, spatial, service, and procurement sources turned single-source findings into falsifiable joins.
- Positive signals, such as childcare expansion, digital rollout, and cycling counts, produced improvement questions without presuming failure.

### Bottlenecks exposed

- Public documents often describe plans and aggregate achievements but not stable transaction-to-outcome joins.
- Common identifiers across budget, procurement, contract, invoice, asset, service, and decision records remain the central scaling dependency.
- Several high-value tests require controlled aggregates; public evidence is enough to frame them but not to complete them.
- Audit evidence is unusually productive but could bias the portfolio toward recently audited functions. Future waves need independent anomaly generation from budgets, accounts, procurement, and operational series.

## Guardrails for the queue

- No external contact, public claim, live-procurement intervention, restricted-data access, or service change follows from this scan.
- Each evidence sprint must receive its own bounded work order and case dossier if accepted.
- A failed recommendation-readiness gate yields a data or research recommendation, not an operational action.
- Existing cases remain separate: adjacency is shown in the machine register through `related_case`.
