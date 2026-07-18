---
id: POC-001-CASE-005
status: recommendation_draft
owner: data_analytics_engineer
created: 2026-07-17
review_date: 2026-08-07
---

# Case Assessment: Municipal Building Decarbonization Portfolio

## Identity and status

- **Review status:** `recommendation_draft`
- **Accountable analyst:** `data_analytics_engineer`
- **Decision owner:** City of Cologne building portfolio and long-term financial planning owners, with climate governance; exact decision rights to be confirmed.
- **Last evidence update:** 2026-07-17.
- **Publication status:** `internal_only`.

## Originating signal

- **Sources and roles:** gpaNRW Cologne audit, `official_assurance`; City response and climate policy, `primary_authoritative`; 2024 Energy Report, `primary_observation` and `primary_authoritative` report.
- **Signal:** The gpaNRW states that the current financial planning does not fully reflect the funding required to achieve a greenhouse-gas-neutral municipal building stock. The City evaluates energy measures within available financial frameworks, while current public energy data already allow building-level prioritization to begin.
- **Why it warrants review now:** The 2035 target is time-bound, building interventions have long lead times and lock-in effects, and Cologne expects a large competing investment programme. Delayed portfolio prioritization can increase cost even when individual projects are reasonable.

## Public purpose and baseline

- **Purpose:** Deliver public services in reliable buildings while reducing lifecycle energy cost and greenhouse-gas emissions in line with adopted goals.
- **Target:** Cologne aims for greenhouse-gas neutrality by 2035. The citywide target is broader than the municipal building portfolio and must not be conflated with it.
- **Existing governance:** The City has an action plan, climate-monitoring platform, energy-management concept, annual energy reports, building project standards, and investment controlling.
- **Existing results:** The City reports for approximately 500 buildings since 2005 a 22 percent reduction in electricity use, 38 percent reduction in carbon dioxide emissions, 34.5 percent heating-cost savings, 34.8 percent water-use reduction, and 23.1 million kWh of solar electricity generated. Baselines and portfolio coverage must be retained when using these aggregate figures.
- **Investment context:** gpaNRW reports that Cologne expects annual investments of approximately EUR 700 million to EUR 800 million in coming years across its broader portfolio, creating financing and delivery competition.

## Current state

- **Funding gap:** gpaNRW concludes that current budget planning does not fully reflect the funding needed for greenhouse-gas neutrality in the City's own buildings.
- **City response:** Energetic measures for buildings in the Building Management special fund are evaluated and included within feasible financial frameworks. This describes a budget-constrained process but does not publicly quantify the target-consistent funding gap.
- **Monitoring response:** The City stated that expanded impact indicators and measurement were planned through Q1 2026. Current completeness and use in investment decisions require verification.
- **Asset evidence:** The 2024 Energy Report contains object-level consumption indicators, comparison values, energy carriers, floor areas, and photovoltaic potential for many buildings.
- **Missing decision layer:** No reviewed public source provides one reconciled portfolio containing asset condition, mandatory maintenance, intervention options, capital and operating cost, grants, carbon effect, service disruption, readiness, and delivery capacity.

## Source coverage

| Perspective | Source used | Evidence role | Coverage status | Temporal and scope fit | Gap or follow-up |
| --- | --- | --- | --- | --- | --- |
| Target, governance, and financial context | City climate policy and gpaNRW audit | `primary_authoritative`, `official_assurance` | `covered` | Strong for stated target and audit conclusion | Quantify municipal-building target path and funded gap |
| Operational energy and asset observations | Energy Report 2024 | `primary_observation` | `covered` | Strong public starting point; some observations refer to 2023 | Normalize coverage, quality flags, and current values |
| Climate progress | Cologne climate monitoring | `primary_authoritative`, `primary_observation` | `not_covered` in extraction | Relevant current platform | Export measure status, targets, and actual effects |
| Procurement lifecycle | Cologne, NRW, and TED notices | `primary_authoritative` | `not_covered` | Needed for delivery readiness and realized price | Link projects, awards, changes, and completion |
| Condition, capex, maintenance, grants, and capacity | Controlled asset and investment records | `primary_observation` | `unavailable` | Essential for portfolio choice | Obtain non-personal governed extract after approval |
| Regional outcome context | INKAR | `official_statistical_context` | `covered_with_limits` | Useful for citywide trends and peers, too coarse for asset priority | Keep separate from municipal building attribution |
| Building users and service operators | None | `stakeholder_account` | `not_covered` | Needed for disruption and service criticality | Use existing service plans or approved engagement |

