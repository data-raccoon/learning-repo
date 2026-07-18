---
id: POC-001-OPPORTUNITY-SCANS
status: active
owner: data_analytics_engineer
created: 2026-07-17
review_date: 2026-08-07
---

# Opportunity Scans

Opportunity scans are the wide, low-commitment stage before case assessment. They connect evidence objects, register falsifiable hypotheses, and identify the cheapest useful next test. They do not produce findings, rankings, savings promises, or operational recommendations.

| Scan | Status | Opportunities | Shortlist candidates | Artifacts |
| --- | --- | ---: | ---: | --- |
| [Scan 001](scan-001/opportunity-register.md) | completed | 29 | 8 | [work order](scan-001/work-order.md), [sources](scan-001/sources.md), [schema](scan-001/schema.md), [JSON register](scan-001/opportunities.json) |

## Lifecycle

`signal -> opportunity scan -> cheap next test -> accepted case or stopped hypothesis -> case assessment -> recommendation-readiness gate`

An opportunity keeps its stable ID if it advances. A case dossier records the originating opportunity ID and may merge related opportunities only with an explicit mapping.

