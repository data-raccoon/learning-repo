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

A local, authenticated, OpenAI-compatible Ministral 3B endpoint is operational on the Founder workstation. A project-local generic OpenAI provider has now passed synthetic Mistral Vibe response, large-history, non-alternating-role, and structured file-tool canaries. Company-OS may consider it as a future low-cost local candidate, but adapter compatibility does not establish model capability or admission. No Company-OS workload should be routed to it until the model-admission controls in the capability backlog are completed for this exact configuration.

## Evidence

| Claim | Type | Evidence |
| --- | --- | --- |
| The model is Mistral AI's Ministral 3B Instruct, quantized as Q4_K_M. | fact | Local file `C:\LLMs\models\mistral\Ministral-3-3B-Instruct-2512-Q4_K_M.gguf`; official repository `mistralai/Ministral-3-3B-Instruct-2512-GGUF`. |
| The runtime is `llama.cpp` b10066 using the Windows Vulkan build. | fact | Local installation and server startup verification on 2026-07-18. |
| The endpoint is loopback-only and OpenAI-compatible. | fact | Verified endpoint `http://127.0.0.1:8081/v1`; server log reported listening on `127.0.0.1:8081`. |
| API authentication is enforced. | fact | The Python verification canary observed HTTP 401 without a key and an authenticated response of `Bereit.`. |
| GPU offload is active on an NVIDIA RTX 2080 SUPER with 8 GB VRAM. | fact | `nvidia-smi` identified exactly one `llama-server.exe` GPU process matching the recorded PID after cleanup. |
| Observed text generation was approximately 68 tokens per second for one short canary. | fact | `llama.cpp` timing log for the initial authenticated local test; this is not a representative benchmark. |
| Vibe can use this endpoint through a generic OpenAI provider. | fact | Project-local provider `local-llama` targets `http://127.0.0.1:8081/v1`; authenticated response, 35-message history, consecutive-role, and structured `read_file` canaries returned HTTP 200. |
| The current server exposes one 32,768-token slot. | fact | Runtime startup reports `n_slots = 1` and `n_ctx_slot = 32768`; the local Vibe model compacts at 24,576 tokens to retain an 8,192-token safety reserve. |
| The Vibe-compatible template retains native Ministral tool syntax. | fact | The runtime template preserves `[INST]`, `[AVAILABLE_TOOLS]`, `[TOOL_CALLS]`, and `[TOOL_RESULTS]` while removing the strict user/assistant alternation exception. |
| The model is suitable for any Company-OS role. | assumption, unverified | No model-admission canary, role benchmark, controlled-write benchmark, or eligibility decision exists. |

## Assumptions

- The workstation runtime remains available only while the local server process is running.
- The API key remains outside the repository at `C:\LLMs\config\api_key.txt` and is not disclosed in prompts or artifacts.
- Performance will vary with context length, concurrent applications, prompt shape, and GPU memory pressure.

## Recommendation

Keep the runtime as an unadmitted candidate. The generic OpenAI adapter has passed local synthetic compatibility checks; the next authorized step is a Company-OS admission fixture using synthetic, read-only content. Execute MOD-003 through MOD-008 before assigning a model tier, role, write permission, or automatic routing. Start with narrow extraction, classification, summarization, and formatting canaries rather than Council, architecture, risk, orchestration, external, or production work.

## Risks

| Risk | Likelihood | Impact | Mitigation | Owner |
| --- | --- | --- | --- | --- |
| Small-model output is accepted without admission evidence. | medium | high | Fail closed; do not route Company-OS work until an eligible model profile exists. | `ai_automation_engineer` |
| A local browser or process targets the endpoint. | low | medium | Keep loopback binding and API-key enforcement; do not expose the port to the LAN. | `security_privacy` |
| The API key enters repository history or logs. | low | high | Read it only from the external file; never copy its value into Company-OS. | `security_privacy` |
| The small model enters long or repetitive tool-call loops. | medium | medium | Use the file-only agent, bound turns, require human review, and record latency and call counts in admission canaries. | `ai_automation_engineer` |
| A short throughput canary is mistaken for a quality benchmark. | medium | medium | Label it operational evidence only and run the admission benchmarks separately. | `qa_reliability` |

## Unresolved Questions

- What task-specific capability tier will the exact quantized configuration earn?
- Do the 32,768-token single-slot context and 24,576-token compaction trigger remain stable under representative Company-OS admission fixtures?
- What maximum turn count prevents unproductive tool loops without truncating valid file-analysis work?

## Proposed Next Action

Create a separate Work Order for a read-only, synthetic Company-OS model-admission canary using the verified generic OpenAI adapter. Do not send Company-OS repository content to the local model under this completed Work Order.
