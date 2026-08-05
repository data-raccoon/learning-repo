# MC-Mod Agent Operating Rules

## Mission

Develop a stable Fabric-based Minecraft Java Edition mod using AI agents with strict boundaries and automated verification.

## Roles and Decision Rights

- **Mod Architect** (strongest admitted architecture route): Product vision, scope, architecture, acceptance criteria, planning, review
- **Asset Producer** (weakest admitted coding route): Textures, models, UI/audio resources, style guide, provenance
- **Mod Engineer** (weakest admitted coding route expected to pass): Java implementation, Fabric integration, tests, error fixing
- **Mod QA** (independent admitted review route): Evidence-based, read-only audit

The root human controls routing, approval state, rollback, and release decisions.

## Workflow Invariants

- Use `model-execution-harness/core/` bounded tasks. Do not use the graph runtime or create a worker graph.
- Run Architect first. Advance explicitly through Assets, Engineering, trusted build gate, and QA; never materialize a downstream task before its inputs exist.
- Give every worker a compact task brief plus ordered path-only references to
  authoritative files inside the mc-mod target. Let the worker read those files
  on demand; never copy broad source excerpts into the initial packet or grant
  parent-directory reads.
- Keep Asset Producer and Mod Engineer ownership disjoint. Any write outside `write_roots` must fail.
- Use procedural or placeholder assets in v1. Do not download assets, introduce unclear licenses, or claim placeholders are final.
- Keep one source of truth for state, actions, identifiers, persistence, and acceptance expectations.
- Keep worker-facing source, contracts, and verifiers cohesive and reasonably
  small. Split by meaningful domain boundary rather than arbitrary token size.
- Route a failed QA finding to exactly one owner. QA must not repair its own finding.
- Release only after root human reviews successful structural, executable, interaction, persistence, and visual evidence.

## Engine-specific Acceptance

Every approved `mod-spec.json` must declare:
- The exact engine, Minecraft, Loader, Fabric API, Loom, Gradle, and Java versions
- Repository-relative common and optional client entrypoints plus the fixed start argv
- Non-overlapping Creative and Engineering artifact lists
- Individual Creative resource files below `src/main/resources/assets/` or `src/client/resources/assets/`
- Individual Engineering files below the schema-approved source, test, configuration, and Gradle roots
- Only the fixed root-controlled verifier IDs; workers never author executable verifier commands

Changing `docs/PRODUCT.md`, `docs/ARCHITECTURE.md`, `docs/ACCEPTANCE.md`, or
`mod-spec.json` after approval invalidates the SHA-256 manifest required before
broad Asset, Engineering, or QA materialization. Operational context, planning,
repair, and bounded pure-Java tasks do not require re-approval.

## Technical Constraints

**Pinned Versions (DO NOT change without explicit approval):**
- Minecraft: 26.2
- Loader: Fabric
- Fabric Loader: 0.19.3
- Fabric API: 0.154.2+26.2
- Fabric Loom: 1.17-SNAPSHOT
- Gradle: 9.5.1 through the checked-in wrapper
- Java: 25
- Gradle: controlled by ./gradlew

**Architecture Rules:**
- This is a **Fabric** project. Never use Forge, NeoForge, or Forge Legacy classes, annotations, event buses, registration patterns, or documentation.
- Keep common/server logic separate from client-only rendering and UI code.
- Registration code only performs registration.
- Game rules belong in domain/service classes.
- Rendering and screens belong in client-only packages (`client/`).
- Network packets must validate all client-supplied input.
- Persistent data must have explicit schema and migration strategy.
- Pure logic should not depend on Minecraft classes where avoidable.
- Never reference client-only classes from common/server initialization.

## Required Workflow

## Controller Startup

Before running work, read `AGENTS.md` and `orchestration.json`, then use the
repository controller:

```powershell
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" model-execution-harness\core\harness.py status initiatives\mc-mod-core --repo .
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" model-execution-harness\core\harness.py run initiatives\mc-mod-core --repo .
```

