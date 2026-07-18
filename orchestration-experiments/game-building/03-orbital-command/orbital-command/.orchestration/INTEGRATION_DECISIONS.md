# Integration decisions

## Deterministic engine fallback

The original `engine_module` run and three targeted repair runs remain recorded under
`.orchestration/runs/`. Browser tests showed persistent schema mismatches: destructive
namespace assignment, object-versus-ID state confusion, nonexistent collections,
incorrect cost fields, and inverted production.

After the third engine repair, the integration boundary was changed. `src/engine.js` is
now a deterministic manifest interpreter maintained by the orchestrator. Mistral remains
responsible for the world, economy, technology, events, interface copy, state module, UI
module, visual system, and documentation. This fallback prevents unbounded repair loops
and records the model-capability boundary explicitly.

## Deterministic state and UI adapters

Later browser tests showed that the repaired state validator rejected valid runtime
states and the UI mixed binding models, mutated crew while rendering, used incorrect
data paths, and duplicated listeners. Their Mistral runs remain recorded, but the final
state and UI files are deterministic contract adapters. Mistral remains the author of
the campaign world, economy, technologies, events, interface copy, and visual system.
