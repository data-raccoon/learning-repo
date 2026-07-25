# AI Learn Workspace

This workspace is organized by concern. Each top-level project should be opened and operated independently unless its README explicitly documents a dependency.

## Directory Map

```text
AI-Learn/
|-- small-context-harness/         Default compact model registry, routing, packets, and gates
|-- agent_orchestrator/            Legacy/advanced graphs, command workers, and durable evidence
|-- gaming-agents/                 Engine-neutral game MVP roles, job scaffolding, approvals, and QA gates
|-- local-models/                  Local model runtimes and model-specific assets
|   |-- ministral/                 Ministral download, server, and Vibe integration
|   |-- soofi/                     Deferred Soofi local-model family scaffold
|   `-- colibri/                   Deferred Colibri local-model family scaffold (POC)
|-- orchestration-experiments/     Agent-controller experiments and generated artifacts
|   |-- compliance-check/          EU AI compliance orchestration
|   `-- game-building/             Four game-building orchestration experiments
|-- company-os/                    Reusable company governance and specialist-agent system
|-- initiatives/                   Domain-specific research and venture ideas
|   |-- cologne-tax-improvements/  Cologne public-spending POC and evidence
|   `-- vector-earth/              Vector Earth product experiment
`-- connectors/                    Connector experiments
```

## Boundary Rules

- Put default model inventory, local-first routing, bounded context packets, and
  deterministic acceptance gates in `small-context-harness/`.
- Extend `agent_orchestrator/` only for advanced graphs, command-capable workers,
  or durable evidence not supported by the default harness.
- Put reusable game-production roles, game job scaffolding, approval contracts, and engine-neutral QA policy in `gaming-agents/`.
- Put model binaries, serving code, chat templates, and model checks in `local-models/`.
- Put controllers, prompts, run evidence, and generated test products in `orchestration-experiments/`.
- Keep reusable operating policy, agent definitions, skills, and governance in `company-os/`.
- Keep topic-specific hypotheses, sources, assessments, and reports in `initiatives/`.
- Keep Soofi and Colibri deferred until exact artifacts, runtimes, hardware limits, and evaluated capabilities are recorded.

Historical run records can contain old absolute paths. They are provenance and should not be rewritten merely because the workspace moved.
