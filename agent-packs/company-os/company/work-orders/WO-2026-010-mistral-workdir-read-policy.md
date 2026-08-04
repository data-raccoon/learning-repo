---
id: WO-2026-010
status: completed
owner: chief_of_staff
created: 2026-07-17
review_date: 2026-10-17
---

# Work Order: Mistral Workdir Read Policy

## Objective

Persist one verifiable Company-OS rule that approved Mistral Vibe calls use the repository root as their workdir and may read ordinary repository content across that workdir.

## Context

### Facts

- The Founder instructed Company-OS to allow Mistral read access to the full workdir on 2026-07-17.
- The project-local Mistral profiles already allow `read_file` and `grep` without per-action approval.
- Vibe workdir scope is selected at invocation time and therefore cannot be guaranteed by agent TOML alone.

### Assumptions

- "Full workdir" means ordinary repository content inside the repository root, not credentials, restricted data, or paths outside the workdir.
- This instruction does not remove existing approval gates for model usage, file changes, shell actions, or other consequential operations.

## Accountable Owner

`chief_of_staff` is the sole writing owner.

## Constraints

- Preserve all existing decision rights and Founder approval gates.
- Do not add credentials, provider settings, or API keys.
- Do not grant access outside the repository workdir.
- Keep the detailed procedure separate from the concise root orchestration instruction.

## Deliverables

- [x] Concise Mistral invocation rule in `AGENTS.md`.
- [x] Detailed execution SOP in `company/automations/mistral-execution.md`.
- [x] Passing Company-OS validation and unit tests.

## Acceptance Criteria

- [x] `AGENTS.md` requires the repository root as `--workdir` for approved Mistral calls.
- [x] The SOP explicitly permits `read_file` and `grep` across ordinary workdir content.
- [x] Credentials, restricted data, writes, shell actions, outside-workdir access, and paid usage retain explicit boundaries.
- [x] The SOP includes reproducible interactive and programmatic commands.
- [x] Required validation and unit tests pass.

## Dependencies

- `.vibe/agents/*.toml`
- `company/decision-rights.md`
- Installed Mistral Vibe CLI

## Ownership Boundaries

| Path or system | Writer | Read-only contributors |
| --- | --- | --- |
| `AGENTS.md` | `chief_of_staff` | `security_privacy`, `qa_reliability` |
| `company/automations/mistral-execution.md` | `chief_of_staff` | `security_privacy`, `qa_reliability` |
| `company/work-orders/WO-2026-010-mistral-workdir-read-policy.md` | `chief_of_staff` | `qa_reliability` |

## Approval Level

`founder-approval-required`

The Founder explicitly requested this persistent external-agent read policy. Existing approval gates remain unchanged.

## Evidence and Closure

- Focused Mistral policy assertions passed for workdir, read tools, sensitive-data boundaries, outside-workdir denial, approval mode, and bounded invocation flags.
- Company-OS validation passed with 19 agents and 6 skills.
- Full repository unit test suite passed: 10/10.
