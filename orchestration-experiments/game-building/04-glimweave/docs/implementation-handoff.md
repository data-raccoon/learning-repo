# Gameplay Engineering handoff

## Outcome delivered

Implemented the approved Living Loom upgrade as a coherent offline runtime. The Canvas is now the dominant playfield; manual capture and automatic retrieval are distinct; all five classes use spatial placement previews and canonical spend-once confirmation; contextual coaching follows verified actions; directives expose exact progress; doctrines unlock visible active abilities; and the finite Dawn, Retune, New Run, save, import/export, offline, responsive, accessibility, renderer, and audio surfaces are integrated.

The authoritative runtime data was migrated to `config/game-data.js`. Immutable legacy `data/` remains present but is no longer loaded.

## Files owned and changed

- Root runtime: `index.html`, `styles.css`, `bootstrap.js`, `smoke.js`
- Canonical configuration: `config/game-data.js`
- Runtime modules: `src/state.js`, `src/simulation.js`, `src/integration.js`, `src/test-bridge.js`, `src/render.js`, `src/ui.js`, `src/smoke-scenarios.js`
- Test definitions: `tests/deterministic-tests.js`, `tests/trajectory-scenarios.js`
- Engineering docs: `docs/architecture.md`, `docs/implementation-handoff.md`

On Windows, `docs/architecture.md` resolves to the pre-existing `docs/ARCHITECTURE.md` case-insensitively. The Director explicitly authorized replacing that one legacy file as the required Engineering architecture artifact; no other uppercase legacy document was edited.

## Commands and gates run

- Searched runtime-owned files for external URLs, fetch, dynamic import, module loading, and stale `data/game-data.js` references: none found.
- Attempted `node --check` for all runtime and test scripts; Node.js is not installed in this environment, so this did not provide evidence.
- Independent verifier intentionally not invoked by Engineering; it remains an independent QA gate.

Exact independent command:

```powershell
Set-Location "C:\Users\stevr\OneDrive\1 - Project\2026 AI-Learn\orchestration-experiments\game-building\04-glimweave"
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" tools\verify_glimweave.py --json
```

## Evidence paths

- Browser smoke status: DOM output `#smoke-result` (`PASS` on successful runtime checks)
- Deterministic suite: `window.GW.DeterministicTests.run()` after loading `tests/deterministic-tests.js` in an isolated verification page
- Trajectory definitions: `window.GW.TrajectoryScenarios.definitions`
- Boot errors: `window.__glimweaveBootErrors`

## Known limitations

- The required 25–40 minute balance claim, doctrine completion variance, 30-second 500-mote performance samples, visual screenshots, listening check, touch-device run, and assistive-technology run require independent physical QA and are not claimed by Engineering.
- Procedural audio uses conservative generated oscillator cues and no samples. Browsers may block sound until the explicit unmute gesture; gameplay never depends on audio.
- The canonical envelope is now version 3 because validation adds phase/run consistency, live-unit cap, doctrine ownership, and prerequisite invariants. Version 3 round-trips are supported. Version 2 is explicitly named unsupported legacy and is safely rejected without replacing current state or stored save.
- Deterministic QA now verifies actual Overflow Prevention deposit/loss outcomes, actual Sustained Flow mote survival, and activation/effect/expiry/rejection/readiness for all four public abilities. Keyboard capture uses an explicit highlighted mote cursor and the same canonical manual-capture action as pointer input.

## Recommended next owner

Independent Gameplay QA: run the verifier unchanged, then perform the contracted desktop/mobile, keyboard/pointer/touch, appearance, timed doctrine, performance, and audio evidence passes. Quarantine or return exact failures to Engineering; do not weaken gates.
