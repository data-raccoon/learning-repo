Correct only the verified regression-gate defects in these files:

- `src/ui.js`, only `TEST.testRetuning` and `TEST.testOfflineProgress` near lines 1517-1540;
- `smoke.js`, only the new UI_PROFILE block after line 75;
- `tools/verify_glimweave.py`, only the Edge argument list.

Observed failure codes and exact causes:

1. `RETUNING`: the helper sets captured totals but never sets phase 2, so production
   Retuning correctly rejects it. Set phase/highest phase to 2 before calling Retune.
2. `OFFLINE_PROGRESS`: `TEST.applyOfflineProgress` returns an object; assert its numeric
   `glimGained > 0`, not `object > 0`.
3. `PURCHASE_BUTTONS_EXIST`: button text "Purchase" is truthy, so the selector never
   considers aria-label. Match against a concatenation of textContent and aria-label.
4. The public action rebuilds purchase DOM. After Glimspinner click, re-query the
   Driftcatcher button before clicking it; do not retain a detached element.
5. Geometry is intended for 1440x900, but Edge has no explicit window size. Add
   `--window-size=1440,900` to the verifier.
6. A fixed 40x40 sample at (10,10) may miss units. Use a deterministic sparse checksum
   across the canvas's full backing width/height (bounded sampling work) before/after.
7. Ensure checks guard missing buttons before reading `.disabled` or calling `.click`, so
   failure codes remain informative rather than throwing.

Use targeted reads only, edit on following turns, and preserve the production-path rule:
the clean journey must click DOM controls and may not mutate/grant state. Run the verifier.
Return a short Markdown report with the final exact result. Do not commit.
