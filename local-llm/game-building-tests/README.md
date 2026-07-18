# Game-Building Orchestration Tests

This directory contains every game-building experiment, its generated game, the tools
used to build or verify it, and the shared lessons derived from the experiments.

## Experiments

| Test | Game | Scope | Associated tools |
|---|---|---|---|
| [`01-center-lock`](01-center-lock/) | Center Lock tic-tac-toe | First local-model file-generation and repair experiment | `01-center-lock/tools/` |
| [`02-meteor-courier`](02-meteor-courier/) | Meteor Courier | Manifest-driven multi-file canvas game | `02-meteor-courier/tools/` |
| [`03-orbital-command`](03-orbital-command/) | Orbital Command | Auditable multi-run strategy-game experiment | `03-orbital-command/tools/` |

## Shared documentation

- [`ORCHESTRATION_LEARNINGS.md`](ORCHESTRATION_LEARNINGS.md) records lessons across all
  three experiments.
- Each numbered experiment has a wrapper README explaining exactly which game and tools
  belong together.
- Orbital Command additionally retains job specifications, run records, rejected-run
  provenance, and integration decisions inside its game directory.

The numbered directories reflect experiment order, not a quality ranking.
