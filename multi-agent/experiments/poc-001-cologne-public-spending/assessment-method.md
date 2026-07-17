---
id: POC-001-METHOD-001
status: active-draft
owner: data_analytics_engineer
created: 2026-07-17
review_date: 2026-08-07
---

# Assessment Method

## Objective

Turn public-spending signals into specific, evidence-backed, feasible recommendations while preserving uncertainty, public value, legal obligations, and the perspectives of affected parties.

The method is a discovery contract. It defines minimum evidence discipline and decision stages without fixing final scoring criteria, weights, or thresholds.

## Evidence roles

| Evidence role | Examples | Permitted use | Prohibited use |
| --- | --- | --- | --- |
| `primary_authoritative` | Council decisions, budgets, annual accounts, contracts where public, official project and performance reports | Establish documented decisions, values, dates, duties, and official explanations | Treat an official claim as independently verified merely because it is official |
| `primary_observation` | Reproducible counts, site observations, direct measurements, public operational data | Establish observed conditions within a stated scope and time | Generalize beyond coverage or infer cause without supporting evidence |
| `official_assurance` | gpaNRW municipal audit findings, recommendations, and defined peer comparisons | Establish what an external public auditor found within a stated scope and reuse audit criteria as hypotheses | Assume audit coverage is complete, current, or proof of fiscal or outcome impact |
| `official_statistical_context` | BBSR INKAR indicators and documented regional comparisons | Establish standardized need, structural, service-access, and outcome context | Attribute an outcome to Cologne spending or treat a citywide average as complete local evidence |
| `secondary_advocacy` | Bund der Steuerzahler case reports and recommendations | Generate leads, reusable failure patterns, source trails, questions, and counterfactuals | Establish waste, blame, avoidability, or recommendation by itself |
| `secondary_journalistic` | Credible local or specialist reporting | Generate leads, discover documents, and corroborate chronology | Replace unavailable primary evidence without an explicit confidence reduction |
| `stakeholder_account` | Statements from administration, users, employees, suppliers, residents, or affected groups | Add operational context, interests, impacts, and disputed facts | Present a single account as neutral consensus |
| `analytical_inference` | Calculated variance, cost per comparable output, causal hypothesis, scenario estimate | Support transparent analysis when inputs and method are traceable | Present assumptions, correlations, or model output as observed fact |

## Role of the Bund der Steuerzahler

The Bund der Steuerzahler (BdSt) is a named `secondary_advocacy` source in this POC. Its cases are used in five ways:

1. **Lead generation:** identify candidate projects, recurring costs, delays, low utilization, transparency gaps, or unresolved decisions.
2. **Pattern library:** derive testable failure patterns that can be searched for systematically across Cologne data.
3. **Source discovery:** locate referenced council decisions, administrative statements, cost histories, usage figures, and earlier reporting.
4. **Method evaluation:** test whether the POC detects known cases and where its available data remains blind.
5. **Outcome learning:** examine follow-up cases in which a service, project, or control changed after criticism.

BdSt language and conclusions are never imported as POC findings. Terms such as "waste", "failure", or "unnecessary" remain attributed claims until the POC's own evidence and review process supports a carefully scoped conclusion.

## Complementary source roles

### gpaNRW municipal audit

The gpaNRW Cologne audit is an `official_assurance` source. It contributes externally developed findings, recommendations, process expectations, strengths, and defined comparisons with other independent cities in North Rhine-Westphalia. The POC uses it to discover candidates, test governance and process maturity, identify positive controls, and monitor implementation of recommendations.

An audit finding proves that the gpaNRW reached that conclusion for its stated period and scope. It does not prove that the condition remains current, that it caused financial loss, or that adopting the recommendation has a positive net effect. Cologne primary evidence and implementation context remain necessary.

### BBSR INKAR regional indicators

INKAR is an `official_statistical_context` source. It contributes standardized longitudinal and geographic indicators for need, structural conditions, service access, and outcomes. The POC uses it to place Cologne trends in context, construct transparent peer comparisons, challenge local narratives, and select possible follow-up measures.

INKAR cannot establish program attribution. Spatial aggregation, reporting lag, territorial status, definition changes, and external drivers must be recorded before an indicator influences a recommendation.

