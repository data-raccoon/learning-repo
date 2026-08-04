---
id: CD-2026-001-legal-risk-governance
status: proposed
owner: legal_risk_governance
created: 2026-07-17
review_date: 2026-07-20
work_order: WO-2026-007
---

# Agent Report: Legal, Risk and Governance

## Executive Summary

Planning the use of up to EUR 10,000 is acceptable, but no allocation should be treated as authority to spend. The safest structure is a ring-fenced reserve plus small, reversible tranches released only after a named owner supplies purpose, evidence, ceiling, stop condition, approval record, and the relevant legal, tax/accounting, privacy/security, procurement, and contracting checks.

The main risks are not the nominal budget alone. They are accidental formation of recurring obligations, unclear tax and accounting treatment, use of personal accounts or credentials, processing personal or confidential data without a lawful and secure design, inadequate ownership of intellectual property, and weak records that make later review or reimbursement unreliable. Until the Founder's explicit approval is recorded, all vendor selection, purchasing, subscriptions, transfers, contract acceptance, credential changes, publication, and external communication remain prohibited.

## Evidence

| Claim | Type | Evidence |
| --- | --- | --- |
| The Founder retains final authority over capital, governance, external commitments, and irreversible actions. | fact | `company/charter.md`, Principle 1. |
| Spend, subscriptions, and credential changes require a Finance recommendation, Legal/Risk or Technology review, and Founder approval. | fact | `company/decision-rights.md`. |
| Silence is not approval; approval must be explicit and attached to the relevant Work Order or Council Decision. | fact | `company/decision-rights.md`. |
| WO-2026-007 authorizes planning only and explicitly prohibits spend, subscriptions, contracts, credential changes, and transfers. | fact | `company/work-orders/WO-2026-007-10k-start-capital.md`. |
| The current Company-OS objective prioritizes a reliable, auditable, supervised operating model before greater autonomy or external integrations. | fact | `company/charter.md`, Company-OS v1 Objective. |
| Small staged releases reduce downside by limiting sunk cost and permitting review before further commitments. | inference | Derived from the Work Order's requirements for sequencing, release gates, ceilings, stop conditions, and a meaningful reserve. |
| A budget approval without transaction-level controls could unintentionally authorize recurring, privacy-relevant, or legally binding commitments. | inference | The decision-rights matrix separates capital recommendations from Founder approval and separately gates external commitments, credentials, and publication. |

## Assumptions

- The relevant operating and tax jurisdiction is Germany. Validate the legal entity, tax residence, VAT status, and business-registration position with a qualified German tax adviser or lawyer before the first transaction.
- The EUR 10,000 is Founder-provided capital, not customer money, regulated client assets, debt, or third-party investment. Validate source, legal form, repayment expectations, and required documentation before receipt or use.
- No employee, contractor, customer, or special-category personal data needs to be processed during initial validation. Validate each proposed tranche with a data inventory before release.
- The Company has not yet adopted separate procurement, expense, records-retention, privacy, incident-response, or contract-playbook policies. Validate against the repository and establish proportionate controls before transactions begin.
- Reversible validation and capital preservation remain preferred. Validate at each tranche review against evidence produced and remaining runway.

## Recommendation

Adopt a **controlled, tranche-based plan** with a meaningful cash reserve and no automatic rollover. Each proposed tranche must be documented in or linked from the Council Decision with:

1. a named accountable owner, purpose, maximum gross amount including taxes and fees, evidence requirement, expiry/review date, and stop condition;
2. an explicit Founder release approval, separate from approval of the overall plan;
3. Finance confirmation of available budget, source of funds, bookkeeping category, invoice requirements, and expected tax/VAT handling;
4. Legal/Risk review for any contract, terms of service, intellectual-property transfer or licence, recurring obligation, refund/cancellation restriction, regulated activity, external communication, or material liability;
5. Security/Privacy review before credentials, integrations, tracking, cloud services, confidential information, or personal data are involved; and
6. a complete transaction record containing the approval, vendor and beneficial recipient, quotation or terms snapshot, invoice/receipt, payment evidence, asset/licence owner, renewal/cancellation date, data-processing role, and outcome evidence.

