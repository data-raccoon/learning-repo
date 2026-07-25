# AI-Learn Root Agent Instructions

## Repository boundaries

- `local-models/` — model binaries, serving code, templates, endpoint checks.
- `small-context-harness/` — default model registry, routing, bounded packets, and gates.
- `agent_orchestrator/` — legacy/advanced multi-model control plane; use only when explicitly required.

## Model delegation

- Use `small-context-harness/harness.py` through the repo-local
  `orchestrate-models` skill when work benefits from a worker model.
- Default to `pack -> route -> invoke`; models return bounded proposals and
  never receive repository write authority.
- Use `agent_orchestrator` only for a requirement the small-context harness does
  not support, such as admitted command workers, graphs, or durable run evidence.
- Delegation is one level deep. Only the root agent creates jobs or graphs.
- Give every worker exactly one target directory with all required context.
- Never widen a worker's read scope to compensate for an incomplete task packet.
- Prefer the weakest admitted model expected to succeed; use the strongest only for critical planning and architecture.
- Keep large responses and trajectories on disk. Return compact status, hashes, gates, usage, cost, and artifact paths.
- Accept worker output only after independent gates pass. Preserve quarantine evidence and rollback on failure.

## Secrets and local runtimes

- Keep credentials, model weights, runtime logs, and PID files outside the repository.
- Do not stop a local runtime unless the orchestrator proves it started that exact process.
- OpenAI/ChatGPT is inventory-only until explicitly admitted.
- Ollama workers use the loopback API and exact registered model digests.
- Gemini proposal workers use the official `agy` executable and its OS-keyring
  session. Do not place OAuth data in the repository or substitute API/Vertex
  credentials for the consumer-account profile.
- Antigravity may use its external project/worktree storage. Gemini file tools write only inside the job target. The admitted Gemini QA profile runs only the fixed commands listed in the job's `allowed_commands`; each run gets a temporary absolute-target policy and an independent verifier. Network, MCP, package installation, downloads, and non-workspace access are forbidden.

## Shell

Windows 11, Git Bash. Avoid && || ; in commands.

## Verification

Python interpreter for all scripts: `& "$env:USERPROFILE\.venvs\all\Scripts\python.exe"`. Never use bare `python`.

```powershell
# small-context-harness/ — after changing the default harness or its skill
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" -m unittest discover -s small-context-harness\tests -v
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" small-context-harness\harness.py inventory

# agent_orchestrator/ — after changing the legacy orchestrator
$env:PYTHONPATH = "src"
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" -m unittest discover -s tests -v
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" orchestrate.py doctor

# repo root — after changing gaming-agents/
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" -m unittest discover -s gaming-agents\tests -v

# local-models/<model>/ — after changing model scripts
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" verify_server.py   # ministral
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" verify_colibri.py  # colibri (deferred)
```
