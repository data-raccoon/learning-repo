---
id: CD-2026-001-VPL
status: proposed
owner: venture_product_lead
created: 2026-07-17
review_date: 2026-08-14
---

# Agent Report: Product Validation Use of EUR 10,000 Start Capital

## Executive Summary

From a product perspective, the capital should buy evidence about a valuable, usable, and responsibly framed customer outcome before it buys a product. I recommend a staged ceiling of EUR 10,000, with EUR 3,000 retained as an unreleased reserve. The first paid releases should validate the customer problem and repair the POC's core evidence chain; prototype and pilot funding should be conditional on explicit learning thresholds.

The proposed product outcome is not a public "waste detector." It is a traceable decision-support workflow that helps an identified user formulate and verify better review questions about municipal resources, services, and outcomes. The current Cologne POC is useful discovery input but does not yet establish demand, repeat use, willingness to adopt or pay, or a reproducible end-to-end data proposition. No spend is authorized by this report.

## Evidence

| Claim | Type | Evidence |
| --- | --- | --- |
| The Founder requested a plan for a maximum of EUR 10,000; no allocation or purchase is approved. | fact | `company/work-orders/WO-2026-007-10k-start-capital.md` |
| The Company Charter prioritizes evidence, testable assumptions, reusable capabilities, reversible decisions, and Founder authority over capital and external commitments. | fact | `company/charter.md` |
| POC-001 is an investigation intended to produce review candidates, not findings of waste, misconduct, or causality. | fact | `experiments/poc-001-cologne-public-spending/README.md` |
| The current POC has 29 traceable hypotheses, eight sprint decisions, and five calibration cases, giving useful material for moderated tests. | fact | `experiments/poc-001-cologne-public-spending/README.md`; `experiments/poc-001-cologne-public-spending/reviews/system-audit-2026-07-17/audit-report.md` |
| The normalized three-product-group sample, consistent claim-level provenance, and execution-ready PDF handoff remain incomplete. | fact | `experiments/poc-001-cologne-public-spending/reviews/system-audit-2026-07-17/audit-report.md` |
| The current PDF is suitable only for internal decision discussion and is not approved for external distribution. | fact | `experiments/poc-001-cologne-public-spending/reports/decision-brief-2026-07-17/quality-gate.md`; subsequent qualification in `experiments/poc-001-cologne-public-spending/reviews/system-audit-2026-07-17/audit-report.md` |
| The highest-value early use of capital is therefore problem/evidence validation rather than public-product development. | inference | Demand is untested and the core data proof remains open; committing to a build now would combine customer, evidence, usability, and governance risk. |
| A reserve of EUR 3,000 preserves the option to respond to validated needs instead of pre-allocating the entire ceiling. | recommendation | Reversible staged funding is consistent with the Work Order assumptions and the Company Charter. |

## Assumptions

- **Primary user hypothesis:** municipal controllers, auditors, budget analysts, or policy staff have recurring difficulty linking resources, outputs, outcomes, and source provenance. Validate through at least 12 problem interviews across at least three roles; do not assume Cologne will participate.
- **Secondary user hypothesis:** civic intermediaries such as journalists or civil-society analysts may value a neutral, traceable question-formulation workflow. Validate separately because their workflow, risk tolerance, and willingness to pay may differ.
- **Value hypothesis:** users can reach a defensible review question faster, with fewer source-navigation steps and fewer unsupported interpretations, using the POC workflow than using their current method. Test by observed task comparison, not stated enthusiasm alone.
- **Adoption hypothesis:** at least one defined segment has a recurring workflow, an identifiable adopter or budget owner, and willingness to continue into a bounded pilot. Validate with follow-up commitments; a complimentary interview is not demand evidence.
- **Data hypothesis:** the normalized sample can preserve source, period, definition, transformation, and comparability metadata well enough for users to verify material claims. Validate by completing and independently checking the sample before prototype claims are shown externally.
- **Acquisition assumption:** qualified participants can be recruited without disproportionate cost. Start with founder/network outreach and professional associations; paid recruitment is released only if two documented low-cost channels fail.
- **Incentive assumption:** some participants may accept incentives, but public-sector ethics or employer rules may prohibit them. Obtain legal-risk guidance before offering anything of value.

## Recommendation

### Proposed capital envelope

