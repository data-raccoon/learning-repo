# Model execution harness

This directory contains the repository's model- and IDE-independent execution
boundary. It runs bounded model workers; it does not store reusable agent packs.

- `core/` is the default compact path for one explicitly selected model,
  bounded reads and writes, durable trajectories, and independent gates.
- `graph-runtime/` is the advanced engine for job graphs, managed runtimes,
  transactional materialization, rollback, and quarantine evidence.

Use `core/` unless a task specifically requires an advanced engine feature.
Agent definitions, skills, and workflows live under `../agent-packs/`. Model and
provider admission remains execution configuration inside the harness, never
part of an agent-pack manifest.
