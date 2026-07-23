---
id: CD-2026-001-portfolio-strategist
status: proposed
owner: portfolio_strategist
created: 2026-07-17
review_date: 2026-08-17
---

# Agent Report: Portfolio Strategy for EUR 10,000 Start Capital

## Executive Summary

The EUR 10,000 should be treated as scarce validation capital, not as a mandate to spend or as a budget for completing Company-OS. The portfolio currently has a governed operating model and one discovery POC, but no evidence in scope of an approved venture charter, customer demand, distribution, or a recommendation-ready Cologne opportunity. The POC audit also records an incomplete normalized sample and insufficient claim-level traceability. Funding a product build now would therefore concentrate capital before the portfolio has established a demand signal.

I recommend a staged barbell: preserve **EUR 4,000 as an unreleased reserve**, make at most **EUR 4,000 available to two sequential venture-validation cycles**, and cap **shared enabling capability, specialist assurance, and contingency at EUR 2,000**. Each release should be reversible, evidence-gated, and separately Founder-approved. No tranche should fund general platform polish, autonomous external actions, production deployment, or a long-term subscription.

This is a proposed portfolio envelope, not approval to spend.

## Evidence

| Claim | Type | Evidence |
| --- | --- | --- |
| The Founder retains final authority over capital and external commitments, and Company-OS prioritizes evidence, reusable capability, explicit ownership, and reversibility. | fact | `company/charter.md`, Principles 1-5 |
| The operating model requires evidence, an owner, review date, and kill criteria for every venture lifecycle transition. | fact | `company/operating-model.md`, Venture Lifecycle |
| The only venture-adjacent asset identified in scope is POC-001, which remains discovery rather than an approved funding recipient. | fact | `company/work-orders/WO-2026-007-10k-start-capital.md`, Context; `initiatives/cologne-tax-improvements/work-order.md`, Objective |
| POC-001 has seven `continue` decisions and one `hold`, but `continue` authorizes only a named next evidence test and none has passed recommendation readiness. | fact | `initiatives/cologne-tax-improvements/evidence-sprints/sprint-001/sprint-results.md`, Executive Decision |
| The POC audit found the core normalized three-product-group sample incomplete and the PDF unsuitable as an execution handoff without further traceability and ownership detail. | fact | `initiatives/cologne-tax-improvements/reviews/system-audit-2026-07-17/audit-report.md`, Data Quality and Goal Interpretation |
| The current decision brief passed only for internal review; external distribution remains approval-gated. | fact | `initiatives/cologne-tax-improvements/reports/decision-brief-2026-07-17/quality-gate.md`, Decision |
| The model capability backlog contains 21 proposed items, while its first usable milestone requires MOD-001 through MOD-008. | fact | `company/model-capability-backlog.md`, Epics and Initial Milestone |
| A product-build-first allocation would be premature because the evidence in scope establishes research feasibility, not a paying customer, repeatable channel, or validated willingness to pay. | inference | Derived from the absence of demand evidence in WO-2026-007 and the POC's discovery/readiness limitations above. |
| Releasing small, sequential tranches should buy more decision-relevant learning per euro and reduce downside relative to one large commitment. | inference | Consistent with the charter's evidence and reversibility principles and the operating model's gated lifecycle. |
| Shared capability should receive capital only when it is required by at least two approved validation cycles or materially reduces a measured bottleneck. | recommendation | Portfolio-compounding interpretation of `company/charter.md`, Purpose and Principle 3. |

## Assumptions

- **Founder time is the binding resource as well as cash.** Validate by time-boxing each cycle and recording Founder hours, not only direct costs.
- **At least two credible venture theses can be framed within 30 days.** Validate with Venture Charters that identify a reachable customer, painful problem, business model, KPI, budget ceiling, and kill criteria. If only one passes intake, do not force diversification; leave the second cycle unreleased.
- **Useful discovery and public-only prototypes can initially be run with existing tools.** Validate through a zero-cost baseline before requesting paid tooling.
- **Customer discovery can be performed lawfully and with limited cash.** Validate the contact method, privacy basis, and communication approval before outreach; no outreach is authorized by this report.
- **The Cologne POC may yield a venture thesis but is not automatically the first funded cycle.** Validate it against other charters using the same scoring rubric: pain, buyer, urgency, access, differentiation, evidence quality, time-to-test, and capital at risk.
- **EUR 4,000 is a meaningful downside reserve.** Reassess after the first cycle using actual burn, remaining runway, and the quality of learning obtained.

