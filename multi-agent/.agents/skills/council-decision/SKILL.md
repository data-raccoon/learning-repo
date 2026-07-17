---
name: council-decision
description: Run a supervised Agent Council decision for venture launches, pauses or stops, portfolio allocation, material strategy changes, material architecture commitments, and governance changes. Use when a choice needs independent portfolio, finance, product, technology, and legal-risk analysis plus explicit Founder approval.
---

# Council Decision

1. Frame the decision, options, deadline, reversibility, and evidence in a Work Order using `company/templates/work-order.md`.
2. Confirm that the decision is material enough for Council review. Route routine scoped work to one accountable owner instead.
3. Ask the root orchestrator to run `portfolio_strategist`, `finance_capital_allocator`, `legal_risk_governance`, `venture_product_lead`, and `technology_architect` independently and in parallel.
4. Require each member to return `company/templates/agent-report.md`. Do not reveal other members' conclusions before all reports finish.
5. Have `chief_of_staff` consolidate the five reports with `company/templates/council-decision.md`. Preserve dissent, evidence gaps, and approval gates.
6. Save the proposal in `company/decisions/` or the venture's `decisions/` directory with status `proposed`.
7. Request an explicit Founder decision. Never interpret silence or a Council recommendation as approval.
8. Record the human outcome and create follow-up Work Orders only after approval.

