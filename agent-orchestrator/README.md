# Agent Orchestrator

Repository-local, vendor-neutral routing and execution for bounded local and cloud model workers.

## Quick start

```powershell
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" .\orchestrate.py doctor
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" .\orchestrate.py inventory
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" .\orchestrate.py route .\examples\route-local.json
```

The CLI prints compact JSON. Raw trajectories, snapshots, locks, evaluation candidates, and quarantine patches stay under the ignored `.runtime/` directory.

## Billing semantics

Provider access plans are canonical in `config/providers.toml`; public model API prices remain reference data in `config/models.toml`. The active Google-account path is `plan = "free"` with quota-based access. The active Mistral Vibe path is `plan = "pro"` and is included in the user's fixed subscription.

Run evidence therefore reports Gemini as `free-quota` with zero direct marginal charge and Mistral Vibe as `included-subscription` with zero marginal charge but no allocated per-run dollar amount. Only metered API providers produce `estimated-token-cost`. This prevents public Mistral API list prices from being mistaken for charges incurred through the PRO subscription. Quota exhaustion, retries, and latency remain operational routing signals even when marginal monetary cost is zero.

## Contracts

- Provider, model, harness, and exact model/harness profiles are separate registry entities under `config/`.
- Jobs use the strict version-1 contract in `schemas/job.schema.json`.
- A target directory must be an existing repository subdirectory containing every context file the worker needs.
- Write jobs may declare `allowed_write_paths`; any changed file outside those target-relative files or directory prefixes fails the ownership gate and triggers quarantine plus rollback. Omitting the field preserves the version-1 whole-target behavior for existing jobs.
- `candidate`, `deferred`, and unavailable profiles cannot be routed.
- Gemini via a free Google account is an executable option through the official Antigravity CLI.

## Gemini with a Google account

Google ended free/individual request serving through the former Gemini CLI on June 18, 2026. The current consumer route is the official Antigravity CLI (`agy`), which still serves Gemini models. Install it outside the repository, without changing shell aliases or the profile `PATH`, then run it once for browser sign-in:

```powershell
& ([scriptblock]::Create((Invoke-RestMethod https://antigravity.google/cli/install.ps1))) --skip-aliases --skip-path
& "$env:LOCALAPPDATA\agy\bin\agy.exe"
```

No Google key or OAuth token is stored in this repository; authentication stays in the operating-system keyring. The orchestrator finds `agy` either on `PATH` or at its standard per-user Windows location. `gemini-auto-free-read` currently selects `Gemini 3.5 Flash (Medium)` explicitly and uses `plan` mode; model names must be revalidated after CLI upgrades. Consumer access is recorded as account quota rather than a guaranteed zero-price API. The admitted `gemini-auto-free-files` profile uses `accept-edits` and an external Antigravity project/worktree, while accepted writes must remain in the job target.

Candidate profiles can only execute through `eval run --job ...` with an explicit `model_profile`; ordinary `route`, `run`, and graph execution continue to reject them. Antigravity may use its external worktree infrastructure during evaluation, but accepted artifacts must still land in the single job target.

The file-only profile allows target-relative file operations; shell commands, web access, MCP, and non-workspace access remain denied. The QA profile `gemini-auto-free-commands` additionally accepts a non-empty `allowed_commands` list from the version-1 job contract. Entries must come from the repository's fixed test/build/status allowlist. For each serialized Gemini command run, the adapter temporarily replaces the external Antigravity permissions with the absolute job target and only that job's commands, then restores the original settings byte-for-byte. Package installation and download commands remain denied. Because tests execute repository code and may have side effects, write snapshots and independent verifiers remain mandatory release gates.

The file profile was admitted by `antigravity-file-canary-v1` with an exact-content verifier and artifact hash. The command profile was admitted by `antigravity-command-canary-v1`: Gemini itself ran `python -m unittest -v`, the independent verifier repeated the test successfully, and the target hashes showed no changes.

After sign-in, run the explicit read canary:

```powershell
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" .\orchestrate.py run .\examples\gemini-read-canary.json
```

A command job declares only the checks it needs, for example:

```json
{
  "tool_class": "commands",
  "allowed_commands": ["python -m unittest -v"]
}
```

## Commands

| Command | Purpose |
| --- | --- |
| `doctor` | Check registry links, executables, credentials, and local runtime state. |
| `inventory` | List providers, models, harnesses, profiles, costs, and availability. |
| `route JOB` | Explain the capability-first route without execution. |
| `run JOB` | Execute one locked, transactional job. |
| `run-graph GRAPH` | Run a dependency graph with bounded parallelism. |
| `status [RUN_ID]` | Return one compact run summary. |
| `runtime start\|status\|stop` | Manage the registered local Ministral runtime. |
| `eval run [--job JOB]` | Audit profiles or retain one live profile-candidate result. |

## Failure behavior

Write jobs snapshot their target directory. If the worker or an independent verifier fails, changed and added files are copied into a quarantine bundle, a text patch and manifest are retained, and the exact pre-run state is restored. The runtime manager refuses to stop a server it did not start.

## Tests

```powershell
$env:PYTHONPATH = "src"
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" -m unittest discover -s tests -v
```
