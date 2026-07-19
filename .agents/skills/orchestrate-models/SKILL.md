---
name: orchestrate-models
description: Route and execute bounded repository tasks through the repo-local vendor-neutral model orchestrator. Use when Codex should inspect model availability, choose an eligible local or cloud model, run one model job or a parallel dependency graph, manage the registered local Ministral runtime, inspect compact run evidence, or audit model capability profiles.
---

# Orchestrate Models

Use the deterministic CLI at `agent-orchestrator/orchestrate.py`. Keep model trajectories and large artifacts out of the main context; consume compact JSON summaries.

## Workflow

1. Run `doctor` when provider or runtime readiness is unknown.
2. Ensure the target subdirectory contains all required context. Never compensate for missing context by granting broader repository access.
3. Create or validate a version-1 job JSON against `agent-orchestrator/schemas/job.schema.json`.
4. Run `route <job>` before consequential work. Treat `candidate`, `deferred`, and `unavailable` profiles as ineligible.
5. Run `run <job>` or `run-graph <graph>` only after target, tools, artifacts, verifiers, and stop limits are explicit.
6. Read the summary. Load `.runtime` trajectories or quarantine files only to diagnose a failure or when explicitly requested.

Invoke the CLI on Windows with:

```powershell
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" agent-orchestrator\orchestrate.py <command>
```

## Safety boundaries

- Keep delegation at one level. Never ask a worker to spawn another worker.
- Give each worker exactly one target subdirectory. Do not add external read directories.
- Use `allowed_write_paths` when a workflow assigns narrower ownership inside that target. Treat an ownership-gate failure like any other rejected write: preserve quarantine evidence and restore the snapshot.
- Prefer file-only profiles for small or unqualified models.
- Preserve independent verifiers; never let a worker weaken its own release gate.
- Read provider `billing` and `plan` from the inventory when cost matters. Treat `free-quota` and `included-subscription` as different operational resources even though both have zero direct marginal charge; do not reinterpret public API list prices as subscription-run costs.
- Let the runner quarantine and roll back failed writes. Do not accept a failed trajectory as completion.
- Never place API keys, model weights, PID files, or provider logs in the repository.
- Do not route OpenAI/ChatGPT while its milestone status remains deferred.
- For Gemini consumer-account work, require Google's current official Antigravity CLI (`agy`) and external Google login. External Antigravity projects/worktrees are allowed. `gemini-auto-free-files` may use target-relative file read/write/edit tools after `antigravity-file-canary-v1`; shell access remains forbidden for that profile. `gemini-auto-free-commands` may run only the fixed commands explicitly listed in the job's non-empty `allowed_commands`, inside the absolute target, after `antigravity-command-canary-v1`. Preserve snapshots and independent verifiers because QA commands execute repository code. Network, MCP, package installation, downloads, parent-directory access, and recursive delegation remain forbidden.

## Common commands

```powershell
python agent-orchestrator\orchestrate.py inventory
python agent-orchestrator\orchestrate.py route path\to\job.json
python agent-orchestrator\orchestrate.py run path\to\job.json
python agent-orchestrator\orchestrate.py run-graph path\to\graph.json
python agent-orchestrator\orchestrate.py status latest
python agent-orchestrator\orchestrate.py eval run
```
