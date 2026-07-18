---
id: CD-2026-001-finance-capital-allocator
status: proposed
owner: finance_capital_allocator
created: 2026-07-17
review_date: 2026-07-31
work_order: WO-2026-007
---

# Agent Report: Finance and Capital Allocation

## Executive Summary

**Recommendation: conditionally allocate, but do not authorize, a maximum cash envelope of EUR 10,000 through four sequential evidence tranches while protecting EUR 4,000 as an unreleased reserve.** The plan favors reversible learning over fixed infrastructure and requires an explicit Founder approval before each commitment or payment.

The proposed envelope is:

| Envelope | Cash ceiling | Share | Release logic |
| --- | ---: | ---: | --- |
| Protected reserve | EUR 4,000 | 40.0% | Not planned for ordinary use; Founder may reallocate only through a recorded decision |
| Tranche A: financial and administrative readiness | EUR 750 | 7.5% | Release only after the operating/legal form and accounting obligations are identified |
| Tranche B: problem and demand validation | EUR 1,250 | 12.5% | Release only for a bounded validation design with measurable learning goals |
| Tranche C: solution and willingness-to-pay validation | EUR 1,750 | 17.5% | Release only after Tranche B meets its evidence gate |
| Tranche D: paid-pilot or MVP proof | EUR 1,750 | 17.5% | Release only after credible demand and an acceptable provisional unit-economic case |
| Controlled contingency | EUR 500 | 5.0% | Founder-approved use only for an evidenced variance within an active tranche |
| **Total maximum** | **EUR 10,000** | **100.0%** | **Allocation proposal only; no spend authorized** |

If evidence is weak, stop after Tranche A or B. In the modeled early-stop downside, spending is capped at EUR 2,000 and EUR 8,000 remains in cash. The current Cologne POC is not automatically entitled to funding: the repository audit rates its agent integration, data quality, and PDF fitness as conditional and records the core normalized financial sample as incomplete.

## Evidence

| Claim | Type | Evidence |
| --- | --- | --- |
| The available planning ceiling is EUR 10,000, and no allocation, vendor, subscription, or purchase has been approved. | fact | `company/work-orders/WO-2026-007-10k-start-capital.md`, Objective and Context |
| Portfolio allocation and every subsequent spend or commitment require explicit Founder approval. | fact | `company/work-orders/WO-2026-007-10k-start-capital.md`, Approval Level; `company/decision-rights.md` |
| The Company-OS prioritizes evidence, testable assumptions, reusable capabilities, explicit ownership, and reversible decisions. | fact | `company/charter.md`, Principles 2-5 |
| The Cologne POC is still internal discovery; its core normalized three-product-group financial sample is open. | fact | `initiatives/cologne-tax-improvements/work-order.md`, Evidence and Closure |
| The POC audit assessed agent integration, data quality, and PDF goal fitness as conditional and prohibited external distribution. | fact | `initiatives/cologne-tax-improvements/reviews/system-audit-2026-07-17/audit-report.md`, Decision and Release Boundary |
| Protecting 40% and releasing the balance sequentially should limit irreversible downside while preserving room for a later validated opportunity. | inference | Finance allocation logic based on the limited current evidence and the charter's reversibility principle; validate at every tranche review |
| Paid behavior is a stronger capital-release signal than interest alone. | inference | Conservative validation principle; must be tested through the defined willingness-to-pay and pilot metrics |

## Assumptions

- **EUR 10,000 is cash available, not revenue, and carries no near-term repayment covenant.** Validate through a Founder declaration and bank/funding documentation before any release.
- **Amounts are gross cash ceilings.** They include VAT and transaction costs unless a qualified adviser confirms recoverability; validate before approving a supplier.
- **The operating entity, tax registration, VAT status, and accounting method may not yet be fixed.** Validate with a qualified German tax adviser or accountant before trading, invoicing, payroll, asset capitalization, or claiming input VAT.
- **Founder labor is not paid from this envelope.** Track Founder hours separately to expose the full economic cost; revisit only through a new capital decision.
- **No employee, contractor, grant, debt, or regulated-service obligation is assumed.** Any such commitment requires a separate cash-flow, legal, and tax review.
- **One venture hypothesis will receive staged attention at a time.** Validate at the first portfolio review; parallel funding would dilute the evidence obtainable from this small pool.
- **Low-cost or free infrastructure is sufficient through demand validation.** Test during Tranches B and C; escalate only where a paid tool is essential to a predefined measurement.