### Release gates

| Gate | Required evidence | Release condition | Stop condition |
| --- | --- | --- | --- |
| G0: Plan approval | Proposed Council Decision, total ceiling at or below EUR 10,000, reserve, downside case, owners, tranche ceilings | Explicit Founder approval recorded | No explicit approval or material evidence gap |
| G1: Transaction readiness | Written purpose and owner, gross ceiling, vendor comparison or sole-source rationale, finance classification, terms/contract review, privacy/security screening | Explicit Founder approval for the specific spend or clearly bounded tranche | Missing invoice capability, unclear counterparty, personal account requirement, unacceptable terms, or unresolved tax/privacy/security issue |
| G2: Commitment | Approved payment method and business-owned account, terms snapshot, renewal/cancellation controls, asset and credential ownership recorded | Commitment matches approved scope and ceiling | Scope/price changed, auto-renewal cannot be controlled, rights are unclear, or new data processing is introduced |
| G3: Continuation | Outcome evidence, remaining budget, reconciliation, risk review, and next hypothesis | New explicit release decision | Kill criterion met, evidence absent, control failure, incident, dispute, or cumulative ceiling reached |
| G4: Closeout | Invoice/receipt, payment record, accounting handoff, cancellation/renewal status, access removal, data deletion/retention record, lessons learned | Owner and Finance confirm closure | Missing records, open liability, continued access, or unresolved data/contract obligation |

### Prohibited actions until separately approved

- Spending, transferring, reimbursing, subscribing, accepting vendor terms, signing contracts, or making verbal commitments.
- Using personal payment accounts, personal cloud tenants, shared credentials, or unapproved reimbursement arrangements for Company activity.
- Splitting purchases to avoid an approval ceiling or extending a pilot through automatic renewal.
- Giving a vendor customer, employee, Founder, prospect, or confidential data before privacy/security review and any required data-processing agreement.
- Publishing claims, contacting external parties, or presenting the capital plan as approved or funded.
- Buying regulated financial products, lending, investing in securities or cryptoassets, making political/charitable contributions, or paying related parties without a separate decision and professional review.
- Engaging workers or contractors without classification, tax, confidentiality, intellectual-property, data-access, and termination terms being reviewed.
- Operating in a regulated field, collecting customer funds, or issuing tax invoices before the applicable legal and tax prerequisites are confirmed.

### Minimum controls

- Keep Company and personal funds, accounts, credentials, records, and assets separate.
- Use least privilege, multi-factor authentication, named accounts, an access register, and prompt access revocation.
- Default to no personal data; minimize collection, define retention/deletion, and prohibit production data in unapproved experiments.
- Require written vendor terms and preserve the exact version accepted; flag governing law, liability, indemnity, IP, confidentiality, data use, model-training rights, subcontractors, termination, refunds, price changes, and auto-renewal.
- Obtain suitable invoices and maintain an immutable chronological approval and transaction ledger; reconcile budget committed, paid, refundable, and remaining.
- Record conflicts of interest and related-party relationships before vendor selection.
- Do not capitalize, expense, deduct, reclaim VAT, or reimburse an amount based solely on an agent recommendation; Finance must obtain qualified advice where treatment is uncertain.
- Escalate suspected fraud, data loss, security incidents, legal demands, tax notices, disputes, or control breaches immediately; freeze the affected tranche pending review.

## Risks