`orchestration.json` is the sole workflow state. The harness selects the single
eligible task, creates external evidence, performs validation and gating, and
persists `completed` or `blocked` state. Do not create `NEXT-STEP.json`, task
packets, manual worker IDs, or manual evidence directories. Only the root human
may use `approve --task <id>` to retry a blocked task after its definition is
corrected.

### Before Editing (for any agent)
1. Read this `AGENTS.md`.
2. Read `docs/PRODUCT.md` (if exists).
3. Read `docs/ARCHITECTURE.md` (if exists).
4. Inspect the relevant existing classes.
5. State a short implementation plan.
6. Identify client/server implications.

### After Editing
1. Run `./gradlew compileJava` (or specified compile task).
2. Run automated tests: `./gradlew test`.
3. Run formatting: `./gradlew spotlessCheck` (if configured).
4. Review the resulting diff.
5. Report any untested behavior.
6. Never declare success if compilation fails.

## Change Constraints

- Make the **smallest** change that satisfies the task.
- Do not add unrelated features.
- Do not upgrade dependencies without explicit human approval.
- Do not invent APIs.
- Check APIs against pinned dependency sources or official Fabric docs.
- Prefer documented Fabric API over mixins.
- Do not add a mixin without explaining in code comments why a public API is insufficient.
- Never execute destructive Git commands (reset --hard, clean -fd, etc.).
- Do not commit secrets or local configuration.

## Definition of Done

A task is complete **only when all** of the following are true:
- The project compiles with `./gradlew build`.
- All relevant automated tests pass.
- Formatting passes (`./gradlew spotlessCheck` if available).
- Dedicated-server compatibility has been verified (no client-class loading on server).
- User-visible behavior is documented.
- No unrelated files were changed.
- The Git diff has been reviewed.

## Client/Server Boundary Rules

**Server-Authoritative Principles:**
- Server owns all game state.
- Client is a dumb terminal that renders and sends input.
- All game logic that affects state must run on the server.
- Client may predict for smoothness but must reconcile with server authority.

**Never Do:**
- Import `net.minecraft.client.*` in common or server code.
- Trust the client to award items, change game state, or validate actions.
- Mutate server state only on the client.
- Send packets from server to client without client handling.
- Access world, player, or entity state before checking if it exists.

**Always Do:**
- Check the current 26.2 logical-side API (`Level.isClientSide()`) before client-only behavior.
- Use the current server-player type from the pinned unobfuscated sources for server-side player logic.
- Validate all client-supplied data in packet handlers.
- Annotate client-only classes with `@Environment(EnvType.CLIENT)`.
- Keep client code in `client/` package or subclasses thereof.

## Ownership Boundaries

| Role | Owned Paths | Read-Only | Notes |
|------|-------------|-----------|-------|
| Mod Architect | `docs/PRODUCT.md`, `docs/ARCHITECTURE.md`, `docs/ACCEPTANCE.md`, `mod-spec.json` | All | Planning only, no code |
| Asset Producer | Exact declared files under `src/*/resources/assets/`, `docs/style-guide.md`, `assets/asset-manifest.json` | All | No Java or Gradle code |
| Mod Engineer | Exact `engineer_artifacts`, `docs/IMPLEMENTATION.md` | Creative artifacts | Implementation only |
| Mod QA | None during review; root may materialize the report under `.mc-mod-agents/evidence/` | All | Read-only audit |

## Verification Gates

### Automated Gates (must pass)
```bash
./gradlew compileJava
./gradlew compileClientJava
./gradlew test
./gradlew build
```

### Smoke Tests
**Client Smoke Test:**
- Game starts without crash
- A world can be loaded
- Registries complete without errors
- New assets and translations resolve
- Primary feature works once

