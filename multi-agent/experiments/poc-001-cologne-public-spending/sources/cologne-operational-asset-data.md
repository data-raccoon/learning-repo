---
id: POC-001-SOURCE-OPERATIONS-ASSETS-001
status: active
owner: data_analytics_engineer
created: 2026-07-17
review_date: 2026-08-07
---

# Source Profile: Cologne Operational Performance and Asset Data

## Classification

- **Publisher or custodian:** City of Cologne and its accountable operating units.
- **Evidence role:** `primary_observation` for measured operations and asset conditions; `primary_authoritative` for formally approved operational reports.
- **Public entry points:** [Building Management reports](https://www.stadt-koeln.de/politik-und-verwaltung/gebaeudewirtschaft-der-stadt-koeln/berichte), [2024 Energy Report](https://www.stadt-koeln.de/mediaasset/content/pdf26/34977_energiebericht_2024_bfrei.pdf), and [Cologne climate monitoring](https://www.klimaschutz-monitoring.koeln/).
- **Controlled extensions:** Aggregated case-management, contract-performance, cost-recovery, asset-condition, maintenance, investment, utilization, and service-quality extracts held by operating units.
- **Access:** Public reports are immediately usable. Controlled records are unavailable in v1 unless separately authorized and supplied with an approved purpose and data boundary.

## Why it complements other sources

Budgets, audits, advocacy cases, statistics, and procurement records describe intentions, findings, context, or transactions. Operational and asset data show whether a service was timely, used, reliable, costly, recovered, maintained, energy-efficient, or improving. They are necessary to estimate realized efficiency and effectiveness.

The source is a governed source family, not one assumed database. Every extract must identify its system, owner, definitions, coverage, and quality limitations.

## Access tiers

| Tier | Content | Default use |
| --- | --- | --- |
| `public_report` | Published energy, performance, monitoring, annual, and project reports | Allowed for internal analysis with provenance |
| `public_aggregate` | Published tables, dashboards, open data, and anonymized service totals | Allowed with definition and extraction metadata |
| `controlled_aggregate` | Non-public but non-personal or sufficiently aggregated operational and asset extracts | Requires purpose, custodian, approval, retention, and access record |
| `restricted_record` | Person-, household-, employee-, supplier-sensitive, security-sensitive, or case-level records | Out of scope unless separately justified, minimized, legally reviewed, and approved |

## Common observation contract

| Field | Meaning |
| --- | --- |
| `dataset_id` | Stable POC identifier for the source system or report |
| `observation_id` | Stable source or generated observation identifier |
| `entity_type` | Service, case aggregate, contract, facility, asset, measure, or geography |
| `entity_id` | Stable official identifier where provided |
| `metric_id` | Stable metric identifier |
| `metric_name` | Published or custodian-approved name |
| `definition` | Numerator, denominator, inclusions, exclusions, and calculation |
| `value` | Observation value; missing remains missing |
| `unit` | Currency, count, duration, energy, emissions, rate, or other unit |
| `period_start` | Observation-period start |
| `period_end` | Observation-period end |
| `recorded_at` | Source-system or report timestamp |
| `status` | Actual, provisional, corrected, estimated, or planned |
| `source_system` | Exact originating report, dashboard, or system |
| `custodian` | Accountable data owner |
| `coverage` | Population, facilities, services, or cases represented |
| `quality_flags` | Missingness, late entry, definition break, estimate, or reconciliation status |
| `privacy_class` | Public, internal aggregate, confidential, personal, or special-category marker |
| `retrieval_date` | Date acquired by the POC |

## Domain extensions

### Service and case operations

- incoming and completed volume;
- backlog age and value;
- legal or service deadline performance;
- processing time and effort;
- service unit cost;
- recoverable, claimed, collected, written-off, and expired value;
- errors, rework, complaints, and accessibility measures.

### Buildings and assets

- facility use and service criticality;
- condition and mandatory maintenance;
- energy and water consumption, cost, and emissions;
- floor area, energy carrier, and normalized intensity;
- planned intervention, capital cost, grant, timing, and readiness;
- expected and realized energy, cost, and emissions effect;
- maintenance interaction, disruption, dependencies, and remaining life.

## POC uses

1. Replace estimated benefit with realized service and financial evidence.
2. Connect contract delivery to service units, quality, and outcomes.
3. Prioritize backlogs and asset investments using transparent operational facts.
4. Establish baselines and follow-up measures for recommendations.
5. Detect data-quality and observability failures as separate improvement opportunities.

## Guardrails

- Request the least granular data that can answer the decision question.
- Prefer aggregates and pseudonymous identifiers; do not ingest names, addresses, health, family, or other case details for the burial case.
- Do not use employee-level productivity data as a proxy for individual performance without a separately approved purpose and labour/privacy review.
- Separate plan, estimate, measured actual, corrected actual, and modelled outcome.
- Do not compare operational units until definitions, service mix, and denominator are aligned.
- An asset with high energy use is not automatically inefficient; operating hours, protected status, technical function, occupancy, and service criticality matter.
- Record retention, deletion, access, and permitted-use conditions for every controlled extract.
- Any request to an external or municipal custodian requires Founder approval.

## First extraction slices

1. **Ordered burials:** monthly aggregated volume, backlog, deadline compliance, claims value, collections, write-offs, processing effort, contractor cost, and service quality without personal data.
2. **Municipal buildings:** object-level public energy observations joined to non-personal condition, planned investment, grant, readiness, and lifecycle estimates when authorized.

## Source maintenance

Version public reports and dashboard exports. For controlled extracts maintain a data register containing purpose, owner, approval, schema, privacy class, retrieval, retention, permitted users, quality statement, and deletion date. No credentials or connectors are added in v1.
