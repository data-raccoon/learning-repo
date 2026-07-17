---
id: POC-001-AUDIT-RISK-001
status: active
owner: legal_risk_governance
created: 2026-07-17
review_date: 2026-07-31
---

# Risk Register: POC-001 System Audit

| ID | Risk | Category | Likelihood | Impact | Early signal | Mitigation | Owner | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| R-001 | Structural validation is mistaken for semantic data quality. | analytical | high | high | A candidate advances without exact locator, transformation, comparability, or freshness evidence. | Complete the normalized sample; add structured claim evidence and semantic/mutation tests. | data_analytics_engineer | open |
| R-002 | Unrecorded handoffs obscure accountability or violate exclusive write ownership. | governance | medium | high | An artifact names a read-only role as owner without a writer/handoff record. | Define nested Work Order precedence and require accepted delivery handoffs. | chief_of_staff | open |
| R-003 | A PDF claim cannot be verified by a decision-maker from the document. | evidence | high | high | A material number or current-status statement has no source ID or direct citation. | Add claim-level citations and independently re-gate link/claim coverage. | operations_knowledge | open |
| R-004 | Directional approval is misread as authority to execute uncontrolled work. | governance | medium | high | A Wave A/B item starts without a new Work Order, owner, stop condition, or specific approval gate. | Add an execution decision record and require scoped Work Orders for every continued item. | chief_of_staff | open |
| R-005 | The dated evidence snapshot becomes stale or a source changes silently. | evidence | medium | medium | Use after review date or source checksum/link change. | Store versions/checksums and run source-health/freshness revalidation. | market_intelligence | open |
| R-006 | Detached or inaccessible PDF pages are misused or cannot be navigated. | accessibility/governance | medium | medium | A body page circulates without classification or a screen-reader user cannot follow its structure. | Add persistent classification and produce a tagged PDF or accessible companion. | operations_knowledge | open |

## Escalations

- Any external distribution or publication.
- Acceptance of any high-impact residual risk.
- Controlled-data access, spend, production action, or service/governance change.

## Accepted Risks

None. Acceptance requires explicit Founder approval and a review date.