## Recommendation

### Strategic options considered

| Option | Allocation logic | Portfolio advantage | Principal downside | Position |
| --- | --- | --- | --- | --- |
| Preserve all capital | Keep EUR 10,000 unreleased until a venture has demand evidence | Maximum downside protection | Slower learning; may leave testable uncertainty unresolved | Viable fallback if no charter passes intake |
| Single concentrated bet | Commit most capital to the Cologne POC or one product | Focus and simpler execution | Treats discovery evidence as venture evidence; high lock-in risk | Reject at current evidence level |
| Broad micro-bet portfolio | Divide funds across many ideas | More surface area | Shallow tests, coordination cost, weak ownership | Reject until repeatable intake and scoring exist |
| **Staged barbell** | Protect reserve; fund at most two sequential validation cycles and narrowly shared capability | Balances learning, optionality, and capital preservation | Requires discipline to stop and leave funds unused | **Recommend** |

### Proposed portfolio envelope

| Envelope | Ceiling | Accountable owner | Purpose | Evidence required before release | Stop condition |
| --- | ---: | --- | --- | --- | --- |
| Protected reserve | **EUR 4,000** | Founder | Preserve optionality and downside capacity | Separate future Council proposal and Founder approval | Remains unreleased under this decision |
| Validation Cycle 1 | **EUR 2,000** | Named venture owner | Test the highest-ranked approved Venture Charter: customer problem, buyer access, and cheapest credible solution/delivery hypothesis | Approved charter; baseline evidence pack; test plan; itemized ceiling; communication/privacy review where applicable | Stop at ceiling or four weeks; stop earlier on any kill criterion below |
| Validation Cycle 2 | **EUR 2,000** | Named venture owner | Validate either a second thesis or the next uncertainty of Cycle 1 | Cycle 1 review completed; comparison against at least one alternative; explicit Council/Founder release decision | No release if Cycle 1 evidence is weak, ownership is unavailable, or a second charter fails intake |
| Reusable capability | **EUR 1,250** | `technology_architect` or named delivery owner | Minimal data, evaluation, automation, or measurement capability serving at least two approved cycles | Two named consumers; reuse case; free/open-source baseline; acceptance test; exit/export plan | Stop if single-venture specific, unmeasured, duplicative, or dependent on an unapproved recurring commitment |
| Legal/accounting/data assurance | **EUR 500** | `legal_risk_governance` with Founder-selected provider if external | Resolve a specific blocking question for an approved validation test | Written question, why internal evidence is insufficient, fixed quote or fee ceiling, and expected decision enabled | Stop if advice is generic, non-blocking, or creates an ongoing engagement |
| Contingency | **EUR 250** | Founder | Absorb a bounded variance in an already approved validation tranche | Documented variance and explicit Founder approval | No use for scope expansion or a new experiment |
| **Total maximum envelope** | **EUR 10,000** | Founder retains release authority | n/a | Every non-reserve release remains separately approval-gated | Unused amounts return to reserve |

The allocation deliberately leaves **EUR 4,000 (40%) protected** and exposes no more than **EUR 2,000 before the first evidence review**. It also caps Company-OS/shared capability at 12.5%: governance and automation are enabling assets, not substitutes for venture evidence.

### Sequence and release logic

1. **Zero-cost intake (days 0-10):** produce and score at least two Venture Charters. Include Cologne only if it can name a customer, buyer, urgent problem, lawful access path, and business model. No capital release.
2. **Cycle 1 (maximum four weeks / EUR 2,000):** attack the most decision-critical uncertainty with the cheapest test. Prefer interviews, source validation, manual concierge work, or a narrow prototype over product build.
3. **Evidence review:** record actual spend, Founder time, customer evidence, counterevidence, reusable assets, and whether kill criteria fired. Compare the thesis again with the best unfunded alternative.
4. **Cycle 2 decision:** release up to EUR 2,000 only for a clearly stronger next test or a second qualified thesis. Do not release merely because the envelope exists.
5. **Capability/assurance releases:** approve only against a demonstrated blocker in an active cycle. Prefer portable data, test fixtures, evaluation methods, and reusable customer-learning artifacts over bespoke infrastructure.
6. **30- and 60-day reviews:** at day 30 review Cycle 1; at day 60 decide whether to continue validating, pause, stop, or return all unused capital to reserve. Scaling requires a new Council decision.

