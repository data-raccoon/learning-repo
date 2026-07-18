# Glimweave Full QA Audit Report

- **Audit Date:** 2026-07-18
- **Auditor:** Independent Release QA (Mistral Vibe)
- **Build:** `cc4b65b` (initial non-working state)
**Evidence Basis:** `FIRST_RUN_EVIDENCE.md`, `first-run-1440x900.png`, production source (index.html, bootstrap.js, data/game-data.json, src/{state,simulation,render,ui,integration}.js, styles.css, smoke.js, smoke-scenarios.js)

---

## Executive Summary

**Release Verdict: FAIL**

The known blocker is **reproduced and verified as P0**. Four additional independent P0 blockers exist that prevent any meaningful gameplay. The old smoke suite falsely passed by bypassing production boot, funding states directly, and checking DOM existence rather than visibility or public reachability. A human player with an empty browser profile **cannot perform any action** and sees **no play field**.

---

## Findings

### P0 Blockers (Release-Blocking)

| ID | Severity | Title |
|---|---|---|
| F001 | P0 | Action handler never wired: all UI controls are inert |
| F002 | P0 | Economic soft-lock: fresh state has zero Glim and no producer |
| F003 | P0 | Canvas occluded by UI: no distinct play field is visible |
| F004 | P0 | Canvas backing dimensions use browser defaults, diverging from CSS display size |

#### F001: Action handler never wired: all UI controls are inert

- **Evidence Class:** SOURCE-CONFIRMED
- **Evidence:**
  - `src/ui.js:107–110`: `dispatchAction` only invokes `actionHandler` if registered.
  - `src/ui.js:1305–1307`: `UI.onAction` function exists to register the handler.
  - **Repository-wide search confirms: no call to `UI.onAction(...)` exists anywhere.**
  - `index.html`: Boot sequence calls `window.GW.init()` but `GW.init` (`src/ui.js:1170–1181`) does not invoke `UI.onAction`.
- **Reproduction:**
  1. Empty storage, open `index.html` in fresh browser profile
  2. Click any button (e.g., "Buy" on Glimspinner)
  3. Observe: No state change, no errors, no feedback
- **Affected Files:** `src/ui.js` (line 1305–1307 unused), `index.html`, `bootstrap.js`
- **User Impact:** Game is completely non-interactive. No public control path can mutate state.
- **Failure Class:** `integration`
- **Repair Direction:** Wire `UI.onAction(Simulation.handleAction.bind(null, state))` during initialization before any UI interaction is possible. The action handler must be registered before the UI is built or shown.
- **Regression Acceptance Test:**
  ```javascript
  // Production boot + public interface test
  // 1. Load index.html with empty storage
  // 2. Click the first enabled Weftling purchase button
  // 3. Assert: state.reservoir decreases AND state.weftlings.length increases
  // 4. Assert: canvas renders at least one Weftling in subsequent frames
  // PASS only if all assertions hold without direct fixture funding
  ```

---

#### F002: Economic soft-lock: fresh state has zero Glim and no producer

- **Evidence Class:** SOURCE-CONFIRMED
- **Evidence:**
  - `src/state.js:462`: Initial `reservoir: 0`
  - `src/state.js:466`: Initial `weftlings: []` (empty array)
  - `data/game-data.json:74`: Cheapest producer `Glimspinner.baseCost: 60`
  - `src/simulation.js:applyProduction` (via `src/simulation.js:550–555`): Production requires at least one `Glimspinner` Weftling; none exist initially.
  - No passive income source or starting grant is present in data or state.
- **Reproduction:**
  1. Empty storage, open `index.html`
  2. Observe: Reservoir shows `0 / 100`
  3. Observe: All purchase buttons (Glimspinner: 60 Glim, Driftcatcher: 75 Glim, all upgrades) are disabled
  4. Observe: No action can produce Glim
- **Affected Files:** `src/state.js:create`, `data/game-data.json`
- **User Impact:** Player is permanently soft-locked at start. Cannot buy first producer to begin economy.
- **Failure Class:** `bootstrap`, `state`, `data`
- **Repair Direction:** Provide a starting producer, a starting Glim grant, or a free initial action. Must be balanced and clearly documented. The simplest repair is adding one free Glimspinner at creation, or starting reservoir at 60.
- **Regression Acceptance Test:**
  ```javascript
  // Production boot test
  // 1. Load index.html with empty storage
  // 2. Wait for UI to render
  // 3. Assert: At least one purchase button is enabled
  // 4. Assert: Either reservoir > 0 OR weftlings.length > 0
  // PASS only if player can take first meaningful action without external funding
  ```