## Claim-evidence matrix

| Claim ID | Claim | Type | Supporting evidence | Contradiction or limit | Confidence | Remaining test |
| --- | --- | --- | --- | --- | --- | --- |
| CLM-001 | Current planning did not fully reflect the funding needed for a neutral own-building stock in the audit period | `attributed_position` | gpaNRW finance and buildings sections | Current 2026 planning may have changed | `high` historically | Reconcile target path with current plan |
| CLM-002 | Cologne has useful object-level energy and photovoltaic data | `fact` | Energy Report 2024 | Coverage, lag, and missing values vary | `high` | Create quality and coverage report |
| CLM-003 | More climate spending alone would achieve the target efficiently | `assumption` | None | Delivery capacity, asset lifecycle, dependencies, and marginal cost unknown | `low` | Costed and capacity-constrained portfolio |
| CLM-004 | Combining energy work with mandatory maintenance can reduce lifecycle cost | `inference` | General asset-planning logic | Asset-specific timing and scope unavailable | `medium` | Join condition and intervention records |
| CLM-005 | The 2035 target is achievable for the municipal building portfolio | `assumption` | Citywide strategy says neutrality is possible | Own-building pathway, residual emissions, finance, and capacity not reconciled | `low` | Scenario and feasibility analysis |

## Positions and affected parties

- **City position:** Existing measures are evaluated and included within possible financial frameworks; monitoring supports adjustment.
- **gpaNRW position:** Quantify the financial requirement and include it in long-term planning; act early or adjust the target if the pathway becomes infeasible.
- **Affected parties:** Schools, cultural and social services, staff, facility users, neighbourhoods, maintenance and construction providers, taxpayers, and future budget holders.
- **Distributional consideration:** Investment priority must include service criticality and user vulnerability, not only carbon or financial return.

## Cause and controllability analysis

- **Observed symptom:** Gap between adopted target, fully quantified funding need, funded plan, and publicly visible delivery pathway.
- **Plausible causes:** Incomplete asset condition and intervention data, volatile prices and grants, competing statutory investment, scarce planning and construction capacity, heat-network dependencies, long building lead times, and portfolio fragmentation.
- **Alternative explanation:** Detailed internal planning may exist but not be visible in reviewed public evidence.
- **Controllable now:** Common portfolio schema, target pathway, scenario budgets, decision rules, coupling with maintenance, readiness gates, procurement linkage, capacity planning, and transparent annual gap reporting.
- **Not established:** The correct total budget, which building should be renovated first, or whether the 2035 date should change.

## Options

| Option | Fiscal and lifecycle effect | Service and outcome effect | Constraints | Risks | Reversibility |
| --- | --- | --- | --- | --- | --- |
| Continue within annual feasible budgets | Avoids explicit new commitment | Incremental progress | May not match target path | Hidden deferral cost and missed windows | High annually |
| Allocate a top-down climate envelope | Creates funding certainty | Faster activity | Weak asset evidence and capacity | Spend-first behaviour and low-value projects | Medium |
| Build a costed, capacity-constrained portfolio | Analytical effort before major allocation | Aligns carbon, condition, service, and readiness | Data integration and ownership | Delayed decisions if over-engineered | High |
| Prioritize only lowest cost per tonne | Potential efficient carbon reduction | May neglect service and condition | Metric uncertainty | Distributional and resilience harm | High before commitment |
| Revise target or scope now | Reduces apparent funding pressure | Changes policy expectation | Political approval | Premature retreat without quantified pathway | Low after decision |

