---
id: WO-2026-007
status: completed
owner: chief_of_staff
created: 2026-07-17
review_date: 2026-07-20
---

# Work Order: EUR 10,000 Start-Capital Plan

## Objective

Produce a Council-reviewed, decision-ready proposal for allocating a maximum of EUR 10,000 in start capital across Company-OS and first-venture validation needs without authorizing spend.

## Context

### Facts

- The Founder requested delegation of a EUR 10,000 start-capital plan on 2026-07-17.
- No allocation, vendor, subscription, or purchase has yet been approved in this Work Order.
- Portfolio allocation requires independent Council review and explicit Founder approval.

### Assumptions

- Capital preservation, learning velocity, and reversible validation are preferred over premature fixed commitments.
- The current Cologne POC is discovery work and may be one candidate for limited validation funding, not an automatic funding recipient.

## Accountable Owner

`chief_of_staff` is the sole writer of the consolidated Council Decision. Each Council member is sole writer of its named report file.

## Constraints

- Budget ceiling: EUR 10,000 total.
- Distinguish cash reserve, validation spend, reusable capabilities, compliance/admin, and contingency.
- State amounts, sequencing, release gates, kill criteria, and review dates.
- No spend, subscription, contract, credential change, or transfer is authorized.
- Council members work independently and do not see other positions before submitting.

## Deliverables

- [x] Five independent Agent Council reports.
- [x] One consolidated Council Decision with options, dissent, risks, and recommendation.
- [x] Explicit Founder decision request.

## Acceptance Criteria

- [x] Proposed allocations sum to no more than EUR 10,000.
- [x] Every release tranche has an owner, purpose, evidence requirement, ceiling, stop condition, and review date.
- [x] A meaningful reserve and downside case are considered.
- [x] Legal, tax/accounting, security, technology, product, and portfolio risks are explicit.
- [x] Recommendation is marked proposed, not approved.

## Dependencies

- `company/templates/agent-report.md`
- `company/templates/council-decision.md`
- Current Company-OS and POC evidence.

## Ownership Boundaries

| Path or system | Writer | Read-only contributors |
| --- | --- | --- |
| `company/decisions/CD-2026-001-10k-start-capital/portfolio-strategist.md` | `portfolio_strategist` | none |
| `company/decisions/CD-2026-001-10k-start-capital/finance-capital-allocator.md` | `finance_capital_allocator` | none |
| `company/decisions/CD-2026-001-10k-start-capital/legal-risk-governance.md` | `legal_risk_governance` | none |
| `company/decisions/CD-2026-001-10k-start-capital/venture-product-lead.md` | `venture_product_lead` | none |
| `company/decisions/CD-2026-001-10k-start-capital/technology-architect.md` | `technology_architect` | none |
| `company/decisions/CD-2026-001-10k-start-capital/council-decision.md` | `chief_of_staff` | Council members read-only after submission |

## Approval Level

`founder-approval-required`

The Founder approved planning and delegation. Explicit Founder approval is still required for the allocation decision and every later spend or commitment.

## Evidence and Closure

- Five independent Council reports:
  - [Portfolio Strategy](../decisions/CD-2026-001-10k-start-capital/portfolio-strategist.md)
  - [Finance and Capital Allocation](../decisions/CD-2026-001-10k-start-capital/finance-capital-allocator.md)
  - [Legal, Risk and Governance](../decisions/CD-2026-001-10k-start-capital/legal-risk-governance.md)
  - [Venture Product](../decisions/CD-2026-001-10k-start-capital/venture-product-lead.md)
  - [Technology Architecture](../decisions/CD-2026-001-10k-start-capital/technology-architect.md)
- [Proposed Council Decision](../decisions/CD-2026-001-10k-start-capital/council-decision.md)
- Planning is complete. The Founder decision remains `pending`; no allocation, spend, subscription, contract, transfer, credential change, outreach, data access, deployment, or publication is approved.
