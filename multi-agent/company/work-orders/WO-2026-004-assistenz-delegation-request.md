---
id: WO-2026-004
status: completed
owner: chief_of_staff
created: 2026-07-17
review_date: 2026-07-31
---

# Work Order: Assistenz Delegation Requests

## Objective

Change the Assistenz heartbeat cadence to fifteen minutes and allow `assistenz` to submit structured requests for Chief of Staff review and root-level start of an existing registered specialist agent, without allowing subagent delegation or unattended authority expansion.

## Context

### Facts

- The Founder requested a fifteen-minute cadence on 2026-07-17.
- The Founder asked whether `assistenz` can request that additional agents be started.
- Company-OS limits subagent depth to one and prohibits subagents from delegating further.

### Assumptions

- "Start a new agent" means start a run of an existing registered agent, not create a new agent type or configuration.
- Requests from an unattended heartbeat require review before an agent run starts.

## Accountable Owner

`chief_of_staff` is the sole writing owner.

## Constraints

- `assistenz` may request delegation but must not spawn or delegate directly.
- Every request names an existing registered agent role, bounded task, scope, deliverable, acceptance criteria, urgency, and approval context.
- Chief of Staff may review and route a request. Only the root orchestration turn starts the agent, and only when a valid Work Order, non-overlapping ownership, capacity, and approval authority exist.
- Creating a new agent definition remains a separate Company-OS change requiring explicit Founder direction.

## Deliverables

- [x] Fifteen-minute cadence in all active heartbeat artifacts.
- [x] Structured delegation-request contract in the Assistenz instructions.
- [x] Matching unattended-heartbeat prompt behavior.
- [x] Passing Company-OS validation and unit tests.

## Acceptance Criteria

- [x] No active artifact still instructs a ten-minute cadence.
- [x] `assistenz` cannot interpret a request as authority to spawn.
- [x] Delegation requests contain enough information for safe routing.
- [x] New agent definitions remain separately Founder-directed.
- [x] Required verification commands pass.

## Dependencies

- `.codex/agents/assistenz.toml`
- `company/automations/assistenz-heartbeat.md`
- `.codex/config.toml`
- `AGENTS.md`

## Ownership Boundaries

| Path or system | Writer | Read-only contributors |
| --- | --- | --- |
| `.codex/agents/assistenz.toml` | `chief_of_staff` | `qa_reliability`, `security_privacy` |
| `company/automations/assistenz-heartbeat.md` | `chief_of_staff` | `qa_reliability`, `security_privacy` |
| `company/work-orders/WO-2026-003-assistenz-heartbeat.md` cadence references only | `chief_of_staff` under explicit handoff from `software_engineer` | `software_engineer` retains scanner/test implementation ownership |
| `company/work-orders/WO-2026-004-assistenz-delegation-request.md` | `chief_of_staff` | `qa_reliability` |

## Approval Level

`routine`

The Founder explicitly approved the cadence and delegation-request changes. Existing decision rights and approval gates remain unchanged.

## Evidence and Closure

- Company-OS validation passed with 19 agents and 6 skills.
- Full repository test suite passed: 10/10.
- Stale cadence and ambiguous delegation wording search returned no matches in active Assistenz artifacts.
- Independent QA/security review passed after confirming root-only starts and the cadence-only ownership handoff.
