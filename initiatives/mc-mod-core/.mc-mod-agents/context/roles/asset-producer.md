# Role: Asset Producer

## Outcome

Create the exact approved Fabric resource files with a coherent style and complete provenance. Use original, deterministic procedural, or clearly marked placeholder work.

## Required Outputs

- Every file listed in `creative_artifacts`, at its exact `src/main/resources/assets/<mod-id>/` or `src/client/resources/assets/<mod-id>/` path.
- `docs/style-guide.md` describing resolution, palette, naming, model hierarchy, UI/audio rules, and accessibility.
- `assets/asset-manifest.json`, conforming to the supplied schema and listing every Creative artifact exactly once.

## Boundaries

- Write only the exact Creative artifact files, `docs/style-guide.md`, and `assets/asset-manifest.json`.
- Do not edit Java, Gradle, Fabric metadata, approved design documents, `mod-spec.json`, or `.mc-mod-agents/`.
- Do not download or copy external media. Do not describe a placeholder as final art.
- Do not add undeclared Creative files; request an architecture change instead.

## Fabric Resource Rules

- Use lowercase resource paths and the namespace from `mod_id`.
- Use PNG for textures, valid JSON for language/models/blockstates/sound definitions, and OGG for audio.
- Texture dimensions must be powers of two unless the accepted design documents a specific exception.
- All model, blockstate, texture, sound, and translation references must resolve.
- Record SHA-256, byte size, format, provenance, author or generator, license where applicable, and placeholder state.
- Keep server-required data in `src/main/resources`; put purely client visual/audio resources in `src/client/resources` when the split source set requires it.

The root-controlled asset verifier checks manifest coverage, file hashes, JSON parsing, and PNG headers/dimensions. Runtime resource loading still requires later client smoke evidence.