### Cologne procurement lifecycle

Cologne, NRW, and TED procurement publications are `primary_authoritative` evidence of the notices and procedure states that were published. They connect a spending intention to a defined service, competition, award, modification, and contract period. They are used to identify current decision windows and test whether audit recommendations reach contract design and management.

A procurement notice is not evidence that the need, price, supplier, or outcome is good or bad. Live procedures must not be contacted, influenced, or materially changed without authority and procurement-law review.

### Cologne operational performance and asset data

Published operational reports and governed extracts are `primary_observation` evidence of service delivery and asset condition within their definitions and coverage. They are used to replace estimated benefits with realized cost, volume, timeliness, utilization, quality, energy, condition, and outcome evidence.

The source is tiered. Public reports are available for immediate analysis; controlled aggregates require purpose, owner, approval, privacy class, retention, and access boundaries. Restricted person-level records are outside the v1 default.

## Source coverage rule

Every accepted case must contain a source-coverage matrix for these perspectives:

| Perspective | Preferred source role | Required treatment |
| --- | --- | --- |
| Decision, mandate, and financial baseline | `primary_authoritative` | Required for an operational recommendation |
| Delivered service or observed condition | `primary_observation` or current primary reporting | Required when the recommendation changes a service or operation |
| Procurement and contract lifecycle | `primary_authoritative` procurement notices and awards | Required when the recommendation concerns a bought service, supplier, contract, or live decision window |
| External assurance and administrative comparison | `official_assurance` | Use if in scope; otherwise record `not_covered`, `outdated`, or `not_applicable` |
| Need, structure, and outcome context | `official_statistical_context` | Use if spatial and temporal fit is adequate; otherwise document the gap |
| Investigative history and failure patterns | `secondary_advocacy` or `secondary_journalistic` | Optional lead and challenge evidence; always retain attribution |
| Affected-party experience | `stakeholder_account` | Required when material access, distributional, or operational effects are claimed |

No operational recommendation may depend on a single publisher or evidence role. It must use a primary authoritative baseline plus at least one independent and materially relevant evidence role. Sources that are unavailable or unsuitable are recorded as coverage gaps rather than silently omitted.

## Assessment flow

### 0. Scan broadly when discovery operates at scale

Before registering full cases, a bounded opportunity scan may connect financial, assurance, procurement, operational, asset, spatial, decision, and stakeholder evidence. Each opportunity must retain a stable ID, at least two source references, explicit join logic, a falsifiable hypothesis, a material caveat, and the cheapest useful next test.

Opportunity scans keep evidence maturity, decision proximity, controllability, test cost, and risk as separate dimensions. They must not add those dimensions into a composite score or represent an untested hypothesis as a finding. Only selected opportunities enter step 1; all others remain versioned, are merged with an explicit mapping, or are stopped with a reason.

### 1. Register a signal

Create a review candidate from a data anomaly, BdSt case, press report, citizen lead, gpaNRW finding, INKAR context trend, or official disclosure. Record the originating source, exact claim, date, scope, and source incentives.

Output: a candidate with status `untriaged`; no evaluative label.

### 2. Triage relevance and testability

Ask whether the candidate concerns material public resources, a meaningful service or outcome, an actionable decision, and evidence that can be responsibly obtained. Reject or defer candidates that are purely rhetorical, outside scope, duplicated, or not testable.

Output: `accepted_for_review`, `deferred`, or `rejected`, with rationale.

### 3. Reconstruct the baseline

Establish what was originally intended and authorized:

- public problem and intended beneficiaries;
- decision owner and legal or political mandate;
- approved scope, schedule, budget, financing, and expected lifecycle cost;
- intended outputs, outcomes, and success measures;
- alternatives documented at the decision point.

Output: a source-linked baseline that separates contemporaneous facts from later expectations.

### 4. Reconstruct current performance

Determine current cumulative and recurring cost, delivered scope, schedule, utilization, service quality, outcomes where observable, and unresolved obligations. Make scope changes, inflation, grants, accounting changes, and one-off effects explicit. Check applicable gpaNRW findings and use fitting INKAR trends to distinguish local performance from structural context.

