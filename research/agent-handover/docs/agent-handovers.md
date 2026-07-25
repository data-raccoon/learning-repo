# Agent Handovers

This document defines the handover protocol for agent-to-agent responsibility transfer within the AI-Learn project. A handover is a **typed, validated transfer of responsibility**—not merely a forwarded chat transcript.

## Overview

This system distinguishes two patterns:

- **Delegation / agent-as-tool:** The originating agent keeps ownership and receives a result from a specialist.
- **Handover / transfer:** The receiving agent becomes responsible for the next stage, potentially interacting directly with the user.

**Rule:** Use delegation by default when one orchestrator should retain control. Use a true handover only when responsibility, workflow state, user interaction, or available capabilities genuinely need to change.

## Handover Lifecycle

```
Prepare -> Validate -> Offer -> Accept -> Activate -> Execute -> Close/Return
```

1. **Prepare:** Sender produces a structured handover packet
2. **Validate:** Runtime validates schema, destination, permissions and limits
3. **Offer:** Receiver is asked whether it can accept the work
4. **Accept/reject:** Receiver explicitly accepts, rejects or requests clarification
5. **Activate:** Ownership changes atomically
6. **Execute:** Receiver works within the delegated scope
7. **Close/return:** Receiver records results, artifacts, status and remaining work

The explicit acceptance step is especially useful across service, team or organizational boundaries. Within a tightly controlled in-process workflow, offer and acceptance may be combined into one atomic transition.

## Key Principles

### 1. Structured Handover Envelope

The envelope must contain the **minimum sufficient state** required to continue safely. See [schemas/handover.schema.json](../schemas/handover.schema.json) for the complete specification.

**Required fields:**
- Handover ID and version (for idempotency and compatibility)
- Source and destination agents (for accountability and routing)
- Goal and requested outcome (defines what the receiver owns)
- Definition of done (prevents subjective completion)
- Current task status (establishes the starting point)
- Completed/remaining work (prevents duplicate work)
- Next action (gives the receiver an actionable start)
- Delegated permissions (limits authority)
- Forbidden actions (makes negative boundaries explicit)
- Evidence references (grounds the handover)

**Recommended fields:**
- Decisions and rationale (prevents reopening settled questions)
- Assumptions and confidence (exposes uncertainty)
- Execution budgets (prevents loops and cost overruns)
- Artifacts (when produced, keeps outputs separate from conversation)

**Optional fields:**
- Raw transcript (debugging or exceptional context only)

### 2. Do Not Forward Complete Transcript by Default

Passing the entire conversation creates several problems:
- Irrelevant context and higher token cost
- Internal reasoning or tool noise confusing the receiver
- Accidental propagation of secrets or untrusted content
- Stale conclusions being treated as facts
- Duplicated or malformed tool-call history
- Difficulty distinguishing instructions from evidence

**Context hierarchy:**
1. Structured handover fields
2. Referenced durable artifacts
3. Selected source evidence
4. Concise conversation summary
5. Raw transcript only when specifically needed

If protocol-level message history is forwarded, preserve structural validity. An assistant tool call must remain paired with its corresponding tool result.

### 3. Transfer Scope, Not Credentials

A handover must not mean: "The previous agent could do this, so the next agent may also do it."

The receiver should get an independently validated, narrowly scoped authorization grant. Permissions should identify:
- The user or service principal
- The exact delegated capabilities
- Affected resources
- Prohibited operations
- Expiration
- Approval requirements
- Delegation depth or hop count
- Whether further delegation is allowed

**Authentication and authorization must be enforced by the runtime or tool gateway—not inferred by the model from conversation text.**

### 4. Require Explicit Receiver Acknowledgement

A receiving agent must return a machine-readable acknowledgement before starting work. See [schemas/handover-ack.schema.json](../schemas/handover-ack.schema.json) for the schema.

**Possible decisions:**
- `accepted`
- `rejected`
- `clarification-required`
- `approval-required`
- `temporarily-unavailable`