---
---
#### F003: Canvas occluded by UI: no distinct play field is visible

- **Evidence Class:** OBSERVED + SOURCE-CONFIRMED
- **Evidence:**
  - `first-run-1440x900.png`: Screenshot shows viewport almost entirely filled by control dashboard; **no canvas content is visible**.
  - `styles.css:150–157`: `#gameCanvas { position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 1; }`
  - `styles.css:235–243`: `#uiRoot { position: relative; z-index: 10; ... width: 100%; }`
  - `styles.css:349–353`: `.main-panels { grid-template-columns: 280px 1fr; }` — but `#uiRoot` is not constrained to reserve space for canvas.
  - `#uiRoot` at z-index 10 **overlays** the canvas at z-index 1.
  - No region is reserved for the play field; UI panels span the full width.
- **Reproduction:**
  1. Empty storage, open `index.html` at 1440×900
  2. Observe: Entire viewport shows UI controls; **no Sky Loom field is visible**
  3. Observe: Scrolling reveals more UI panels, still no game area
- **Affected Files:** `styles.css`, `index.html`
- **User Impact:** Player cannot see the core game visualization (motes, Weftlings, Sky Loom). The primary interactive surface is hidden.
- **Failure Class:** `css`, `ui`
- **Repair Direction:**
  - Reserve a central canvas region by restructuring the layout: place `#gameShell` as a flex container with `#gameCanvas` and `#uiRoot` as siblings, or create a split-view grid.
  - Ensure canvas has higher or equal z-index within its reserved region.
  - Ensure canvas backing store matches displayed dimensions.
- **Regression Acceptance Test:**
  ```javascript
  // Visual/geometry test using production boot
  // 1. Load index.html with empty storage
  // 2. Measure #gameCanvas getBoundingClientRect()
  // 3. Assert: canvas rect has width > 200 AND height > 200
  // 4. Assert: canvas is not occluded (computed z-index >= parent stacking context)
  // 5. Assert: At least 30% of viewport area is dedicated to canvas
  // 6. After first purchase: Assert canvas renders new Weftling (pixel checksum change)
  // PASS only if canvas is visible and receives rendered content
  ```

---
#### F004: Canvas backing dimensions use browser defaults, diverging from CSS display size

- **Evidence Class:** SOURCE-CONFIRMED
- **Evidence:**
  - `index.html`: `<canvas id="gameCanvas" aria-label="...">` — **no `width` or `height` attributes**
  - `src/render.js:30–35`: `resize` reads `canvas.width` and `canvas.height` attributes (browser defaults: 300×150)
  - `src/render.js:40–44`: Sets `canvas.style.width/height` for display but backing store remains 300×150 unless HTML attributes are set
  - CSS makes canvas fill the viewport, but backing store is tiny, causing **scaled, pixelated rendering**
- **Reproduction:**
  1. Open `index.html` at 1440×900
  2. Inspect `#gameCanvas` element
  3. Observe: HTML attributes `width="300" height="150"` (browser defaults)
  4. Observe: CSS `width: 100%`, `height: 100%` stretches the 300×150 bitmap
- **Affected Files:** `index.html` (missing attributes), `src/render.js:30–35`
- **User Impact:** All rendering is blurred/scaled incorrectly. Motes and Weftlings appear pixelated. Hit testing and visual fidelity are broken.
- **Failure Class:** `renderer`, `integration`
- **Repair Direction:**
  - Add explicit `width` and `height` attributes to `<canvas>` in HTML matching intended display dimensions, OR
  - In `Renderer.init`, set both HTML attributes and CSS size to match the display dimensions (accounting for DPR)
- **Regression Acceptance Test:**
  ```javascript
  // Backing store test
  // 1. Load index.html
  // 2. After render init: Assert canvas.width >= 800 AND canvas.height >= 600
  // 3. Assert canvas.width === canvas.style.width * DPR (within 1px)
  // PASS only if backing store matches display size
  ```

---

---

### P1 Major

