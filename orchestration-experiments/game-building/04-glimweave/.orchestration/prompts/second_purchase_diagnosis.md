Diagnose and repair a verified production interaction defect in Glimweave.

Clean-profile browser evidence:

- initial Reservoir 100;
- exact public `#purchaseList button[aria-label^="Buy Glimspinner"]` click succeeds and
  displays 55;
- the DOM is re-queried;
- exact public `#purchaseList button[aria-label^="Buy Driftcatcher"]` exists and is enabled;
- calling `.click()` leaves Reservoir at 55 instead of 0;
- canvas pixel hash also remains unchanged after the public journey.

Read only these targeted regions:

- `src/ui.js`: `updatePurchaseButtons`, the installed `actionHandler`, `updateUI`, and
  render-loop functions;
- `src/simulation.js`: `getWeftlingCost`, `canBuyWeftling`, and `BUY_WEFTLING` action;
- `src/integration.js`: handleAction wrapper;
- relevant current UI_PROFILE section in `smoke.js` for reproduction only.

Trace the actual second-click path. Fix production code if the second public purchase is
being rejected or detached; do not bypass it in the test, grant resources, call simulation
directly, or weaken gates. Also determine why purchased Weftlings do not change the canvas
hash after 500ms and fix renderer/UI-loop integration if it is a production fault. Preserve
one action per click, persistence, accessibility feedback, and all game semantics.

Run `py -3 04-glimweave/tools/verify_glimweave.py`. Return a concise
root-cause/fix report with exact result. Do not commit.
