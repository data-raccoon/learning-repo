---
id: WO-2026-008
status: completed
owner: chief_of_staff
created: 2026-07-17
review_date: 2026-07-31
---

# Work Order: Mistral Routine Agent Profiles

## Objective

Add three project-local Mistral Vibe agent profiles for bounded routine work, with observable permission boundaries and without changing Company-OS decision rights.

## Context

### Facts

- The Founder requested Mistral profiles for `assistenz`, `operations_knowledge`, and `qa_reliability` on 2026-07-17.
- Mistral Vibe supports project-level custom agents in `.vibe/agents/` and project-level prompts in `.vibe/prompts/`.
- The corresponding Company-OS roles already exist in `.codex/agents/` and `company/agent-registry.md`.

### Assumptions

- "Create" means add selectable Mistral Vibe profiles, not start an unattended run.
- The active model and provider remain controlled by the existing Mistral Vibe installation and user configuration.
- Lower-capability execution is appropriate only for bounded routine tasks with human-visible tool approvals.

## Accountable Owner

`chief_of_staff` is the sole writing owner.

## Constraints

- All repository artifacts and agent instructions are written in English.
- Profiles must not expand existing role authority or Company-OS approval rights.
- Writing agents require approval for each write or replacement tool action.
- QA remains read-only and requires approval before shell execution.
- No credential, subscription, provider, default-model, or production setting changes are in scope.

## Deliverables

- [x] Project-local Mistral Vibe profile and prompt for `assistenz`.
- [x] Project-local Mistral Vibe profile and prompt for `operations_knowledge`.
- [x] Project-local read-only Mistral Vibe profile and prompt for `qa_reliability`.
- [x] Syntax validation and Company-OS regression verification.

## Acceptance Criteria

- [x] All three agent TOML files parse successfully.
- [x] Every profile is directly selectable and references an existing project-local prompt.
- [x] Assistenz and Operations Knowledge require approval for file changes.
- [x] QA has no file-writing tool and requires approval for shell commands.
- [x] Company-OS validation and unit tests pass.

## Dependencies

- Installed Mistral Vibe VS Code extension.
- Existing local Mistral authentication and provider configuration for actual execution.
- `.codex/agents/assistenz.toml`
- `.codex/agents/operations_knowledge.toml`
- `.codex/agents/qa_reliability.toml`

## Ownership Boundaries

| Path or system | Writer | Read-only contributors |
| --- | --- | --- |
| `.vibe/agents/*.toml` created by this Work Order | `chief_of_staff` | `qa_reliability` |
| `.vibe/prompts/*.md` created by this Work Order | `chief_of_staff` | `qa_reliability` |
| `company/work-orders/WO-2026-008-mistral-routine-agents.md` | `chief_of_staff` | `qa_reliability` |
| Existing `.codex/agents/` and governance files | None | `chief_of_staff` |

## Approval Level

`routine`

The Founder explicitly requested these internal profiles. The Work Order does not change governance, credentials, spend, deployment, or production data.

## Evidence and Closure

- Parsed all three agent files with Python `tomllib`; all are valid TOML.
- Confirmed all three referenced project-local prompt files exist.
- Permission-boundary assertions passed for both writing profiles and the read-only QA profile.
- Company-OS validation passed with 19 agents and 6 skills.
- Full repository unit test suite passed: 10/10.
- Actual Mistral execution was intentionally not started; it depends on the user's existing Vibe authentication and may consume API quota.