## Recommendation

### 1. Ring-fence the cash before allocating it

- Keep the EUR 10,000 visible in a dedicated business cash account or equivalent clearly segregated ledger once the legal/account structure permits it.
- Record every proposed commitment in a commitment register before purchase: supplier, purpose, gross ceiling, VAT assumption, renewal/cancellation date, accountable owner, Work Order, approval evidence, and remaining envelope.
- Treat subscriptions at their non-cancellable full-term cash exposure, not their monthly headline price.
- Prohibit credit, debt, guarantees, annual auto-renewals, personal reimbursement without receipts, cash withdrawals, and transfers between categories unless the Founder explicitly approves and the decision record is updated.
- Reconcile bank, receipts, commitments, and the allocation ledger monthly. Finance prepares the reconciliation; the Founder reviews and signs it.
- Track both cash spent and accrued/committed exposure so that outstanding invoices cannot overrun a tranche.

### 2. Release capital through staged tranches

| Stage | Ceiling | Accountable delivery owner | Permitted purpose | Evidence required before release | Milestone required to advance | Stop condition |
| --- | ---: | --- | --- | --- | --- | --- |
| A: financial and administrative readiness | EUR 750 | `finance_capital_allocator` | Essential banking, bookkeeping setup, and bounded professional tax/accounting clarification; no branding or product tooling | Entity/operating status, cash ownership, invoice requirements, VAT assumption, chart of accounts, receipt workflow, and written gross-cost quote | Founder accepts a one-page finance-control baseline; obligations and recurring costs are known; no uncapped liability | Legal/tax path is unclear, recurring compliance cost is disproportionate, or a proposed commitment could consume more than the tranche ceiling |
| B: problem and demand validation | EUR 1,250 | `venture_product_lead` | Research recruitment, narrowly targeted discovery materials, or essential access to evidence; default to free channels | Approved venture hypothesis, target customer and problem, sample plan, learning questions, data/privacy review, channel plan, and per-item budget | At least 10 qualified target-customer interactions; at least 5 independently confirm the same costly/urgent problem; at least 3 agree to a concrete next step; all counter-evidence logged | Fewer than 3 of 10 confirm material urgency; no lawful/reachable buyer; evidence depends on unsupported claims; or acquisition learning cannot be measured |
| C: solution and willingness-to-pay validation | EUR 1,750 | `venture_product_lead` | Prototype, landing page, demo, bounded experiment, and only the minimum reusable technical capability needed to test purchase behavior | Tranche B gate met; testable proposition; price hypothesis; prototype scope; measurement plan; security/privacy boundary; cancellation dates | At least 5 qualified solution evaluations; at least 3 explicit price discussions; and at least 2 credible purchase signals such as a signed non-binding pilot intent, deposit-ready confirmation, or procurement next step; provisional contribution margin positive under base assumptions | No credible purchase signal after the predefined sample; material objection cannot be resolved within the ceiling; fixed cost is required before demand proof; or legal/security constraints make the offer uneconomic |
| D: paid-pilot or MVP proof | EUR 1,750 | designated venture owner | Delivery of one bounded pilot/MVP, essential hosting or tooling, and direct pilot costs; exclude production scale-up | Tranche C gate met; Founder-approved pilot scope and price; contract/legal review; delivery owner; data/security controls; support boundary; gross cash-flow model | At least one paid or contractually committed pilot; price covers 100% of direct variable delivery cost; modeled contribution margin at least 50% before Founder labor; time-to-value measured; repeat/expansion decision captured | No paid commitment, direct cash margin non-positive, delivery requires unbounded Founder time, security/compliance remediation exceeds remaining envelope, or customer-specific work is not reusable |