| Pool | Ceiling | Accountable owner | Purpose and evidence deliverable | Release condition | Stop condition |
| --- | ---: | --- | --- | --- | --- |
| Customer/problem validation | EUR 1,200 | `venture_product_lead` | Recruitment, permitted incentives, interview accessibility, 12-18 interviews, coded problem evidence, segment comparison, current-workflow map | Founder approves the specific tranche and research protocol; privacy/legal review completed before participant data is collected | Stop if fewer than 8 qualified interviews can be secured after two recruitment approaches, or if no recurring high-cost problem appears in at least one segment |
| Core data/evidence validation | EUR 1,500 | `data_analytics_engineer` | Complete the three-product-group normalized sample, structured claim/evidence ledger, transformation notes, and independent spot-check evidence | A scoped Work Order defines source rights, acceptance criteria, and QA reviewer | Hold product work if provenance or comparability cannot support verification of material claims; stop the selected slice if two remediation cycles fail |
| Prototype and usability tests | EUR 1,300 | `venture_product_lead` | Low-fidelity workflow prototype, at least two iterations, 8 moderated task tests, task-success and misinterpretation log | Problem evidence passes Milestone 1 and the test content passes the evidence gate | Stop if fewer than 5 of 8 target users can complete the core task after two iterations, or if material claims are repeatedly misread as findings of waste |
| Accessibility and ethics assurance | EUR 700 | `qa_reliability` with `legal_risk_governance` review | Accessible research materials, keyboard/screen-reader/contrast checks, neutral-language and foreseeable-harm review, remediation record | Prototype content and participant protocol are frozen for review | Do not advance while a critical accessibility barrier, privacy issue, or material misleading-claim risk remains open |
| Bounded pilot | EUR 1,800 | owner assigned in a new pilot Work Order | One segment-specific pilot, onboarding/support, usage evidence, outcome comparison, adoption interview, and pilot closeout | Milestones 1-3 pass; one named pilot partner or internal proxy commits to the test; Founder separately approves any external contact, terms, data, and spend | Stop if no qualified pilot commitment, no repeat use within the agreed workflow window, no measurable improvement over baseline, or controlled data is required without approval |
| Compliance/admin allowance | EUR 500 | `legal_risk_governance` / finance-designated owner | Only product-validation-specific privacy, terms, accounting, or participant-governance needs identified by review | Specific need and vendor/service are documented and Founder-approved | Return unused amount to reserve; no speculative subscription or standing commitment |
| Unreleased reserve | EUR 3,000 | Founder | Preserve runway for the best-supported next test, remediation, or deliberate stop | New evidence-backed Work Order and explicit Founder approval | Do not release to rescue a failed hypothesis without a changed premise and new test |
| **Total ceiling** | **EUR 10,000** |  |  |  |  |

Ceilings are not targets. Unused amounts remain in reserve; passing a milestone permits a Founder decision on the next tranche but does not automatically release it. Prefer one-off, cancellable services and reusable research/data artifacts over subscriptions, custom production code, branding, paid promotion, or a public launch.

### Sequence and learning milestones

1. **Milestone 0 - evidence readiness (EUR 0 before approval):** freeze the product hypotheses, segments, measures, participant-data plan, and baseline task. Handoff threshold: a Work Order with one owner, research script, consent/privacy handling, neutral terminology, and a claim-safe test artifact.
2. **Milestone 1 - problem/segment validation (up to EUR 1,200):** pass only if at least one segment shows a recurring problem in at least 6 qualified interviews, at least 4 participants demonstrate a concrete recent workaround or consequence, and at least 3 agree to a prototype follow-up. Treat numerical thresholds as decision aids alongside coded qualitative evidence, not statistical proof.
3. **Milestone 2 - evidence-chain validation (up to EUR 1,500, may run in parallel with interviews):** pass only when the normalized sample meets its Work Order, a reviewer can trace every material displayed value to source and transformation, and unresolved comparability limits are visible to the user.
4. **Milestone 3 - usable and safe prototype (up to EUR 2,000 including assurance):** pass only if at least 5 of 8 target users independently complete the core task, no critical accessibility barrier remains, and no participant converts a review candidate into an allegation after the final iteration. Record failures and counter-evidence, not only aggregate success.
5. **Milestone 4 - pilot commitment (up to EUR 1,800):** start only with a named segment, baseline, test window, success metric, data boundary, exit condition, and accountable owner. A non-binding expression of interest is insufficient; require a concrete participation commitment that incurs no unauthorized external obligation.
6. **Milestone 5 - venture handoff:** recommend a Venture Charter only if the pilot demonstrates repeat use, a measurable improvement in the selected workflow, an identifiable adopter/economic buyer, and a credible route to lawful data access. Otherwise hold, pivot the user/problem pair, or stop and preserve the reserve.

