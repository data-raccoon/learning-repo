---
id: POC-001-CASE-002
status: evidence_building
owner: data_analytics_engineer
created: 2026-07-17
review_date: 2026-08-07
---

# Case Assessment: Citywide Software Licence Management

## Identity and status

- **Review status:** `evidence_building`
- **Accountable analyst:** `data_analytics_engineer`
- **Decision owner:** City of Cologne IT governance owner, to be confirmed.
- **Last evidence update:** 2026-07-17.
- **Publication status:** `internal_only`.

## Originating signal

- **Source and evidence role:** Cologne Rechnungsprüfungsamt, `primary_authoritative`, corroborated by gpaNRW, `official_assurance`.
- **Signal:** A complete central overview of software licences and their cost and utilization was still missing in the audit of the 2023 annual accounts; gpaNRW subsequently recommended improving legally compliant and economic licensing and advancing licence-management software procurement.
- **Why it warrants review:** The stated gap affects asset completeness, compliance exposure, purchasing decisions, unused licences, and negotiating leverage across a large administration.

## Public purpose and baseline

- **Purpose:** Ensure that software entitlements are complete, lawful, cost-effective, used, renewably controlled, and visible for accounting and operational decisions.
- **Historical baseline:** The local audit states that it had requested central software-licence overviews since its 2012 audit of the 2008 opening balance.
- **Expected control:** A central inventory connecting licence entitlement, deployment or allocation, utilization where lawful and proportionate, cost, contract, owner, renewal, and accounting treatment.
- **Budget and total exposure:** Not available in the reviewed public evidence.

## Current state

- **2023 account audit:** The local audit reported that central overviews were still absent and the project remained incomplete.
- **2024 gpaNRW observation:** Overall IT operating and governance conditions were assessed positively, with targeted improvement potential in decentralized resource visibility and licence management.
- **gpaNRW recommendation:** Improve lawful and economic licensing and consistently advance procurement of licence-management software.
- **July 2026 status:** Unknown. Public procurement search did not provide sufficient evidence that a citywide solution is operational.
- **Financial performance:** Unknown. No complete licence population, unused-licence value, compliance exposure, or tool business case was located.

## Source coverage

| Perspective | Source used | Evidence role | Coverage status | Fit | Gap or follow-up |
| --- | --- | --- | --- | --- | --- |
| Decision, control, and accounting baseline | Local annual-account audit | `primary_authoritative` | `covered` | Direct for status through the 2023 account audit | Verify current project decision, owner, milestones, and budget |
| Current inventory and usage | None public | `primary_observation` | `unavailable` | Essential for savings and compliance assessment | Obtain inventory coverage and top-vendor reconciliation |
| External assurance | gpaNRW Cologne audit | `official_assurance` | `covered` | Direct, current audit scope and explicit recommendation | Retain exact scope and current implementation status |
| Structural and outcome context | INKAR | `official_statistical_context` | `not_applicable` | Regional indicators cannot assess internal software controls | Use internal operational data |
| Investigative history | No BdSt case used | `secondary_advocacy` | `not_applicable` | Official audits are the originating evidence | None required |
| Affected-party experience | None | `stakeholder_account` | `not_covered` | Useful for process design, not for establishing the control gap | Gather internally during implementation |

## Claim-evidence matrix

| Claim ID | Claim | Type | Supporting evidence | Contradiction or limit | Confidence | Remaining test |
| --- | --- | --- | --- | --- | --- | --- |
| CLM-001 | A complete central licence overview was still missing in the 2023 account audit | `fact` | Local audit section 4.1.2 | Status may have changed since | `high` historically | Verify July 2026 status |
| CLM-002 | The gap persisted for many years | `fact` | Local audit references request since 2012 | Milestones during interval not reconstructed | `high` | Build project chronology |
| CLM-003 | gpaNRW found targeted improvement potential in licence management | `attributed_position` | gpaNRW F1/E1 | Audit does not quantify loss | `high` | Record city response and implementation |
| CLM-004 | Completing licence management will generate net savings | `assumption` | General control logic only | Tool, implementation, data, and operating costs unknown | `low` | Baseline top-vendor spend, usage, and compliance risk |