## Recommendation

### Preliminary assessment

The City has meaningful energy data, governance, and demonstrated reductions, but the public evidence does not show one target-consistent, funded, and delivery-feasible municipal building portfolio. The immediate recommendation is better capital allocation, not an unqualified increase or reduction in spending.

### Recommended action

Create a versioned building-decarbonization portfolio that joins public energy observations with condition, mandatory maintenance, intervention options, capital and lifecycle cost, grants, annual savings, carbon effect, service criticality, disruption, dependencies, readiness, and delivery capacity.

Produce three scenarios on a common price and carbon basis:

1. currently funded and deliverable;
2. realistic finance- and capacity-constrained pathway;
3. target-consistent 2035 pathway.

Report the gap between them and group interventions into no-regret operational measures, maintenance-coupled measures, and strategic deep renovations. Use marginal abatement cost as one input, not the sole ranking rule. Require project-level business cases only after portfolio fit and readiness are established.

- **Expected effect:** Direct limited capital and delivery capacity to measures with explicit lifecycle, service, and climate value; expose infeasible assumptions early.
- **Financial effect:** Unknown until current investment, condition, and intervention estimates are joined.
- **Owner:** Building portfolio owner and Finance, with climate monitoring, service departments, Procurement, and capital-delivery capacity owners.
- **Success indicators:** Portfolio coverage; target-path emissions; funded versus unfunded capital; lifecycle net cost; emissions reduction; energy savings; grants secured; maintenance coupled; projects ready, delivered, and delayed; service disruption; forecast accuracy.
- **Review point:** Initial portfolio baseline, annual budget cycle, and quarterly delivery-capacity review for committed projects.
- **Readiness:** Operational governance recommendation ready; individual investment recommendations not ready.
- **Confidence:** `high` that integrated portfolio planning is needed; `medium` in the proposed scenario method; `low` for any current total funding estimate.

## Evidence log

| ID | Role | Source | Date | Retrieval | Use and limitation |
| --- | --- | --- | --- | --- | --- |
| EVD-001 | `official_assurance` | [gpaNRW Cologne audit 2024/2025](https://gpanrw.de/sites/default/files/2026-01/Gesamtbericht_Stadt_Koeln_2024_2025.pdf) | 2024/2025 | 2026-07-17 | Funding-gap conclusion, investment context, and recommendations; current plan may have advanced |
| EVD-002 | `primary_authoritative` | [City response to gpaNRW](https://gpanrw.de/sites/default/files/2026-02/Stellungnahme_Stadt_K%C3%B6ln_2025.pdf) | 2025 response | 2026-07-17 | Describes current approach and planned monitoring expansion |
| EVD-003 | `primary_observation` | [City of Cologne 2024 Energy Report](https://www.stadt-koeln.de/mediaasset/content/pdf26/34977_energiebericht_2024_bfrei.pdf) | Report published 2026; underlying periods vary | 2026-07-17 | Object-level energy, comparison, and photovoltaic evidence; quality and timing vary |
| EVD-004 | `primary_authoritative` | [Building Management reports](https://www.stadt-koeln.de/politik-und-verwaltung/gebaeudewirtschaft-der-stadt-koeln/berichte) | Current page | 2026-07-17 | Aggregate historic results and report archive |
| EVD-005 | `primary_authoritative` | [Cologne Climate Action Plan](https://www.stadt-koeln.de/artikel/73693/index.html) | Current page | 2026-07-17 | Target, action structure, and monitoring description; citywide scope differs from own buildings |
| EVD-006 | `official_statistical_context` | [BBSR INKAR](https://www.inkar.de/) | Edition 07/2025 baseline | 2026-07-17 | Regional context only; not asset attribution |

## Assurance and approvals

- No capital allocation, procurement, publication, or target change is authorized by this assessment.
- Controlled asset records require an approved purpose, non-personal schema, custodian, retention terms, and access boundary.
- Finance, legal, climate-method, service continuity, procurement, and data-quality assurance are required before investment recommendations.
