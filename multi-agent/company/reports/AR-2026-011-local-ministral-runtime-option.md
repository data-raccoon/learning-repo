---
id: AR-2026-011
status: completed
owner: ai_automation_engineer
created: 2026-07-18
review_date: 2026-08-18
work_order: WO-2026-011
---

# Agent Report: Local Ministral Runtime Option

## Executive Summary

A local, authenticated, OpenAI-compatible Ministral 3B endpoint is operational on the Founder workstation. Company-OS may consider it as a future low-cost, local model candidate, but it is not yet an admitted model profile and has not been shown to work as a Mistral Vibe provider. No Company-OS workload should be routed to it until adapter compatibility and the model-admission controls in the capability backlog are verified.

## Evidence

| Claim | Type | Evidence |
| --- | --- | --- |
| The model is Mistral AI's Ministral 3B Instruct, quantized as Q4_K_M. | fact | Local file `C:\LLMs\models\mistral\Ministral-3-3B-Instruct-2512-Q4_K_M.gguf`; official repository `mistralai/Ministral-3-3B-Instruct-2512-GGUF`. |
| The runtime is `llama.cpp` b10066 using the Windows Vulkan build. | fact | Local installation and server startup verification on 2026-07-18. |
| The endpoint is loopback-only and OpenAI-compatible. | fact | Verified endpoint `http://127.0.0.1:8081/v1`; server log reported listening on `127.0.0.1:8081`. |
| API authentication is enforced. | fact | The Python verification canary observed HTTP 401 without a key and an authenticated response of `Bereit.`. |
| GPU offload is active on an NVIDIA RTX 2080 SUPER with 8 GB VRAM. | fact | `nvidia-smi` identified exactly one `llama-server.exe` GPU process matching the recorded PID after cleanup. |
| Observed text generation was approximately 68 tokens per second for one short canary. | fact | `llama.cpp` timing log for the initial authenticated local test; this is not a representative benchmark. |
| Vibe can use this endpoint directly. | assumption, unverified | No provider-adapter configuration or Vibe compatibility test was performed. |
| The model is suitable for any Company-OS role. | assumption, unverified | No model-admission canary, role benchmark, controlled-write benchmark, or eligibility decision exists. |

## Assumptions

- The workstation runtime remains available only while the local server process is running.
- The API key remains outside the repository at `C:\LLMs\config\api_key.txt` and is not disclosed in prompts or artifacts.
- Performance will vary with context length, concurrent applications, prompt shape, and GPU memory pressure.

## Recommendation

Keep the runtime as an unadmitted candidate. First verify an OpenAI-compatible adapter in a read-only synthetic fixture. Then execute MOD-003 through MOD-008 before assigning a model tier, role, write permission, or automatic routing. Start with narrow extraction, classification, summarization, and formatting canaries rather than Council, architecture, risk, orchestration, external, or production work.

## Risks

| Risk | Likelihood | Impact | Mitigation | Owner |
| --- | --- | --- | --- | --- |
| Small-model output is accepted without admission evidence. | medium | high | Fail closed; do not route Company-OS work until an eligible model profile exists. | `ai_automation_engineer` |
| A local browser or process targets the endpoint. | low | medium | Keep loopback binding and API-key enforcement; do not expose the port to the LAN. | `security_privacy` |
| The API key enters repository history or logs. | low | high | Read it only from the external file; never copy its value into Company-OS. | `security_privacy` |
| Vibe adapter semantics differ from the OpenAI-compatible API. | medium | medium | Test in a synthetic read-only fixture before any repository context is provided. | `ai_automation_engineer` |
| A short throughput canary is mistaken for a quality benchmark. | medium | medium | Label it operational evidence only and run the admission benchmarks separately. | `qa_reliability` |

## Unresolved Questions

- Which supported Vibe or Company-OS adapter can target this authenticated OpenAI-compatible endpoint?
- What task-specific capability tier will the exact quantized configuration earn?
- What context size and concurrency limits provide stable operation on the current 8 GB GPU?

## Proposed Next Action

Create a separate Work Order for a read-only, synthetic adapter and model-admission canary. Do not change the active Vibe provider or send Company-OS repository content to the local model under this Work Order.