| ID | Severity | Title |
|---|---|---|
| F005 | P1 | Smoke tests bypass production boot and check existence, not visibility or reachability |
| F006 | P1 | Tutorial cannot progress because economy is locked |
| F007 | P1 | Button enabled/disabled state is misleading when actions are inert |

#### F005: Smoke tests bypass production boot and check existence, not visibility or reachability

- **Evidence Class:** SOURCE-CONFIRMED
- **Evidence:**
  - `smoke.js:73–74`: Only checks `#uiRoot.children.length > 0` and `#gameCanvas.width > 0`
  - `smoke-scenarios.js`: Defines `fundState(state, target)` which **directly sets `state.reservoir`**, bypassing economic constraints
  - `smoke-scenarios.js`: Uses test helpers (`test.buyWeftling`, `test.step`) that invoke `Simulation.handleAction` **directly on state**, not through UI
  - `smoke.js:73–74`: **Does not check**: canvas visibility, UI occlusion, enabled buttons, action handler wiring, pixel rendering, public click path
- **Reproduction:** Run `index.html?smoke` — observes "PASS" despite F001-F004 being present
- **Affected Files:** `smoke.js`, `src/smoke-scenarios.js`
- **User Impact:** False confidence in release readiness. Critical blockers undetected.
- **Failure Class:** `test-harness`
- **Repair Direction:**
  - Add acceptance tests that:
    1. Use production `index.html` with empty storage (no `?smoke`, no `?test`)
    2. Verify canvas visibility and non-occlusion
    3. Verify at least one enabled, clickable first action
    4. Verify public click causes state mutation
    5. Verify canvas pixel change after state mutation
  - Remove direct state funding from smoke scenarios; use only public UI path
- **Regression Acceptance Test:** See F001-F004 regression tests above (they serve as replacements)

---
#### F006: Tutorial cannot progress because economy is locked

- **Evidence Class:** INFERRED (from F002 + source)
- **Evidence:**
  - `src/ui.js:createTutorialOverlay`: Tutorial exists with 8 steps
  - Tutorial Step 1: "The Glimspinner produces Glim. Purchase one to begin."
  - `src/state.js:create`: Player starts with 0 Glim
  - `data/game-data.json:74`: Glimspinner costs 60 Glim
  - Result: Player **cannot complete** the first tutorial step
- **Reproduction:**
  1. Empty storage, open `index.html`
  2. Tutorial shows Step 1: "Purchase one to begin"
  3. Glimspinner button shows cost 60 Glim, but reservoir is 0
  4. Button is disabled
  5. Player cannot progress tutorial
- **Affected Files:** `src/ui.js:createTutorialOverlay`, `src/state.js:create`, `data/game-data.json`
- **User Impact:** Onboarding fails immediately. New players have no path to learn the game.
- **Failure Class:** `ui`, `bootstrap`
- **Repair Direction:** Fix economic bootstrap (F002) OR provide tutorial-specific starting grants. Tutorial must be skippable if player cannot progress, with clear explanation.
- **Regression Acceptance Test:**
  ```javascript
  // Tutorial test with production boot
  // 1. Load index.html with empty storage
  // 2. If tutorial shown: Assert first tutorial step action is possible (button enabled)
  // 3. OR assert tutorial can be skipped
  // PASS only if tutorial does not block on impossible action
  ```

---
#### F007: Button enabled/disabled state is misleading when actions are inert

- **Evidence Class:** SOURCE-CONFIRMED
- **Evidence:**
  - `src/ui.js:updatePurchaseButtons`: Buttons disabled when `reservoir < cost`
  - If a player somehow had Glim (e.g., through save import), buttons would be **enabled** but clicks would **still do nothing** (F001)
  - User sees enabled button, clicks, nothing happens — **no feedback**
- **Reproduction:**
  1. Import a save with reservoir >= 60
  2. Observe: Glimspinner "Buy" button is enabled
  3. Click button
  4. Observe: No error, no state change, no notification
- **Affected Files:** `src/ui.js:updatePurchaseButtons`, `src/ui.js:dispatchAction`
- **User Impact:** Misleading UI. User believes action is available but it silently fails. Frustration and confusion.
- **Failure Class:** `ui`, `integration`
- **Repair Direction:** Wire action handler (F001) first. Then, ensure all action paths either succeed or provide clear error feedback.
- **Regression Acceptance Test:**
  ```javascript
  // Feedback test
  // 1. Load index.html with imported save (reservoir >= 60)
  // 2. Click enabled purchase button
  // 3. Assert: Either (a) state changes, OR (b) notification/error appears
  // PASS only if user receives clear feedback
  ```

