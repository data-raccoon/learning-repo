Return ONLY the complete corrected `src/integration.js` as concise ES5 JavaScript. The current 3 KB draft is rejected because it invented wrong public signatures. Fix all of these exact contracts:

- The real signature is `GW.Simulation.handleAction(state, action)`, and delegation is `originalHandleAction(state, action)`.
- Doctrine actions are `{ type:'CHOOSE_DOCTRINE', doctrineId:<id> }`. Copy the action, preserve `doctrineId`, translate stable key to display/stored value, then delegate.
- Non-enumerable doctrine aliases must map each display value to ITSELF (e.g. `doctrines.Luminance === 'Luminance'`) so state validation and effect comparisons accept the stored display value. They must remain absent from `Object.keys`.
- State validation is `GW.State.validate(state)`. There is no `GW.Simulation.validateState`.
- Production handlers mutate the supplied `state` in place. Permanent purchase must validate, subtract Iridescence, push onto `state.permanentUpgrades`, update immediate capacity for ReservoirBlueprint, validate, and return the same state object. Do not clone.
- Preserve stackable/non-stackable rules and require a nonnegative finite integer cost plus sufficient finite nonnegative Iridescence.
- `RETUNE` delegates first. The original mutates `state` and returns `{success, iridescenceGained}`. After success, count surviving ReservoirBlueprint entries on `state`, ensure `state.maxCapacity` immediately includes `state.baseCapacity + 100 * count` (Retuning clears run-specific capacity sources), keep reservoir bounded, validate `state`, and return the ORIGINAL result object.
- For all other actions delegate with correct argument order and preserve return/exception behavior.
- Guard safely with `typeof window.GW`, not a bare undeclared `GW` reference. Remain idempotent and expose `GW.Integration.installed` only after successful installation.

Do not change data, simulation, UI, DOM, tests, or prices. No Markdown/commentary.
