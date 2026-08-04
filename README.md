# AI Learn Workspace

This workspace is organized by concern. Each top-level project should be opened and operated independently unless its README explicitly documents a dependency.

## Directory Map

```text
AI-Learn/
|-- agent_orchestrator/            Legacy/advanced graphs, command workers, and durable evidence
|-- agent_projectstart/            Reusable small-model project discovery and architecture workflow
|-- agents_company-os/             Company governance, specialist agents, skills, and templates
|-- agents_editorial/              Reusable editorial role definitions
|-- agents_gaming-studio/          Engine-neutral game MVP roles, scaffolding, approvals, and QA
|-- connectors/                    External-system connector integrations and access policy
|-- initiatives/                   Domain-specific research, evidence, and venture experiments
|-- local-models/                  Local model runtimes, integrations, and model-specific assets
|-- orchestration-experiments/     Agent-controller experiments and generated artifacts
|-- research/                      Cross-cutting technical research and architecture documents
`-- small-context-harness/         Bounded Mistral planning/coding, durable artifacts, and gates
```

## Boundary Rules

- Put registered Mistral Vibe profiles, bounded planning and coding tasks,
  durable artifacts, and independent acceptance gates in `small-context-harness/`.
- Put reusable intent normalization, archetype selection, typed initial architecture,
  deterministic project-document rendering, and architecture approval in `agent_projectstart/`.
- Extend `agent_orchestrator/` only for advanced graphs, command-capable workers,
  or durable evidence not supported by the default harness.
- Keep reusable operating policy, agent definitions, skills, governance, and
  venture templates in `agents_company-os/`.
- Put reusable editorial roles in `agents_editorial/`.
- Put reusable game-production roles, job scaffolding, approval contracts, and
  engine-neutral QA policy in `agents_gaming-studio/`.
- Put external-system integrations and their least-privilege access policy in `connectors/`.
- Keep topic-specific hypotheses, sources, assessments, and reports in `initiatives/`.
- Put local model runtimes, integrations, model assets, and model checks in `local-models/`.
- Put controllers, prompts, run evidence, and generated test products in `orchestration-experiments/`.
- Put cross-cutting technical research and architecture documents in `research/`.

Historical run records can contain old absolute paths. They are provenance and should not be rewritten merely because the workspace moved.
