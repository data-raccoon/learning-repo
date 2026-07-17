---
id: POC-001-SCAN-001-SCHEMA
status: active-draft
owner: data_analytics_engineer
created: 2026-07-17
review_date: 2026-08-07
---

# Opportunity Register Schema

## Purpose

The register is normalized at one record per opportunity. Repeated evidence is referenced through stable `source_ids` instead of copying source descriptions into every record. This keeps provenance consistent as the register grows.

## Required fields

| Field | Meaning |
| --- | --- |
| `id` | Stable identifier in the form `POC-001-OPP-NNN` |
| `title` | Neutral, action-oriented candidate title |
| `domain` | Primary operating domain |
| `status` | Lifecycle state: `untriaged`, `shortlist_candidate`, `evidence_continue`, `evidence_hold`, or `evidence_stop` |
| `signal` | Observable fact or attributed position that triggered the idea |
| `source_ids` | Two or more entries in the source ledger |
| `join_logic` | Why the sources become more useful when combined |
| `hypothesis` | Falsifiable improvement proposition, not an established conclusion |
| `levers` | One or more possible municipal control levers |
| `efficiency_effect` | Possible resource-to-output effect |
| `effectiveness_effect` | Possible output-to-outcome or service-quality effect |
| `evidence_maturity` | `low`, `medium`, or `high` for the signal only |
| `decision_proximity` | `low`, `medium`, or `high` |
| `controllability` | `low`, `medium`, or `high` |
| `test_cost` | `low`, `medium`, or `high` |
| `risk_level` | `low`, `medium`, or `high` for the next test |
| `caveat` | Material counter-explanation or limitation |
| `next_test` | Cheapest useful test that can falsify or strengthen the hypothesis |
| `approval_flags` | Gates that would apply beyond public desk research |
| `related_case` | Existing dossier if the candidate is adjacent; otherwise `null` |

## Deliberate exclusions

- No composite score, rank, savings promise, blame field, or waste label.
- No personal data, supplier evaluation, or inference about individual performance.
- No recommendation field until the assessment-method readiness gate is met.

## Scaling path

At larger scale, split sources, observations, joins, opportunities, tests, and decisions into separate tables while retaining stable IDs. The JSON register is the v1 interchange format, not the final database model.
