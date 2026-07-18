# Test 01 — Center Lock

The first experiment tested whether a small local Mistral model could design and build a
self-contained browser game under an outer orchestration loop.

## Files that belong to this test

- [`kebab-case-tic-tac-toe/`](kebab-case-tic-tac-toe/) — playable game and original
  model-authored specification.
- [`tools/local_game_orchestrator.py`](tools/local_game_orchestrator.py) — final
  manifest-based generator and browser verifier for this game.

Open [`kebab-case-tic-tac-toe/index.html`](kebab-case-tic-tac-toe/index.html) to play.

From the workspace root, reproduce the build with:

```powershell
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" .\01-center-lock\tools\local_game_orchestrator.py
```
