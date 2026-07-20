# AI-Learn Root Agent Instructions

## Repository boundaries

- `local-models/` — model binaries, serving code, templates, endpoint checks.
- `agent-orchestrator/` — reusable multi-model control plane.

## Model delegation

- Use the repo-local `orchestrate-models` skill when work benefits from a worker model.
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
- Gemini workers use the official `agy` executable and its OS-keyring session. Do not place OAuth data in the repository or substitute API/Vertex credentials for the consumer-account profile.
- Antigravity may use its external project/worktree storage. Gemini file tools write only inside the job target. The admitted Gemini QA profile runs only the fixed commands listed in the job's `allowed_commands`; each run gets a temporary absolute-target policy and an independent verifier. Network, MCP, package installation, downloads, and non-workspace access are forbidden.

## Verification

Python interpreter for all scripts: `& "$env:USERPROFILE\.venvs\all\Scripts\python.exe"`. Never use bare `python`.

```powershell
# agent-orchestrator/ — after changing the orchestrator or its skill
$env:PYTHONPATH = "src"
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" -m unittest discover -s tests -v
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" orchestrate.py doctor

# repo root — after changing gaming-agents/
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" -m unittest discover -s gaming-agents\tests -v

# local-models/<model>/ — after changing model scripts
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" verify_server.py   # ministral
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" verify_colibri.py  # colibri (deferred)
```
