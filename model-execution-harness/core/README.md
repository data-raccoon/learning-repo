# Core model execution harness

A dependency-free task boundary and compact model-worker router designed to
keep full trajectories out of the controlling agent's token context.

```text
task --pack--> packet --route--> model --accept--> snapshot
                                                  |
                                              execute
                                                  |
                         durable files + trajectory + result --gate--> accepted
```

The public tool set remains one CLI:

- `inventory` checks the declared registry against live Ollama tags and the
  installed Gemini `agy` and Mistral Vibe CLIs.
- `canary` invokes one explicit profile with a fixed exact-response contract.
- `pack` resolves target-local file slices, rejects likely secrets, enforces a
  character budget, hashes every excerpt, and binds the packet to the task.
- `route` validates the explicitly human-selected profile and never substitutes
  or ranks models automatically.
- `accept` validates the packet and creates an acknowledgement bound to its hash.
- `snapshot` records a packet-bound target manifest outside the target before a
  mutating worker runs.
- `execute` runs Medium or Devstral with target-bounded reads, exact write roots,
  and exact admitted command vectors; it persists the full trajectory and
  derives a compact result envelope from the baseline diff.
- `gate` checks acknowledgement, task/packet identity, output size, the scope and
  digest of every reported artifact, optionally proves the complete target diff
  against a baseline, and then runs trusted verifiers without a shell.

## Why this shape

The source research agrees on a small deterministic control kernel around
probabilistic model calls. This kit keeps only the mechanisms needed for a
bounded repository task:

- explicit workflow instead of a free-form agent loop;
- minimal controller context and durable trajectories rather than transcript transfer;
- typed, hash-bound handover and acknowledgement;
- one target directory and least-privilege write roots;
- hard packet, output, tool-call, verifier-count, and verifier-time limits;
- fail-closed validation and independent end-state checks;
- compact machine-readable evidence.

It intentionally omits durable execution, databases, agent graphs, multi-agent
fan-out, policy engines, and sandboxes. Add those only when a measured
requirement cannot be met by this boundary. The harness does not make worker
code safe to execute; run untrusted code in an appropriate external sandbox.

## Registered models

`models.json` registers:

| Profile | Provider | Physical / compact / session | Default use |
|---|---|---:|---|
| `ollama-ministral-3-3b` | Local Ollama | 8k / — / 8k | low-cost extraction, classification, formatting, summarization |
| `ollama-ministral-3-8b` | Local Ollama | 8k / — / 8k | extraction, classification, formatting, summarization |
| `ollama-ornith-9b` | Local Ollama | 8k / — / 8k | coding proposals, reasoning, and review |
| `ollama-gemma4-e4b` | Local Ollama | 8k / — / 8k | reasoning, review, and summarization |
| `ollama-ministral-3-14b` | Local Ollama | 8k / — / 8k | planning, architecture, and stronger review |
| `gemini-auto-free` | Official Antigravity `agy` CLI | 16k / — / 16k | broad proposal work |
| `devstral-small` | Mistral Vibe CLI cloud provider | 256k / 200k / 1M | Devstral Small 2 implementation |
| `mistral-medium-3.5` | Mistral Vibe CLI cloud provider | 128k / 100k / 500k | durable task definition, planning, architecture, and review artifacts |

All profiles use deliberately smaller runtime context caps than their advertised
maximums. Ollama model digests are pinned and checked against `/api/tags`.
Gemini uses the external OS-keyring account; API and Vertex environment
credentials are removed before invocation. It runs in plan mode with
`--sandbox` from an isolated empty OS-temporary directory. Unlike the direct
Ollama API, the external CLI owns its internal tool surface; the harness supplies
no repository path and grants no repository write authority.
Ollama and Gemini remain available for inventory and provider canaries. Bounded
repository execution uses the registered Mistral Vibe profiles.

## Mistral Vibe integration

Both aliases must be present in `%USERPROFILE%\.vibe\config.toml`. For each
execution the harness copies that model catalog into an isolated temporary
`VIBE_HOME`, sets `VIBE_ACTIVE_MODEL` to the selected profile, and overrides
that alias's auto-compaction threshold with the lower of the registered
threshold and the task-admitted context. No project-local registry or selector
is needed.

