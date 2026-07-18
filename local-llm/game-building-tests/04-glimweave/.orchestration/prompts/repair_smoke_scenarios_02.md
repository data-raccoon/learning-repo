Return ONLY the complete final corrected contents of `src/smoke-scenarios.js` as concise plain ES5 JavaScript. No fences or commentary.

The current small scenario layer fails because a real purchase recomputes `maxCapacity` from owned capacity sources. Any manually raised capacity is therefore discarded, and a reservoir above the derived capacity fails validation.

Apply these exact architectural constraints across all eleven smoke scenarios:

1. The funding helper must NEVER manually raise `maxCapacity`. It may refill `reservoir` only to a target `<= state.maxCapacity`, while raising `totalGlimCaptured` and `totalGlimCapturedThisRun` consistently. Validate it and throw on an over-cap target so bad test setup is visible.
2. Refill between legal purchases. Example for producer + capturer: refill to 100, buy Glimspinner (60); refill to 100 again, buy Driftcatcher (75). Do not fund 200 at base capacity.
3. `WeftlingEfficiency` costs exactly 100 and can test an upgrade purchase from a legally full base reservoir.
4. Phase progression: seed cumulative captured totals to 500 while reservoir remains at most 100, then use a real step to trigger phase 2. No capacity fabrication.
5. Retuning: seed cumulative/run totals to at least 1000 while reservoir remains at most 100, use a real step to reach phase 2, then call `test.retune`. That helper returns the numeric Iridescence gained, not a boolean. Assert gain > 0 and the reset state.
6. Overflow: buy a producer legally, refill only to the then-current derived capacity, step, and assert it stays bounded.
7. Save/load compares actual saved values.
8. Victory should be a direct, fully contract-valid late-game state fixture, because it tests the victory predicate rather than the whole campaign:
   - Set phase and highestPhaseUnlocked to 4.
   - Set total capture and run totals to at least 10000.
   - Seed exactly one valid Weftling object of each of the five types with unique IDs and nonnegative coordinates; set ownedClassCount to 5.
   - Seed 12 valid UNIQUE global upgrade IDs from `GW_DATA`; no placeholders and no purchase actions that recompute capacity.
   - Keep maxCapacity/baseCapacity legal and reservoir exactly maxCapacity.
   - Validate, then call `test.step(state, 60000)` so the reservoir is full for the real 60 continuous seconds, validate again, and require strict `state.victory === true`.
9. Fade must first prove a positive mote count before testing expiration.
10. All scenario functions return strict booleans; no unconditional success, validation weakening, or production changes.

Audit every call for the base-capacity rule before returning the file.
