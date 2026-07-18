Return ONLY the complete replacement contents of `smoke.js` as plain ES5-compatible browser JavaScript. Preserve every current check, compact PASS/FAIL protocol, delayed load execution, error phase reporting, UI assertions, and smoke-query guard.

Add a focused `INTEGRATION` phase after the initial state/data checks and before economy scenarios. It must perform real strict checks with distinct failure codes:

1. `GW.Integration.installed === true`.
2. `Object.keys(GW_DATA.doctrines).length === 3` so non-enumerable display aliases do not duplicate UI entries.
3. Create a fresh valid state and call PUBLIC `GW.Simulation.handleAction(state, {type:'CHOOSE_DOCTRINE', doctrineId:'LUMINANCE'})`; require the stored doctrine to equal the canonical display value `'Luminance'` and state validation to pass. Attempt a second choice with `'CAPTIVATION'` and require the expected rejection.
4. Create another fresh state, seed exactly 3 Iridescence, validate it, then call PUBLIC `GW.Simulation.handleAction(state, {type:'BUY_UPGRADE', upgradeId:'ReservoirBlueprint'})`. Require: the returned object is the identical state, Iridescence is 1, the upgrade is owned once, maxCapacity is 200, and validation passes.
5. On that same Blueprint state, seed a contract-valid Retuning-ready setup (`phase` and `highestPhaseUnlocked` 2; both cumulative totals at least 1000; reservoir no more than capacity), validate, then call PUBLIC `handleAction` with `{type:'RETUNE'}`. Require success, Blueprint survival, phase reset to 1, and immediate maxCapacity 200; validate again.

Do not weaken/catch unexpected errors. Catch only the expected second-doctrine rejection. Do not modify state/simulation/data/UI. Keep final output exactly `PASS` when every check passes, otherwise the existing `FAIL:<codes>` format. No Markdown/commentary.
