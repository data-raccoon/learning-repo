---
id: POC-001-SOURCE-INKAR-001
status: active
owner: data_analytics_engineer
created: 2026-07-17
review_date: 2026-08-07
---

# Source Profile: BBSR INKAR Regional Indicators

## Classification

- **Publisher:** Federal Institute for Research on Building, Urban Affairs and Spatial Development (BBSR).
- **Evidence role:** `official_statistical_context`.
- **Primary source:** [INKAR online atlas and database downloads](https://www.inkar.de/).
- **Current profile baseline:** INKAR edition 07/2025, with data on a common territorial status of 2023 as described by the publisher.
- **Format:** Full database ZIP, interactive tables, CSV or XLS exports, indicator documentation, and maps.
- **Coverage:** Approximately 600 indicators across education, demography, labour, economy, housing, transport, environment, public services, and selected municipal SDG measures.

## Why it complements other sources

INKAR adds standardized need, environment, service-access, and outcome context that expenditure documents and case reports often lack. It supports longitudinal and peer comparison and helps test whether an observed change is Cologne-specific or part of a wider regional trend.

INKAR does not establish that a Cologne expenditure caused an observed outcome. Many indicators operate at municipal, district, or functional-region level and are influenced by external factors and long time lags.

## Initial integration contract

Use the downloadable full dataset or a documented CSV/XLS export. Preserve the publisher's indicator metadata rather than renaming variables without a mapping.

### Indicator observation fields

| Field | Meaning |
| --- | --- |
| `edition` | INKAR release identifier |
| `indicator_id` | Publisher identifier where available; otherwise a stable POC mapping |
| `indicator_name` | Publisher label |
| `definition` | Exact or attributed publisher definition |
| `unit` | Unit and denominator |
| `topic` | Publisher topic grouping |
| `geography_type` | Municipality, district, labour-market region, or other spatial level |
| `geography_id` | Stable official area identifier where provided |
| `geography_name` | Published area name |
| `reference_year` | Observation period, distinct from release year |
| `value` | Published value with missing values preserved as missing |
| `source_origin` | Underlying statistical or administrative source listed by INKAR |
| `territorial_status` | Geographic reference status used by the edition |
| `revision_status` | Revision or provisional marker where available |
| `retrieval_date` | Date acquired by the POC |

### Derived comparison fields

Derived values remain `analytical_inference` and retain the peer definition:

- change over a comparable period;
- Cologne percentile or distance from a defined peer median;
- direction relative to NRW, Germany, or a comparable-city group;
- indicator availability and reporting lag;
- break or non-comparability flag.

## POC uses

1. Add demand and structural context to financial and service observations.
2. Identify outcome trends that may justify deeper domain research.
3. Select transparent comparison groups and test whether Cologne differs from broader trends.
4. Check plausibility of narratives about population, labour, housing, mobility, education, environment, or service access.
5. Define outcome measures for recommendation follow-up where temporal and geographic fit is adequate.
6. Reveal where city-level indicators are too aggregated and a Cologne-specific dataset is still required.

## Limitations and guardrails

- Statistical association is not attribution; INKAR values cannot prove that a municipal program caused an outcome.
- Release year, reference year, and territorial status are separate fields and must never be conflated.
- Indicators may have long publication lags, revisions, suppressed values, or changes in underlying definition.
- A national peer group may be inappropriate without controlling for city size, function, demographics, and regional interdependencies.
- Citywide averages can hide neighbourhood and population-group differences.
- Direction is not automatically normative: an increase or decrease is not labelled good or bad without an explicit public objective.
- Do not combine indicators into a composite score without documented rationale, sensitivity analysis, and Founder-approved interpretation policy.

## First extraction slice

Choose no more than twelve indicators across three domains relevant to the first expenditure cases. Include:

- at least one need or demand indicator;
- at least one service-access or output-context indicator;
- at least one outcome indicator;
- Cologne, NRW, Germany, and a documented comparable-city group where supported;
- at least five comparable reference years where available.

The first slice evaluates metadata quality, temporal fit, spatial fit, and interpretability. Indicator selection does not establish the final effectiveness framework.

## Source maintenance

Version the complete edition or export, checksum acquired files, retain indicator documentation, and record retrieval date. Never silently replace an older edition because historical values or territorial mappings may be revised.
