---
id: WO-2026-011
status: completed
owner: ai_automation_engineer
created: 2026-07-18
review_date: 2026-08-18
---

# Work Order: Document Local Ministral Runtime Option

## Objective

Record the verified local Ministral 3B runtime as an available but unadmitted Company-OS model option without changing the active Vibe provider, credentials, permissions, or model routing.

## Context

### Facts

- The Founder instructed Company-OS to be informed of the local runtime option on 2026-07-18.
- `Ministral-3-3B-Instruct-2512-Q4_K_M.gguf` is stored outside the repository under `C:\LLMs\models\mistral`.
- A local `llama.cpp` server was verified on `http://127.0.0.1:8081/v1` with Vulkan GPU offload and API-key enforcement.
- The authenticated Python canary returned `Bereit.` while an unauthenticated request returned HTTP 401.

### Inferences

- The runtime may reduce provider disclosure and marginal inference cost for bounded tasks once compatibility and capability admission are proven.
- A successful transport canary does not establish Company-OS task capability, safety, tool use, or Vibe adapter compatibility.

## Accountable Owner

`ai_automation_engineer` is the sole writing owner.

## Constraints

- Write all artifacts in English.
- Do not copy the API key, model weights, logs, PID files, or machine-specific credentials into the repository.
- Do not change `.vibe/config.toml`, active provider settings, default models, agent permissions, or approval gates.
- Treat the runtime as unadmitted until the model-admission backlog produces an eligible profile.
- Keep the endpoint bound to loopback and require API authentication.

## Deliverables

- [x] Local-runtime section in `company/automations/mistral-execution.md`.
- [x] Evidence and handoff report in `company/reports/AR-2026-011-local-ministral-runtime-option.md`.
- [x] Passing Company-OS validation and unit tests.

## Acceptance Criteria

- [x] The model, quantization, runtime, endpoint, storage boundary, authentication, and observed canary are recorded.
- [x] The documentation distinguishes transport availability from model admission and Vibe compatibility.
- [x] No secret or API-key value is committed.
- [x] No active provider, model, agent, or permission setting changes.
- [x] Required validation and tests pass.

## Dependencies

- Local runtime under `C:\LLMs`.
- `company/model-capability-backlog.md`, especially MOD-003 through MOD-008.
- A future verified OpenAI-compatible adapter for the selected agent runtime.

## Ownership Boundaries

| Path or system | Writer | Read-only contributors |
| --- | --- | --- |
| `company/automations/mistral-execution.md` | `ai_automation_engineer` | `security_privacy`, `qa_reliability` |
| `company/reports/AR-2026-011-local-ministral-runtime-option.md` | `ai_automation_engineer` | `qa_reliability` |
| `company/work-orders/WO-2026-011-local-ministral-runtime-option.md` | `ai_automation_engineer` | `chief_of_staff` |

## Approval Level

`routine`

The Founder explicitly requested documentation of the existing local option. This Work Order does not authorize a model run on Company-OS data or a provider configuration change.

## Evidence and Closure

- Company-OS validation passed with 19 agents, 6 skills, governance, templates, and references valid.
- Full unit test suite passed: 10/10.
- The SOP records the local runtime as an unadmitted candidate and links the evidence report.
- No `.vibe` configuration, provider selection, model route, agent permission, credential, or API-key value changed.
