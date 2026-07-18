Repair Glimweave's browser regression coverage and one obsolete deterministic assertion.
Work only in:

- `04-glimweave/index.html`
- `04-glimweave/smoke.js`
- the `TEST.testRetuning` function near the bottom of `src/ui.js`

Use targeted reads. Do not read unrelated production modules or design documents.

Required changes:

1. Remove the duplicate second `<script src="src/test-bridge.js">` include from HTML.
2. Update `TEST.testRetuning` to expect the deliberate post-Retuning 100-Glim Sky Loom
   priming charge instead of zero, while still requiring zero transient units/run capture
   and increased Iridescence.
3. Strengthen `smoke.js` so a fresh isolated browser profile proves production behavior
   through public DOM controls, not direct fixture funding:
   - the canvas rectangle is materially sized and visible;
   - desktop layout exposes a meaningful horizontal gap/playfield between left and right
     panel columns rather than merely finding DOM children;
   - initial displayed Reservoir is 100 and both opening purchase roles are reachable in
     sequence through enabled purchase buttons;
   - clicking the public Glimspinner control changes displayed Reservoir exactly once;
   - re-querying and clicking the public Driftcatcher control reaches two owned units and
     consumes the opening budget, using visible DOM evidence or existing read-only public
     test access only; never assign state or grant funds;
   - capture a small canvas pixel checksum before public actions and compare after the
     renderer has had time to draw the purchased units; fail if unchanged;
   - retain all useful deterministic phase/doctrine/persistence/victory checks.

The smoke runner may use nested short timeouts so render verification happens after public
clicks, but it must always write PASS/FAIL to `#smoke-result` within the verifier's five
second virtual-time budget. Use stable failure codes. Do not make tests pass by weakening
assertions or using direct state mutation for the clean-profile gates.

Inspect each changed region and run the repository verifier if possible. Return only a
concise Markdown report with public journey gates and exact test result. Do not commit.
