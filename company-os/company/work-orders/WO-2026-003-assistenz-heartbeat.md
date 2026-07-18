---
id: WO-2026-003
status: ready
owner: software_engineer
created: 2026-07-17
review_date: 2026-07-31
---

# Work Order: Assistenz Heartbeat

## Objective

Provide a deterministic, tested heartbeat workflow that lets a scheduled `assistenz` run detect newly actionable Company-OS work every fifteen minutes without producing duplicate noise or starting work without authority.

## Context

### Facts

- The Founder approved implementation on 2026-07-17.
- The `assistenz` agent exists and has no independent decision or approval authority.
- Chat-based scheduled tasks can use minute intervals and retain chat context.
- Local runtime state under `.runtime/` is excluded from Git.

### Assumptions

- Work Orders and risk registers are the initial canonical repository inputs.
- Founder instructions that exist only in chat are evaluated by the scheduled chat prompt, not by the repository scanner.
- The ChatGPT desktop app will be used for the final fifteen-minute schedule activation.

## Accountable Owner

`software_engineer` is the sole writing owner.

## Constraints

- Use only the Python standard library.
- The scanner may write only its ignored `.runtime/` checkpoint state by default.
- No implementation, external communication, restricted-data access, spend, deployment, or approval may be initiated by the heartbeat.
- Produce no output when no actionable state changed.

## Deliverables

- [x] Deterministic heartbeat scanner.
- [x] Unit tests for first-run, quiet-run, and changed-state behavior.
- [x] Durable scheduled-task prompt and operating instructions.
- [x] Verification evidence and activation boundary.

## Acceptance Criteria

- [x] Active or overdue Work Orders and open risks are detected with path, owner, status, and approval context.
- [x] An unchanged second run is silent.
- [x] Newly added, changed, and resolved findings are distinguished.
- [x] Checkpoint state is stored only below `.runtime/`.
- [x] Company-OS validation, repository tests, and heartbeat tests pass.
- [x] The scheduled prompt invokes `assistenz`, checks chat instructions, and preserves all Founder gates.

## Dependencies

- `.codex/agents/assistenz.toml`
- `company/decision-rights.md`
- ChatGPT Scheduled Tasks availability in the Founder workspace.

## Ownership Boundaries

| Path or system | Writer | Read-only contributors |
| --- | --- | --- |
| `scripts/check_assistenz_heartbeat.py` | `software_engineer` | `qa_reliability`, `security_privacy` |
| `tests/test_assistenz_heartbeat.py` | `software_engineer` | `qa_reliability` |
| `company/automations/assistenz-heartbeat.md` | `software_engineer` | `assistenz`, `chief_of_staff`, `security_privacy` |
| `company/work-orders/WO-2026-003-assistenz-heartbeat.md` | `software_engineer` | `chief_of_staff`, `qa_reliability` |
| `.runtime/assistenz-heartbeat/state.json` | scheduled `assistenz` run | local runtime only |

## Approval Level

`founder-approval-required`

The Founder approved implementation. Activation of an unattended recurring task is recorded separately from code completion; existing gates continue to apply to every discovered action.

## Evidence and Closure

- Heartbeat tests passed: 6/6.
- Full repository tests passed: 10/10.
- Company-OS validation passed with 19 agents and 6 skills.
- Independent QA/security remediation review: pass for technical activation readiness.
- Manual scanner sequence passed: changed finding -> visible delivery -> `--ack` -> silent unchanged run.
- Activation status: ready; the fifteen-minute Scheduled Task must still be enabled in the ChatGPT desktop Scheduled interface and its first three runs reviewed.
- Residual control: `assistenz` retains `workspace-write`; scheduled prompt restrictions and scanner path containment are therefore monitored during the first three runs.
- Ownership handoff: for the cadence-only amendment on 2026-07-17, `software_engineer` transferred writing control of this Work Order to `chief_of_staff` under `WO-2026-004`; implementation ownership of the scanner and tests remains unchanged.