| Risk | Likelihood | Impact | Mitigation | Owner |
| --- | --- | --- | --- | --- |
| Spend occurs without explicit authority or exceeds the cumulative ceiling | medium | high | Transaction-level Founder approval, central ledger, gross ceilings, no purchase splitting, reconciliation before each release | Founder / Finance |
| Capital source or legal form is undocumented, creating tax, accounting, ownership, or repayment ambiguity | medium | high | Document source and legal form before receipt/use; obtain German tax/accounting advice | Finance |
| Vendor terms create recurring costs, foreign-law exposure, uncapped liability, weak remedies, or lock-in | high | medium-high | Terms snapshot and review; prefer short, cancellable pilots; renewal register; reject unacceptable clauses | Legal/Risk / tranche owner |
| Incorrect VAT, income-tax, capitalization, expense, or reimbursement treatment | medium | high | Qualified tax/accounting advice, compliant invoices, consistent chart of accounts and supporting records | Finance |
| Personal data or confidential information is processed without lawful basis, transparency, minimization, security, or processor terms | medium | high | Data inventory, privacy/security gate, DPA where required, least data, retention/deletion controls | Security/Privacy / Legal/Risk |
| Company IP, source code, designs, data, domains, or accounts are personally owned or subject to vendor training/reuse rights | medium | high | Business-owned accounts, written IP/licence terms, repository and asset register, prohibit unreviewed reuse/training rights | Legal/Risk / Technology |
| Contractor or worker engagement is misclassified or lacks confidentiality, IP assignment, tax, and access controls | low-medium | high | Separate professional review and written agreement before engagement | Legal/Risk / Finance |
| Procurement is conflicted, poorly evidenced, or directed to an unclear counterparty | low-medium | medium-high | Counterparty identification, conflict declaration, comparison or documented sole-source rationale | Tranche owner / Finance |
| Records are incomplete, preventing audit, tax filing, dispute defence, cancellation, or measurement of outcomes | medium | high | Mandatory evidence pack, records owner, retention schedule, monthly reconciliation and closeout gate | Finance / Operations |
| Validation drifts into regulated activity or unsupported public claims | low-medium | high | Scope check before launch; Legal/Risk review for regulated domains and external claims; Founder publication approval | Legal/Risk / Founder |
| Security incident, credential misuse, or service loss follows tool/vendor adoption | medium | high | Security review, MFA, least privilege, backups/export plan, incident escalation, offboarding | Security/Privacy / Technology |
| Reserve is depleted by low-value pilots or non-refundable commitments | medium | high | Ring-fenced reserve, small tranches, kill criteria, no automatic rollover, downside review | Founder / Finance |

## Unresolved Questions

Questions requiring qualified professional advice before the relevant transaction:

- What legal entity or individual will receive and spend the capital, and should the funding be documented as equity/capital contribution, shareholder loan, reimbursement float, or another form?
- What business-registration, trade-tax, corporate/income-tax, VAT registration, VAT recovery, bookkeeping, annual-accounts, and document-retention duties apply in Germany?
- Are Founder-funded pre-incorporation or pre-registration expenses deductible or reimbursable, and what contemporaneous evidence is required?
- Does any proposed product, customer segment, payment flow, public-sector interaction, dataset, AI use, or advice enter a regulated domain or trigger licensing, procurement, consumer, competition, accessibility, records, or transparency obligations?
- For each vendor and data flow, who is controller, joint controller, or processor; is a data-processing agreement required; and are international transfers, subprocessors, telemetry, or model-training uses lawful and acceptable?
- What insurance, liability limitation, IP assignment/licensing, open-source compliance, confidentiality, contractor-classification, and employment controls are proportionate before external delivery?
- What accounting basis and approval evidence are necessary for hardware, software, domains, cloud credits, marketing, professional services, travel, and mixed personal/business use?
- Are any proposed counterparties related parties, and what conflict, transfer-pricing, market-terms, or disclosure requirements apply?

Operational questions for the Founder/Council:

- What minimum reserve must remain unavailable for experiments?
- Does Founder approval apply to every individual transaction, or may narrowly bounded tranches authorize multiple listed transactions under one ceiling?
- Who will hold the business payment account, bookkeeping system, contract register, renewal calendar, asset register, and data-processing register?
- What loss threshold, incident type, control failure, or evidence shortfall automatically freezes all remaining capital rather than one tranche?

## Proposed Next Action

The `chief_of_staff` should incorporate these controls and unresolved questions into the proposed Council Decision without treating them as approval. Before requesting the Founder decision, confirm that every proposed release has a gross ceiling, owner, purpose, evidence requirement, review date, kill condition, reserve impact, and applicable Finance, Legal/Risk, and Security/Privacy gates. After Founder approval of the plan, create separate transaction or tranche Work Orders and obtain professional German tax/legal advice before the first transaction where entity, tax, regulated-activity, employment, IP, or personal-data treatment remains uncertain.
