# Gaming Agents

Vendor-neutral role packets and job scaffolding for small-to-medium playable game MVPs. This is an engine-neutral production workflow, not a game engine and not a collection of Codex-specific custom agents.

## Minimal team

| Role | Owns | Access |
| --- | --- | --- |
| Game Director | Player promise, core loop, MVP scope, game specification, acceptance journeys | Scoped write to three approved design artifacts |
| Creative Producer | Art direction, UI language, procedural or placeholder art/audio, provenance | Scoped write to `assets/` and the style guide |
| Gameplay Engineer | Architecture, runtime, integration, persistence, developer tests | Scoped write to declared implementation paths |
| QA and Playtest | Independent findings and release evidence | Read-only; external verifiers execute separately |

The root AI controls routing, approval state, rollback, and release. It is deliberately not counted as another specialist role.

## Workflow

Initialize an existing or new repository subdirectory:

```powershell
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" gaming-agents\manage.py init --target initiatives\my-game --id my-game
```

Edit `.game-agents/intent.md`, then execute the generated Director graph through the repository orchestrator:

```powershell
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" agent-orchestrator\orchestrate.py run-graph initiatives\my-game\.game-agents\jobs\01-game-director.graph.json
```

Review `docs/game-brief.md`, `docs/acceptance-contract.md`, and `docs/game-spec.json`. A human then records the approval and materializes the remaining jobs:

```powershell
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" gaming-agents\manage.py approve --target initiatives\my-game
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" gaming-agents\manage.py materialize-build --target initiatives\my-game
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" gaming-agents\manage.py validate --target initiatives\my-game
```

Run the generated build graph only after approval:

```powershell
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" agent-orchestrator\orchestrate.py run-graph initiatives\my-game\.game-agents\jobs\02-build-and-qa.graph.json
```

The graph is deliberately serial: Creative establishes the asset contract, Engineering integrates it, and QA independently evaluates the resulting product. A passed graph is release evidence, not an automatic release decision.

## Game specification contract

`docs/game-spec.json` is the machine-readable engine boundary. Version 1 requires:

- the game ID and exact engine/version;
- one repository-relative entrypoint and a non-empty start argv;
- non-overlapping Creative and Engineering artifact lists;
- Creative artifacts below `assets/`;
- nested Engineering artifacts below `src/`, `tests/`, or `config/`;
- at least one independent verifier using an orchestrator-allowlisted executable.

Changing the brief, acceptance contract, or game specification after approval invalidates its SHA-256 manifest. The build graph cannot be materialized or validated until a human approves the new hashes.

## Safety and acceptance

- All worker context is copied into the game target under `.game-agents/`.
- Write jobs declare `allowed_write_paths`. Out-of-ownership changes are quarantined and rolled back by the orchestrator.
- QA is a read-only model job. Verifier commands are executed independently by the root runner.
- V1 uses procedural or clearly marked placeholder media and forbids unapproved downloads or unclear licenses.
- Engine-specific visual, interaction, accessibility, persistence, and performance gates must be declared in each game's acceptance contract.

## Tests

```powershell
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" -m unittest discover -s gaming-agents\tests -v
```

The suite covers path traversal, protected roots, slug validation, missing contracts, stale approvals, graph cycles, ownership, read-only QA, a full fake-adapter lifecycle, and the offline game canary.

