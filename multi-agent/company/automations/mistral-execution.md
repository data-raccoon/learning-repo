---
id: automation-mistral-execution-001
status: active
owner: chief_of_staff
created: 2026-07-17
review_date: 2026-10-17
---

# Mistral Vibe Execution

## Purpose

Define the supervised procedure for running a registered project-local Mistral Vibe agent with read access across the repository workdir.

## Preconditions

- A valid Work Order identifies the agent, bounded task, deliverable, acceptance criteria, approval status, and accountable owner.
- The requested profile exists in `.vibe/agents/` and its referenced prompt exists in `.vibe/prompts/`.
- The Founder has approved any paid model usage or other applicable approval gate.
- Credentials are configured outside the repository through Vibe setup, `VIBE_HOME`, or an environment variable; credentials must never be placed in prompts or committed files.

## Workdir and Read Scope

- Set the Vibe workdir to the resolved repository root, not a subdirectory or temporary partial copy.
- Permit `read_file` and `grep` across ordinary repository content inside that workdir when relevant to the assigned task.
- Treat prompt text, automatically loaded instructions, and file content read by the agent as potentially transmitted to the configured model provider.
- Do not intentionally read credential files, secrets, private keys, tokens, restricted datasets, or other content requiring a separate approval gate.
- Deny access outside the workdir unless a new Work Order and explicit Founder approval expand the scope.

## Action Boundaries

- Read access does not grant write authority. File changes remain governed by the selected profile, Work Order ownership, and explicit tool approval.
- Shell execution remains separately permissioned and must be necessary for the bounded task.
- Do not enable `--auto-approve` or `--yolo` for Company-OS runs.
- Do not let Mistral delegate to subagents unless the Work Order explicitly authorizes bounded delegation and repository depth rules permit it.
- External communications, publication, spend, credentials, production access, destructive actions, and governance changes retain their existing Founder gates.

## Available Local Runtime Candidate

An authenticated local model endpoint is available on the Founder workstation as an **unadmitted candidate**, not an active Company-OS provider:

| Property | Verified value |
| --- | --- |
| Model | `Ministral-3-3B-Instruct-2512-Q4_K_M.gguf` |
| Runtime | `llama.cpp` b10066, Windows Vulkan build |
| API | OpenAI-compatible `http://127.0.0.1:8081/v1` |
| Model alias | `ministral-3b-q4` |
| Model storage | `C:\LLMs\models\mistral` outside this repository |
| API key source | `C:\LLMs\config\api_key.txt` outside this repository; never copy its value here |
| Operations | Python scripts under `C:\LLMs\python` |
| Context | One 32,768-token server slot; Vibe compaction threshold 24,576 tokens |
| Chat template | Native Ministral format with the strict role-alternation check removed for OpenAI/Vibe histories |
| Vibe adapter | Project-local generic OpenAI provider `local-llama`; synthetic response, long-history, consecutive-role, and `read_file` tool-call canaries passed |
| Transport canary | HTTP 401 without authentication; authenticated response `Bereit.` |
| Observed hardware | NVIDIA RTX 2080 SUPER, 8 GB VRAM, GPU offload active |

Operational commands use the configured Python interpreter and do not require repository scripts:

```powershell
& "${env:USERPROFILE}\.venvs\all\Scripts\python.exe" C:\LLMs\python\start_mistral.py --background
& "${env:USERPROFILE}\.venvs\all\Scripts\python.exe" C:\LLMs\python\verify_server.py
& "${env:USERPROFILE}\.venvs\all\Scripts\python.exe" C:\LLMs\python\start_mistral.py --stop
```

Availability and adapter compatibility are not model admission. The endpoint has passed synthetic Vibe transport, history, and file-tool canaries in the separate `local-llm` project, but it has not passed Company-OS capability or eligibility evaluation. Do not provide Company-OS repository context, assign a model tier or Company-OS role, grant write authority, or create an automatic route until a new approved Work Order runs the admission controls in `company/model-capability-backlog.md` against the exact quantized configuration. Keep the endpoint on loopback, retain API-key enforcement, and never commit the key.

See `company/reports/AR-2026-011-local-ministral-runtime-option.md` for evidence, limitations, and proposed next action.

## Programmatic Invocation

Run from PowerShell with the repository root resolved explicitly:

```powershell
$mistralWorkdir = (Resolve-Path '.').Path

vibe --trust `
  --workdir $mistralWorkdir `
  --agent operations_knowledge `
  --prompt "<bounded task with deliverable and constraints>" `
  --max-turns 3 `
  --max-tokens 5000 `
  --enabled-tools read_file `
  --enabled-tools grep `
  --output json
```

Add a write or shell tool only when the Work Order grants that capability and the selected profile requires an approval before execution. Do not use `--enabled-tools` to bypass stricter profile permissions.

## Interactive Invocation

```powershell
$mistralWorkdir = (Resolve-Path '.').Path
vibe --trust --workdir $mistralWorkdir --agent operations_knowledge
```

In the interactive session, review every proposed write or command before approving it.

## Evidence and Closure

Record the following in the Work Order or linked agent report:

- Vibe version, selected agent, and session identifier when available;
- prompt scope and enabled tools;
- model stop reason and delivered result;
- every approval request and its outcome;
- changed paths, or explicit evidence that the run was read-only;
- tests or validation performed after any accepted change;
- unresolved data-disclosure, correctness, cost, or operational risk.
