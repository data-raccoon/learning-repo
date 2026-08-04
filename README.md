# AI Learn Workspace

This workspace is organized by concern. Each top-level project should be opened and operated independently unless its README explicitly documents a dependency.

## Directory Map

```text
AI-Learn/
|-- agent-packs/                   Portable definitions, skills, workflows, and pack contracts
|-- connectors/                    External-system connector integrations and access policy
|-- initiatives/                   Domain-specific research, evidence, and venture experiments
|-- local-models/                  Local model runtimes, integrations, and model-specific assets
|-- model-execution-harness/       Bounded model execution, graphs, evidence, and gates
|-- orchestration-experiments/     Agent-controller experiments and generated artifacts
`-- research/                      Cross-cutting technical research and architecture documents
```

`agent-packs/` is model- and IDE-agnostic. A pack stores inert definitions and
reusable procedures. `model-execution-harness/` creates a running worker by
combining a selected model, one pack entry point, a task, tools, and limits.

Root dot folders are thin discovery adapters only. Canonical agent-pack content
lives in `agent-packs/`, connector metadata in `connectors/registry.json`, and
model execution policy in `model-execution-harness/`. Runtime state belongs
outside the repository.

## Boundary Rules

- Put reusable model-neutral definitions, skills, workflows, templates, and
  pack manifests in `agent-packs/`.
- Put bounded model execution, registered model profiles, durable trajectories,
  advanced graphs, rollback, quarantine, and independent gates in
  `model-execution-harness/`.
- Keep reusable operating policy, agent definitions, skills, governance, and
  venture templates in `agent-packs/company-os/`.
- Put reusable project discovery and architecture workflows in
  `agent-packs/project-start/`.
- Put reusable editorial definitions in `agent-packs/editorial/`.
- Put reusable game-production roles, job scaffolding, approval contracts, and
  engine-neutral QA policy in `agent-packs/gaming-studio/`.
- Put external-system integrations and their least-privilege access policy in `connectors/`.
- Keep topic-specific hypotheses, sources, assessments, and reports in `initiatives/`.
- Put local model runtimes, integrations, model assets, and model checks in `local-models/`.
- Put controllers, prompts, run evidence, and generated test products in `orchestration-experiments/`.
- Put cross-cutting technical research and architecture documents in `research/`.

Historical run records can contain old absolute paths. They are provenance and should not be rewritten merely because the workspace moved.