Each stage is a ceiling, not a target. Unspent cash returns to the protected pool and does not become automatically available to the next stage. A milestone is necessary but not sufficient for release: the Founder must still record an explicit approval for each tranche and every spend or commitment.

### 3. Constrain reusable capability investment

Within Tranches C and D combined, cap reusable software, hosting, domains, and tooling at **EUR 1,000 gross and committed** until a paid-pilot signal exists. Prefer month-to-month terms, exportable data, open formats, and cancellation within 30 days. Do not capitalize custom platform work merely because it may be reusable; its value is unproven until at least two plausible uses or one paying use are evidenced.

### 4. Measure learning and provisional unit economics

Maintain a stage scorecard with definitions fixed before each test:

| Metric | Definition | Gate use |
| --- | --- | --- |
| Qualified interaction | Person or organization matching the recorded buyer/user criteria with decision-relevant knowledge | Prevents counting friendly or irrelevant feedback |
| Problem confirmation rate | Qualified interactions independently confirming the defined problem divided by total qualified interactions | Tranche B learning quality |
| Concrete-next-step rate | Qualified interactions agreeing to a dated demo, data review, budget conversation, or procurement step divided by total qualified interactions | Demand strength |
| Credible purchase signals | Documented, attributable buyer actions stronger than general interest; non-binding signals must be labeled as such | Tranche C release gate |
| Customer acquisition cash cost | Direct campaign, recruitment, travel, and sales-tool cash attributable to acquired paying customers divided by acquired paying customers | Early acquisition economics |
| Direct variable delivery cost | Hosting/usage, paid data, transaction fees, contractor delivery, and other cash that increases with the pilot | Contribution margin calculation |
| Contribution margin | `(cash revenue - direct variable delivery cost) / cash revenue`; exclude VAT collected and show Founder labor separately | Tranche D viability |
| Founder delivery hours | Actual hours to acquire, configure, deliver, support, and report per customer | Tests whether apparent margin hides an uneconomic labor burden |
| Learning cost | Gross tranche cash spent divided by material assumptions resolved | Compares capital efficiency across stages |

Do not report lifetime value or payback as reliable until retention and repeat-purchase evidence exists. Show base, downside, and upside assumptions separately; never use a single-point forecast to release cash.

### 5. Tax and accounting boundaries

This is a management allocation proposal, not tax or legal advice. Before the first commercial commitment, confirm with a qualified German adviser as applicable:

- legal form, business registration, tax registration, invoicing obligations, and whether the activity triggers trade tax or other filings;
- VAT status, small-business treatment if relevant, place-of-supply rules, and actual input-VAT deductibility;
- whether software, equipment, setup fees, and internally produced assets are expensed, depreciated, or capitalized;
- treatment of Founder-funded amounts as equity, capital contribution, shareholder loan, or reimbursement;
- documentation and withholding implications for contractors, cross-border suppliers, digital services, grants, and benefits in kind;
- required retention periods and audit trail for quotes, approvals, contracts, invoices, receipts, payments, and cancellations.

Budget decisions should use gross cash outflow until the adviser documents a different treatment. Tax savings, grants, or refundable VAT must not fund a release gate before the cash is actually received or recoverability is sufficiently certain.

### 6. Review cadence and release control

- **Weekly during an active tranche:** delivery owner reports spend, commitments, remaining ceiling, evidence collected, metric denominator, adverse evidence, and forecast-to-complete.
- **At each tranche boundary:** Finance verifies cash and commitments; Product verifies evidence; Legal/Technology review only where their gates apply; Founder records approve, revise, hold, or stop.
- **Monthly regardless of activity:** reconcile cash and commitments, review subscription cancellations, update a 13-week cash outlook, and confirm reserve integrity.
- **Quarterly or on a material change:** Council-level reallocation review if the opportunity, business model, legal form, funding source, or required architecture materially changes.
- **Immediate exception review:** suspected fraud, privacy/security incident, disputed invoice, tax notice, cash variance above EUR 100, or forecast tranche overrun above 10%. Freeze new commitments until resolved.

