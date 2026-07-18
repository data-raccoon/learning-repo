Return ONLY the complete corrected `src/integration.js` as plain ES5 JavaScript. Preserve all working doctrine and permanent-purchase behavior.

Fix the RETUNE branch only: `GW.State.resetForRetuning`, called by the original handler, already folds every surviving ReservoirBlueprint into the new `state.baseCapacity` and sets `state.maxCapacity` accordingly. The wrapper currently adds `100 * blueprintCount` a second time, producing 300 instead of 200 for one Blueprint.

After a successful original Retuning result, do NOT add Blueprint capacity again. Set/ensure `state.maxCapacity = state.baseCapacity` (Retuning has cleared all run-specific Weftlings/global upgrades), bound reservoir, validate state, and return the original `{success, iridescenceGained}` result. Leave immediate capacity addition on the original permanent-purchase branch unchanged.

No other changes. No Markdown/commentary.
