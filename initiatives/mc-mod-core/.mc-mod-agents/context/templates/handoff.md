# Implementation Handoff

## Build Identity

- Mod ID: [from mod-spec.json]
- Minecraft: 26.2
- Fabric Loader: 0.19.3
- Fabric API: 0.154.2+26.2
- Fabric Loom: 1.17-SNAPSHOT
- Gradle: 9.5.1
- Java: 25

## Acceptance Traceability

For every numbered acceptance criterion, list the implementing files, automated test IDs, manual scenario if required, status, and known limitation. Do not mark unexecuted behavior as passing.

## Architecture and Sides

Document common, client, domain, service, registry, networking, and persistence packages actually created. Identify the authoritative side of each state transition and every client-only entrypoint.

## Networking

For each custom payload record direction, codec, registration site, handler, server validation, rate behavior, and negative tests. State “none” when vanilla synchronization is sufficient.

## Persistence

Record storage mechanism, schema version, fields, defaults, migration paths, corruption behavior, and test coverage. State “none” when the MVP has no persistent custom state.

## Commands and Controls

List exact commands, permissions, arguments, failure messages, key mappings, and usage examples.

## Tests and Manual Evidence

List unit, integration, and GameTest identifiers with their purpose. List client and dedicated-server smoke scenarios still requiring root execution. The trusted gate result is recorded separately and must not be fabricated here.

## Known Limitations and Release Risks

List concrete limitations, affected scenarios, workarounds, and proposed owners. Include untested runtime behavior.
