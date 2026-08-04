# ProjectStart Agent Instructions

## Mission

Turn a human-owned project intent into a small, coherent, testable initial architecture that a modest-capability model can produce reliably and a trusted controller can validate mechanically.

## Authority

- The human owns product intent, consequential constraints, approval, and release decisions.
- The model may select only from admitted archetypes and the chosen stack pack.
- Deterministic code validates, renders, hashes, and advances lifecycle state.
- A proposal is not approval. A rendered architecture is not a deployed or production-ready system.

## Workflow

Advance in this order only:

1. Human completes `project-intent.json`.
2. Discovery model normalizes requirements and returns questions/conflicts.
3. Human resolves blockers and accepts a clean discovery result.
4. Architect model returns one typed `project-design.json`.
5. The manager validates and deterministically renders project documents.
6. A fresh reviewer audits the design without the architect trajectory.
7. Human approves the current hashes.
8. A trusted stack-specific generator may implement `bootstrap-plan.json` separately.

Use `model-execution-harness/core/`. Do not create worker graphs or give
architecture workers network, package-installation, credential, deployment, or
unrestricted write access.

## Small-model Rules

- Prefer selecting and adapting an admitted archetype over blank-slate invention.
- Supply one stack pack, one intent, one schema, and only relevant examples.
- Treat `unknown` as a question, never as permission to guess.
- Every assumption, deviation, risk, and reversible decision must be explicit.
- List individual artifacts; never use globs or directory placeholders.
- Use exact pinned components from the selected stack pack.
- Reject unnecessary services, queues, caches, frameworks, and abstractions.
- Keep the first vertical slice small enough to validate the architecture.

## Modification Boundaries

- Discovery owns only `discovery.json`.
- Architecture owns only `project-design.json`.
- The trusted renderer owns `AGENTS.md`, `docs/`, and `bootstrap-plan.json` in the target.
- Review is read-only; the root may materialize its validated report under `.projectstart/evidence/`.
- No model may edit `.projectstart/`, approval records, schemas, catalogs, stack packs, or trusted tools.

## Completion

Do not claim success unless schemas, cross-field validation, deterministic rendering, review, approval freshness, and relevant tests pass. Report all runtime, build, deployment, security, and usability behavior not actually exercised.