---

### P2 Moderate

| ID | Severity | Title |
|---|---|---|
| F008 | P2 | Performance risk: 100ms sim updates + full UI rebuilds + 500 mote cap |
| F009 | P2 | Render loop runs when canvas is hidden or occluded |
| F010 | P2 | Duplicate script include may cause errors |

#### F008: Performance risk: 100ms sim updates + full UI rebuilds + 500 mote cap

- **Evidence Class:** SOURCE-CONFIRMED
- **Evidence:**
  - `src/ui.js:1170–1181`: `startSimLoop` runs `setInterval` every `GW.TICK_MS` (100ms) = **10 FPS simulation**
  - Each tick: `Simulation.step` + `updateUI` which **rebuilds entire purchase/upgrade DOM lists**
  - `data/game-data.json:13`: `maxMotes: 500`
  - `src/render.js:render` iterates all motes and weftlings each frame (animation frame rate, ~60 FPS)
  - With 500 motes: Each render does 500+ iterations; each sim tick rebuilds DOM
- **Reproduction:** Profile CPU with 500 motes on low-end device
- **Affected Files:** `src/ui.js:startSimLoop`, `src/ui.js:updateUI`, `src/render.js:render`
- **User Impact:** Potential jank on low-end devices, especially mobile. Battery drain.
- **Failure Class:** `performance`
- **Repair Direction:**
  - Throttle UI rebuilds (e.g., only when state changes that affect visibility)
  - Use requestAnimationFrame for simulation if possible
  - Implement object pooling for DOM elements instead of full rebuilds
  - Consider reducing mote cap or implementing LOD
- **Regression Acceptance Test:**
  ```javascript
  // Performance budget test
  // 1. Load index.html
  // 2. Fund state to 5000 Glim, buy 50 Glimspinners
  // 3. Run for 10 seconds
  // 4. Assert: No frame > 33ms (30 FPS target) on reference device
  // PASS only if performance budget met
  ```

---
#### F009: Render loop runs when canvas is hidden or occluded

- **Evidence Class:** SOURCE-CONFIRMED
- **Evidence:**
  - `src/ui.js:startRenderLoop`: Uses `requestAnimationFrame` unconditionally
  - No check for `canvas` visibility, display:none, or occlusion
  - `src/ui.js:setupVisibility`: Handles page visibility but not canvas-specific visibility
- **Reproduction:**
  1. Open game
  2. Minimize browser tab
  3. Observe: render loop continues (CPU usage remains high)
- **Affected Files:** `src/ui.js:startRenderLoop`
- **User Impact:** Wasted CPU cycles when game not visible. Battery drain on mobile.
- **Failure Class:** `renderer`
- **Repair Direction:** Pause render loop when canvas is not visible or page is hidden. Use `IntersectionObserver` for canvas visibility.
- **Regression Acceptance Test:**
  ```javascript
  // Render pause test
  // 1. Load index.html
  // 2. Hide #gameCanvas (display: none)
  // 3. Assert: Render loop stops (no canvas draw calls)
  // 4. Show #gameCanvas
  // 5. Assert: Render loop resumes
  // PASS only if render respects visibility
  ```

---
#### F010: Duplicate script include may cause errors

- **Evidence Class:** SOURCE-CONFIRMED
- **Evidence:**
  - `index.html`: `<script src="src/test-bridge.js"></script>` appears **twice** (lines 21 and 23)
  - While not always harmful, duplicate script loading can cause: re-execution of IIFE, symbol conflicts, or errors if script assumes single load
- **Affected Files:** `index.html`
- **User Impact:** Potential runtime errors or unexpected behavior. Hard to debug.
- **Failure Class:** `integration`
- **Repair Direction:** Remove duplicate script tag.
- **Regression Acceptance Test:**
  ```javascript
  // Script load test
  // 1. Load index.html
  // 2. Assert: No duplicate script elements in DOM
  // 3. Assert: No console errors from script re-execution
  // PASS only if clean load
  ```

---

## Release Verdict

**FAIL**

