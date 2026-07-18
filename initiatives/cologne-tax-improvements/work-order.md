---
id: WO-2026-001
status: ready
owner: data_analytics_engineer
created: 2026-07-17
review_date: 2026-08-07
---

# Work Order: Cologne public-spending evidence spike

## Objective

Determine whether official Cologne public-finance documents can support a reproducible sample that links planned and actual municipal resources to product objectives and available service indicators, without prematurely judging expenditure quality.

## Context

POC-001 explores how Cologne could use public information to improve the efficient and effective use of tax money. Final criteria are intentionally part of discovery. The immediate need is to establish what can be observed, normalized, compared, and responsibly interpreted.

### Facts

- Cologne publishes budgets, annual accounts, participation reports, and council documents in heterogeneous formats.
- The Bund der Steuerzahler publishes selected public-spending cases, including cases concerning Cologne, and describes a case-based research process involving leads, document review, responses from responsible institutions, and sometimes site observation.
- BdSt cases are editorially selected and do not represent the complete population of Cologne expenditure.
- gpaNRW has published a text-extractable 2024/2025 external audit report for Cologne containing findings, recommendations, strengths, and comparisons with 23 independent NRW cities.
- BBSR provides INKAR as a free downloadable and exportable regional indicator resource with approximately 600 indicators and historical comparison data.
- Cologne, NRW, and EU procurement platforms publish current notices and lifecycle events for many public contracts.
- Cologne publishes operational building energy reports and climate monitoring, while more detailed service and asset records require governed access.

### Assumptions to test

- BdSt cases contain reusable patterns and source trails that improve candidate discovery.
- A systematic data screen can detect some known patterns and expose blind spots where case-based research remains necessary.
- Combining financial, service, legal, operational, stakeholder, and outcome evidence can support more actionable recommendations than financial anomalies alone.
- gpaNRW can provide independent assurance and positive controls, while INKAR can provide structural and outcome context without implying attribution.
- Procurement events can reveal current decision windows, and operational or asset evidence can test whether expected value was realized.

## Owner

`data_analytics_engineer` is the single accountable owner and writer for `initiatives/cologne-tax-improvements/**` during this Work Order.

Read-only specialist input may be requested from:

- `finance_capital_allocator` for public-finance and accounting interpretation;
- `legal_risk_governance` for mandates, licences, and claims risk;
- `venture_product_lead` for usefulness of the resulting questions.

## Constraints

- Use official, publicly accessible sources as the primary factual basis for the first sample; secondary sources may generate and contextualize leads.
- Install no packages and use no credentials or external write access.
- Preserve source URL, retrieval time, reporting period, document version, page or table location, and transformation notes.
- Classify evidence by role and distinguish attributed BdSt positions from POC facts, inferences, assumptions, and recommendations.
- Independently corroborate every material BdSt claim before it contributes to a POC finding or recommendation.
- Preserve gpaNRW audit scope, observation period, peer group, finding and recommendation identifiers, and any stated limitations.
- Preserve INKAR edition, indicator definition, unit, reference year, geography, territorial status, source origin, and revision metadata.
- Do not issue an operational recommendation from one publisher or evidence role alone; document unavailable or unsuitable coverage.
- Preserve procurement notice identifiers, lifecycle state, procedure, value basis, dates, versions, and coverage limitations.
- Use only public operational reports by default; controlled aggregates require explicit purpose, approval, minimization, privacy class, retention, and custodian.
- Do not contact or attempt to influence a live procurement without Founder approval and procurement-law review.
- Do not describe any expenditure as wasteful, ineffective, or inefficient on the basis of a financial variance alone.
- Do not establish fixed criteria, thresholds, weights, or rankings in this Work Order.
- Do not publish, deploy, or communicate externally without Founder approval.
- Keep personal data out of the sample unless separately justified and approved.

## Deliverables