`model_context_tokens` limits the live working context. `model_session_tokens`
limits cumulative prompt plus completion usage across the Vibe session and may
be admitted up to the profile's registered extended-session cap. Compaction is
lossy: the larger session budget permits several summarized working epochs; it
does not enlarge a single model request. Important state must therefore remain
in target files and may be reread after compaction.

The worker gets `read_file` and `grep` inside one target. `edit` and `write_file`
are auto-approved only for declared write roots. The custom `limited_bash` tool
accepts only exact task-declared argv vectors admitted by the harness's fixed
policy and executes them with `shell=False`; it performs no shell expansion,
pipelines, redirects, or substitutions. Network, MCP, connectors, generic
shells, and subagents are disabled.

Planning is a write task: assign Medium an exact plan or task-definition path.
Coding uses the same path with Devstral. In both cases the complete Vibe JSON
trajectory is written outside the target and the CLI returns only compact
metadata. Do not load the full trajectory into controller context by default.
Use at least a 16k cumulative Vibe token budget for file-tool work; the live
Medium smoke run measured roughly 10k tokens of system/tool-session overhead.

## Quick start

From this directory, using the repository's required Python interpreter:

```powershell
Copy-Item examples\task.json task.json
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" harness.py inventory
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" harness.py pack task.json packet.json --repo ..
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" harness.py route packet.json
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" harness.py accept packet.json ack.json --worker local-worker
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" harness.py snapshot task.json packet.json ack.json baseline.json --repo ..
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" harness.py execute packet.json ack.json baseline.json result.json trajectory.json --repo ..
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" harness.py gate task.json packet.json ack.json result.json --baseline baseline.json --repo ..
```

All commands emit one compact JSON object. Exit code `0` means success; `2`
means the contract or gate rejected the input.

## Contracts

`task.schema.json`, `result.schema.json`, and `baseline.schema.json` document the
public contracts.
Runtime validation is implemented with the Python standard library so the
harness has no installation step.

Important task fields:

- `target`: the only repository subtree visible to the task.
- `model`: capability, importance, and one explicit human-selected profile.
- `context`: exact target-relative files and inclusive line slices.
- `write_roots`: up to 256 target-relative files or directories the worker may
  change; prefer exact files over broad directories.
- `allowed_commands`: optional exact argv vectors admitted by the global command
  policy and exposed through `limited_bash`.
- `done`: concise, testable outcomes given to the worker.
- `verifiers`: trusted argument arrays executed by the gate in `target`.
- `limits`: hard packet, output, model-context, cumulative model-session,
  tool-call, verifier, and timeout caps. The `packet_chars` cap covers the
  complete serialized worker packet, not just file excerpts.

The `max_tool_calls` limit bounds the Vibe programmatic turn budget.

## Architecture decision

This is a level-2 workflow with one durable worker path and a file-write release gate:

1. The controlling agent creates and packs an immutable task.
2. The router validates one explicitly selected Medium or Devstral profile.
3. The worker explicitly acknowledges the exact packet.
4. The controller records a packet-bound target baseline outside the target.
5. The worker reads the target and writes durable artifacts through bounded
   tools; its full trajectory remains on disk.
6. The worker runner enforces declared write roots; baseline audit also
   rejects unreported writes, deletions, and files outside them.
7. The controller checks current file digests and independently runs verifiers.
8. Anything unknown or inconsistent fails closed.

There is no ownership transfer of user authority. Acceptance records task
receipt, not permission escalation. Consequential actions such as deployment,
publishing, credential access, or external communication remain outside this
harness and require their own approval and enforcement point.

Without `--baseline`, the gate cannot discover unreported filesystem writes.
For mutating workers, use both runner-enforced `write_roots` where available and
the packet-bound `snapshot`/`gate --baseline` flow. The baseline must be stored
outside the target so the worker cannot alter its own audit evidence.

## Verification

```powershell
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" -m unittest discover -s tests -v
```