- **Reason:** Five P0 blockers (F001-F004 confirmed, plus the known report) prevent any meaningful gameplay from a clean profile.
- **Blocker Count:** 4 independent P0 findings
- **Smoke Test Status:** Existing smoke suite **falsely passes** despite P0 blockers
- **Recommendation:** Do not release. Fix all P0 blockers before any release candidate.

---

## First 15 Minutes Journey Table

| Step | Description | Current Status | Evidence | Notes |
|---|---|---|---|---|
| First Load | Game loads without errors, UI visible | FAIL | OBSERVED: No play field visible; only controls | F003 |
| First Actionable Step | At least one enabled, clickable action | FAIL | OBSERVED: All buttons disabled (0 Glim) | F002 |
| First Producer | Purchase first Glimspinner | FAIL | UNTESTED (cannot reach due to F002) | Blocked by F002 |
| First Visible Mote | See drifting Glim mote | FAIL | UNTESTED (cannot reach due to F002) | Blocked by F002, F001 |
| First Capture | Driftcatcher captures a mote | FAIL | UNTESTED | Blocked by F001, F002 |
| First Purchase | Buy first upgrade | FAIL | UNTESTED | Blocked by F002 |
| First Phase Progress | Advance to Phase 2 | FAIL | UNTESTED | Blocked by F001, F002 |

**Summary:** Journey **completely blocked at first load**. No step beyond "load" is reachable.

---

## Full Path Checklist

| Category | Requirement | Status | Evidence | Notes |
|---|---|---|---|---|
| **Phase Progression** | Advance through all 4 phases | UNTESTED | Blocked by F001-F002 | Requires economy |
| **Doctrine** | Choose doctrine, purchase doctrine upgrades | UNTESTED | Blocked by F001-F002 | Requires Glim |
| **Retuning** | Perform Retuning with Iridescence gain | UNTESTED | Blocked by F001-F002 | Requires phase 2+ |
| **Persistence** | Save/load round-trip | UNTESTED | Source suggests capable | Needs production path test |
| **Reset** | Reset game data | FAIL | SOURCE-CONFIRMED | Settings panel present but game inert | F001 |
| **Victory** | Achieve victory conditions | UNTESTED | Blocked by F001-F002 | Requires full progression |
| **Desktop (1440×900)** | Usable layout | FAIL | OBSERVED | No play field visible | F003 |
| **Mobile/Narrow** | Usable at 360 CSS px | UNTESTED | Needs testing | Likely worse than desktop |
| **Keyboard** | Full keyboard navigation | UNTESTED | Source has handlers | Blocked by F001 |
| **Reduced Motion** | Respects reduced motion | UNTESTED | Source has setting | Blocked by F001 |

---

## Repair Ordering (By Dependency)

| Priority | Finding IDs | Description | Dependencies |
|---|---|---|---|
| 1 | F001, F002 | **Core Bootstrapping**: Wire actions + economic start | None (foundational) |
| 2 | F003, F004 | **Visual Foundation**: Canvas visibility + backing size | F001 (needs working game to test) |
| 3 | F005 | **Test Infrastructure**: Replace smoke suite | F001-F004 (tests must verify fixes) |
| 4 | F006, F007 | **UX Polish**: Tutorial + feedback | F001, F002 |
| 5 | F008-F010 | **Performance + Cosmetic**: Optimizations | All P0/P1 |

**Critical Path:** F001 must be fixed first, as it blocks all UI interaction. F002 must be fixed concurrently or immediately after, as it blocks economic progression. Without both, no gameplay is possible.

---

## Replacement QA Gates

The following gates **must** be added to the release pipeline. They use production boot and public interfaces only.

### G1: Visible Play Field Gate
- **Check:** Canvas has non-zero display area and is not fully occluded
- **Test:**
  ```javascript
  const canvas = document.querySelector('#gameCanvas');
  const rect = canvas.getBoundingClientRect();
  assert(rect.width > 200 && rect.height > 200, 'Canvas too small');
  const uiRect = document.querySelector('#uiRoot').getBoundingClientRect();
  // Check canvas is not fully behind UI (z-index or positioning)
  const canvasZ = parseInt(getComputedStyle(canvas).zIndex);
  const uiZ = parseInt(getComputedStyle(document.querySelector('#uiRoot')).zIndex);
  assert(canvasZ >= 1, 'Canvas z-index too low');
  ```

