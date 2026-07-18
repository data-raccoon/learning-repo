# AI Learn Workspace

This workspace is organized by concern. Each top-level project should be opened and operated independently unless its README explicitly documents a dependency.

## Directory Map

```text
AI-Learn/
|-- local-models/                  Local model runtimes and model-specific assets
|   `-- ministral/                 Ministral download, server, and Vibe integration
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

- Put model binaries, serving code, chat templates, and model checks in `local-models/`.
- Put controllers, prompts, run evidence, and generated test products in `orchestration-experiments/`.
- Keep reusable operating policy, agent definitions, skills, and governance in `company-os/`.
- Keep topic-specific hypotheses, sources, assessments, and reports in `initiatives/`.
- Add Soofi as a sibling of `local-models/ministral/` when its runtime work begins.

Historical run records can contain old absolute paths. They are provenance and should not be rewritten merely because the workspace moved.
