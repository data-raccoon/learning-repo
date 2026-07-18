---
id: POC-001
status: exploring
owner: data_analytics_engineer
created: 2026-07-17
review_date: 2026-08-07
---

# Cologne Public Spending Explorer

## Purpose

Help Cologne examine whether public money is being used efficiently and effectively by making difficult public-finance information easier to inspect, connect, and question.

This proof of concept is an investigation, not a waste ranking. It will identify **review candidates**: expenditure areas for which observable signals justify closer examination. A signal is not evidence of waste, misconduct, or a causal relationship.

## Discovery question

Can official public data be transformed into a traceable view that connects municipal resources with services and intended results closely enough to support useful questions about efficiency and effectiveness?

## Working concepts

- **Economy:** Were required inputs acquired at an appropriate cost?
- **Efficiency:** What service or output was produced for the resources used?
- **Effectiveness:** To what extent did the service contribute to its stated objective or outcome?

The POC uses the conceptual chain:

`resources -> activities -> outputs -> outcomes`

These concepts are starting vocabulary, not final scoring criteria. Definitions, thresholds, comparisons, and weights remain discovery work.

## Initial evidence map

| Evidence layer | Initial Cologne source | What it may contribute | Important limitation |
| --- | --- | --- | --- |
| Planned resources | Municipal budgets | Planned revenue, expenditure, product groups, objectives, and some indicators | A plan is not actual execution |
| Actual resources | Annual accounts | Actual financial results and variances | Accounting results alone do not establish value or waste |
| Services and outputs | Product descriptions and indicators | Objectives, quantities, service levels, or output proxies where documented | Definitions and coverage may change or be incomplete |
| External assurance | gpaNRW municipal audit | Findings, recommendations, strengths, process criteria, and comparisons with other independent NRW cities | Periodic thematic scope; audit conclusions are not current implementation or impact evidence |
| Structural and outcome context | BBSR INKAR | Standardized longitudinal indicators for need, access, living conditions, and transparent geographic comparison | Aggregated indicators have lags and cannot establish program attribution |
| Procurement lifecycle | Cologne procurement platforms, Vergabemarktplatz NRW, and TED | Current competitions, awards, modifications, duration, value where published, and contract decision windows | Publication coverage is incomplete and does not establish value for money or delivery quality |
| Operational and asset performance | Cologne operating reports, climate monitoring, energy reports, and governed aggregates | Actual volume, timeliness, utilization, quality, recovery, cost, energy, emissions, condition, and delivery | Definitions vary; controlled records require approval, minimization, and data governance |
| Municipal companies | Participation reports and consolidated accounts | Financial and governance context outside the core administration | Entities and accounting scopes differ |
| Decisions and explanations | Council information system | Political decisions, mandates, documents, and explanatory context | Documents are heterogeneous and difficult to link |
| Investigative case patterns | Bund der Steuerzahler Schwarzbuch and case platform | Leads, recurring failure patterns, source trails, counterfactuals, and follow-up cases | Advocacy and editorial selection; every material claim requires independent corroboration |
| Outcomes | Domain-specific public datasets | Possible measures of social, mobility, environmental, or service outcomes | Outcomes are influenced by many factors beyond municipal spending |

The canonical source descriptions live in [the Company-OS source inventory](../../company-os/company/data-source-inventory.md).

## Assessment process

The [assessment method](assessment-method.md) governs how a signal becomes a recommendation. It requires primary-source reconstruction, counterpositions, cause and controllability analysis, option comparison, and a recommendation-readiness gate.

The process uses five named complementary source families:

- the Bund der Steuerzahler as `secondary_advocacy` for leads and failure patterns, governed by its [source profile](sources/bund-der-steuerzahler.md);
- gpaNRW as `official_assurance` for external findings, recommendations, positive controls, and defined municipal comparisons, governed by its [source profile](sources/gpanrw-municipal-audit.md);
- BBSR INKAR as `official_statistical_context` for longitudinal need, structural, service-access, and outcome context, governed by its [source profile](sources/inkar-regional-indicators.md).
- Cologne, NRW, and TED procurement publications for the public contract lifecycle, governed by the [procurement source profile](sources/cologne-procurement-lifecycle.md);
- Cologne operational performance and asset data for realized service and asset evidence, governed by the [operational and asset-data source profile](sources/cologne-operational-asset-data.md).