**The receiver should reject the handover when:**
- The task falls outside its declared capabilities
- Required context or evidence is absent
- Permissions are insufficient or excessive
- The definition of done is not testable
- The request conflicts with policy
- The task is already completed or stale
- A concurrency or ownership conflict exists

### 5. Make Ownership Atomic and Queryable

Store workflow ownership outside model context:

```yaml
Task ID: task_456
State: working
Active Agent: implementer
Handover ID: ho_01K123...
Ownership Version: 7
Updated At: 2026-07-23T08:31:00Z
```

Use compare-and-swap or an equivalent transaction to prevent:
- Two agents believing they own the same task
- An old handover overwriting newer work
- Duplicate state-changing tool calls
- Circular transfers

### 6. Separate Communication, State and Artifacts

| Concept | Contains | Example |
|---|---|---|
| **Message** | Human- or agent-readable communication | "I need the API version." |
| **Task state** | Current lifecycle and ownership | `input-required` |
| **Artifact** | Durable work product | Patch, report, test output, plan |

**Rule:** Do not place critical results only inside an ephemeral status message. Store them as artifacts with stable identifiers, versions and integrity digests.

### 7. Use a Return Handover

Completion should produce another structured envelope rather than an informal "done." The return handover should include:
- Summary of work completed
- Changed files and modifications
- Verification results with evidence
- Decisions made during execution
- Unresolved issues or remaining work
- Risks identified
- Claims with backing evidence

**Important rule:** Every meaningful claim in a handover should be backed by inspectable evidence.

## Allowed Source-to-Destination Transitions

The following transitions are permitted:

| Source Agent | Destination Agent | Allowed? | Notes |
|---|---|---|---|
| planner | implementer | Yes | Standard workflow |
| planner | reviewer | Yes | For review-only tasks |
| implementer | reviewer | Yes | Completion handover |
| implementer | tester | Yes | For specialized testing |
| reviewer | planner | Yes | For clarification |
| reviewer | implementer | Yes | For rework |
| Any | human | Yes | Escalation required |

**Restriction:** Circular transitions (A -> B -> A) are rejected by default unless explicitly approved.

## Mandatory Envelope Fields

See [schemas/handover.schema.json](../schemas/handover.schema.json) for the complete list of required fields.

## Acceptance and Rejection Rules

### Acceptance Criteria

A receiver must accept a handover if and only if:
1. The handover schema is valid and version is supported
2. The requested goal is within its declared capabilities
3. The definition of done is specific and testable
4. Required evidence and artifacts are accessible
5. Delegated permissions are sufficient but not excessive
6. Accepting will not create duplicate ownership
7. No loops or excessive delegation depth exist
8. Human approval is present when required

### Rejection Criteria

A receiver must reject a handover if:
1. The handover schema is invalid or version is unsupported
2. The requested goal is outside its declared capabilities
3. Required evidence or artifacts are missing or inaccessible
4. Delegated permissions are insufficient or excessive
5. The definition of done is vague or untestable
6. The request conflicts with policy
7. A concurrency or ownership conflict exists
8. The task appears to be already completed or stale

## Context-Selection Policy

When preparing a handover, the sender must:

1. Include all required fields from the schema
2. Reference durable artifacts for any produced outputs
3. Select only the most relevant evidence for the next stage
4. Remove secrets, irrelevant history, and internal reasoning
5. Provide a concise summary if additional context is needed
6. Never include raw transcript by default

When receiving a handover, the receiver must:

1. Verify all referenced artifacts are accessible
2. Treat summaries and claims as untrusted until verified
3. Inspect referenced evidence before relying on sender's conclusions
4. Request missing context rather than proceeding with incomplete information

## Authorization Propagation

Authorization is propagated according to the following rules:

1. **Least privilege:** Only the minimum required permissions are delegated
2. **No credential forwarding:** Authentication tokens are never forwarded
3. **Resource-specific:** Capabilities are scoped to specific resources
4. **Time-limited:** All delegated permissions have explicit expiration
5. **No implicit inheritance:** Receiver does not inherit sender's permissions
6. **Approval gates:** High-risk actions require explicit human approval

