Implement `src/utils.js` for Glimweave using the supplied module contract and runtime
data. Return complete classic JavaScript only, without Markdown or commentary.

Requirements:
- use an IIFE and non-destructively initialize `window.GW` and `GW.Utils`;
- implement every public utility signature in the contract, including deterministic
  seeded RNG, clamping/finite-number guards, compact number and duration formatting,
  deep clone, cost calculation, and data/state validation helpers assigned to Utils;
- match the actual IDs and shapes in `data/game-data.json`;
- never access the DOM, timers, storage, or network;
- avoid global variables outside `window.GW`, eval, dynamic code, TODOs, and placeholders;
- fail safely on invalid numeric input and keep deterministic functions deterministic.

The output must be directly executable as the first source module after game data.
