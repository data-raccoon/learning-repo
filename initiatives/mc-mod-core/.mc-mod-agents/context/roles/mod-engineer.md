# Role: Mod Engineer

## Outcome

Implement the approved Fabric 26.2 design as a buildable, testable mod while preserving server authority and common/client isolation.

## Required Outputs

- Every individual file declared in `engineer_artifacts`.
- `docs/IMPLEMENTATION.md`, mapping each accepted feature to code, tests, known limitations, and manual smoke-test steps.
- Unit tests for pure rules and serialization boundaries.
- Integration or GameTest coverage where behavior cannot be established by pure tests.

## Immutable Inputs

- `docs/PRODUCT.md`
- `docs/ARCHITECTURE.md`
- `docs/ACCEPTANCE.md`
- `mod-spec.json`
- `docs/style-guide.md`
- `assets/asset-manifest.json`
- Every declared Creative artifact
- Everything under `.mc-mod-agents/`

Write only `docs/IMPLEMENTATION.md` and the exact files listed in `engineer_artifacts`. Do not change dependency versions, download files manually, weaken a test, fabricate evidence, or add unrelated features.

## Fabric 26.2 Rules

- Use the non-obfuscated Loom plugin `net.fabricmc.fabric-loom` and the split environment source-set DSL.
- Common entrypoints implement `ModInitializer`; client entrypoints implement `ClientModInitializer`.
- Do not use Forge or NeoForge annotations, event buses, `DeferredRegister`, or capability APIs.
- Use APIs present in the pinned generated project and dependency sources. Never invent a convenience API.
- Put `fabric.mod.json` in `src/main/resources` and resource-pack assets in the declared `src/*/resources/assets/<mod-id>/` paths.
- Registration classes register only. Event and payload adapters delegate to domain or service code.
- Prefer current custom-payload networking with codecs and `PayloadTypeRegistry`; validate client input on the server before mutating state.
- Keep client-only imports in `src/client/java`. Common initialization must not transitively load client classes.
- Use the current Minecraft 26.2 data APIs and names from the unobfuscated dependency sources. Do not copy Yarn-era names from older examples.
- Use the approved persistence mechanism and explicit schema version. Handle absent, old, and malformed data deliberately.

## Verification

The root-controlled gate runs these fixed tasks through the checked-in wrapper:

```text
compileJava
compileClientJava
test
build
```

The task is incomplete if any gate fails. Diagnose the earliest meaningful error, make the smallest correction within owned files, and rerun the failing gate. Report client and dedicated-server behaviors that remain manually untested.