## Cause and controllability analysis

- **Observed symptom:** Missing complete central overview and unfinished project.
- **Plausible causes:** Decentralized acquisition and administration, fragmented ownership, heterogeneous licence metrics, incomplete discovery data, unclear governance, or delayed tool procurement.
- **Alternative explanation:** Partial operational controls may exist but not satisfy accounting completeness or central visibility requirements.
- **Controllable now:** Ownership, minimum data standard, top-vendor prioritization, reconciliation cadence, procurement decision, renewal gates, and reporting to local audit.
- **Not established:** Material over-licensing, under-licensing, a specific euro loss, or vendor misconduct.

## Options

| Option | Fiscal and lifecycle effect | Service and outcome effect | Constraints | Risks | Reversibility |
| --- | --- | --- | --- | --- | --- |
| Continue current project without new gate | Unknown | May eventually close gap | Existing dependencies unknown | Further delay and weak accountability | High |
| Buy a tool immediately | Licence and implementation cost unknown | Could automate discovery and reconciliation | Data ownership, integrations, procurement | Tool without clean data or process | Medium |
| Minimum viable central register first, then tool business case | Low initial process cost; exposes material vendors and data gaps | Faster control visibility and clearer requirements | Requires cross-department ownership | Manual effort and incomplete long tail | High |
| Full central operating model and tool rollout | Highest implementation effort; potential compliance and purchasing benefit | Durable control if adopted | Change capacity and decentralized systems | Long program and adoption failure | Medium |

## Recommendation

### Preliminary assessment

The historical control gap is substantiated by two independent official audit perspectives. The current gap and financial impact are not yet established. Buying software before confirming data ownership, coverage, and control design could add cost without resolving the underlying issue.

### Recommended action

First verify the current implementation status. If the central overview is still incomplete, create a twelve-week minimum viable licence register covering the highest-value software vendors and all material renewal decisions. Record entitlement, allocation or deployment, permitted utilization evidence, cost, contract owner, renewal date, compliance position, and reconciliation status. Use the result to produce a tool and operating-model business case rather than treating tool procurement as the outcome.

- **Expected effect:** Immediate risk visibility, prevention of uninformed renewals, and evidence for a proportionate permanent solution.
- **Financial effect:** Not yet quantified; report identified avoidable renewals, compliance exposure, and implementation cost separately.
- **Owner:** Central IT governance with Finance, Procurement, decentralized IT owners, and local audit assurance.
- **Success indicators:** Share of top-vendor spend reconciled; share of material renewals reviewed; unresolved entitlement exceptions; unused allocation identified; control owner assigned; audited update cadence.
- **Review point:** End of status verification and again after the twelve-week register slice.
- **Readiness:** Conditional operational recommendation. Execute only if the July 2026 status check confirms the gap remains.
- **Confidence:** `high` in need for status verification; `medium` in the minimum-register approach; `low` in any savings estimate.

## Evidence log

| ID | Role | Source | Date | Retrieval | Use and limitation |
| --- | --- | --- | --- | --- | --- |
| EVD-001 | `primary_authoritative` | [Cologne audit of the 2023 annual accounts, section 4.1.2](https://ratsinformation.stadt-koeln.de/getfile.asp?id=1060520&type=do) | 2023 accounts; published later | 2026-07-17 | Direct statement that overview was absent and project incomplete |
| EVD-002 | `official_assurance` | [gpaNRW Cologne audit 2024/2025, IT F1/E1](https://gpanrw.de/sites/default/files/2026-01/Gesamtbericht_Stadt_Koeln_2024_2025.pdf) | 2024/2025 | 2026-07-17 | Positive overall context plus targeted recommendation; no quantified loss |
| EVD-003 | `secondary_journalistic` | [City summary of gpaNRW audit](https://www.stadt-koeln.de/politik-und-verwaltung/presse/mitteilungen/27686/index.html) | 2025-06-20 | 2026-07-17 | Confirms audit scope and intermunicipal comparison; not licence-specific detail |

## Assurance and approvals

- The recommendation does not assume savings or purchase authority.
- Procurement, spend, credentials, or external communication require their normal approval gates.
- Security and privacy review are required before collecting device- or user-level utilization data.
