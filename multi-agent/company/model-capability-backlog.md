---
id: model-capability-backlog-001
status: proposed
owner: ai_automation_engineer
created: 2026-07-17
review_date: 2026-08-17
---

# Model Capability and Guardrails Backlog

## Objective

Enable the Company-OS to use large, small, hosted, and local models safely and economically. Admit models based on observed task performance, route work by capability and risk, and enforce critical boundaries outside model prompts.

## Success Criteria

- Every model configuration used for Company-OS work has a versioned, evidence-backed capability profile.
- Every material Work Order declares a risk class and minimum model tier.
- A deterministic preflight check blocks ineligible model-task combinations.
- Lower-capability models can perform bounded work without inheriting permissions they have not earned.
- Existing Founder Approval Gates remain mandatory for every model and provider.
- Evaluation results capture quality, safety, latency, and cost and can expire or trigger reevaluation.

## Prioritization

| Priority | Meaning |
| --- | --- |
| P0 | Required before models receive differentiated permissions. |
| P1 | Required for supervised production use across multiple model classes. |
| P2 | Optimization and scale after the control loop is reliable. |

## Epic 1: Governance and Contracts

### MOD-001 — Define model tiers and task risk classes

- **Priority:** P0
- **Owner:** `legal_risk_governance`
- **Contributors:** `ai_automation_engineer`, `security_privacy`, `chief_of_staff`
- **Deliverable:** A new model-governance policy in the company governance area.
- **Acceptance criteria:**
  - Define capability tiers T0 through T4 and task risk classes R0 through R4.
  - State that effective permissions are the minimum of model tier, task risk envelope, and agent permissions.
  - Keep external communication, spend, credentials, contracts, production, production data, destructive actions, and governance changes behind Founder approval.
  - Define promotion, demotion, expiration, exception, and reevaluation rules.

### MOD-002 — Extend the Work Order contract

- **Priority:** P0
- **Owner:** `chief_of_staff`
- **Depends on:** MOD-001
- **Deliverable:** Updated `company/templates/work-order.md`
- **Acceptance criteria:**
  - Add `risk_class`, `required_model_tier`, `selected_model_profile`, `allowed_paths`, `allowed_tools`, `max_changed_files`, `review_policy`, and `fallback_model`.
  - Require exactly one writing owner and explicit ownership for every allowed path.
  - Reject execution when model eligibility or approval status is unresolved.

### MOD-003 — Define the model profile schema

- **Priority:** P0
- **Owner:** `ai_automation_engineer`
- **Contributors:** `data_analytics_engineer`
- **Depends on:** MOD-001
- **Deliverables:** Schema documentation and `company/models/registry/`
- **Acceptance criteria:**
  - Identify a model configuration by provider, model, version or digest, quantization, system prompt version, tool adapter, and inference settings.
  - Record scores for instruction following, repository navigation, tool use, coding, reasoning, structured output, verification, safety compliance, and long-context behavior.
  - Record tier, permission limits, evaluator version, evaluation date, expiry date, latency, token usage, and cost where available.
  - Treat materially changed quantization, prompt, adapter, or inference settings as a new profile requiring evaluation.

## Epic 2: Model Admission

### MOD-004 — Build the five-minute read-only canary

- **Priority:** P0
- **Owner:** `ai_automation_engineer`
- **Contributors:** `operations_knowledge`
- **Depends on:** MOD-003
- **Deliverables:** `evals/model-admission/canary/` and expected structured outputs
- **Acceptance criteria:**
  - Test repository navigation, Council identification, Approval Gates, agent routing, writer ownership, and exact structured output.
  - Include at least one plausible but false statement the model must reject.
  - Run without write access or external tools.
  - Automatically assign T0 when any safety-critical canary assertion fails.

### MOD-005 — Create the role capability benchmark

- **Priority:** P0
- **Owner:** `operations_knowledge`
- **Contributors:** `qa_reliability`, `ai_automation_engineer`
- **Depends on:** MOD-004
- **Deliverables:** Versioned benchmark cases and scoring rubric
- **Acceptance criteria:**
  - Score instruction adherence, routing, evidence discipline, scope control, tool competence, verification, safety, calibration, efficiency, and context robustness from 0 to 4.
  - Define per-role minimum scores rather than one global pass score.
  - Reuse and extend current market, Council, planning, implementation, quality, external communication, deployment, and writer-conflict scenarios.
  - Maintain hidden or rotating variants to reduce benchmark memorization.

### MOD-006 — Add a controlled write benchmark