### Portfolio-level kill criteria

Stop a validation cycle and preserve the remainder when any of the following occurs:

- no named accountable venture owner can sustain the time-box;
- after 15 qualified customer conversations, fewer than three independently confirm the same material problem and current workaround, unless a pre-approved alternative evidence threshold was defined;
- the presumed buyer cannot be reached lawfully or cannot control a budget relevant to the proposed offer;
- evidence shows the problem is infrequent, low-cost, already adequately solved, or dependent on prohibited/non-obtainable data;
- the test reaches its EUR 2,000 or four-week ceiling without resolving its primary uncertainty;
- material legal, privacy, procurement, or reputational risk cannot be reduced within the envelope;
- the concept requires production build, long-term subscription, hiring, paid acquisition scale, or external commitment before demand evidence exists;
- evidence quality cannot be made reproducible enough for a continue/stop decision.

No automatic conversion from `continue` to additional funding is allowed. A positive Cycle 1 result should authorize only a specifically bounded Cycle 2 test, not venture launch or scale.

## Risks

| Risk | Likelihood | Impact | Mitigation | Owner |
| --- | --- | --- | --- | --- |
| Capital is consumed by Company-OS polish rather than market learning | medium | high | Cap reusable capability at EUR 1,250; require two consumers and a measured blocker | `chief_of_staff` |
| Cologne POC receives funding because it is most developed, not because it has the best venture economics | high | high | Require comparable Venture Charters and common scoring before Cycle 1 selection | `portfolio_strategist` |
| Small tranches create false confidence from weak samples | medium | high | Pre-register primary uncertainty, evidence threshold, counterevidence, and kill criteria | Named venture owner |
| Founder time is omitted from burn and makes tests appear artificially cheap | high | medium | Track Founder and agent/human hours alongside cash | `finance_capital_allocator` |
| Reserve is gradually reclassified as contingency | medium | high | Require a new Council decision to release protected reserve | Founder / `chief_of_staff` |
| Paid tools create recurring commitments or data lock-in | medium | medium | Free baseline, monthly terms only if approved, export/exit plan, no annual prepayment | `technology_architect` |
| Outreach or data access crosses an approval, privacy, or procurement boundary | medium | high | Separate Founder approval and legal/privacy review before external contact or restricted access | `legal_risk_governance` |
| Two-cycle design fragments limited attention | medium | medium | Run cycles sequentially; one accountable owner; no parallel second cycle by default | `chief_of_staff` |

## Unresolved Questions

- What personal runway, tax obligations, and liquidity needs sit outside this EUR 10,000? The protected reserve may need to be higher once those facts are known.
- Is the capital intended for a legal entity, an individual Founder, or a future entity? This affects which costs can responsibly be contemplated.
- How many Founder hours per week are available for customer discovery and delivery?
- Which customer segments and distribution channels are already accessible without paid acquisition?
- Are there any existing subscriptions, hardware, credits, datasets, or professional-services relationships that reduce the need for cash?
- What minimum commercial signal should precede further funding: paid pilot, signed letter of intent, procurement-qualified discovery, or another segment-specific indicator?
- Which alternative venture thesis will be compared with the Cologne opportunity to avoid incumbent-bias allocation?

## Proposed Next Action

The `chief_of_staff` should consolidate this report with the other independent Council lenses and present the Founder with a decision between: (1) the staged barbell envelope above, (2) full capital preservation pending stronger inputs, or (3) a revised envelope after personal-runway/legal-entity facts are supplied. If the staged barbell is approved, assign one owner to produce two comparable Venture Charters and a zero-cost scoring memo before any release request.

No spend, subscription, contract, outreach, data access, or transfer is authorized by this recommendation.