**Delegation depth:** Maximum of 3 hops by default (configurable).

**Further delegation:** Not allowed unless explicitly permitted in the authorization grant.

## Ownership Semantics

- Only one agent may own a task at any given time
- Ownership is transferred atomically via compare-and-swap
- Ownership version increments with each transfer
- Stale handovers (where ownership has changed) are rejected
- Concurrent handover attempts are resolved via version comparison

## Loop and Retry Limits

- **Maximum handover depth:** 3 (configurable via policy)
- **Loop detection:** Circular transitions are automatically rejected
- **Retry budget:** Each handover may specify a retry budget (default: 2)
- **Max turns:** Each handover may specify maximum interaction turns (default: 20)
- **Max tool calls:** Each handover may specify maximum tool calls (default: 50)

## Human Escalation

Human escalation is required when:

- High-risk actions are requested (deploy, publish, production access)
- Policy conflicts are detected
- Approval requirements are not met
- Ambiguous or conflicting instructions are received
- The receiver cannot verify critical claims

**Escalation mechanism:** Handover to a special "human" agent with appropriate context.

## Observability Requirements

All handovers must be logged with the following information:

- Handover ID and parent handover ID (if applicable)
- Source and destination agents
- Timestamp of preparation, offer, acceptance, and completion
- Decision (accepted/rejected/clarification-required)
- Reason for rejection or clarification needed
- Ownership version before and after
- Authorization grant details
- Artifacts produced and referenced

## Default Policy

```yaml
handover_policy:
  prefer_delegation_over_transfer: true
  require_structured_envelope: true
  require_receiver_acknowledgement: true
  transfer_full_transcript: false
  require_definition_of_done: true
  require_evidence_for_completion_claims: true
  authorization_mode: "least-privilege"
  atomic_ownership_transfer: true
  max_handover_depth: 3
  reject_cycles: true
  handover_timeout_seconds: 30
  require_human_approval_for_high_risk_actions: true
  persist_handover_receipts: true
```

## Implementation

The handover system is implemented in:

- [`src/orchestration/handover_service.py`](../src/orchestration/handover_service.py) - Core handover logic
- [`src/orchestration/handover_policy.py`](../src/orchestration/handover_policy.py) - Policy enforcement
- [`src/orchestration/ownership_store.py`](../src/orchestration/ownership_store.py) - Ownership state management
- [`src/orchestration/context_filter.py`](../src/orchestration/context_filter.py) - Context filtering for handovers

## Testing

Tests are organized in:

- [`tests/contract/test_handover_schema.py`](../tests/contract/test_handover_schema.py) - Schema validation tests
- [`tests/integration/test_handover_lifecycle.py`](../tests/integration/test_handover_lifecycle.py) - Lifecycle tests
- [`tests/security/test_handover_authorization.py`](../tests/security/test_handover_authorization.py) - Authorization tests

## Evaluation

Evaluation scenarios are defined in:

- [`evals/handovers/routing.jsonl`](../evals/handovers/routing.jsonl) - Routing accuracy tests
- [`evals/handovers/context-quality.jsonl`](../evals/handovers/context-quality.jsonl) - Context selection tests
- [`evals/handovers/authorization.jsonl`](../evals/handovers/authorization.jsonl) - Authorization tests
- [`evals/handovers/loops.jsonl`](../evals/handovers/loops.jsonl) - Loop detection tests

## Five Indispensable Properties

A robust handover has five indispensable properties:

1. **Typed:** Machine-readable and schema-validated
2. **Minimal:** Contains relevant state, not indiscriminate history
3. **Scoped:** Transfers responsibility and least-privilege authority explicitly
4. **Acknowledged:** Receiver accepts or rejects before ownership changes
5. **Auditable:** Decisions, artifacts, evidence and lifecycle transitions remain inspectable
