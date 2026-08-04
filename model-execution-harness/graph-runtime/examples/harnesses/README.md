# Synthetic harness manifests

These manifests demonstrate the three bounded topology contracts. They are structural examples, not experiments or benchmarks. `harness validate` and `harness run --dry-run` do not invoke a model; actual execution uses the explicitly pinned admitted profiles and is intentionally not part of this example set.

```powershell
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" .\orchestrate.py harness validate .\examples\harnesses\pipeline\harness.json
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" .\orchestrate.py harness run .\examples\harnesses\fanout-fanin\harness.json --dry-run
```

The jobs share one synthetic target so handoff paths resolve to the same canonical files. Parallel write nodes own disjoint paths. The current target lock serializes workers sharing a target even when the logical harness permits parallel execution.
