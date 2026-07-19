# Glimweave: Living Loom architecture

## Runtime and ownership

The checked-in runtime is a dependency-free classic-script application launched directly from `index.html`. Script order is deliberate: boot error capture, canonical configuration, utilities, state, simulation, integration, test seam, renderer, UI, smoke scenarios, smoke runner, then one `GW.init()` call. Nothing fetches files or uses modules, packages, a server, or the stale assembler.

- `config/game-data.js` is the single runtime catalogue for phases, directives, five Weftling classes, prices, unlocks, eighteen global upgrades, doctrine and permanent upgrades, abilities, renderer modes, field dimensions, and victory constants. Immutable legacy `data/` is not loaded.
- `src/state.js` owns creation, deep validation, deterministic version-3 save envelopes, atomic parsing/import, local persistence, offline accounting, and the shared Retune/New Run reset constructor.
- `src/simulation.js` owns all formulas and eligibility. UI never calculates prices, unlocks, ability readiness, Retune reward, phase requirements, or victory. Placement is a canonical transaction: begin creates a no-cost preview; confirmation validates bounds/obstruction/eligibility, then charges and creates exactly once.
- `src/integration.js` owns the one fixed-step loop, action dispatch, autosave, hidden-tab pause/resume, state replacement, and lifecycle events.
- `src/render.js` owns DPR-aware Canvas sizing, CSS-to-field coordinate conversion, procedural field/glyph/range drawing, appearance modes, placement validity, and static textual feedback.
- `src/ui.js` owns native DOM controls, tabs, contextual coaching, accessible dialogs/focus restoration, live announcements, pointer/keyboard routing, settings/import/export, and optional muted-by-default Web Audio cues.
- `src/test-bridge.js` exposes deterministic state/action seams. It is not used by player interactions.

## State and invariants

The version-3 state separates transient run data from permanent profile data. Transient state includes Reservoir, motes, placements, Weftlings, phase, doctrine, global/doctrine upgrades, ability timers, pressure, counters, hold time, and victory. Permanent state includes Iridescence, permanent upgrades, highest phase, settings, tutorial milestones, recaps, and doctrine-partitioned bests. Version 3 adds enforced phase/run consistency, canonical live-Weftling limits, and doctrine ownership/prerequisite invariants. Version 2 is a named unsupported legacy format and is rejected without mutation; a Retuned profile may retain a high `highestPhase` while its valid current phase returns to one.

The simulation operates in 100 ms fixed steps. Renderer frame rate never changes economy results. Victory freezes gameplay. A hidden tab records no simulation delta and resumes the existing loop once. The Dawn hold increments only while the four other conditions are simultaneously true and Reservoir equals canonical capacity; any below-full update resets it immediately.

## Persistence and offline progress

Exports are actual JSON envelopes with `format: "glimweave-save"`, `version: 3`, `savedAt`, and validated state. Import parses into a copy and installs only after full validation. Empty, malformed, oversized, version-2/unknown-version, invalid-enum, impossible-resource, phase-inconsistent, over-unit-cap, prerequisite-invalid, and invalid-entity inputs are rejected. No legacy version is silently migrated; legacy policy is explicit rejection. A corrupt stored save starts a clean recoverable state rather than breaking boot while preserving the rejected stored text.

Offline credit uses the retained envelope timestamp, milliseconds throughout, a one-hour cap, one 50% multiplier, canonical production, and available capacity. It never spawns motes and produces a one-time report.

## Test seams

`window.__glimweaveTest` supports creation, clone, fixed stepping, public action dispatch, mote spawning for isolated boundaries, canonical metrics/directives, victory/Retune queries, serialization/parse/validation, and offline credit. `tests/deterministic-tests.js` exercises placement, capture, tutorial events, all declared upgrade families, abilities/cooldowns, Harmonizer unlock, phase and 60-second boundaries, reset permanence, persistence rejection, and offline caps. `tests/trajectory-scenarios.js` declares the three required doctrine trajectories without claiming unperformed timed evidence.

## Launch and verification

Open `index.html` directly. Engineering-local static checks may inspect classic script order and forbidden remote paths. The independent owner must run the contract command from this target:

```powershell
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" tools\verify_glimweave.py --json
```
