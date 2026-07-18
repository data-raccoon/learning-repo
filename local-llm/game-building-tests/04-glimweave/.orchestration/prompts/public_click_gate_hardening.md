Harden only the UI_PROFILE journey in `game-building-tests/04-glimweave/smoke.js`:

1. Select opening controls exactly from `#purchaseList button` using aria-label prefixes
   `Buy Glimspinner` and `Buy Driftcatcher`. After the first click, re-query the latter with
   that exact selector. Do not search all page buttons by loose text.
2. If the final displayed Reservoir is not zero, include the numeric observed value in a
   stable failure code such as `RESERVOIR_AFTER_DRIFTCATCHER_<value>` and also check the
   announcer text for a rejected-action message.
3. Replace the additive pixel checksum with a position-sensitive 32-bit FNV-style hash
   using `Math.imul`, sampling every fourth pixel across the full backing image. Use the
   same helper for before/after.
4. Allow 500ms after the second click before hashing/finalizing, still well inside the
   five-second virtual-time budget.

Do not weaken geometry, action, owned-unit, or deterministic gates. Do not touch production
files. Use a targeted read, edit next turn, run the verifier, and return its exact output.
Do not commit.
