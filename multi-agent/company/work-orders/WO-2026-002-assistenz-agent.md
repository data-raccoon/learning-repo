---
id: WO-2026-002
status: completed
owner: chief_of_staff
created: 2026-07-17
review_date: 2026-10-17
---

# Work Order: Assistenz Agent

## Objective

Add one validated `assistenz` agent that can prepare internal administrative and coordination artifacts without gaining decision, approval, governance, or external-communication authority.

## Context

### Facts

- The Founder requested an `assistenz` agent on 2026-07-17.
- Company-OS currently registers 18 custom agents.
- Agent configuration, registry, validator expectations, and tests must remain consistent.

### Assumptions

- `assistenz` belongs to the Founder Office support cell.
- The role needs workspace write access only for explicitly assigned internal paths.

## Accountable Owner

`chief_of_staff` is the sole writing owner.

## Constraints

- All repository artifacts and agent instructions are written in English.
- The agent must not approve decisions, change governance, send external communications, incur spend, use credentials, or access restricted data without a separately approved Work Order.
- The agent must not duplicate Council analysis or Chief of Staff routing and consolidation responsibilities.

## Deliverables

- [x] `.codex/agents/assistenz.toml`
- [x] Agent Registry entry
- [x] Updated Company-OS agent validation expectation
- [x] Passing Company-OS validation and unit tests

## Acceptance Criteria

- [x] The TOML parses and its filename matches the agent name.
- [x] The role, access, outputs, and approval boundaries are explicit.
- [x] The registry and validator recognize exactly 19 agents.
- [x] Required verification commands pass.

## Dependencies

- `company/agent-registry.md`
- `scripts/validate_company_os.py`

## Ownership Boundaries

| Path or system | Writer | Read-only contributors |
| --- | --- | --- |
| `.codex/agents/assistenz.toml` | `chief_of_staff` | `qa_reliability` |
| `company/agent-registry.md` | `chief_of_staff` | `qa_reliability` |
| `scripts/validate_company_os.py` | `chief_of_staff` | `qa_reliability` |
| `company/work-orders/WO-2026-002-assistenz-agent.md` | `chief_of_staff` | `qa_reliability` |

## Approval Level

`routine`

The Founder explicitly requested creation of this internal agent. Existing decision rights and approval gates remain unchanged.

## Evidence and Closure

- Company-OS validation passed with 19 agents and 6 skills.
- Unit tests passed: 4/4.
- Existing decision rights and Founder approval gates are unchanged.
