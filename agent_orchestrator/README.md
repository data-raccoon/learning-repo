# Agent Orchestrator

Repository-local, vendor-neutral routing and execution for bounded local and cloud model workers.

## Quick start

```powershell
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" .\orchestrate.py doctor
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" .\orchestrate.py inventory
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" .\orchestrate.py route .\examples\route-local.json
```

The CLI prints compact JSON. Raw trajectories, snapshots, locks, evaluation candidates, and quarantine patches stay under the `.runtime/` directory, which defaults to `%LOCALAPPDATA%\agent-orchestrator\.runtime` outside OneDrive to avoid sync issues. Override with the `AGENT_ORCHESTRATOR_RUNTIME` environment variable if needed.

## Billing semantics

Provider access plans are canonical in `config/providers.toml`; public model API prices remain reference data in `config/models.toml`. The active Google-account path is `plan = "free"` with quota-based access. The active Mistral Vibe path is `plan = "pro"` and is included in the user's fixed subscription.

Run evidence therefore reports Gemini as `free-quota` with zero direct marginal charge and Mistral Vibe as `included-subscription` with zero marginal charge but no allocated per-run dollar amount. Only metered API providers produce `estimated-token-cost`. This prevents public Mistral API list prices from being mistaken for charges incurred through the PRO subscription. Quota exhaustion, retries, and latency remain operational routing signals even when marginal monetary cost is zero.

## Contracts

- Provider, model, harness, and exact model/harness profiles are separate registry entities under `config/`.
- Jobs use the strict version-1 contract in `schemas/job.schema.json`.
- A target directory must be an existing repository subdirectory containing every context file the worker needs.
- Write jobs may declare `allowed_write_paths`; any changed file outside those target-relative files or directory prefixes fails the ownership gate and triggers quarantine plus rollback. Omitting the field preserves the version-1 whole-target behavior for existing jobs.
- A write-mode `inference` job may declare `materialization` to turn validated JSON into a file append or write. The model receives no file tools: the orchestrator validates `output_schema`, renders a scalar-only template, performs the declared mutation, and then applies the normal artifact, ownership, verifier, and rollback gates.
- `candidate`, `deferred`, and unavailable profiles cannot be routed.
- Gemini via a free Google account is an executable option through the official Antigravity CLI.

## Bounded harnesses

`schemas/harness.schema.json` composes existing version-1 jobs without changing their public contract. A harness is deliberately not a free-form agent chat: it is a deterministic controller for one of three bounded topologies:

- `pipeline` — one connected sequence;
- `fanout-fanin` — independent branches followed by an `all`, manifest-ordered `first-passing`, or allowlisted `verifier` join;
- `repair` — work, independent verification, and a bounded number of repair/reverify cycles.

Every write node in a harness must declare `allowed_write_paths`. Concurrent nodes targeting the same directory must own disjoint paths; the existing target lock may still serialize them. Handoffs are producer artifacts that the consumer also declares as context. Harness v1 permits only same-target handoffs, validates their media type and optional JSON schema/pinned hash before the producer transaction commits, and checks their recorded SHA-256 again before consumption.

Harness-wide limits bound admitted nodes, total attempts, parallelism, deadline, and optionally tokens and marginal cost. Strict token limits require a provider with measured usage. Strict cost limits require a route whose marginal cost can be measured; use `best-effort` explicitly when incomplete accounting is acceptable. Running jobs are never force-killed by a graph limit and remain bounded by their job timeout, so they may move actual usage past a threshold; no new node starts after the measured graph limit is reached.

Harness evidence is separate from child-job evidence under `%LOCALAPPDATA%\agent-orchestrator\.runtime\harness-runs`. Explicit `--resume RUN_ID` reuses a passed node only when the normalized harness, job contract, resolved route, upstream reuse chain, and produced artifact hashes still match. See `examples/harnesses/` for synthetic manifests. These examples and all harness tests are offline; they do not constitute model experiments.

For iterative prose, prefer a pipeline of tool-free inference jobs over a file-tool conversation. Seed one transcript file, make each node read it, constrain each response with a small JSON schema, and let every node append through `materialization`. This keeps the full conversation and model trajectories on disk while the root orchestrator only receives compact node summaries. Sequential dependencies safely permit the nodes to share ownership of the transcript.

## Creating jobs

**Target directory rules:** Use relative paths only; absolute paths raise `absolute paths are forbidden`. Target must be a subdirectory (not the workspace root); targeting `.` raises `path escapes its allowed root`. Do not use parent traversal (`..`). All context files must live inside the target.

**Required workflow:** Always `route` before `run`. The `route` command validates the job, selects the weakest eligible profile meeting the 0.85 success threshold, and explains acceptance/rejection reasons for each candidate. This catches path errors and capability mismatches before execution.

**Profile selection:** Specify `model_profile` in the job to pin a profile, or let the orchestrator auto-select. Ensure `required_capabilities` in the job are a subset of the profile's capabilities. Use `route` to verify the selected profile matches expectations.

**Worker isolation:** Each job gets exactly one target subdirectory. Provide all needed context within that directory. For cross-directory work, create separate jobs per subdirectory.

Example minimal read job:
```json
{
  "schema_version": 1,
  "id": "analyze-subdir",
  "objective": "Review and summarize code in target directory",
  "target_dir": "src/module",
  "mode": "read",
  "importance": "normal",
  "risk": "low",
  "tool_class": "files_read",
  "model_profile": "gemini-auto-free-read",
  "required_capabilities": ["review", "reasoning", "summarization"],
  "limits": {"timeout_seconds": 180, "max_turns": 5, "max_tokens": 40000}
}
```

Example deterministic append job:

```json
{
  "schema_version": 1,
  "id": "dialogue-turn-1",
  "objective": "Return the first dialogue turn as the required JSON object.",
  "target_dir": "dialogue-run",
  "mode": "write",
  "importance": "low",
  "risk": "low",
  "tool_class": "inference",
  "model_profile": "local-ministral-inference",
  "context": ["dialogue.md"],
  "output_schema": "turn-1.schema.json",
  "expected_artifacts": ["dialogue.md"],
  "allowed_write_paths": ["dialogue.md"],
  "materialization": {
    "path": "dialogue.md",
    "operation": "append",
    "template": "<!-- TURN {turn} -->\n**{speaker}:** {text}\n\n"
  },
  "limits": {
    "timeout_seconds": 180,
    "max_turns": 1,
    "max_tokens": 32000,
    "max_output_tokens": 1200
  }
}
```

`max_tokens` remains the worker/harness accounting ceiling. `max_output_tokens` independently caps direct local inference generation, so a model can retain its full context budget without being invited to produce a 32k-token answer. Effective-model attestations are included in compact run summaries; a local API model mismatch or a Vibe fallback warning fails the run closed.

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
| `harness validate MANIFEST` | Validate paths, topology, routes, ownership, handoffs, and budgets without execution. |
| `harness run MANIFEST [--dry-run] [--resume RUN_ID]` | Preview or execute a bounded harness. |
| `harness status [RUN_ID]` | Return one compact harness summary from the separate evidence namespace. |
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
