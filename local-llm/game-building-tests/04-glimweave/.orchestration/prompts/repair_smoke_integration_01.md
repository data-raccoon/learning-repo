Return ONLY the complete corrected `smoke.js` as plain ES5 JavaScript. Preserve all original and newly added checks, but correct the INTEGRATION phase's invented field assumptions:

- Chosen doctrine is stored at `intState1.upgrades.doctrine`, not `intState1.doctrine`; require `'Luminance'` there.
- Permanent upgrades are IDs in `intState2.permanentUpgrades`; require exactly one `'ReservoirBlueprint'` entry. They are not properties on `state.upgrades`.
- Retuning readiness uses `totalGlimCaptured = 1000` and `totalGlimCapturedThisRun = 1000`, not invented Iridescence total/spent fields. Keep reservoir <= maxCapacity and validate.
- `GW.Simulation.handleAction(state,{type:'RETUNE'})` returns `{success, iridescenceGained}` while mutating the supplied state. Require `intResult3.success === true` and positive numeric gain; do NOT require result identity with state.
- After Retuning, require phase 1, `permanentUpgrades` still contains exactly one ReservoirBlueprint, maxCapacity 200, and valid state.

Keep the expected doctrine rejection catch narrow, compact PASS/FAIL protocol, query guard, and every other test unchanged. No Markdown/commentary.
