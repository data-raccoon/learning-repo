# Small-context agent harness

A dependency-free task boundary and compact model router for orchestrator and
worker models with small context windows. It is the default model harness for
this repository.

The default path gives Ollama or Gemini no repository write access:

```text
trusted task --pack--> bounded packet --route--> model --invoke--> proposal
      |
      +--accept--> externally scoped writer --result--> gate
```

The public tool set remains one CLI:

- `inventory` checks the declared registry against live Ollama tags and the
  installed Gemini `agy` CLI.
- `canary` invokes one explicit profile with a fixed exact-response contract.
- `pack` resolves target-local file slices, rejects likely secrets, enforces a
  character budget, hashes every excerpt, and binds the packet to the task.
- `route` chooses the weakest eligible available model that supports the
  declared capability and importance.
- `invoke` runs a bounded proposal call and writes a compact, hash-bound
  response envelope.
- `accept` validates the packet and creates an acknowledgement bound to its hash.
- `gate` checks acknowledgement, task/packet identity, output size, the scope and
  digest of every reported artifact, and then runs the trusted task's verifiers
  without a shell.

## Why this shape

The source research agrees on a small deterministic control kernel around
probabilistic model calls. This kit keeps only the mechanisms needed for a
bounded repository task:

- explicit workflow instead of a free-form agent loop;
- minimal context rather than transcript transfer;
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

| Profile | Provider | Default use |
|---|---|---|
| `ollama-ministral-3-8b` | Local Ollama | extraction, classification, formatting, summarization |
| `ollama-qwen3.5-9b` | Local Ollama | coding proposals, reasoning, and review |
| `ollama-ministral-3-14b` | Local Ollama | planning, architecture, and stronger review |
| `gemini-auto-free` | Official Antigravity `agy` CLI | critical work that clears the higher routing threshold |

All profiles use deliberately smaller runtime context caps than their advertised
maximums. Ollama model digests are pinned and checked against `/api/tags`.
Gemini uses the external OS-keyring account; API and Vertex environment
credentials are removed before invocation. It runs in plan mode with
`--sandbox` from an isolated empty OS-temporary directory. Unlike the direct
Ollama API, the external CLI owns its internal tool surface; the harness supplies
no repository path and grants no repository write authority.

## Quick start

From this directory, using the repository's required Python interpreter:

```powershell
Copy-Item examples\task.json task.json
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" harness.py inventory
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" harness.py pack task.json packet.json --repo ..
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" harness.py route packet.json
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" harness.py invoke packet.json response.json
```

The response is advisory; the model did not edit or verify repository files.
For an external mutating worker, acknowledge the packet, enforce its write
roots, and have it return JSON shaped like `examples/result.json`:

```powershell
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" harness.py accept packet.json ack.json --worker local-worker
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" harness.py gate task.json packet.json ack.json result.json --repo ..
```

All commands emit one compact JSON object. Exit code `0` means success; `2`
means the contract or gate rejected the input.

## Contracts

`task.schema.json` and `result.schema.json` document the public contracts.
Runtime validation is implemented with the Python standard library so the
harness has no installation step.

Important task fields:

- `target`: the only repository subtree visible to the task.
- `model`: routing capability, importance, and optional explicit profile.
- `context`: exact target-relative files and inclusive line slices.
- `write_roots`: target-relative files or directories the worker may change.
- `done`: concise, testable outcomes given to the worker.
- `verifiers`: trusted argument arrays executed by the gate in `target`.
- `limits`: hard packet, output, tool-call, verifier, and timeout caps. The
  `packet_chars` cap covers the complete serialized worker packet, not just file
  excerpts.

The `max_tool_calls` limit is part of the worker contract but must be enforced by
the model runner. This CLI cannot observe an external runner's tool calls.

## Architecture decision

This is a level-2 workflow with a proposal default and a file-write release gate:

1. The controlling agent creates and packs an immutable task.
2. A local-first router selects an available eligible proposal model.
3. The model receives only the packet and returns a bound response. Ollama gets
   no tools; Gemini is isolated from repository paths and write authority.
4. A mutating worker explicitly acknowledges that exact packet when needed.
5. The external worker runner enforces declared write roots; the gate rejects
   reported artifacts outside them.
6. The controller checks current file digests and independently runs verifiers.
7. Anything unknown or inconsistent fails closed.

There is no ownership transfer of user authority. Acceptance records task
receipt, not permission escalation. Consequential actions such as deployment,
publishing, credential access, or external communication remain outside this
harness and require their own approval and enforcement point.

The gate cannot discover unreported filesystem writes by itself. Use a runner
that enforces `write_roots` or snapshots and restores the target. This limitation
is explicit because a result contract is evidence, not an authorization barrier.

## Verification

```powershell
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" -m unittest discover -s tests -v
```
