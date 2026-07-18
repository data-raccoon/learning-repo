# Test 03 — Orbital Command

This is the ambitious, auditable multi-run experiment. Each Mistral task and repair was
a separate process with hashes, timestamps, output metadata, and token usage.

## Files that belong to this test

- [`orbital-command/`](orbital-command/) — playable strategy game, contracts, task
  graph, design data, runtime, browser smoke test, documentation, job specifications,
  run records, and integration decisions.
- [`tools/run_local_job.py`](tools/run_local_job.py) — executes exactly one auditable
  local-Mistral job.
- [`tools/assemble_orbital_data.py`](tools/assemble_orbital_data.py) — validates design
  artifacts and creates the runtime data interface.
- [`tools/verify_orbital_command.py`](tools/verify_orbital_command.py) — runs the final
  integration scenario in headless Edge.

Open [`orbital-command/index.html`](orbital-command/index.html) to play. Start with the
game's [`TASK_GRAPH.md`](orbital-command/TASK_GRAPH.md) and
[`README.md`](orbital-command/README.md) when inspecting the orchestration history.

Example verification command from the workspace root:

```powershell
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" .\game-building-tests\03-orbital-command\tools\verify_orbital_command.py
```
