# AI-Learn Root Agent Instructions

## Repository boundaries

- Keep model binaries, serving code, templates, and endpoint checks in `local-models/`.
- Keep historical controller experiments and their evidence in `orchestration-experiments/`.
- Keep the reusable multi-model control plane in `agent-orchestrator/`.
- Keep the reusable engine-neutral game MVP roles, scaffolding, and approval workflow in `gaming-agents/`.
- Treat Company-OS and every future OS or initiative as independent use cases, not as global policy.

## Model delegation

- Use the repo-local `orchestrate-models` skill when work benefits from a local or cloud worker model.
- Keep delegation one level deep. Only the root agent may create model jobs or graphs.
- Give every worker one target subdirectory containing all necessary context.
- Never widen a worker's read scope to compensate for an incomplete task packet.
- Prefer the weakest admitted model expected to succeed, except critical planning and architecture, which use the strongest eligible profile.
- Keep large responses and trajectories on disk. Return compact status, hashes, gates, usage, cost, and artifact paths.
- Accept worker output only after independent gates pass. Preserve quarantine evidence and rollback on failure.

## Secrets and local runtimes

- Keep credentials, model weights, runtime logs, and PID files outside the repository.
- Do not stop a local runtime unless the orchestrator proves it started that exact process.
- OpenAI/ChatGPT remains inventory-only until explicitly admitted.
- Gemini Google-account workers must use Google's current official `agy` executable and its external OS-keyring session. Do not place OAuth data in the repository or substitute API/Vertex credentials for the consumer-account profile.
- Antigravity may use its external project/worktree storage. Gemini file tools may write only inside the job target. The admitted Gemini QA profile may execute only fixed repository-approved commands explicitly listed in the job's `allowed_commands`; each run receives a temporary absolute-target policy and an independent verifier. Network, MCP, package installation, downloads, and non-workspace access remain forbidden.

## Verification

Run these commands from `agent-orchestrator/` after changing the orchestrator or its skill:

```powershell
$env:PYTHONPATH = "src"
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" -m unittest discover -s tests -v
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" orchestrate.py doctor
```

After changing `gaming-agents/` or its orchestration contract, also run from the repository root:

```powershell
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" -m unittest discover -s gaming-agents\tests -v
```
