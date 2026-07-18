Return ONLY the complete replacement contents of `src/simulation.js` as plain JavaScript. No Markdown, commentary, or omitted sections. Preserve all currently corrected APIs and behavior.

Critical production bug proven in a real browser diagnostic:

- `TICK_MS` is 100.
- One Glimspinner produces 1 Glim/second.
- `applyProduction` computes `productionAmount = rate * deltaMs / 1000`, then immediately uses `Math.floor(productionAmount)` on every tick.
- At normal ticks this is `Math.floor(0.1) === 0`, forever, so starter Glimspinners never create a mote and the actual game cannot progress.

Focused repair requirements:

1. Implement deterministic fractional production accumulation on the runtime state. Initialize a private numeric accumulator field in `init` when missing/invalid.
2. Each active production step adds the nonnegative finite fractional `productionAmount` to that accumulator; spawn `Math.floor(accumulator)` motes, then retain the fractional remainder.
3. Do not accumulate production while paused or when there are no Glimspinners.
4. Respect the existing mote cap, `canSpawnMote`, placement, value/upgrades, RNG, production multipliers, and all existing state validation.
5. If spawning stops because the field is capped, prevent an unbounded backlog/burst: retain only a safe fractional remainder rather than queued whole motes.
6. The accumulator is runtime-only and must not require persistence or state-contract changes. Ensure old/loaded states initialize safely.
7. Preserve `GW.Simulation.step` and the existing `window.__glimweaveTest` API exactly, including the prior corrected `BUY_WEFTLING` action using `action.weftlingType` and exported `getFadeRate`.
8. Do not alter costs, progression, doctrines, fade rules, UI, or smoke tests.

Audit syntax and return the entire module.
