# Game-Building Orchestration Tests

This directory contains every game-building experiment, its generated game, the tools
used to build or verify it, and the shared lessons derived from the experiments.

## Experiments

| Test | Game | Scope | Associated tools |
|---|---|---|---|
| [`01-center-lock`](01-center-lock/) | Center Lock tic-tac-toe | First local-model file-generation and repair experiment | `01-center-lock/tools/` |
| [`02-meteor-courier`](02-meteor-courier/) | Meteor Courier | Manifest-driven multi-file canvas game | `02-meteor-courier/tools/` |
| [`03-orbital-command`](03-orbital-command/) | Orbital Command | Auditable multi-run strategy-game experiment | `03-orbital-command/tools/` |
| [`04-glimweave`](04-glimweave/) | Glimweave | Mistral Cloud strategic incremental experiment | `04-glimweave/tools/` |

## Shared documentation

- [`ORCHESTRATION_LEARNINGS.md`](ORCHESTRATION_LEARNINGS.md) indexes the universal,
  local-model, and cloud-model conclusions.
- [`LOCAL_MODEL_ORCHESTRATION_LEARNINGS.md`](LOCAL_MODEL_ORCHESTRATION_LEARNINGS.md)
  contains lessons specific to experiments 01–03 and the constrained local model.
- [`CLOUD_MODEL_ORCHESTRATION_LEARNINGS.md`](CLOUD_MODEL_ORCHESTRATION_LEARNINGS.md)
  contains the outer orchestrator's Mistral Cloud findings from Glimweave.
- [`04-glimweave/docs/ORCHESTRATION_LEARNINGS.md`](04-glimweave/docs/ORCHESTRATION_LEARNINGS.md)
  is the detailed Mistral-authored experiment postmortem.
- Each numbered experiment has a wrapper README explaining exactly which game and tools
  belong together.
- Orbital Command and Glimweave additionally retain job specifications, run records,
  provenance, and integration decisions inside their game directories.

The numbered directories reflect experiment order, not a quality ranking.
