# Acceptance Contract

Replace this template with numbered, feature-specific criteria. Every criterion must state preconditions, action, observable result, authority side, verification method, and retained evidence. Mark irrelevant sections explicitly rather than leaving generic checklists.

## Pinned Runtime

- Minecraft Java Edition 26.2
- Fabric Loader 0.19.3
- Fabric API 0.154.2+26.2
- Fabric Loom 1.17-SNAPSHOT
- Gradle 9.5.1 through the checked-in wrapper
- Java 25

## Automated Release Gates

The trusted gate must pass all four fixed IDs:

1. `compile-common` → `compileJava`
2. `compile-client` → `compileClientJava`
3. `unit-tests` → `test`
4. `build` → `build`

Define additional feature tests by name inside the standard test task; do not add architect-authored executable commands.

## Player Journeys

For each MVP journey specify:

- Initial world/player state.
- Exact interaction or command.
- Server-authoritative state transition.
- Client-visible, text, audio, and visual feedback.
- Failure and recovery behavior.
- Single-player and multiplayer differences.
- Automated coverage and manual smoke-test steps.

## Client and Dedicated-Server Gates

Retain evidence for:

- Client start and world load without registry or resource errors.
- Primary journey completed once from a clean state.
- Dedicated server start without client-class loading.
- Player connection and authoritative feature execution.
- Malformed, unauthorized, stale, out-of-range, and rate-excessive payload handling where networking exists.

## Persistence Gates

When state persists, define and verify:

- New-save defaults and schema version.
- Save/reload identity for every persisted field.
- Missing and malformed data behavior.
- Migration from each supported prior schema.
- Failure behavior that avoids crashes, duplication, and silent destructive reset.

## Accessibility and Usability Gates

Define applicable controls, remapping, subtitles or visual audio equivalents, text alternatives, contrast, non-color cues, timing requirements, and multiplayer feedback. State how each property is inspected or measured.

## Performance and Network Budgets

Do not write “reasonable” or “minimal.” Define a test environment, workload, sampling method, baseline, threshold, and evidence path for every claimed CPU, memory, frame-time, packet-size, or packet-frequency budget.

## Assets and Packaging

- Every declared Creative file is listed once in the provenance manifest and passes the asset contract.
- Every resource and translation reference resolves at runtime.
- Placeholder resources are visibly and accurately disclosed.
- The built JAR contains `fabric.mod.json`, common classes, client classes, and declared resources at their expected paths.

## Evidence Retention

Retain trusted gate JSON, test reports, client/server smoke logs, screenshots or video only where needed, QA report, approval hashes, and the Git diff reviewed for the release candidate.
