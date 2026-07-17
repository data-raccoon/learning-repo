---
id: CD-2026-001-TECHNOLOGY-ARCHITECT
status: proposed
owner: technology_architect
created: 2026-07-17
review_date: 2026-08-17
---

# Agent Report: Technology Architecture for EUR 10,000 Start Capital

## Executive Summary

From a technology perspective, the portfolio should not make a material platform commitment yet. The current Company-OS is a local, dependency-free, supervised operating model, while the first POC still lacks its core normalized data sample, end-to-end semantic quality controls, and execution-ready output traceability. The highest-value technical action is therefore to prove a small reusable evidence pipeline before buying a broad software stack or building a production platform.

I recommend a **technology activation ceiling of EUR 3,000** in four gated tranches and retaining **EUR 7,000 outside the technology allocation as portfolio reserve**. The first tranche is a no-spend architecture and tool-selection proof. Later tranches may be released only after their evidence gates pass and the Founder explicitly approves the specific spend, subscription, vendor, credential, or deployment. Open formats, replaceable adapters, export tests, least privilege, data minimization, and reproducible local builds should be mandatory to preserve optionality.

This is a proposed allocation, not approval. It does not authorize spend, subscriptions, credentials, vendor selection, production deployment, controlled-data access, or a public release.

## Evidence

| Claim | Type | Evidence |
| --- | --- | --- |
| The Company-OS v1 objective is a reliable, auditable, supervised agent model before increased autonomy or external integrations. | fact | `company/charter.md`, "Company-OS v1 Objective". |
| Shared capabilities should be reusable and venture-specific complexity isolated. | fact | `company/charter.md`, Principle 3. |
| Spend, subscriptions, credential changes, material architecture commitments, and production deployment require explicit Founder approval. | fact | `company/decision-rights.md`; `company/work-orders/WO-2026-007-10k-start-capital.md`. |
| The current repository validation is dependency-free and the configured workflow uses a local Python environment. | fact | `README.md`, "Validate" and repository map. |
| The first POC remains internal discovery; a public prototype is a separate Founder-approved decision. | fact | `experiments/poc-001-cologne-public-spending/README.md`, "Non-goals" and "Next checkpoint". |
| The POC's core three-product-group normalized sample is not complete. | fact | `experiments/poc-001-cologne-public-spending/reviews/system-audit-2026-07-17/audit-report.md`, Data Quality finding 1. |
| Existing POC checks are stronger on structure than semantic quality, provenance, freshness, comparability, and transformation correctness. | fact | `experiments/poc-001-cologne-public-spending/reviews/system-audit-2026-07-17/audit-report.md`, Data Quality findings 2-5. |
| The current PDF is adequate only as an internal discussion draft; external distribution remains prohibited and claim-level traceability is incomplete. | fact | `experiments/poc-001-cologne-public-spending/reviews/system-audit-2026-07-17/audit-report.md`, Decision and PDF Goal Fitness. |
| Buying a broad platform before the normalized sample and semantic quality gate pass would create cost and lock-in without proving that the core data problem is tractable. | inference | Derived from the open POC evidence gaps and the charter's reversibility and evidence principles. Validate through Tranche 0 and Tranche 1 proof points. |
| A small adapter-based evidence pipeline can plausibly serve later analytics and AI ventures if it stores source, transformation, validation, and claim metadata in open schemas. | inference | Derived from the portfolio's software, analytics, and AI scope in `company/charter.md`. Validate by demonstrating a second use case without changing the core schema. |

## Assumptions

- The existing developer workstation and local Python environment are adequate for the first proof. Validate by recording runtime, storage, and failure behavior for the normalized sample before buying compute.
- Public or synthetic data is sufficient for the first technical proof. Validate by classifying every input and blocking controlled or personal data until a separate approved data-access Work Order exists.
- The initial workload is low-volume and asynchronous. Validate with measured source size, processing time, run frequency, and concurrency; revisit architecture only when thresholds are exceeded.
- Open-source libraries and free service tiers can cover most of Tranches 0 and 1. Validate with a tool inventory, licence review, total-cost estimate, and an offline export/rebuild test.
- No production service-level objective is required during discovery. Validate with the product owner before any hosted prototype or operational commitment.
- EUR 7,000 can remain uncommitted at this stage. This is a technology recommendation for Council consolidation, not a claim about the final portfolio allocation.

## Recommendation

