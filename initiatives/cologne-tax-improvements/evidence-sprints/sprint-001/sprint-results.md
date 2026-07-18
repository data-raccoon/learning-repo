---
id: POC-001-EVS-001-RESULTS
status: completed
owner: data_analytics_engineer
created: 2026-07-17
review_date: 2026-08-07
---

# Evidence Sprint 001 Results

## Outcome

Seven opportunities continue to a more specific evidence test; one is held until current benefit evidence or approved controlled aggregates become available. No opportunity has passed the recommendation-readiness gate.

| Opportunity | Decision | Confidence | What the sprint established | Required next evidence |
| --- | --- | --- | --- | --- |
| OPP-001 Investment appraisal thresholds | `continue` | medium | The audited control question is real and public decision files can contain economic calculations; consistency and current thresholds remain unknown | Stratified 30-decision public sample |
| OPP-002 Capital-plan realism | `continue` | high | Public accounts expose sufficient plan, actual, carryover, and cause detail for a longitudinal cohort | Three-year measure cohort and cause taxonomy |
| OPP-008 Electronic-file benefits | `hold` | high | Rollout intent, scale, and local adoption are documented; current citywide realized benefits are not | Current implementation report or approved aggregate workflow measures |
| OPP-014 Youth reimbursement control | `continue` | medium | The audit gap, planned revenue module, and financial context justify an implementation-status test | Approved aggregate closed-claim cohort |
| OPP-018 Health service-finance control | `continue` | medium | Finance integration was unresolved and a March 2026 organizational-review milestone is now testable | Current status plus three-service aggregate reconciliation |
| OPP-021 Earlier permit consultation | `continue` | medium | A specific two-stage process change and milestone-capture plan exist | Comparable de-identified before/after process cohorts |
| OPP-023 Small-area childcare matching | `continue` | high | A public supply-and-context prototype is feasible below city level | Current extracts plus governed staffed-capacity and demand gaps |
| OPP-029 Procurement-performance spine | `continue` | high | Public notices and awards provide a workable lifecycle spine; realized performance remains unjoined | Five closed procurements, with non-public fields explicitly unknown |

`Continue` authorizes only the named next evidence test. `Hold` preserves the hypothesis without consuming active research capacity.

## Material findings by test

### OPP-001 — investment appraisal thresholds

- **Fact:** gpaNRW found an appraisal guide but no mandatory value threshold at the audited point (`ES1-S01`).
- **Counterevidence:** a 2025 decision agenda includes explicit economic calculations, a photovoltaic calculation, and audit-office review for a material housing project (`ES1-S06`).
- **Inference:** the useful question is consistency and proportionality across the portfolio, not whether Cologne ever performs appraisals.
- **Decision:** `continue` with a stratified public sample. No governance recommendation is ready.

### OPP-002 — capital-plan delivery realism

- **Fact:** the 2023 accounts report EUR 253.9 million of investment-payment authorizations carried into 2024, compared with EUR 295.6 million carried into 2023 (`ES1-S04`).
- **Fact:** the 2024 draft contains measure-level plan, adjusted plan, actual, carryover, and explanations including project-delay examples (`ES1-S05`).
- **Counterevidence:** gpaNRW recognizes both the reduction in carryovers and Cologne's comparatively strong drawdown of available investment funds (`ES1-S01`).
- **Decision:** `continue`; analyze forecast error and legitimate causes, not carryover as a negative label.

### OPP-008 — electronic-file realized benefits

- **Fact:** the rollout was designed for more than 14,600 users by the end of 2025 and claimed benefits such as search, workflow, access, and shorter processing (`ES1-S07`).
- **Fact:** at least one department reported adoption in 2024 (`ES1-S08`).
- **Gap:** the sprint found no current public, comparable citywide before/after evidence for processing time, rework, search, storage, support, or service quality.
- **Decision:** `hold`; deployment must not be reported as realized value.

### OPP-014 — youth-welfare reimbursement control

- **Fact:** gpaNRW found that reimbursement cases and revenue could not be evaluated by type (`ES1-S01`).
- **Attributed position:** the city planned to introduce the LMG revenue-management module (`ES1-S02`).
- **Context:** planned economic-youth-welfare expenditure increases materially while planned revenue remains EUR 33.5 million annually through 2029 (`ES1-S09`).
- **Limitation:** stable planned revenue does not demonstrate missed claims or recoverable savings.
- **Decision:** `continue` with implementation status and an approved aggregate closed-claim cohort.

### OPP-018 — public-health finance and service control

- **Attributed position:** the city said specialist controlling was under construction, financial integration was unresolved, SAP Analytics Cloud was being introduced, and an organizational review would run through March 2026 (`ES1-S02`).
- **Gap:** the sprint found no public closure evidence for those milestones.
- **Limitation:** absence from public search does not establish non-implementation.
- **Decision:** `continue` with a status check and a three-service aggregate reconciliation; no service-performance conclusion is ready.

### OPP-021 — earlier permit consultation

- **Attributed position:** the city described a two-stage internal note intended to start consultation a few days after receipt and planned completeness-date capture (`ES1-S02`).
- **Context:** 2025 produced 4,623 completed homes but 2,323 permitted homes, while the 2024 digital baseline showed partial digital intake (`ES1-S10`, `ES1-S11`).
- **Limitation:** housing output and permit counts do not isolate internal cycle time, applicant completeness, demand, or market conditions.
- **Decision:** `continue` only at process-cohort level.

### OPP-023 — small-area childcare matching

- **Fact:** Cologne reports 14,708 U3 and 32,210 older-child places for 2025/2026 and citywide target achievement (`ES1-S12`).
- **Feasibility evidence:** municipal monitoring documentation supports annual childcare indicators below city level; LITTLE BIRD exposes facility and offer geography (`ES1-S13`, `ES1-S14`).
- **Counterevidence:** not all providers participate in the portal, and nominal supply does not establish staffed availability, unmet demand, hours, inclusion fit, or actual travel.
- **Decision:** `continue` with a public supply-side prototype and explicit controlled-data gaps.

### OPP-029 — procurement-to-performance spine

- **Fact:** the procurement platform exposes current and awarded objects with identifiers, procedure, subject, supplier, term, quantities, ceilings, criteria, and e-invoice metadata where published (`ES1-S15` to `ES1-S17`).
- **Gap:** price, invoices, realized quantity, service levels, modifications, and renewal rationale are not consistently public.
- **Inference:** a public lifecycle spine is feasible; the performance join remains a data dependency, not evidence of poor management.
- **Decision:** `continue` with five closed procurements. Live procedures remain out of scope.

## Portfolio decision

The next queue should be sequenced by data boundary:

1. **Public-only prototypes:** OPP-002, OPP-001, OPP-023, and OPP-029.
2. **Controlled-aggregate proposals requiring approval:** OPP-014, OPP-018, and OPP-021.
3. **Hold:** OPP-008 until a current public report or approved measurement basis exists.

This ordering maximizes learning before requesting access to sensitive or non-public evidence.

## Approval boundary

No external communication, publication, restricted-data access, live-procurement analysis, or operational change was performed. The three controlled-aggregate tests require separate Founder approval and data-owner, legal, privacy, and domain review.

