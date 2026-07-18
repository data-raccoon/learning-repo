Make four exact regression corrections, with targeted reads only:

In `game-building-tests/04-glimweave/src/smoke-scenarios.js`:

1. In the overriding `test.testRetuning`, change the final expected Reservoir from 0 to
   the intended 100-Glim post-Retuning priming charge. Preserve the other assertions.
2. In the overriding `test.testOfflineProgress`, `applyOfflineProgress` returns an object;
   return `gained.glimGained > 0` instead of `gained > 0`.

In `game-building-tests/04-glimweave/smoke.js` UI_PROFILE block:

3. The re-queried Driftcatcher button has accessible label "Buy Driftcatcher...", not
   "Purchase". Match `driftcatcher` in combined text+aria-label without requiring the word
   `purchase`; explicitly add a stable failure if the re-query is missing/disabled before
   attempting click.
4. The checksum currently advances by roughly 144 pixels at 1440 width and can miss small
   units. In both before/after loops sample every fourth pixel (`i += 16`, `j += 16`) across
   the full image data so a newly drawn center unit materially changes the checksum.

Do not change production code or weaken any gate. Run
`py -3 game-building-tests/04-glimweave/tools/verify_glimweave.py`. Return exactly the
command and result plus one summary sentence. Do not commit.
