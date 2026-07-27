# AI-Learn Root Agent Instructions

## Repository boundaries

- `small-context-harness/` — default model registry, routing, bounded packets, and gates.

## Model delegation

- Use `small-context-harness/harness.py` through the repo-local
  `orchestrate-models` skill when work benefits from a worker model.
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

```