Output: comparable actuals and an explicit comparability assessment.

### 5. Triangulate and hear counterpositions

For each material claim, seek primary documentation and at least one relevant counterposition. Record the administration's published explanation or mark a direct response as `not_requested`, `requested`, `received`, or `declined`. Contacting an external party requires Founder approval.

Output: a claim-evidence matrix containing support, contradiction, gaps, and confidence.

### 6. Diagnose causes and controllability

Separate symptoms from plausible causes across need, planning, procurement, delivery, operations, external change, and governance. Identify what was foreseeable at the time, what was avoidable, and what remains controllable now. Do not infer individual fault from system-level evidence.

Output: a causal map with alternative explanations and evidence strength.

### 7. Develop options

Include the status quo and, where feasible, at least two materially different options. Options may improve measurement, governance, procurement, scope, scheduling, utilization, operating model, collaboration, or orderly exit. A spending cut is not the default option.

For every option assess:

- fiscal effect and lifecycle cost as a range;
- service, outcome, access, and distributional effects;
- legal, contractual, operational, and political constraints;
- implementation cost, time, dependencies, and capacity;
- reversibility and major risks;
- measurement plan and earliest useful review point.

Output: an option comparison with common assumptions.

### 8. Recommend and design verification

A recommendation must name the action, accountable decision owner, prerequisites, sequence, expected effects, uncertainty, safeguards, success indicators, and reconsideration point. Prefer staged and reversible action where uncertainty is material.

Output: `recommendation_draft`. Publication or external communication requires Founder approval and assurance review.

### 9. Follow up

Track whether the recommendation was accepted, implemented, changed, or rejected and whether expected effects occurred. Update the case rather than preserving an outdated verdict.

Output: versioned outcome evidence and method learning.

## Claim and confidence rules

Each material claim must be classified as `fact`, `inference`, `assumption`, `attributed_position`, or `recommendation`.

Confidence is recorded per claim, not only per case:

- `high`: directly supported by stable, comparable primary evidence and no unresolved material contradiction;
- `medium`: supported but affected by a material scope, quality, timeliness, or interpretation limitation;
- `low`: plausible lead or inference with missing primary evidence or unresolved contradiction;
- `unknown`: not yet assessed.

A high-confidence financial variance does not imply high confidence about its cause, avoidability, effect, or recommended response.

## Recommendation readiness gate

A case may advance to a recommendation only when:

- the baseline and current state are source-linked;
- the source-coverage matrix is complete and the recommendation does not depend on one publisher or evidence role;
- financial concepts and scopes are comparable or the limitation is explicit;
- public purpose, legal obligations, and affected groups are documented;
- plausible counter-explanations were tested;
- the relevant official position is represented or its absence is explicit;
- at least the status quo and one actionable alternative are evaluated;
- fiscal and service effects are both addressed;
- uncertainties and missing evidence are visible;
- the proposed action has an owner, prerequisites, measures, and review point.

Failure to meet the gate produces a research recommendation, not an operational recommendation.

## Non-negotiable guardrails

- Never treat selection into the BdSt Schwarzbuch as proof of waste.
- Never use a composite score to conceal value judgments or missing evidence.
- Never compare original and current cost without reconciling scope, price basis, financing, and included lifecycle components.
- Never interpret low utilization without considering access, capacity, service purpose, ramp-up, and distributional effects.
- Never recommend stopping an initiative without estimating exit, sunk, contractual, transition, and service-loss consequences.
- Preserve exact provenance and attributed language.
- Version findings when new decisions, costs, explanations, or outcomes emerge.
- Apply legal-risk and quality review before any public claim about identifiable institutions or people.

## Related artifacts

- [BdSt source profile](sources/bund-der-steuerzahler.md)
- [gpaNRW source profile](sources/gpanrw-municipal-audit.md)
- [INKAR source profile](sources/inkar-regional-indicators.md)
- [Cologne procurement source profile](sources/cologne-procurement-lifecycle.md)
- [Cologne operational and asset-data source profile](sources/cologne-operational-asset-data.md)
- [Case dossier template](templates/case-dossier.md)
- [POC overview](README.md)
- [Work Order](work-order.md)
