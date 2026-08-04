# Model Execution Harness Instructions

- Treat `core/` as the default execution engine.
- Use `graph-runtime/` only for graphs, managed runtime lifecycle,
  transactional materialization, rollback, or durable quarantine management.
- Keep agent-pack content outside this directory.
- Keep model/provider bindings out of agent-pack manifests.
- Preserve bounded targets, exact write roots, durable trajectories, and
  independent verification across both engines.
- Run the tests for both engines after shared path or contract changes.