### G2: Reachable First Action Gate
- **Check:** At least one purchase or action button is enabled and clickable
- **Test:**
  ```javascript
  // After production boot with empty storage
  const enabledButtons = document.querySelectorAll('button:not([disabled]):not(.disabled)');
  assert(enabledButtons.length > 0, 'No enabled actions');
  ```

### G3: Public Action State Mutation Gate
- **Check:** Clicking an enabled button mutates state
- **Test:**
  ```javascript
  const initialReservoir = parseInt(document.querySelector('#reservoirValue').textContent);
  const initialWeftlings = state.weftlings.length;
  const btn = document.querySelector('button:not([disabled]):not(.disabled)');
  btn.click();
  // Wait for sim tick
  setTimeout(() => {
    const newReservoir = parseInt(document.querySelector('#reservoirValue').textContent);
    const newWeftlings = state.weftlings.length;
    assert(newReservoir !== initialReservoir || newWeftlings !== initialWeftlings, 'Action had no effect');
  }, 200);
  ```

### G4: Canvas Pixel Change Gate
- **Check:** State mutation causes canvas rendering
- **Test:**
  ```javascript
  const canvas = document.querySelector('#gameCanvas');
  const ctx = canvas.getContext('2d');
  const initialImage = ctx.getImageData(0, 0, canvas.width, canvas.height);
  // Trigger action that adds Weftling
  btn.click();
  setTimeout(() => {
    const newImage = ctx.getImageData(0, 0, canvas.width, canvas.height);
    assert(!areImageDatasEqual(initialImage, newImage), 'Canvas did not update');
  }, 200);
  ```

### G5: Clean-Profile Journey Gate
- **Check:** Full journey without direct fixture funding
- **Test:**
  ```javascript
  // 1. Load index.html?test=clean (empty storage, no smoke flag)
  // 2. Wait for first enabled action
  // 3. Click to purchase first producer
  // 4. Wait for first mote to appear
  // 5. Assert: reservoir > 0 after capture
  // PASS only if all steps complete
  ```

---
## Evidence Gaps

These require human verification or browser automation harness with pixel inspection:

| ID | Gap | Type | Required Tool |
|---|---|---|---|
| EG001 | Canvas actual pixel content at first load | Visual | Browser automation + PNG capture |
| EG002 | Canvas pixel difference after action | Visual | Browser automation + PNG diff |
| EG003 | Mobile layout at 360 CSS px | Layout | Device emulation |
| EG004 | Keyboard navigation focus order | Accessibility | Manual/browser automation |
| EG005 | Screen reader announcements | Accessibility | Screen reader testing |
| EG006 | Performance on low-end mobile | Performance | Device testing |
| EG007 | Reduced motion compliance | Visual | Manual inspection |

**Note:** EG001 and EG002 are critical. The existing `first-run-1440x900.png` confirms F003 (no play field visible), but pixel-level verification of rendering changes requires automation.

---
## Contradictions Found

| Area | Contradiction | Impact |
|---|---|---|
| **State vs UI** | State can have valid data but UI actions are inert (F001) | Player cannot affect state |
| **Data vs Bootstrap** | Game data defines costs but bootstrap provides no starting resources (F002) | Soft-lock |
| **CSS vs Renderer** | CSS sizes canvas to viewport but renderer uses HTML attributes (F004) | Blurred rendering |
| **Smoke Tests vs Reality** | Smoke passes but game is unplayable (F005) | False release confidence |
| **UI Design vs Implementation** | Purchase buttons exist but cannot be used | Misleading UX |

---
## Conclusion

Glimweave **cannot be released** in its current state. The combination of unwired UI actions (F001), economic soft-lock (F002), invisible canvas (F003), and incorrect canvas sizing (F004) creates a product that displays only greyed-out buttons with no game area — **exactly matching the user's report**.

All P0 findings are **source-confirmed** and **independent** — fixing one does not resolve the others. The smoke test suite **must not be trusted** as it bypasses production boot paths.

**Minimum Viable Fix:** Wire the action handler (F001) and provide a starting economic bootstrap (F002), then fix canvas visibility (F003) and sizing (F004). Only after these can the remaining polish items be addressed.

**Do not release until all P0 findings are closed with production-path verification.**