### Allocation and release plan

| Tranche | Owner | Purpose and preferred approach | Ceiling | Evidence required before release or completion | Stop condition |
| --- | --- | --- | ---: | --- | --- |
| 0 — architecture baseline | `technology_architect` | **Build/configure locally first:** inventory data flows, schemas, trust boundaries, current tools, licences, recurring costs, export paths, and operational ownership. Define vendor-neutral interfaces and decision thresholds. | EUR 0 | Architecture note; data classification; threat model; tool scorecard; three-year total-cost comparison; explicit buy-vs-build criteria; approval map. | Stop vendor evaluation if the POC objective or accountable owner is unresolved. Do not create accounts or credentials. |
| 1 — reusable evidence and data-quality proof | `data_analytics_engineer` | **Build the differentiating core; buy commodity execution only if measured constraints require it:** open-schema claim/evidence ledger, provenance, transformation records, semantic tests, freshness checks, deterministic export, and normalized sample. | EUR 900 | Three-product-group sample reproduced from clean inputs; claim-to-source traceability; comparability and mutation tests; documented failure modes; second-use-case schema test; independent QA pass. | Stop if stable identifiers, lawful source use, reproducibility, or meaningful semantic checks cannot be demonstrated within the ceiling. Do not fund scale-up. |
| 2 — security, privacy, and recoverability baseline | `security_privacy` | **Buy commodity controls where cheaper to operate; keep data portable:** secrets management, encrypted backup, access logging, dependency/secret scanning, retention and restore procedures. Prefer services with export, deletion, regional-processing, and role-based-access support. | EUR 600 | Threat model reviewed; no secrets in repository; least-privilege roles; encrypted backup; successful restore drill; retention/deletion test; vendor data-processing and exit checklist; security review pass. | Stop onboarding if required export/deletion, access control, processing-location, or contractual evidence is unavailable. No controlled data. |
| 3 — automation and reproducible delivery proof | `platform_devops` | **Configure before custom-building:** isolated checks for schema, quality, security, document build, artifact hash, and release evidence. Use replaceable adapters around any hosted CI or storage provider. | EUR 500 | Clean-environment build; pinned dependencies/toolchain; automated quality and security checks; immutable evidence manifest; monthly cost alert; complete local export and rebuild; QA pass. | Stop if the workflow cannot be reproduced outside the selected vendor or recurring cost cannot be bounded. |
| 4 — optional hosted validation | `software_engineer` | **Buy managed commodity hosting, do not build platform infrastructure:** one time-boxed, non-production prototype only after product evidence supports it. Use static/serverless patterns and no controlled data where feasible. | EUR 1,000 | Separate approved Work Order; target user and test defined; security/privacy/QA gates passed; cost cap and auto-shutdown; observability and rollback; accessible output; explicit Founder deployment/publication approval. | Kill after the timebox if no named user test, measurable learning, safe data path, or credible continuation case exists; shut down resources and export/delete data. |
| Portfolio reserve — not allocated to technology | Founder / Council | Preserve optionality for validated product, legal/admin, customer, or downside needs. No technology team claim on this amount. | EUR 7,000 | New Council or scoped Work Order evidence and explicit Founder approval. | Do not convert reserve into subscriptions, prepaid credits, hardware, or platform commitments merely to use the budget. |
| **Total ceiling** |  |  | **EUR 10,000** |  |  |

The technology tranches are sequential by default. Unspent amounts return to reserve and do not roll forward automatically. Each paid tranche should have a maximum initial commitment of one month or the shortest practical term, no auto-renewal unless explicitly approved, a named cancellation owner, and a review within 30 days of activation.

### Buy-versus-build boundary

- **Build or configure in-house:** venture-specific evidence schemas, transformation logic, semantic quality rules, claim-to-source traceability, approval records, and vendor adapters. These encode differentiating knowledge and auditability.
- **Prefer managed or established commodity tools:** source control hosting, CI runners, encrypted backup, secrets storage, monitoring, and low-volume hosting—only when their full operational cost is lower than maintaining equivalents and exit requirements pass.
- **Do not build now:** a general agent platform, custom workflow engine, data lake, warehouse, identity system, Kubernetes estate, proprietary dashboard framework, or production-grade public portal. Current evidence does not justify their operational burden.
- **Do not buy now:** annual enterprise plans, prepaid cloud commitments, overlapping AI subscriptions, broad analytics suites, vendor-specific data pipelines, dedicated servers, or hardware. They reduce reversibility before demand and scale are known.