Every candidate investigation uses the [case dossier template](templates/case-dossier.md). No operational recommendation may depend on a single publisher or evidence role.

## Initial assessments

The [initial case index](cases/README.md) contains three internal calibration assessments:

- [Heinrich-Böll-Platz guarding](cases/case-001-heinrich-boell-platz.md);
- [citywide software licence management](cases/case-002-software-licence-management.md);
- [Lentpark fixed-route and TaxiBus service](cases/case-003-lentpark-transit-service.md).

They deliberately include a recurring-cost signal, an official audit finding, and a retrospective service-model change. None is a public waste finding or ranking.

Two additional current assessments use the new source families:

- [ordered burials and cost recovery](cases/case-004-ordered-burials.md);
- [municipal building decarbonization portfolio](cases/case-005-municipal-building-decarbonization.md).

## Scaled opportunity discovery

The [opportunity-scan mechanism](opportunity-scans/README.md) separates broad hypothesis generation from full case assessment. [Opportunity Scan 001](opportunity-scans/scan-001/opportunity-register.md) contains 29 traceable hypotheses produced from cross-source joins and identifies eight candidates for possible evidence sprints. None is a finding, ranking, savings estimate, or approved recommendation.

[Evidence Sprint 001](evidence-sprints/sprint-001/sprint-results.md) ran public-data stop-or-continue tests on those eight candidates. Seven continue to a more specific evidence test and the electronic-file benefit hypothesis is held until current outcome evidence or approved controlled aggregates are available.

## First investigation slice

Start with a small, representative sample of municipal product groups. The sample should test different data conditions rather than select politically interesting or unusually large values. For each sample, attempt to retain:

1. product and organizational identity;
2. reporting period and plan version;
3. planned and actual financial values;
4. stated objectives and available output indicators;
5. exact document, page, table, and retrieval provenance;
6. known breaks in definition, scope, or accounting treatment.

The first slice ends with a feasibility assessment and a data-gap map. It does not require a public-facing product or a judgment about an expenditure area.

## Candidate signals to test, not adopt

- repeated material plan-to-actual variance;
- rising cost with stable or falling comparable output;
- missed service targets despite increased resources;
- persistent under-execution of an approved budget;
- unusual changes that cannot yet be explained by demand, mandates, inflation, grants, one-offs, or accounting changes;
- large expenditure areas for which objectives or results are not measurable from available public data.

No signal receives a threshold, weight, or negative label until its meaning, comparability, and likely failure modes have been reviewed.

## Interpretation guardrails

- Use neutral terms such as **review candidate**, **signal**, **variance**, and **data gap**.
- Keep planned expenditure, actual expenditure, expense, cost, cash flow, and transfer payments distinct.
- Record legal mandates and service demand where available; high or rising expenditure is not itself inefficiency.
- Separate output from outcome and correlation from attribution.
- Treat missing indicators as an observability problem, not proof of poor performance.
- Do not compare years, product groups, or municipalities without checking definition and scope stability.
- Trace every displayed number to its source location and transformation.
- Require Founder approval before publication or external communication.

## Non-goals for this stage

- naming the "worst" department, program, company, or expenditure;
- producing a league table or composite score;
- making allegations or causal claims;
- recommending service cuts;
- defining the final efficiency or effectiveness framework;
- deploying a public website or monetization.

## Open discovery questions

- At what granularity do plan and actual values share stable identifiers?
- Which product groups contain usable targets, output quantities, and historical actuals?
- Which outcome datasets can be linked without implying false causality?
- How are reorganizations, supplementary budgets, internal allocations, grants, and one-off effects represented?
- What explanatory context is available for large variances?
- Which views would help residents and decision-makers ask better questions without oversimplifying the evidence?

## Next checkpoint

Review the extraction sample and decide whether to continue with a normalized longitudinal dataset, change the evidence slice, or stop the POC. Any public prototype is a separate, Founder-approved decision.
