Implement `src/state.js` for the supplied Orbital Command project contract. Return
JavaScript only, without Markdown fences or commentary. Use an IIFE, `window.OC ||= {}`,
and expose exactly these functions:

- `OC.createInitialState(data)`
- `OC.validateState(value, data)`
- `OC.saveState(state)`
- `OC.loadState(data)`
- `OC.clearSave()`

The initial state must contain: version 1, turn 1, a copied resources object from
`data.world.starting_resources`, crew assignments engineering/science/operations totaling
`data.world.crew_total`, empty `modules` and `completedTech` arrays, `activeResearch` null,
`researchProgress` 0, empty `log`, `pendingEvent` null, `zeroStreak` with energy and morale
zero, and status `playing`. Use localStorage key `orbital-command-save-v1`. Validation
must reject malformed saves and load must safely fall back to a new state. No network,
eval, imports, exports, HTML, or DOM access.
