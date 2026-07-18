---
id: POC-001-SOURCE-PROCUREMENT-001
status: active
owner: data_analytics_engineer
created: 2026-07-17
review_date: 2026-08-07
---

# Source Profile: Cologne Public Procurement Lifecycle

## Classification

- **Publishers:** City of Cologne procurement platforms, Vergabemarktplatz NRW, and the EU Tenders Electronic Daily service where applicable.
- **Evidence role:** `primary_authoritative` for the content and status of published procurement notices.
- **Primary entry points:** [City procurement platform](https://vergabeplattform.stadt-koeln.de/NetServer/), [City procurement service](https://www.stadt-koeln.de/wirtschaft/ausschreibungsservice/index.html), [Vergabemarktplatz NRW](https://www.evergabe.nrw.de/), and [TED](https://ted.europa.eu/).
- **Format:** Searchable HTML, notice detail pages, downloadable documents, and EU eForms or exports where available.
- **Access:** Public notice access without credentials; participation features and some documents may require registration.

## Why it complements other sources

Budgets describe authorization and accounts describe financial results. Procurement notices expose the operational transition between intent and contracted delivery: subject, procedure, dates, estimated value where published, lots, duration, award, modification, and supplier. They also reveal time-sensitive intervention windows before a contract becomes difficult to change.

Procurement publication does not establish that the need is valid, the price is economic, delivery succeeded, or the full lifecycle cost is known.

## Initial integration contract

Store notices as versioned lifecycle events rather than overwriting one current record.

| Field | Meaning |
| --- | --- |
| `procurement_id` | Stable POC identifier |
| `publisher_notice_id` | Exact notice or procedure identifier |
| `buyer_name` | Published contracting authority |
| `title` | Published procedure title |
| `notice_type` | Planned notice, competition, award, modification, cancellation, or other |
| `procedure_type` | Published procurement procedure |
| `legal_regime` | VgV, UVgO, VOB, SektVO, concession, or other published basis |
| `cpv_codes` | Published procurement classification codes |
| `description` | Attributed scope description |
| `estimated_value` | Published estimate with currency, tax basis, and range flag |
| `award_value` | Published award value with the same metadata |
| `publication_date` | Notice publication date |
| `deadline` | Bid or participation deadline |
| `contract_start` | Published start date |
| `contract_end` | Published end date |
| `extensions_options` | Published options and renewal rights |
| `lots` | Lot identifiers and scope |
| `supplier` | Awarded supplier where publicly disclosed |
| `modification_reason` | Published reason for a contract change |
| `source_url` | Exact notice URL |
| `retrieval_timestamp` | Time the POC observed the record |
| `content_version` | Document version, checksum, or snapshot identifier |
| `coverage_limit` | Threshold, missing field, registration, or publication limitation |

## POC uses

1. Detect current decision windows and recurring procurements.
2. Connect planned expenditure to a specific service, procedure, duration, and later award.
3. Identify repeated extensions, modifications, cancellations, limited competition, or fragmented buying as review signals.
4. Check whether a recommendation can still influence contract design or only future contract management.
5. Compare estimate, award, modification, and realized account values without treating them as interchangeable.
6. Verify whether audit recommendations are reflected in service specifications, reporting requirements, and performance measures.

## Guardrails

- A current procurement is not evidence of waste or a flawed need.
- Never interfere with, contact participants in, or attempt to influence a live procedure without explicit authority and legal review.
- Material changes to a published procedure may be legally restricted; recommendations must distinguish the current award, contract mobilization, contract management, and the next procurement cycle.
- Published value may be absent, estimated, net of tax, cover options, or differ from actual expenditure.
- Coverage is incomplete for low-value, exempt, internal, framework-call-off, and non-public transactions.
- Preserve every observed version because notices and documents can change or expire.
- Do not infer favouritism, collusion, or illegality from procedure type or supplier concentration alone.

## First extraction slice

Capture all visible lifecycle events for the two current cases and ten additional Cologne procedures across services, software, and construction. Test identifier stability, document access, estimate-to-award linkage, modification history, and archival survival.

## Source maintenance

Poll politely and infrequently, retain retrieval timestamps, and prefer official structured exports where offered. Cross-link the same procedure across City, NRW, and TED identifiers. Credentials, registration, automated high-volume access, or external communication require separate approval.