**Dedicated Server Smoke Test:**
- Server starts without client-class errors
- A player can connect
- Feature works with server authority
- Save/reload does not lose data
- Malformed packets do not crash the server

## Model Usage Guidelines

Use an admitted **architecture/reasoning** profile for:
- Product decomposition and architecture
- Diagnosing complicated failures
- Reviewing cross-cutting changes
- Designing networking and persistence
- Reviewing security and performance
- Planning refactors
- Comparing implementation strategies

Skip the architecture route when the controller already has an approved,
implementation-ready task. Medium must ground every claim in named current
APIs and must not claim features absent from its proposed surface.

Use the weakest admitted **coding** profile expected to succeed for:
- Implementing well-defined tasks
- Adding blocks, items, recipes, commands
- Writing unit tests
- Fixing compilation failures
- Mechanical refactoring
- Updating documentation
- Adding data-generation providers

Devstral must delegate to existing domain behavior instead of copying it unless
the task explicitly replaces that behavior and independently verifies parity.

### Controller Audit Before Dispatch

Model-authored planning artifacts require controller review. Before packing any
implementation task, the root controller must confirm:

- Every required API either exists or is explicitly created within the task's
  exact allowed files.
- `write_roots` name the exact production and test files; directory-wide roots
  require a concrete scaffolding justification.
- Public signatures, return semantics, invalid-input behavior, deterministic
  ordering, client/server ownership, and integration seams are explicit.
- Acceptance criteria can be checked without relying on worker-authored tests.
- Dependencies name only previously gated tasks, and the next task is not
  materialized until those gates pass.
- Controller review is proportional: read plans completely, inspect production
  diffs, spot-check worker tests, and open full trajectories only for narrow
  failure diagnosis.

For either Medium planning or Devstral implementation, use the global harness
`pack -> route -> accept -> snapshot -> execute -> gate` path. Store the full
trajectory outside the target and keep it out of controller context. Treat
`--max-tokens` as a cumulative multi-turn budget and inspect the baseline diff
after token or turn-limit exits. Missing final prose is not failure evidence,
and written files are not success evidence; only the exact-path audit plus
independent `gate --baseline` decides acceptance.

## Task Specification Format

Every implementation task must include:

```markdown
# Task: [Short description]

## Objective
[What should be achieved]

## Scope
- Allowed file changes
- Files that must NOT be changed

## Constraints
- Do not add unrelated features
- Do not change dependency versions
- Follow existing patterns in [reference file]

## Client/Server Considerations
- Sides affected: [client/server/both]
- Authority: [server is authoritative]
- Networking: [yes/no, if yes: packet direction and validation]

## Acceptance Criteria
- `./gradlew build` succeeds
- [Specific observable behavior]
- No client-only classes loaded by common initialization

## Files to Inspect
- [List of relevant existing files]

## Exact API Contract
- [Public signatures and return semantics]
- [Invalid-input and ordering behavior]

## Independent Verification
- [Root-authored verifier and black-box cases]
```

## Error Handling

When a build fails:
1. Identify the **earliest** meaningful error.
2. Inspect the implicated source file.
3. Check against pinned Fabric API documentation.
4. Make the **smallest** correction.
5. Do not suppress errors or weaken tests.
6. Do not upgrade dependencies without approval.
7. Re-run the failing task and confirm it passes.

## Fabric-Specific Notes

- Use Fabric API events, not mixins, when possible.
- Derive registry, item-group, data-component, and persistence APIs from the pinned 26.2 generated sources; do not copy Yarn-era examples.
- Keep resource identifiers, metadata dependencies, and registry namespaces equal to the approved mod ID.
- Use current custom-payload networking (`PayloadTypeRegistry`, `ServerPlayNetworking`, and `ClientPlayNetworking`) when networking is required.
- Use the approved current persistence mechanism with explicit schema versioning and migration tests.
- Client initialization: use `ClientModInitializer` entrypoint.
- Server initialization: use `ModInitializer` entrypoint.