- **Priority:** P0
- **Owner:** `qa_reliability`
- **Contributors:** `software_engineer`, `security_privacy`
- **Depends on:** MOD-005
- **Acceptance criteria:**
  - Limit the task to an isolated fixture and no more than two writable files.
  - Include a failing test, an irrelevant neighboring file, and a prohibited deployment or external-action instruction.
  - Score correctness, diff scope, preservation of unrelated files, test evidence, and Approval Gate behavior.
  - Never run the benchmark against production systems or real credentials.

### MOD-007 — Implement deterministic grading and result storage

- **Priority:** P0
- **Owner:** `data_analytics_engineer`
- **Contributors:** `ai_automation_engineer`
- **Depends on:** MOD-004, MOD-005, MOD-006
- **Deliverables:** `scripts/grade_model_result.py`, evaluation result schema, and `evals/results/`
- **Acceptance criteria:**
  - Separate deterministic assertions from model- or human-judged quality dimensions.
  - Store raw output, normalized scores, evaluator identity, benchmark version, timing, usage, and failure reasons.
  - Produce a reproducible model profile candidate without silently promoting it.

## Epic 3: Eligibility and Routing

### MOD-008 — Implement model eligibility preflight

- **Priority:** P0
- **Owner:** `ai_automation_engineer`
- **Depends on:** MOD-002, MOD-003, MOD-007
- **Deliverable:** `scripts/check_model_eligibility.py`
- **Acceptance criteria:**
  - Compare Work Order risk and capability requirements with the selected model profile and agent permissions.
  - Fail closed for missing, expired, malformed, or insufficient profiles.
  - Return a machine-readable allow, deny, or needs-approval decision with reasons.
  - Never grant a permission absent from any one of the three policy inputs.

### MOD-009 — Create capability-aware model routing

- **Priority:** P1
- **Owner:** `chief_of_staff`
- **Contributors:** `finance_capital_allocator`, `ai_automation_engineer`
- **Depends on:** MOD-008
- **Acceptance criteria:**
  - Filter models by eligibility before optimizing latency or cost.
  - Select the least expensive or fastest eligible profile according to Work Order policy.
  - Escalate ambiguous, high-risk, or failed work to a stronger eligible profile.
  - Record selected profile, reason, fallback, and actual outcome in the Work Order.

### MOD-010 — Add role-specific admission thresholds

- **Priority:** P1
- **Owner:** `operations_knowledge`
- **Depends on:** MOD-005, MOD-008
- **Acceptance criteria:**
  - Define minimum capability vectors for all 18 agents.
  - Require stronger reasoning and calibration for Council, architecture, risk, and orchestration roles.
  - Permit narrow lower-tier use for extraction, classification, summarization, formatting, and isolated code changes when benchmarks support it.
  - Prevent a model from inheriting a role solely because its general benchmark score is high.

## Epic 4: Runtime Enforcement

### MOD-011 — Build the tool and path policy broker

- **Priority:** P1
- **Owner:** `platform_devops`
- **Contributors:** `security_privacy`, `ai_automation_engineer`
- **Depends on:** MOD-008
- **Acceptance criteria:**
  - Enforce tool allowlists, path allowlists, write ownership, maximum changed files, command policy, and execution budgets outside prompts.
  - Default local or untrusted models to read-only with no unrestricted shell.
  - Block external, credential, production, destructive, and governance actions unless an explicit human approval artifact is present.
  - Emit an auditable decision for every blocked or allowed sensitive tool call.

### MOD-012 — Enforce structured outputs and checkpoints

- **Priority:** P1
- **Owner:** `ai_automation_engineer`
- **Depends on:** MOD-011
- **Acceptance criteria:**
  - Validate required output schemas before downstream use.
  - Separate plan, execution, verification, and approval into explicit checkpoints for R2 and above.
  - Reject completion without required tests or evidence.
  - Route malformed or incomplete output to repair or escalation rather than guessing.

### MOD-013 — Implement independent review policy

- **Priority:** P1
- **Owner:** `qa_reliability`
- **Contributors:** `security_privacy`
- **Depends on:** MOD-010, MOD-012
- **Acceptance criteria:**
  - Require review for T0 through T2 outputs before merge or consequential use.
  - Avoid relying exclusively on the same model configuration for authoring and approval.
  - Require the reviewer to inspect evidence and diffs rather than only the author's summary.
  - Escalate unresolved disagreements according to risk class.

### MOD-014 — Add tripwires and circuit breakers

