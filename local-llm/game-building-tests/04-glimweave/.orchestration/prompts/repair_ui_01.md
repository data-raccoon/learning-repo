You are repairing one integration fault in the Glimweave browser game's UI module.

Return ONLY the complete replacement contents of `src/ui.js` as plain JavaScript. No Markdown fences, no commentary, no omitted sections. Preserve all existing game and UI behavior except for the focused repair below.

Observed browser failure:

`STATE_VALIDATION_FAILED_OWNEDCLASSCOUNT_MUST_EQUAL_NUMBER_OF_UNIQUE_WEFTLING_TYPES_GOT_0_EXPECTED_1`

Cause established by inspection: `ui.js` replaces `window.__glimweaveTest` and several of its built-in scenario tests directly assign non-empty `state.weftlings` without synchronizing the derived `state.ownedClassCount`. The simulation validates state on every step/action. This makes the browser smoke suite fail before it can test the runtime.

Repair requirements:

1. Make every scenario exposed through `window.__glimweaveTest` construct states that satisfy the state contract before calling simulation actions, stepping, saving/loading, offline progress, retuning, or validation.
2. Do not weaken, bypass, catch, or remove state validation.
3. Prefer driving setup through the public simulation actions/helpers. When a scenario must directly seed a state, update every affected derived field consistently, including `ownedClassCount`, capacity, phase, unlocked classes, and related totals where the contracts require them.
4. Keep the existing test API method names because `smoke.js` calls them.
5. Preserve the corrected purchase action interface: `{ type: 'BUY_WEFTLING', weftlingType: <class>, x, y }`.
6. Preserve normal UI boot, rendering, accessibility, persistence, controls, modal behavior, and gameplay.
7. Do not invent alternate data fields or duplicate simulation rules in production UI code.
8. Ensure all built-in scenario tests return booleans and exercise the intended behavior rather than merely returning true.
9. Use ES5-compatible plain browser JavaScript consistent with the existing module. No dependencies.

The attached inputs contain the full current UI, simulation/state modules, data, and browser smoke harness. Reconcile them precisely.
