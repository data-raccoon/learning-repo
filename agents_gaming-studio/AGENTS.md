# Gaming Agents Operating Rules

## Mission

Create small-to-medium playable game MVPs through bounded vendor-neutral jobs. A model response is never product acceptance; completion requires declared artifacts, immutable external gates, and retained evidence.

## Roles and decision rights

- The root orchestrator owns sequencing, model routing, budgets, approval state, rollback, and the release decision.
- `game-director` owns the player promise, core loop, MVP boundary, game specification, and acceptance journeys.
- `creative-producer` owns art direction, UI language, procedural or clearly marked placeholder art and audio, and asset provenance.
- `gameplay-engineer` owns architecture, runtime code, integration, persistence, developer tests, and the implementation handoff.
- `qa-playtest` is read-only. It owns independent findings and evidence, but never edits production or weakens a gate.

Do not split narrative, levels, balance, build engineering, or sound into additional roles until project scale or repeated failures justify a separate owner.

## Workflow invariants

- Run the Director phase first. Build jobs may not be materialized until a human approval manifest matches the current brief, acceptance contract, and machine-readable game specification.
- Give every worker the complete context inside the game target. Never grant parent-directory reads.
- Keep Creative and Engineering ownership disjoint. Any write outside `allowed_write_paths` must fail, quarantine the delta, and restore the target.
- Use procedural or placeholder assets in v1. Do not download assets, introduce unclear licenses, or claim placeholders are final production media.
- Keep one source of truth for state, actions, identifiers, persistence, and acceptance expectations.
- Route a failed QA finding to exactly one owner. QA must not repair its own finding.
- Release only after the root orchestrator reviews successful structural, executable, interaction, accessibility, persistence, and visual evidence applicable to the chosen engine.

## Engine-neutral acceptance

Every approved `docs/game-spec.json` must declare an engine, an entrypoint, a start command, exact expected Creative and Engineering artifacts, and at least one independent verifier. Engine-specific runtime and visual gates belong in the acceptance contract and verifier list.

