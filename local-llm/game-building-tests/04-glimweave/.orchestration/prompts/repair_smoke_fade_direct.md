Return ONLY the complete `src/smoke-scenarios.js` as plain JavaScript. Preserve every passing scenario. In `testFadeImpact` only, remove ambiguity from the test helper's step-count abstraction:

- Legally produce at least one real finite-fade mote as now.
- Remove Weftlings and synchronize `ownedClassCount`.
- Keep exactly one real target mote, reset its age to 0, and validate.
- Call the PUBLIC production API directly once: `GW.Simulation.step(state, targetMote.fadeTime + 1)`. That argument is elapsed milliseconds.
- Return strict true only if `state.motes.length === 0` afterward.

Do not change other scenarios, production modules, or validation. Keep smoke guards and ES5 compatibility. No Markdown/commentary.
