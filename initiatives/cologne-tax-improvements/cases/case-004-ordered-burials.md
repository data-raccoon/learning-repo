---
id: POC-001-CASE-004
status: recommendation_draft
owner: data_analytics_engineer
created: 2026-07-17
review_date: 2026-08-07
---

# Case Assessment: Ordered Burials and Cost Recovery

## Identity and status

- **Review status:** `recommendation_draft`
- **Accountable analyst:** `data_analytics_engineer`
- **Decision owner:** City of Cologne public-order service owner, with Finance, HR, Procurement, and legal support; exact accountability to be confirmed.
- **Last evidence update:** 2026-07-17.
- **Publication status:** `internal_only`.

## Originating signal

- **Sources and roles:** gpaNRW Cologne audit, `official_assurance`; City response, `primary_authoritative`; live Cologne procurement notice, `primary_authoritative`.
- **Signal:** The gpaNRW found delays in some legally time-sensitive cases, untimely pursuit of cost-recovery claims, a financially relevant backlog, and a high 2023 deficit per completed ordered burial. A new procurement for delivery of ordered burials was published on 2026-07-07 with a bid deadline of 2026-08-17.
- **Why it warrants review now:** Contract renewal and acknowledged process backlogs create a current opportunity to improve operational data, contract management, legal compliance, and recovery without reducing the dignity or timeliness of the statutory service.

## Public purpose and baseline

- **Purpose:** Ensure a lawful, timely, and dignified burial when the responsible parties do not arrange one, while identifying responsible relatives and recovering eligible public cost where lawful.
- **Priority order:** The City states that identifying relatives and arranging the burial take priority over downstream cost recovery. The POC accepts this service and legal priority.
- **Documented controls:** gpaNRW reports a comprehensive written procedure, case master sheet, chronological action log, cost and income overview, four-eyes closure, supervisory samples, and periodic local audit. These are positive controls.
- **Relevant legal timing:** The audit applies burial-law deadlines and recommends documenting statutory extensions where appropriate. Legal interpretation remains with the City.

## Current state

- **Timeliness:** gpaNRW found that cases were not always processed within burial-law deadlines. The City responded that the extension mechanism is now used and documented where appropriate.
- **Recovery backlog:** gpaNRW found that potential reimbursement claims were not pursued promptly and consistently. The City confirmed that rising cases and current staffing prevented complete processing of downstream claims and that backlogs remained.
- **Staffing response:** The City states that staffing need was analysed in 2024 and an additional requirement was submitted through the responsible internal process. Current approval, staffing, and backlog status are unknown.
- **2023 peer position:** The deficit was EUR 1,306 per completed burial. Only four of 19 comparison cities had a higher figure.
- **2023 unit economics:** Cologne reported EUR 1,511 revenue and EUR 2,817 expenditure per completed burial. The peer medians were EUR 1,056 and EUR 1,933 respectively. High revenue therefore did not offset the comparatively high expenditure.
- **Trend:** The reported deficit per completed burial was EUR 992 in 2020, EUR 1,002 in 2021, EUR 645 in 2022, and EUR 1,306 in 2023. The series alone does not identify cause.
- **Audit caution:** gpaNRW explicitly states that its review did not establish uneconomic conduct by Cologne.
- **Procurement:** A current open procedure titled "Durchführung von ordnungsbehördlich angeordneten Bestattungen" carries identifier `2026-0108-320-21` and a published deadline of 2026-08-17.

## Source coverage

| Perspective | Source used | Evidence role | Coverage status | Temporal and scope fit | Gap or follow-up |
| --- | --- | --- | --- | --- | --- |
| Legal, process, financial, and peer baseline | gpaNRW audit | `official_assurance` | `covered` | Strong through 2023 and the audit period | Reconcile definitions and update 2024-2026 |
| Official explanation and response | City response to gpaNRW | `primary_authoritative` | `covered` | Explains priority, workload, and 2024 staffing request | Verify implementation and current backlog |
| Procurement lifecycle | Cologne procurement platform | `primary_authoritative` | `covered` | Current notice and deadline | Capture scope, lots, value, award, reporting clauses, and later modifications |
| Current service operations | Controlled case and finance aggregates | `primary_observation` | `unavailable` | Essential for quantified recommendation | Obtain privacy-safe monthly aggregate after approval |
| Structural statistical context | INKAR | `official_statistical_context` | `not_applicable` | Regional statistics cannot evaluate this workflow | Use case-flow and service evidence |
| Affected-party experience | None | `stakeholder_account` | `not_covered` | Dignity and timeliness are material | Use complaints or aggregated quality evidence; avoid family-level research |

## Claim-evidence matrix

| Claim ID | Claim | Type | Supporting evidence | Contradiction or limit | Confidence | Remaining test |
| --- | --- | --- | --- | --- | --- | --- |
| CLM-001 | Potential reimbursement claims were not pursued promptly and consistently in the audit period | `attributed_position` | gpaNRW F2/E2 and City acknowledgement | Current status unknown | `high` historically | Update backlog and recovery data |
| CLM-002 | The 2023 deficit per completed burial was EUR 1,306 | `fact` | gpaNRW table | Definition must remain stable for updates | `high` | Reconcile to Cologne accounts |
| CLM-003 | High expenditure per case materially contributed to the 2023 deficit | `analytical_inference` | EUR 2,817 expenditure and EUR 1,511 revenue; peer table | Case mix and provider prices may differ | `medium` | Decompose service, staffing, and case-mix cost |
| CLM-004 | More recovery staff would pay for themselves | `assumption` | Backlog has financial effect | Recoverability, age, staff cost, and legal effort unknown | `low` | Backlog value and marginal recovery experiment |
| CLM-005 | The live procurement can still be changed to add requirements | `assumption` | Procedure is open | Procurement law and current documents may restrict material change | `low` | Legal and procurement review; otherwise use mobilization or next cycle |

