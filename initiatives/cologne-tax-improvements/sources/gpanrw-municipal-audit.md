---
id: POC-001-SOURCE-GPANRW-001
status: active
owner: data_analytics_engineer
created: 2026-07-17
review_date: 2026-08-07
---

# Source Profile: gpaNRW Municipal Audit

## Classification

- **Publisher:** Gemeindeprüfungsanstalt Nordrhein-Westfalen (gpaNRW).
- **Evidence role:** `official_assurance`.
- **Primary Cologne source:** [Municipal audit of the City of Cologne 2024/2025](https://gpanrw.de/sites/default/files/2026-01/Gesamtbericht_Stadt_Koeln_2024_2025.pdf).
- **Comparison source:** [gpaNRW download center](https://gpanrw.de/service/downloadcenter/aktuelle-downloads).
- **Format:** Text-extractable PDF reports and selected XLSX benchmark files.
- **Coverage:** Periodic thematic audit rather than continuous or complete monitoring of all expenditure.

## Why it complements other sources

The gpaNRW report contributes an external public-sector assurance perspective. The Cologne 2024/2025 report contains structured findings and recommendations, descriptions of expected administrative practice, and comparisons with 23 independent cities in North Rhine-Westphalia. It covers both strengths and improvement opportunities, reducing the negative-case selection bias of an advocacy source.

The report does not replace Cologne primary records. It establishes what an official external auditor found within a defined audit scope and period.

## Initial integration contract

Extract one record per finding and one linked record per recommendation.

### Finding fields

| Field | Meaning |
| --- | --- |
| `audit_id` | Stable POC identifier for report edition and audit area |
| `finding_id` | Source finding identifier such as `F1` within its section |
| `audit_area` | Report section or service domain |
| `finding_text` | Exact attributed finding or a marked paraphrase |
| `finding_polarity` | `strength | mixed | improvement_opportunity | risk` |
| `period_observed` | Period to which the finding applies |
| `source_page` | Printed and PDF page where practical |
| `comparison_population` | Peer group and number of observations |
| `metric_definition` | Definition and unit of a referenced measure |
| `cologne_value` | Cologne value where reported |
| `peer_distribution` | Minimum, quartiles, median, maximum, or other available comparator values |
| `limitations` | Scope, structure, sample, or comparability caveats stated or identified |

### Recommendation fields

| Field | Meaning |
| --- | --- |
| `recommendation_id` | Source recommendation identifier such as `E1` |
| `finding_id` | Finding supported by the recommendation |
| `recommendation_text` | Exact attributed recommendation or marked paraphrase |
| `responsible_domain` | Likely accountable municipal function, not an inferred person |
| `city_response` | Published response or implementation status where available |
| `status_date` | Date at which implementation status was observed |
| `primary_evidence_needed` | Cologne records needed before adopting or updating the recommendation |

## POC uses

1. Create review candidates from explicit findings and recommendations.
2. Add positive controls: identify areas where evidence indicates strong performance and test whether the POC avoids false negative flags.
3. Compare Cologne with a defined municipal peer group when definitions and structures are sufficiently aligned.
4. Reuse audit criteria as candidate process, governance, and control measures.
5. Check whether recommendations were implemented and whether expected operational effects followed.
6. Discover relevant Cologne documents and responsible administrative domains.

## Limitations and guardrails

- Audit coverage is thematic and periodic; absence of a finding is not evidence of good performance.
- A finding is authoritative evidence of the gpaNRW's audit conclusion, not automatic proof of current conditions or causal effect.
- Recommendations may optimize compliance or process maturity without quantifying fiscal or outcome impact.
- Peer comparisons may be limited by city size, organization, service model, insourcing, accounting, and data quality.
- The report itself warns that structural differences limit intermunicipal comparison in some areas.
- A high process-fulfilment score must not be presented as proof of efficient spending or effective public outcomes.
- Before a POC recommendation is issued, verify current status, local constraints, implementation cost, and expected service effect with Cologne primary sources.

## First extraction slice

Extract the report's consolidated findings and recommendations table, retaining section, identifiers, page references, and wording. Select three contrasting test cases:

- a documented strength as a false-positive control;
- an improvement recommendation with an operational owner and observable implementation status;
- a recommendation whose financial or outcome effect cannot be inferred without additional evidence.

This slice tests extraction and reasoning discipline; it does not attempt to reproduce the complete audit.

## Source maintenance

Retain report title, audit identifier, publication and retrieval dates, version, exact page, audit scope, period, peer group, metric definition, and any later city response. Recheck the download center and Cologne council records before relying on an older recommendation.