### Architecture and security baseline

1. Store canonical evidence and decisions in versioned, human-readable, machine-readable open formats; generated PDFs and dashboards are outputs, not sources of truth.
2. Separate shared schemas and validation interfaces from venture-specific transformations and presentation code.
3. Wrap external APIs, model providers, storage, and automation services behind narrow adapters; maintain a tested local/export path for critical artifacts.
4. Minimize collected data; use public or synthetic data by default; document classification, retention, deletion, and lawful-use boundaries before ingestion.
5. Apply least privilege, separate human and automation identities, prohibit secrets in source control, and log material access and release actions.
6. Pin dependencies and toolchain versions, record source and artifact hashes, and require clean-environment rebuilds.
7. Set spend alerts, hard usage ceilings where supported, auto-shutdown for experiments, and a named owner for every recurring resource.
8. Require QA, security/privacy, and Founder gates before production, publication, controlled data, credentials, or external integrations.

### Portfolio-level technical kill criteria

Pause further technology allocation and return unused funds to reserve if any of the following occurs:

- the normalized evidence proof cannot reproduce material claims from clean inputs;
- source identity, permissions, provenance, comparability, or deletion obligations cannot be established;
- a selected vendor cannot provide a complete, usable export or the workflow cannot be rebuilt without it;
- measured recurring run cost exceeds the approved ceiling or cannot be attributed to an owner and workload;
- operational maintenance consumes more capacity than the validated user learning justifies;
- independent QA or security/privacy review finds an unresolved high-impact risk;
- no named user, decision, or reusable second use case is demonstrated by the tranche review date.

## Risks

| Risk | Likelihood | Impact | Mitigation | Owner |
| --- | --- | --- | --- | --- |
| Premature platform purchase or custom build consumes capital before data feasibility is proven. | medium | high | No-spend Tranche 0; sequential gates; EUR 3,000 technology ceiling; reserve does not roll forward automatically. | `technology_architect` |
| Structural checks are mistaken for semantic data quality. | high | high | Make normalized sample, provenance, comparability, mutation tests, and independent QA prerequisites for paid scale-up. | `data_analytics_engineer` |
| Vendor lock-in prevents migration or increases recurring cost. | medium | high | Open schemas, adapters, short terms, export/deletion tests, local rebuild, no prepaid commitments. | `platform_devops` |
| Credentials, personal data, or controlled records enter an immature workflow. | medium | high | Public/synthetic data default; classification and threat model; least privilege; secrets scanning; separate approval before controlled data. | `security_privacy` |
| Subscription sprawl and auto-renewal create silent burn. | medium | medium | Central inventory, monthly ceiling alerts, named cancellation owner, shortest practical term, explicit renewal approval. | `finance_capital_allocator` |
| Reusable platform work becomes abstract infrastructure without a second consumer. | medium | medium | Require a second-use-case schema test before promoting any component into `shared/`. | `technology_architect` |
| Prototype hosting creates production expectations and support burden. | medium | high | Time-boxed non-production label, auto-shutdown, rollback, no SLA, explicit deployment/publication gates. | `software_engineer` |
| Open-source dependency or licence risk is not tracked. | medium | medium | Dependency inventory, licence/security review, pinned versions, replaceability test, update owner. | `security_privacy` |

## Unresolved Questions

- Which user decision and measurable learning would justify the optional hosted validation tranche?
- What are the measured volume, runtime, update frequency, and retention needs of the normalized sample?
- Will any future evidence require controlled, personal, licensed, or non-EU-hosted data processing?
- Which current tools or subscriptions already exist and can be reused without new spend or credential changes?
- What maximum monthly recurring cost and operational-hours budget will the Founder accept after the initial proof?
- Which second venture or workflow is the best test of genuine reuse for the evidence schema and automation interfaces?

## Proposed Next Action

Approve only the **planning activity of Tranche 0 at EUR 0** under a scoped follow-up Work Order, with `technology_architect` accountable and read-only input from data, platform, security/privacy, QA, and finance. The output should be the architecture baseline, tool inventory, threat model, buy-vs-build scorecard, total-cost view, and tranche-specific approval requests. After independent assurance, return the completed evidence to the Founder; do not activate Tranches 1-4 or any vendor, subscription, credential, spend, deployment, or public release without explicit approval.
