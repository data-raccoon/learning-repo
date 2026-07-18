# QA Review: Glimweave Release Readiness

## Release Verdict
**Conditional Green** – Glimweave meets its core experimental objectives as an offline, single-file browser game. All acceptance tests pass in headless Edge, the simulation is deterministic, and the full surface (4 phases, 5 Weftling classes, 3 doctrines, 18 upgrades) is verified. It is ready for experimental release to early players willing to tolerate rough edges. It is not yet polished for a general audience.

## Verified Functional Surface
- Real-time simulation: production, drift, fade, capture, and overflow mechanics work as designed. Glim motes move independently on canvas; capacity and fade rates make retrieval strategically meaningful.
- Full content surface: 5 distinct Weftling classes, 3 mutually exclusive Refraction doctrines, 18 upgrades, 4 Loom phases, and the “Weave the Dawn” victory condition are all implemented and testable.
- Economy: production and capture rates are independently measurable; purchasing units and upgrades produces observable state changes; doctrine choice materially alters builds.
- Progression: Retuning resets transient factory state while preserving permanent Iridescence; phase unlocking gates new mechanics.
- Persistence: save/load round-trips valid campaigns; offline progress is capped and applied safely.
- Accessibility: UI renders at 360 CSS pixels, supports reduced motion, and exposes ARIA live regions. Keyboard controls are present.
- Presentation: original procedural vector/canvas graphics with no external assets.

## Defects Found and Repaired
| Defect | Impact | Fix |
|---|---|---|
| **Action discriminator mismatch** | Doctrine selection failed because action types used mismatched string constants between caller and simulation | Integrated a normalization layer that maps external doctrine IDs to internal keys before processing |
| **Missing fade-rate export** | Simulation constants referenced in tests were not exported, causing verification failures | Exposed fade rate constants in the public simulation API for test access |
| **UI test API contract drift** | Test harness expected specific state shapes and function signatures that diverged from implementation | Aligned test API with actual runtime contracts; added validation helpers |
| **Monolithic-repair token failures** | Large regenerated modules (40–50 KB) introduced cascading errors that were hard to isolate and re-test | Abandoned full-module regeneration in favor of targeted fixes via small bridge/integration modules |
| **Test seam extraction** | Deterministic tests could not be cleanly injected into the monolithic UI | Extracted a minimal test API (`createState`, `validateState`, `handleAction`) from state/simulation to enable headless verification |
| **Fractional production flooring** | Starter producer emitted fractional Glim that Math.floor reduced to zero, making the first unit effectively inert | Adjusted base production rate upward to ensure non-zero yield after flooring |
| **Doctrine key/display normalization** | Doctrine identifiers used in UI and data were inconsistent (e.g., "LUMINANCE" vs "Luminance") | Integration layer maps display labels to canonical internal keys; doctrine objects expose both |
| **Permanent-upgrade routing** | Permanent upgrades like ReservoirBlueprint were not routed through the simulation, causing capacity to be ignored | Integration layer intercepts BUY_UPGRADE actions for permanent items, applies effects, and persists them across Retuning |
| **Blueprint capacity double counting** | ReservoirBlueprint stacking logic added capacity twice: once in the upgrade effect and once in the base capacity calculation | Fixed the stacking arithmetic to apply only the intended +100 capacity per Blueprint |

## Orchestration Boundary Rationale
Small bridge/scenario/integration modules proved superior to repeatedly regenerating 40–50 KB modules for three reasons. First, **blast radius**: a single token error in a large file requires regenerating the entire artifact, risking new regressions elsewhere. Small modules localize changes. Second, **testability**: targeted fixes can be verified in isolation before integration, reducing the feedback loop from hours to minutes. Third, **determinism**: transport normalizations (removing prose wrappers, fence markers) are trivial for small artifacts and can be recorded explicitly; for large files, normalization becomes a fragile, manual process. The integration layer itself is ~60 lines and handles all cross-cutting concerns (ID normalization, permanent upgrade side effects, Retuning invariants).

## Limitations and Risks
- **No human balance pass**: Verification is automated and deterministic, not a full playthrough. No claim is made that the economy is fun, balanced, or winnable without exploits. The acceptance suite proves mechanics, not pacing.
- **UI monolith**: `ui.js` remains a large, tightly coupled module. Future work should split rendering, input handling, and panel management into separate files for easier maintenance.
- **Compatibility layer technical debt**: The integration module papered over mismatches between data keys, doctrine IDs, and action types. A cleaner design would unify these contracts at the data layer.
- **Doctrine chosen-label cosmetic risk**: Doctrine display names are shown to players, but internal keys differ. If UI code ever bypasses the integration layer, players may see raw keys or mismatched labels.
- **Automated browser coverage limits**: Headless Edge testing cannot verify visual fidelity, animation smoothness, or touch input. The smoke harness also cannot catch races or timing-dependent bugs in the real-time simulation loop.
- **Offline progress edge cases**: Capped offline progress is applied safely, but the cap formula and explanation text have not been user-tested for clarity.
- **Save/load format stability**: The serialized format is not versioned. Future changes to state shape could break existing saves.

## Reproduction
The exact verification commands from `VERIFICATION.md` are:
```text
python 04-glimweave\tools\assemble_runtime.py
python 04-glimweave\tools\verify_glimweave.py
```
These run deterministic assembly and the full headless Edge browser suite, producing:
```
PASS phases=4 weftlings=5 doctrines=3 upgrades=18
PASS browser_suite=core+integration
```

## Provenance
All product and runtime artifacts (`src/state.js`, `src/simulation.js`, `src/render.js`, `src/ui.js`, `styles.css`, and data files) were authored by Mistral Cloud using `mistral-medium-3.5`. Repairs to those artifacts were also performed by `mistral-medium-3.5` under orchestrated prompts. Deterministic assembly, the compact verifier, prompts/jobs/run records, acceptance decisions, and the integration layer belong to the outer orchestrator. Cloud credentials never entered the repository or prompts.
