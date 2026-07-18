Return ONLY the complete corrected contents of `src/smoke-scenarios.js` as plain ES5-compatible JavaScript. No Markdown, commentary, or omitted sections. Preserve its smoke-only isolation and the existing global test API.

The first generated version fails immediately with:

`Cannot buy Weftling: not unlocked, insufficient Glim, or max owned reached`

Repair and audit the entire small scenario layer, using the attached authoritative state, simulation, data, and smoke files.

Required corrections:

1. Replace the broken `fundState` loop. Test setup is allowed to seed funding directly, but must atomically keep the contract valid: ensure `maxCapacity >= target`, set `reservoir` to the requested legal target, and make both cumulative capture fields consistent (at minimum no less than reservoir and never decreasing). Validate afterward.
2. Ensure any funding that crosses phase thresholds is followed by a legal simulation step before buying phase-locked classes, and maintain `highestPhaseUnlocked` only through the simulation unless direct late-game setup is fully contract-valid.
3. Audit every scenario, not just the first exception.
4. Overflow: purchase/setup first, then refill to current capacity, then step and assert the reservoir does not exceed capacity and overflow behavior remains bounded. Do not expect a just-purchased state to still be full.
5. Save/load: compare loaded state with the actual state at save time, after purchase costs, rather than an obsolete pre-purchase literal.
6. Upgrades in production are unique and cannot be bought repeatedly. Use valid, available unique upgrade IDs and meet their unlock/cost requirements. Never invent placeholder IDs.
7. Victory: create all five valid Weftling types only after their actual unlock conditions are met; use 12 valid unique owned global-upgrade IDs (purchased legally when practical, or seeded consistently for this late-game contract test), set phase/highest phase and all cumulative/derived fields consistently, validate, then invoke the real victory check through stepping. The scenario must prove `state.victory === true`.
8. Fade: create motes through production stepping, ensure the pre-fade count is positive, then establish that motes expire/fade under real stepping.
9. Phase progression and Retuning must have enough cumulative capture to meet their real thresholds and return strict booleans.
10. Offline and persistence scenarios must begin from valid states and test real state functions.
11. Do not weaken/catch validation, modify production modules, or return unconditional success.

Keep the result concise and focused on scenario setup.