### User-value and experiment measures

- **Task outcome:** time and steps needed to formulate one traceable review question and verify its evidence trail against a fixed case.
- **Comprehension:** whether the user correctly distinguishes plan from actual, output from outcome, signal from finding, and correlation from attribution.
- **Decision usefulness:** whether the workflow changes the user's next evidence request or review action, with the reason captured.
- **Trust calibration:** ability to identify source limitations and uncertainty, rather than maximizing perceived confidence.
- **Adoption:** return for a second task, willingness to supply a real bounded use case, and identification of an owner or budget route.
- **Equity/accessibility:** successful completion using keyboard and screen-reader paths where applicable; recruitment and test materials accessible by design; document who is excluded by source, language, or access assumptions.

### Product kill criteria

Stop or materially reframe the product thesis if any of the following occurs:

- no segment passes Milestone 1 after the planned sample and one revised recruitment/message cycle;
- users value the analysis only as a one-off report and show no recurring workflow or adoption path;
- the evidence chain cannot reliably support the core task without controlled data whose access is not feasible or proportionate;
- the product repeatedly encourages defamatory, politicized, or causally unsupported interpretations that cannot be mitigated through workflow and language design;
- accessibility remediation would require replacing the core interaction and no accessible alternative can meet the same outcome within the ceiling;
- the pilot shows no material improvement over the baseline or no repeat use;
- cumulative approved spend reaches EUR 7,000 without all pre-pilot milestones passing; retain the EUR 3,000 reserve pending a fresh Founder decision.

## Risks

| Risk | Likelihood | Impact | Mitigation | Owner |
| --- | --- | --- | --- | --- |
| Building for an interesting dataset rather than a recurring user problem | high | high | Problem interviews and observed baseline tasks precede build; require segment and follow-up thresholds | `venture_product_lead` |
| Participants mistake signals for findings of waste or misconduct | medium | high | Neutral language, comprehension tests, counter-evidence, claim-level provenance, legal-risk review | `venture_product_lead` / `legal_risk_governance` |
| Public-sector participants cannot accept incentives or disclose workflows/data | medium | medium | Pre-clear incentives; offer no-value participation; minimize collection; use synthetic/public cases | `legal_risk_governance` |
| Small convenience sample creates false confidence | high | medium | Recruit across roles, record negative cases, avoid statistical claims, require behavioral evidence | `venture_product_lead` |
| Data provenance or comparability fails behind a polished prototype | high | high | Separate Milestone 2 gate and independent QA before moderated product claims | `data_analytics_engineer` / `qa_reliability` |
| Accessibility is deferred until after interaction choices harden | medium | high | Include accessible materials and assistive-technology checks from first prototype | `qa_reliability` |
| Pilot introduces personal, controlled, procurement-sensitive, or politically sensitive data | medium | high | Public/synthetic data by default; data inventory and approval before any controlled source | `legal_risk_governance` |
| Early subscriptions or custom code consume runway without learning | medium | medium | One-off reversible purchases, explicit ceilings, no auto-renewal, reserve protected | tranche owner / Founder |
| External partner interest is treated as permission to communicate or commit | medium | high | Founder approval remains required before outreach, terms, publication, or commitment | `chief_of_staff` |

## Unresolved Questions

- Which initial segment has the strongest combination of recurring need, accessible participants, and lawful data access?
- Is the economic buyer the same person as the day-to-day user, and what budget or procurement route would apply?
- What baseline task and outcome would be credible enough to show improvement without implying financial savings?
- Can the core value be demonstrated entirely with public data, or does a viable workflow depend on controlled operational data?
- What participant-data retention period and research-consent mechanism will legal-risk approve?
- Which portions of the EUR 500 compliance/admin allowance are actually needed after finance and legal review?

## Proposed Next Action

The `chief_of_staff` should compare this independent product position with the other Council reports and preserve any dissent in a proposed Council Decision. If the Founder approves a first release, create a separate customer/problem-validation Work Order with a maximum initial tranche of EUR 1,200, named research owner, participant-data controls, experiment protocol, milestone date, and stop conditions. In parallel, the existing POC owner may propose the EUR 1,500 evidence-validation Work Order. Neither action authorizes spend, outreach, incentives, data access, subscriptions, contracts, or publication without the applicable Founder approval.