## Positions and affected parties

- **City position:** Timely burial and relative identification properly come before recovery; rising volume and staffing constraints created a downstream backlog.
- **gpaNRW position:** Use legal extensions consistently, pursue recovery promptly, analyse staffing against volume, and address financially relevant backlogs.
- **Affected parties:** Deceased persons, relatives, service providers, public-order staff, taxpayers, and communities using burial services.
- **Safeguard:** No efficiency measure may delay, degrade, or commoditize dignified statutory service.

## Cause and controllability analysis

- **Observed symptoms:** Recovery backlog, high 2023 unit expenditure, elevated deficit, and historic timeliness exceptions.
- **Plausible causes:** Rising case volume, staffing below workload, service prices, case complexity, delayed relative identification, weak workflow separation, missing ageing and recoverability triage, or incomplete integration between case and finance records.
- **Alternative explanations:** Cologne may face a different case or service mix from peers; higher expenditure may fund legitimate quality or local requirements.
- **Controllable now:** Backlog measurement, triage, staffing experiment, case-to-invoice coding, claim workflow, management reporting, and future contract-performance requirements.
- **Not established:** Waste, excessive provider prices, recoverable total, or the optimal permanent staffing level.

## Options

| Option | Fiscal and lifecycle effect | Service and outcome effect | Constraints | Risks | Reversibility |
| --- | --- | --- | --- | --- | --- |
| Continue current prioritization without backlog intervention | Avoids change cost; claims may age or expire | Protects primary service | Existing capacity | Persistent lost recovery and limited visibility | High |
| Time-boxed recovery backlog team | Temporary staff cost versus measured collections | Ring-fences primary burial workflow | Access, training, legal complexity | Chasing low-value or unrecoverable claims | High |
| Permanent staffing increase | Recurring personnel cost | Could stabilize both service and recovery | Budget and recruitment | Capacity fixed above future need | Medium |
| Outsource recovery activity | Variable contract cost | May accelerate work | Legal basis, dignity, data protection, debt treatment | Poor incentives and reputational harm | Medium |
| Workflow and contract-data redesign | Implementation cost | Better control and future evaluation | Procurement timing and systems | Data burden without use | High |

## Recommendation

### Preliminary assessment

There is high-confidence evidence of a historical recovery and workload-control problem and a current procurement window. There is not enough current operational evidence to set a savings target, conclude that provider pricing is excessive, or select permanent staffing.

### Recommended action

Separate the protected statutory service lane from a measured recovery lane. First, produce a current aggregated backlog and recoverability inventory. Then run a twelve-week backlog intervention prioritized by legal expiry, expected recoverable value, and processing effort. Compare incremental collections and prevented expiry with incremental staff and operating cost.

In parallel, ensure that contract mobilization and management can provide case-linked but privacy-minimized service, invoice, timeliness, and quality data. Do not alter a live procurement unless the procurement owner and legal review confirm that the change is lawful and non-material; otherwise implement permissible contract-management reporting or prepare requirements for the next cycle.

- **Expected effect:** Reduce avoidable claim ageing, establish the economically justified capacity level, and create reliable unit-cost evidence without compromising service dignity.
- **Financial effect:** Unknown until backlog value, recovery probability, and marginal processing cost are measured.
- **Owner:** Public-order service owner, with Finance and HR; Procurement owns contract constraints; Data Protection and Legal own safeguards.
- **Success indicators:** Burial deadline compliance; extension documentation; backlog count and value by age; days to claim; claim, collection, expiry, and write-off rates; incremental collections net of intervention cost; expenditure and deficit per completed case; complaints and quality exceptions.
- **Review point:** Four weeks after backlog inventory and twelve weeks after intervention start; contract review after award or mobilization.
- **Readiness:** Conditional operational recommendation ready. Staffing and procurement decisions remain evidence-gated.
- **Confidence:** `high` for measurement and backlog intervention need; `medium` for the proposed experiment; `low` for savings magnitude.

## Evidence log

| ID | Role | Source | Date | Retrieval | Use and limitation |
| --- | --- | --- | --- | --- | --- |
| EVD-001 | `official_assurance` | [gpaNRW Cologne audit 2024/2025, ordered burials](https://gpanrw.de/sites/default/files/2026-01/Gesamtbericht_Stadt_Koeln_2024_2025.pdf) | 2024/2025 report using data through 2023 | 2026-07-17 | Findings, recommendations, peer and unit-cost data; not current operations |
| EVD-002 | `primary_authoritative` | [City response to gpaNRW](https://gpanrw.de/sites/default/files/2026-02/Stellungnahme_Stadt_K%C3%B6ln_2025.pdf) | 2025 response | 2026-07-17 | Workload, priority, and staffing explanation; current implementation not verified |
| EVD-003 | `primary_authoritative` | [Cologne procurement platform](https://vergabeplattform.stadt-koeln.de/NetServer/) | Notice published 2026-07-07 | 2026-07-17 | Current procedure title, identifier, regime, and deadline; documents and value not yet captured |

## Assurance and approvals

- No personal, relative, health, address, estate, or case-level data is authorized for the POC.
- Any controlled data request, live-procedure action, or external communication requires Founder approval and relevant legal review.
- This recommendation protects statutory timeliness and dignity ahead of recovery optimization.
