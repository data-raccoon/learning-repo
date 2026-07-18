Fix one production defect in `04-glimweave/src/ui.js`, only inside
`updatePurchaseButtons` around lines 745-760.

The Buy button is already assigned a truthful `disabled` state, and
`Simulation.handleAction` is the authoritative validator. Its click closure redundantly
checks captured `reservoir`, `cost`, and `atMax` values; that stale closure silently drops
the enabled Driftcatcher click after buying Glimspinner, before `dispatchAction` runs.

Remove the closure-level `if (reservoir >= cost && !atMax)` guard. For an actual click,
always calculate placement from the current canvas rectangle and dispatch exactly one
`BUY_WEFTLING` action. Keep the button's disabled assignment and let the simulation reject
invalid/programmatic actions through the existing accessible error path. Do not alter cost,
state, tests, or other buttons.

Use a targeted read, edit next turn, inspect the region, then run
`py -3 04-glimweave/tools/verify_glimweave.py`. Return the exact result
and one root-cause sentence. Do not commit.
