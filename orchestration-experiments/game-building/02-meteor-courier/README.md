# Test 02 — Meteor Courier

This experiment applied a manifest-driven architecture to a larger multi-file canvas
game. Local Mistral supplied bounded design artifacts while a deterministic runtime and
browser smoke suite handled integration.

## Files that belong to this test

- [`meteor-courier/`](meteor-courier/) — playable game, configuration, runtime, smoke
  test, visual system, and game README.
- [`tools/local_multifile_game_orchestrator.py`](tools/local_multifile_game_orchestrator.py)
  — generator, staging controller, assembler, and headless-browser verifier.

Open [`meteor-courier/index.html`](meteor-courier/index.html) to play.

From the workspace root, reproduce the build with:

```powershell
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" .\02-meteor-courier\tools\local_multifile_game_orchestrator.py
```