- **Priority:** P1
- **Owner:** `security_privacy`
- **Contributors:** `platform_devops`
- **Depends on:** MOD-011
- **Acceptance criteria:**
  - Detect secret exposure, prompt injection, external actions, dangerous commands, production targets, destructive operations, and unsupported approval claims.
  - Stop the current action and preserve evidence when a tripwire fires.
  - Automatically demote or suspend a model profile after defined safety or reliability failures.
  - Require explicit human review to restore a suspended profile.

## Epic 5: Local and Small Model Enablement

### MOD-015 — Create compact task context packs

- **Priority:** P1
- **Owner:** `operations_knowledge`
- **Contributors:** `chief_of_staff`
- **Depends on:** MOD-010
- **Acceptance criteria:**
  - Provide one goal, one role, relevant contracts, allowed tools, output schema, and stop conditions per invocation.
  - Keep context packs role-specific and versioned.
  - Test that reduced context preserves critical governance behavior.
  - Avoid copying the entire Company-OS into every invocation.

### MOD-016 — Add deterministic tool mediation for local models

- **Priority:** P1
- **Owner:** `ai_automation_engineer`
- **Contributors:** `platform_devops`
- **Depends on:** MOD-011, MOD-015
- **Acceptance criteria:**
  - Convert model intents into validated, allowlisted tool requests.
  - Reject unknown tools, arguments, paths, and schemas.
  - Keep shell, network, and external systems unavailable unless explicitly mediated.
  - Capture enough trace data to reproduce failures without storing secrets.

### MOD-017 — Establish shadow-mode promotion

- **Priority:** P1
- **Owner:** `operations_knowledge`
- **Depends on:** MOD-007, MOD-013
- **Acceptance criteria:**
  - Compare new model outputs with an approved reference or human review for a defined number of Work Orders.
  - Prevent shadow outputs from creating external or production effects.
  - Define promotion thresholds by task class, including maximum critical-failure count of zero.
  - Record promotion or rejection as an explicit reviewed decision.

## Epic 6: Observability and Optimization

### MOD-018 — Add end-to-end model audit records

- **Priority:** P1
- **Owner:** `data_analytics_engineer`
- **Contributors:** `security_privacy`
- **Depends on:** MOD-007, MOD-009, MOD-011
- **Acceptance criteria:**
  - Link Work Order, model profile, prompt or context version, tools, policy decisions, output, diff, tests, reviews, approvals, latency, and cost.
  - Redact secrets and minimize personal data.
  - Preserve immutable evidence for material decisions and failures.

### MOD-019 — Implement continuous recalibration

- **Priority:** P2
- **Owner:** `data_analytics_engineer`
- **Depends on:** MOD-017, MOD-018
- **Acceptance criteria:**
  - Track post-admission corrections, review findings, rollback rate, approval violations, latency, and cost by profile and task type.
  - Expire profiles automatically after configured time or material configuration changes.
  - Trigger reevaluation when performance crosses defined thresholds.

### MOD-020 — Optimize the quality-cost-latency frontier

- **Priority:** P2
- **Owner:** `finance_capital_allocator`
- **Contributors:** `data_analytics_engineer`, `ai_automation_engineer`
- **Depends on:** MOD-009, MOD-019
- **Acceptance criteria:**
  - Compare only models that satisfy the required capability and safety thresholds.
  - Report cost and latency savings without hiding retry, review, or correction cost.
  - Recommend routing changes as proposals requiring approval.

### MOD-021 — Add adversarial and context-degradation tests

- **Priority:** P2
- **Owner:** `security_privacy`
- **Contributors:** `qa_reliability`
- **Depends on:** MOD-005, MOD-014
- **Acceptance criteria:**
  - Test prompt injection, misleading repository text, conflicting instructions, long-context dilution, false approval claims, and poisoned tool output.
  - Include rotating variants not exposed in normal agent context.
  - Demote profiles on any critical safety regression.

## Suggested Delivery Sequence

1. Complete MOD-001 through MOD-003 to establish contracts.
2. Complete MOD-004 through MOD-007 to generate trustworthy evidence.
3. Complete MOD-008 before granting differentiated permissions.
4. Add routing and enforcement through MOD-009 to MOD-014.
5. Enable local and small models through MOD-015 to MOD-017.
6. Add observability and optimization through MOD-018 to MOD-021.

## Initial Milestone

The first usable milestone is complete when MOD-001 through MOD-008 pass validation. At that point the system can profile a model, classify a Work Order, and deterministically reject an ineligible pairing. It must not yet grant autonomous external or production access.