## Downside Case

### Early evidence failure

If Tranches A and B consume their full ceilings and demand evidence fails, total cash outflow is capped at **EUR 2,000**. No C or D capital is released, the EUR 500 contingency remains unused, and **EUR 8,000 remains in cash**. The closeout deliverable is a short evidence memo, cancellation of all recurring services, settlement of approved liabilities, and an explicit stop/redirect decision.

### Late pilot failure

If A through D are fully spent but contingency is not released, cash outflow is capped at **EUR 5,500** and **EUR 4,500 remains in cash**. If the Founder also releases the full contingency, the maximum planned cash outflow is **EUR 6,000**, leaving the protected **EUR 4,000 reserve**. This case is acceptable only if each prior gate was genuinely passed and the resulting evidence is reusable; otherwise the sequence has failed its control objective.

### Reserve breach rule

Do not use the EUR 4,000 protected reserve to rescue sunk costs, complete an over-budget pilot, or preserve a subscription. A proposal to use it must state the new decision, expected cash return or learning, alternatives, total downside, and stop conditions, and must receive a new recorded Founder approval. If liabilities threaten the reserve, stop all discretionary commitments and produce a 13-week cash preservation plan.

## Risks

| Risk | Likelihood | Impact | Mitigation | Owner |
| --- | --- | --- | --- | --- |
| Small purchases and subscriptions consume the envelope without resolving material assumptions | medium | high | Pre-register each expense against a learning question; monthly cancellation review; stage ceilings | `finance_capital_allocator` |
| False-positive demand signals cause premature build spend | high | high | Require qualified samples, price discussion, attributable buyer action, and adverse-evidence log | `venture_product_lead` |
| VAT, tax, or accounting assumptions understate gross cash needs | medium | high | Budget gross; obtain bounded qualified advice in Tranche A; do not count uncertain recoveries | Founder / qualified adviser |
| Founder labor makes an apparently positive pilot uneconomic | high | high | Track hours per customer and report margin both before and after a shadow labor cost | designated venture owner |
| Tooling creates lock-in, renewal exposure, or stranded capability | medium | medium | EUR 1,000 tooling cap; month-to-month terms; exportability; cancellation register | `technology_architect` |
| A customer-specific pilot diverts the portfolio from reusable capability | medium | high | Bound customization; require reusable artifact and explicit exception approval | `venture_product_lead` |
| Unrecorded commitments cause a tranche or total-envelope overrun | low/medium | high | Commitment ledger, pre-approval, full-term subscription exposure, monthly reconciliation | `finance_capital_allocator` |
| Reserve is used to continue a weak case because of sunk costs | medium | high | Reserve breach rule and fresh Council/Founder decision | Founder |
| Current POC evidence is mistaken for market validation | medium | high | Keep POC discovery separate from buyer, willingness-to-pay, and paid-pilot gates | `chief_of_staff` |

## Unresolved Questions

- What is the legal owner and funding characterization of the EUR 10,000?
- What entity, tax registration, VAT treatment, and bank/accounting setup currently exist?
- Which single venture hypothesis will be proposed for Tranche B, and who is its accountable owner?
- What minimum personal cash reserve or other liquidity does the Founder require outside this business envelope?
- Are Founder time, travel, equipment, insurance, or adviser costs expected to be funded from this ceiling?
- Does the target customer impose procurement, insurance, security, data-protection, or payment-term requirements that could exceed the staged envelope?
- What shadow hourly cost should be used to test whether Founder-intensive delivery is economically credible?

## Proposed Next Action

The `chief_of_staff` should incorporate this report into the proposed Council Decision without treating it as approval. Before requesting the Founder's capital-allocation decision, resolve the cash ownership/legal-form questions and present at least these alternatives: (1) keep all EUR 10,000 unallocated, (2) approve only Tranche A as a ceiling, or (3) approve the staged envelope while retaining transaction-by-transaction Founder gates. If the Founder accepts an allocation, create a separate Work Order for Tranche A; no payment, subscription, contract, transfer, or reserve use follows from this report.
