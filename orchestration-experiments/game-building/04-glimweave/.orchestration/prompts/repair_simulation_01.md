Repair the supplied complete `src/simulation.js` and return the full replacement
JavaScript only, with no Markdown or commentary. Preserve all existing implemented game
systems and public APIs except for the exact integration fixes below.

Observed browser failures:
1. `BUY_WEFTLING` confuses the action discriminator with the purchased unit type.
2. `GW.Simulation.getFadeRate` is missing but the generated UI requires it.

Required fixes:
- `action.type` must remain the discriminator string `BUY_WEFTLING`.
- the purchased class ID must be read exclusively from `action.weftlingType`.
- validation, affordability, cost lookup, created `weftling.type`, and every test helper
  must consistently use `weftlingType`.
- `testBuyWeftling` must dispatch exactly
  `{type:'BUY_WEFTLING', weftlingType:type, x:x, y:y}` with no duplicate keys.
- implement and export deterministic `getFadeRate(state)`, using existing mote ages,
  fade-time rules, upgrades, phase modifiers, and reduced-motion-independent simulation
  data. It returns a finite nonnegative Glim-per-second estimate and never mutates state.
- keep `GW.Simulation` and `window.__glimweaveTest` APIs intact, updating test helpers as
  needed so production/capture, fade, overflow, unit purchase, phase, Retuning, offline,
  save/load, and victory tests are executable.
- do not weaken `GW.State.validate`, bypass invariants, hard-code tests to true, or remove
  any system to make tests pass.

No TODOs, placeholders, prose, or code fences.