1. A source and field map for budget, annual-account, product, and indicator evidence.
2. An extraction-feasibility note covering formats, identifiers, tables, provenance, and known comparability breaks.
3. A normalized sample for at least three representative product groups, if the source documents permit it.
4. A data dictionary that distinguishes plan, actual, expense, cost, cash flow, transfer, output, and outcome fields.
5. A discovery note listing candidate signals, counter-explanations, data gaps, and unresolved questions.
6. A recommendation to continue, redirect, or stop the POC before public product work begins.
7. A documented assessment method with an explicit role for BdSt evidence and a recommendation-readiness gate.
8. A reusable case dossier containing claim-level provenance, counterpositions, causes, options, assurance, and follow-up.
9. A maintained BdSt source profile and pattern library with initial Cologne seed cases.
10. A gpaNRW source profile and initial extraction contract for findings, recommendations, positive controls, and peer comparisons.
11. An INKAR source profile and initial extraction contract for standardized need, context, access, and outcome indicators.
12. A source-coverage matrix in every case dossier.
13. A versioned procurement-lifecycle source contract covering City, NRW, and TED publication channels.
14. A tiered operational and asset-data source contract separating public reports, controlled aggregates, and restricted records.
15. Two current case assessments covering ordered burials and municipal building decarbonization.

## Acceptance criteria

- Every extracted value is traceable to an exact official source location and documented transformation.
- Plan and actual values, financial concepts, outputs, and outcomes are not conflated.
- The sample tests at least three different data conditions or explains why this is not feasible.
- Cross-period comparisons identify known definition, organization, and accounting breaks.
- Candidate signals are presented as hypotheses with plausible alternative explanations.
- BdSt-derived candidates retain attribution and selection-bias warnings, and no BdSt conclusion is imported as a POC finding.
- Every recommendation considers public purpose, legal duties, affected groups, lifecycle cost, service effect, alternatives, implementation ownership, and a review point.
- Cases that fail the recommendation-readiness gate produce a bounded research recommendation rather than an operational recommendation.
- Every operational recommendation uses a primary authoritative baseline and at least one independent, materially relevant evidence role.
- gpaNRW comparisons retain peer definitions and do not equate process maturity with efficiency or effectiveness.
- INKAR comparisons retain temporal and spatial metadata and do not imply program attribution.
- Procurement assessments separate notice, estimate, award, modification, contract performance, and account actuals.
- Controlled operational data are minimized, governed, and never assumed available.
- No ranking, accusation, cut recommendation, or unsupported causal claim is produced.
- Licence, accessibility, privacy, and publication risks are recorded.
- The checkpoint recommendation states what evidence would be needed for the next step.

## Dependencies

- Cologne municipal budgets and annual accounts.
- Product objectives and indicators contained in, or linked from, those documents.
- Participation reports or consolidated accounts where the selected scope requires them.
- Council documents when needed to explain a variance or mandate.
- Bund der Steuerzahler case reports as secondary leads and pattern evidence.
- gpaNRW Cologne and comparison reports as official external assurance evidence.
- BBSR INKAR downloads and metadata as official statistical context.
- Cologne, NRW, and TED procurement publications as authoritative notice evidence.
- Cologne public operational reports and approved aggregated service or asset extracts as primary operational evidence.
- Domain outcome datasets only after their definitions and linkage limits are understood.

## Ownership boundaries

| Path or system | Writer | Read-only contributors |
| --- | --- | --- |
| `initiatives/cologne-tax-improvements/**` | `data_analytics_engineer` | `finance_capital_allocator`, `legal_risk_governance`, `venture_product_lead` |
| `company/data-source-inventory.md` entries used by POC-001 | `data_analytics_engineer` | `operations_knowledge`, `legal_risk_governance` |
| External BdSt, Cologne, or stakeholder systems | None | All roles are read-only unless separately Founder-approved |

## Approval level

Routine internal research and workspace changes are pre-approved within this Work Order. Founder approval is required before external communication, publication, deployment, paid services, or a decision to label or rank expenditure performance.

## Evidence and closure

- Five method-calibration and current assessments are indexed in [the case assessment index](cases/README.md).
- Each assessment records claim-level confidence, source coverage, alternatives, recommendation readiness, and unresolved evidence.
- The three assessments are not the three normalized municipal product groups required by the extraction deliverable; that financial-document sample remains open.
- External data requests, responses, and publication remain Founder-gated.
