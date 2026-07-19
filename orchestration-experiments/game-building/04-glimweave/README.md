# Glimweave

**A strategic incremental game of luminous possibility around a living Sky Loom.**

Glimweave unfolds across four phases at the living aurora machine called the Sky Loom. Tiny engineers known as Weftlings coax **Glim**—luminous possibility—from the Loom, then guide it to the Reservoir before it drifts away and fades. Stored Glim funds new units, Loom structures, and mutually exclusive Refraction doctrines. Balance production against retrieval, navigate doctrine choices that lock competing paths, and progress through the Loom’s phases toward the finite “Weave the Dawn” victory. After victory, Retuning resets your transient progress while preserving permanent Iridescence, letting you refine your strategy across iterations.

---

## Play the Game

Open [`index.html`](index.html) directly in any modern browser. It is the multi-file entry point and loads all runtime modules. No installation, build step, or external dependencies are required.

---

## Gameplay Loop

**Core mechanics.** Glim appears at the Loom, drifts independently across the field, and fades if uncaptured. Weftlings produce, transport, and support to guide Glim into the Reservoir, whose capacity limits how much can be stored. Production and capture are separate optimization problems: better producers create more Glim, but without effective capture units, it vanishes.

**Controls & features.**
- Real-time simulation with adjustable speed and pause
- Compact number formatting and reduced-motion support
- Keyboard-accessible controls and ARIA live regions for screen readers
- Save/load with capped offline progress
- Responsive UI usable at 360 CSS pixels

**Progression.** Advance through four distinct Loom phases, each introducing new mechanics. Choose among three Refraction doctrines that permanently lock competing branches, materially altering your build. Purchase 18 upgrades across doctrine trees, deploy five Weftling classes with distinct roles, and expand Reservoir capacity to bank more Glim. Retuning resets transient factory state while preserving Iridescence, enabling prestige-style refinement.

---

## Project Map

### Playable Runtime
| File | Purpose |
|------|---------|
| [`index.html`](index.html) | Multi-file browser entry point; loads all modules |
| [`bootstrap.js`](bootstrap.js) | Production module loader for the multi-file runtime |
| [`config/game-data.js`](config/game-data.js) | Canonical Living Loom data, visual tokens, audio recipes, and progression definitions |
| [`src/state.js`](src/state.js) | Core state management, save/load, offline progress |
| [`src/simulation.js`](src/simulation.js) | Deterministic simulation: production, drift, fade, capture, overflow |
| [`src/render.js`](src/render.js) | Procedural vector/canvas rendering of Glim, Weftlings, and Loom |
| [`src/ui.js`](src/ui.js) | UI panels, controls, doctrine selection, and accessibility |
| [`src/integration.js`](src/integration.js) | Integration layer: ID normalization, upgrade side effects, Retuning invariants |
| [`src/test-bridge.js`](src/test-bridge.js) | Test seam module for headless verification |
| [`src/smoke-scenarios.js`](src/smoke-scenarios.js) | Smoke-only test scenarios |
| [`smoke.js`](smoke.js) | Smoke-only harness |
| [`styles.css`](styles.css) | Styling and responsive layout |
| [`tests/deterministic-tests.js`](tests/deterministic-tests.js) | Gameplay-boundary, persistence, progression, ability, and invariant checks |

### Design & Contracts
| File | Purpose |
|------|---------|
| [`EXPERIMENT_BRIEF.md`](EXPERIMENT_BRIEF.md) | Original IP description, ambition, acceptance tests, and ownership |
| [`docs/GAME_DESIGN.md`](docs/GAME_DESIGN.md) | Game systems, units, doctrines, progression, and economy |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | Module boundaries, data flow, and technical constraints |
| [`docs/QA_REVIEW.md`](docs/QA_REVIEW.md) | Defect log, repairs, orchestration rationale, limitations |
| [`docs/VERIFICATION.md`](docs/VERIFICATION.md) | Deterministic assembly and browser suite evidence |
| [`docs/ORCHESTRATION_LEARNINGS.md`](docs/ORCHESTRATION_LEARNINGS.md) | Orchestration process learnings and decisions |

### Orchestration Evidence
| File | Purpose |
|------|---------|
| [`.orchestration/prompts/`](.orchestration/prompts/) | All generation and repair prompts for each artifact |
| [`.orchestration/jobs/`](.orchestration/jobs/) | Executable job specifications |
| [`.orchestration/runs/`](.orchestration/runs/) | Accepted run evidence with model, input/output hashes, timestamps, duration, and usage when exposed |
| [`.orchestration/NORMALIZATIONS.md`](.orchestration/NORMALIZATIONS.md) | Mechanical transport normalizations |

### Deterministic Tools
| File | Purpose |
|------|---------|
| [`tools/run_cloud_vibe_job.py`](tools/run_cloud_vibe_job.py) | Runs a single Cloud job and records evidence |
| [`tools/extract_contract_packets.py`](tools/extract_contract_packets.py) | Extracts contract packets for orchestration |
| [`tools/assemble_runtime.py`](tools/assemble_runtime.py) | **Legacy only; do not run against Living Loom** |
| [`tools/verify_glimweave.py`](tools/verify_glimweave.py) | Headless Edge test suite and deterministic checks |

---
## Verification

**Status.** The automated release gate passes against the checked-in Living Loom runtime. It verifies boot, public smoke interactions, spatial placement and capture, declared upgrade and ability effects, phase progression, exact victory timing, Retuning invariants, version-3 persistence, invalid-state rejection, and offline progress.

**Output:**
```json
{"status":"pass","result":"PASS"}
```

**Reproduce it yourself:**
```powershell
python 04-glimweave/tools/verify_glimweave.py --json
```

Do not run `tools/assemble_runtime.py`; it targets the superseded experiment layout and can overwrite current files.

**Limitations.** Automated checks do not prove the 25–40 minute balance target, doctrine parity, listening quality, assistive-technology behavior, or real-device touch comfort. Those remain explicit physical release gates rather than implied passes.

---
## Provenance

The original experiment and retained historical evidence were produced through the recorded Mistral Cloud workflow. The Living Loom elevation was planned, implemented, repaired, and independently audited through the repository's `gaming-agents` workflow using Codex sub-agents with disjoint Director, Creative, Engineering, and read-only QA ownership. Creative media remains original, procedural, dependency-free, and documented in `assets/asset-manifest.json`.

---
## Learn More

- [Experiment brief and original IP](EXPERIMENT_BRIEF.md)
- [Game design document](docs/GAME_DESIGN.md)
- [Technical architecture](docs/ARCHITECTURE.md)
- [QA review, defects, and repairs](docs/QA_REVIEW.md)
- [Verification commands and coverage](docs/VERIFICATION.md)
- [Orchestration learnings](docs/ORCHESTRATION_LEARNINGS.md)
- [Outer orchestrator's cloud-model learnings](../CLOUD_MODEL_ORCHESTRATION_LEARNINGS.md)
