# Glimweave — Renderer Implementation Contract

Extracted verbatim by heading from `docs/ARCHITECTURE.md`.

### 2.2 HTML Structure (`index.html`)
```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Glimweave</title>
  <link rel="stylesheet" href="styles.css">
</head>
<body>
  <canvas id="gameCanvas"></canvas>
  <div id="uiRoot"></div>
  <script src="data/game-data.js"></script>
  <script src="src/utils.js"></script>
  <script src="src/state.js"></script>
  <script src="src/simulation.js"></script>
  <script src="src/render.js"></script>
  <script src="src/ui.js"></script>
  <script>window.GW.init();</script>
</body>
</html>
```


## 3. Global Namespace and Initialization

### 3.1 `window.GW` Layout
```js
window.GW = {
  // Constants
  VERSION: "1.0",
  TICK_MS: 100,          // Simulation fixed step
  FPS: 60,               // Render FPS
  MAX_MOTES: 500,        // Hard cap on visible Glim motes

  // Modules
  State: { /* ... */ },
  Simulation: { /* ... */ },
  Renderer: { /* ... */ },
  UI: { /* ... */ },
  Utils: { /* ... */ },

  // Entry point
  init: function() { /* ... */ },

  // Data (injected by game-data.js)
  DATA: { /* ... */ }
};
```

### 3.2 Initialization Sequence
1. `GW.Utils.RNG.seed(hashOfUserAgentOrTimestamp)` — Seeds deterministic RNG.
2. `GW.State.create()` — Produces initial state.
3. `GW.Renderer.init(canvasElement)` — Sets up canvas.
4. `GW.UI.init(document.getElementById('uiRoot'))` — Binds DOM and event handlers.
5. Start render loop via `requestAnimationFrame`.
6. Start simulation loop via `setInterval` (aligned to `TICK_MS`).
7. Load saved state if present via `GW.State.deserialize()` + `GW.State.applyOfflineProgress()`.

---

---


### 5.1 Runtime State Schema
The **full internal state** object passed between modules. All fields are **primitives or plain objects/arrays**.

```js
{
  // === Metadata ===
  version: "1.0",                 // State schema version (for migration)
  rngSeed: number,                // Deterministic RNG seed (integer)
  lastUpdate: number,             // Unix ms timestamp of last state change

  // === Core Progress ===
  phase: number,                  // 1-4 (current phase)
  highestPhaseUnlocked: number,  // 1-4 (persistent across Retunings)
  totalGlimCaptured: number,     // Lifetime total (monotonic, never resets)
  totalGlimCapturedThisRun: number, // Resets on Retune

  // === Resources ===
  reservoir: number,             // Current stored Glim (0 ≤ reservoir ≤ maxCapacity)
  iridescence: number,            // Permanent currency (never resets)

  // === Capacity ===
  maxCapacity: number,            // Current Reservoir max (≥ 100)
  baseCapacity: number,           // Base capacity before Harmonizer bonuses

  // === Entities ===
  weftlings: [                    // Array of owned Weftlings
    {
      id: string,                 // UUID (generated on purchase)
      type: string,               // One of GW_DATA.weftlingTypes.*
      x: number,                  // px (0 ≤ x ≤ canvasWidth)
      y: number                   // px (0 ≤ y ≤ canvasHeight)
      // Note: level is NOT included; all Weftlings are level 1.
      // Stats are derived from type + upgrades.
    }
  ],
  // Owned class count cache (computed on load/save)
  ownedClassCount: number,        // Number of distinct weftling types owned

  // === Upgrades ===
  upgrades: {
    global: [string],             // Array of purchased global upgrade IDs
    doctrine: string | null,     // Chosen doctrine ID or null
    doctrineUpgrades: [string]   // Array of purchased doctrine upgrade IDs
  },
  permanentUpgrades: [string],   // Array of purchased permanent upgrade IDs

  // === Prestige ===
  retuningCount: number,          // Total Retunings performed (≥ 0)
  lastRetuningTime: number | null, // Unix ms of last Retuning

  // === Simulation State (NOT PERSISTED) ===
  motes: [                        // Active Glim motes (max length = GW.MAX_MOTES)
    {
      id: string,                 // UUID
      x: number,                  // px
      y: number,                  // px
      vx: number,                 // px per second
      vy: number,                 // px per second
      age: number,                // ms (0 ≤ age ≤ fadeTime)
      value: number,              // 1 or 2 (from Brilliant Synthesis)
      fadeTime: number            // ms (computed at spawn)
    }
  ],
  // Bottleneck tracking
  pressure: number,               // 0-1 (current pressure level)
  bottleneckTimer: number,        // ms of continuous production > capture
  // Radiance phase: Irradiance motes
  irradianceActive: boolean,      // True in Phase 4

  // === Victory ===
  victory: boolean,               // True when all victory conditions are met
  victoryTime: number | null,     // Unix ms when victory was achieved

  // === Settings ===
  settings: {
    reducedMotion: boolean,       // Default: false
    colorblindMode: string,       // One of GW_DATA.colorblindModes.*
    speed: number,                // 0.5, 1, 2, or 4 (simulation speed multiplier)
    paused: boolean,              // Default: false
    tutorialComplete: boolean,   // Default: false (set to true after tutorial or skip)
    audioEnabled: boolean        // Default: true (future-proofing)
  },

  // === Tutorial ===
  tutorialStep: number            // 0-8 (0 = not started, 8 = complete)
};
```


### 6.3 `GW.Renderer`
Owns **all canvas rendering** and visual presentation.

```js
GW.Renderer = {
  // --- Constants ---
  CANVAS_WIDTH: 800,   // Default; resized to window
  CANVAS_HEIGHT: 600,
  MOTE_RADIUS: 8,      // px (base)
  AURORA_OPACITY: 0.3, // Background aurora opacity

  // --- Lifecycle ---
  /**
   * Initializes renderer with canvas element.
   * @param {HTMLCanvasElement} canvas
   */
  init: function(canvas: HTMLCanvasElement): void,

  /**
   * Renders the current state to canvas.
   * @param {Object} state - Runtime state.
   * @param {number} deltaMs - Time since last render (for animations).
   */
  render: function(state: Object, deltaMs: number): void,

  // --- Configuration ---
  /**
   * Sets reduced motion mode.
   * @param {boolean} enabled
   */
  setReducedMotion: function(enabled: boolean): void,

  /**
   * Sets colorblind mode.
   * @param {string} mode - One of GW_DATA.colorblindModes.*
   */
  setColorblindMode: function(mode: string): void,

  /**
   * Resizes canvas to new dimensions.
   * @param {number} width
   * @param {number} height
   */
  resize: function(width: number, height: number): void,

  // --- Utilities ---
  /**
   * @param {number} value - Mote value (1 or 2).
   * @returns {string} CSS color for the mote.
   */
  getMoteColor: function(value: number): string,

  /**
   * @param {number} pressure - Current pressure (0-1).
   * @returns {string} Background gradient string.
   */
  getAuroraGradient: function(pressure: number): string
};
```

**Reduced Motion Behavior:**
- When `enabled = true`:
  - Motes are rendered as **static circles** at their spawn position (no `x`, `y` updates).
  - Aurora background is a **static gradient** (no animation).
  - All CSS animations are disabled via `animation: none`.
  - `requestAnimationFrame` still runs (for UI updates), but mote positions are frozen.

**Colorblind Modes:**
| Mode | Mote 1 | Mote 2 | Captured | Fading | Background |
|------|--------|--------|----------|--------|------------|
| `default` | Pale blue (`#7FFFD4`) | Cyan (`#00FFFF`) | White glow | Yellow → Red | Aurora gradient |
| `high-contrast` | Bright green (`#00FF00`) | Bright yellow (`#FFFF00`) | White | Orange → Red | Black |
| `deuteranopia-protanopia` | Circle | Square | Triangle (captured) | Diamond (fading) | Static gray |


## 7. Ownership and Responsibility Matrix

| Concern | Owner | Notes |
|---------|-------|-------|
| **State Data** | `GW.State` | Serialization, migration, validation. |
| **State Mutation** | `GW.Simulation` | Only via `handleAction()` or `step()`. |
| **Simulation Logic** | `GW.Simulation` | Fixed-step updates, RNG, Glim lifecycle. |
| **Canvas Rendering** | `GW.Renderer` | 60 FPS, reduced motion, colorblind. |
| **DOM Manipulation** | `GW.UI` | All HTML/CSS, event binding, accessibility. |
| **User Input** | `GW.UI` | Keyboard, mouse, touch. |
| **Time Management** | `GW.Simulation` | Simulation clock, speed, pause. |
| **RNG** | `GW.Utils.RNG` | Seeded, deterministic. |
| **Save/Load** | `GW.State` | `localStorage`, compression, offline progress. |
| **Offline Progress** | `GW.State` | Calculation on load. |
| **Victory Conditions** | `GW.Simulation` | Checked via `checkVictory()`. |
| **Tutorial** | `GW.UI` + `GW.Simulation` | UI displays, simulation tracks steps. |
| **Error Handling** | All modules | Validate inputs, throw descriptive errors. |
| **Performance** | All modules | Meet budgets (§14). |

**Mutation Rules:**
- **Only `GW.Simulation` may mutate `state`** (via `step()` or `handleAction()`).
- **`GW.State`** may mutate state during `create()`, `fromPersistent()`, `applyOfflineProgress()`, and `migrate()`.
- **`GW.UI` and `GW.Renderer` are read-only** with respect to `state`.
- All mutations **MUST** be followed by `GW.State.validate(state)`.

**Rendering Rules:**
- **`GW.Renderer`** reads `state` but **never writes**.
- **`GW.UI`** reads `state` for display, dispatches actions to `GW.Simulation`.
- **No module** directly modifies DOM except `GW.UI`.

---

---


### 8.2 Glim Mote Lifecycle
Each mote goes through:
1. **Spawn** (by `Glimspinner` or `BrilliantSynthesis`):
   - Position: Random near producer (or random on field if no producer).
   - Velocity: Random direction at `baseDriftSpeed` (modified by `SwiftCurrent`, `MagneticField`).
   - Value: 1 (or 2 if `BrilliantSynthesis` triggers).
   - Fade time: Computed from base + modifiers.
2. **Drift**:
   - Position updated by `vx`, `vy` each simulation tick.
   - If `reducedMotion`, position is frozen at spawn.
3. **Capture**:
   - Spatial hash query for `Driftcatcher` within `captureRadius`.
   - Capture rate scaled by `Threadweaver` bonuses and doctrine effects.
   - On capture: Add `value` to `reservoir` (capped at `maxCapacity`), remove mote.
4. **Fade**:
   - If `age >= fadeTime`, remove mote (lost forever).
   - Fade time modified by:
     - `Loomguard` (+50% in radius)
     - `DriftReduction` (-15% multiplicative)
     - `EnduringGlow` (+100%)
     - `SustainedFlow` (-25% when reservoir > 50%)
     - Phase 3+ fade acceleration (`fadeTime *= (1 - pressure * 2)`)
5. **Overflow**:
   - If `reservoir + value > maxCapacity`, mote is **discarded** (not captured).


## 11. Formatting and Units

### 11.1 Number Formatting
| Input | Output | Notes |
|-------|--------|-------|
| `0` | `"0"` | |
| `500` | `"500"` | |
| `1500` | `"1.5K"` | |
| `1234567` | `"1.23M"` | |
| `1234567890` | `"1.23B"` | |
| `-100` | `"-100"` | Negative values preserved |

**Implementation:**
```js
GW.Utils.formatNumber = function(value, precision = 1) {
  if (value < 1000) return Math.floor(value).toString();
  const units = ["", "K", "M", "B"];
  const tier = Math.floor(Math.log10(Math.abs(value)) / 3);
  const scaled = value / Math.pow(1000, tier);
  return scaled.toFixed(precision) + units[tier];
};
```

### 11.2 Time Formatting
| Input (seconds) | Output |
|-----------------|--------|
| `5` | `"0:05"` |
| `60` | `"1:00"` |
| `125` | `"2:05"` |
| `3661` | `"1:01:01"` |

**Implementation:**
```js
GW.Utils.formatTime = function(seconds) {
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = Math.floor(seconds % 60);
  return h > 0
    ? `${h}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`
    : `${m}:${s.toString().padStart(2, '0')}`;
};
```

### 11.3 Time Units in State
| Field | Unit | Notes |
|-------|------|-------|
| `lastUpdate` | Unix ms | |
| `age` (mote) | ms | |
| `fadeTime` (mote) | ms | |
| `bottleneckTimer` | ms | |
| `lastRetuningTime` | Unix ms | |
| Simulation `deltaMs` | ms | Fixed at 100ms per tick |

---

---


## 12. Test API: `window.__glimweaveTest`

Exposes **deterministic** methods for headless testing. All methods are **synchronous** and **idempotent** given the same seed.

```js
window.__glimweaveTest = {
  // === State Management ===
  /**
   * Creates a new state with optional seed.
   * @param {number} [seed] - RNG seed.
   * @returns {Object} Runtime state.
   */
  createState: function(seed?: number): Object,

  /**
   * Deep-clones a state (for isolation in tests).
   * @param {Object} state
   * @returns {Object}
   */
  cloneState: function(state: Object): Object,

  // === Simulation Control ===
  /**
   * Steps the simulation N times (each step = 100ms).
   * @param {Object} state - State to mutate.
   * @param {number} steps - Number of steps.
   */
  step: function(state: Object, steps: number): void,

  /**
   * Runs simulation until a condition is met or maxSteps reached.
   * @param {Object} state
   * @param {Function} condition - (state) => boolean
   * @param {number} maxSteps - Maximum steps to run.
   * @returns {number} Steps taken.
   */
  stepUntil: function(state: Object, condition: Function, maxSteps: number): number,

  // === Actions (Wrappers around GW.Simulation.handleAction) ===
  buyWeftling: function(state: Object, type: string, x: number, y: number): void,
  buyUpgrade: function(state: Object, upgradeId: string): void,
  chooseDoctrine: function(state: Object, doctrineId: string): void,
  retune: function(state: Object): number, // Returns iridescence gained
  activateAbility: function(state: Object, abilityId: string): void,

  // === Queries ===
  getProductionRate: function(state: Object): number,
  getCaptureRate: function(state: Object): number,
  getPressure: function(state: Object): number,
  getMoteCount: function(state: Object): number,
  getReservoir: function(state: Object): number,
  getPhase: function(state: Object): number,
  isVictory: function(state: Object): boolean,

  // === Offline Progress ===
  applyOfflineProgress: function(state: Object, seconds: number): number, // Returns Glim gained

  // === Save/Load ===
  saveState: function(state: Object): string, // Returns serialized JSON
  loadState: function(json: string): Object,  // Returns runtime state

  // === Validation ===
  validateState: function(state: Object): boolean,
  assertStateInvariants: function(state: Object): void, // Throws on failure

  // === Test Scenarios (Pre-built) ===
  /**
   * Tests that production and capture are independent.
   * @returns {boolean}
   */
  testProductionCaptureIndependence: function(): boolean,

  /**
   * Tests fade impact (all motes fade if uncaptured).
   * @returns {boolean}
   */
  testFadeImpact: function(): boolean,

  /**
   * Tests overflow (excess Glim is lost).
   * @returns {boolean}
   */
  testOverflow: function(): boolean,

  /**
   * Tests unit purchase (Weftling added, Glim deducted).
   * @returns {boolean}
   */
  testUnitPurchase: function(): boolean,

  /**
   * Tests upgrade purchase and effect application.
   * @returns {boolean}
   */
  testUpgradePurchase: function(): boolean,

  /**
   * Tests doctrine lock (other doctrines become unpurchasable).
   * @returns {boolean}
   */
  testDoctrineLock: function(): boolean,

  /**
   * Tests phase progression triggers.
   * @returns {boolean}
   */
  testPhaseProgression: function(): boolean,

  /**
   * Tests Retuning (resets transient, preserves permanent).
   * @returns {boolean}
   */
  testRetuning: function(): boolean,

  /**
   * Tests offline progress calculation.
   * @returns {boolean}
   */
  testOfflineProgress: function(): boolean,

  /**
   * Tests save/load round-trip.
   * @returns {boolean}
   */
  testSaveLoad: function(): boolean,

  /**
   * Tests victory conditions and state freeze.
   * @returns {boolean}
   */
  testVictory: function(): boolean
};
```

**Determinism Guarantee:**
- All methods use the **same RNG seed** if created via `createState(seed)`.
- Example:
  ```js
  const state1 = window.__glimweaveTest.createState(42);
  const state2 = window.__glimweaveTest.createState(42);
  window.__glimweaveTest.step(state1, 100);
  window.__glimweaveTest.step(state2, 100);
  // state1 and state2 are now identical
  ```

---

---


## 14. Accessibility Requirements

### 14.1 Reduced Motion
- **Respects**: `prefers-reduced-motion: reduce` media query **AND** `settings.reducedMotion`.
- **Behavior**:
  - Motes are **static circles** (no drift animation).
  - Aurora background is **static gradient**.
  - All CSS transitions/animations are **disabled**.
- **Implementation**:
  ```css
  @media (prefers-reduced-motion: reduce), (forced-colors: active) {
    * { animation: none !important; transition: none !important; }
  }
  ```
  Plus JS enforcement in `GW.Renderer.setReducedMotion()`.

### 14.2 Colorblind Modes
| Mode | Implementation | Colors/Shapes |
|------|----------------|---------------|
| `default` | Aurora gradient background, colored motes | Mote value = color |
| `high-contrast` | Black background, bright colors | Mote value = color (high contrast) |
| `deuteranopia-protanopia` | Black background, shape-coded | Mote value = shape (circle/square) |

**Shape Coding:**
- Drifting mote (value=1): **Circle**
- Drifting mote (value=2): **Square**
- Captured mote: **Triangle** (briefly before disappearing)
- Fading mote: **Diamond** (last 2s of life)

### 14.3 Keyboard Navigation
| Element | Focus Order | Interaction |
|---------|-------------|-------------|
| Weftling purchase buttons | Tab order | Enter/Space to buy |
| Upgrade buttons | Tab order | Enter/Space to buy |
| Doctrine choice buttons | Tab order | Enter/Space to select |
| Retune button | Tab order | Enter/Space to confirm |
| Settings menu | Tab order | Enter to open, Escape to close |
| Pause button | Tab order | Enter/Space to toggle |
| Speed controls | Tab order | Arrow keys to cycle |

**Requirements:**
- All interactive elements have `tabindex="0"`.
- All have `focus-visible` styles (visible focus ring).
- All have `aria-label` describing their action.
- Modal dialogs **trap focus** (Tab cycles within modal).

### 14.4 Screen Reader Support
- **Live Regions**: `aria-live="polite"` for dynamic updates (e.g., Reservoir level).
- **Labels**: All buttons have `aria-label` (e.g., `"Buy Glimspinner (60 Glim)"`).
- **Tooltips**: Hidden by default, shown on focus/hover (via `aria-describedby`).
- **State Announcements**: Phase changes announced via `aria-live`.

### 14.5 Minimum Viewport (360px)
**Layout Adaptations:**
- Canvas: `width: 100%; height: auto;` (aspect ratio 4:3).
- UI: Stacks vertically.
- Stats panel: Collapses into expandable drawer.
- Buttons: Full-width, minimum `44x44px` touch targets.
- Text: Uses `vw` units for scaling.

**Testing:**
- Chrome DevTools Device Mode: 360×640 (e.g., Galaxy Fold).
- All interactive elements must be **clickable/tappable**.

---

---

## 15. Performance Budgets

| Metric | Budget | Measurement |
|--------|--------|-------------|
| **Simulation Step** | ≤ 5ms | `step()` with 500 motes |
| **Render Frame** | ≤ 16ms | `render()` at 60 FPS |
| **Memory Usage** | ≤ 100MB | Heap snapshot after 30min play |
| **Load Time** | ≤ 500ms | Time to first render |
| **Save Time** | ≤ 50ms | `GW.State.save()` |
| **Load Time** | ≤ 100ms | `GW.State.load()` |
| **Mote Spawn** | ≤ 0.1ms | `spawnMote()` |
| **Capture Query** | ≤ 1ms | Spatial hash query for 50 Driftcatchers |

**Optimizations:**
- **Spatial Hash**: O(1) mote capture lookups (cell size = 200px).
- **Object Pooling**: Reuse mote objects to avoid GC.
- **Canvas Batching**: Group draw calls (e.g., all motes of same color).
- **Throttling**: Offline progress calculation is O(1).
- **No GC in `step()`**: Pre-allocate arrays for motes/weftlings.

---
---

## 16. Automated Acceptance Checks

The following **24+ checks** are implemented as deterministic tests using `window.__glimweaveTest`. Each maps to an owning module.

| # | Check | Module | Success Criteria |
|---|-------|--------|------------------|
| **State & Serialization** |
| 1 | New state is valid | `GW.State` | `validate(createState())` passes |
| 2 | Serialization round-trip | `GW.State` | `loadState(saveState(state))` equals original |
| 3 | Migration from v0.9 | `GW.State` | Migrated state has `ownedClassCount` |
| 4 | Offline progress cap | `GW.State` | 7200s offline → only 3600s counted |
| 5 | Offline progress formula | `GW.State` | Glim gained = `min(production * 0.5 * cappedSec, headroom)` |
| **Simulation Core** |
| 6 | Fixed-step determinism | `GW.Simulation` | Same seed + same steps → same state |
| 7 | Production rate calculation | `GW.Simulation` | 1 Glimspinner → 1 Glim/s (no modifiers) |
| 8 | Capture rate calculation | `GW.Simulation` | 1 Driftcatcher → 0.5 Glim/s (no modifiers) |
| 9 | Pressure calculation | `GW.Simulation` | Phase 2, 100 motes → pressure = 1.0 |
| 10 | Fade time modifiers | `GW.Simulation` | Loomguard in range → fadeTime *= 1.5 |
| 11 | Drift speed modifiers | `GW.Simulation` | SwiftCurrent → driftSpeed *= 1.1 |
| **Units & Upgrades** |
| 12 | Weftling purchase | `GW.Simulation` | `buyWeftling("Glimspinner")` → reservoir -= 60, weftling added |
| 13 | Upgrade purchase | `GW.Simulation` | `buyUpgrade("WeftlingEfficiency")` → reservoir -= 100, effect applied |
| 14 | Doctrine lock | `GW.Simulation` | After `chooseDoctrine("Luminance")`, other doctrines unpurchasable |
| 15 | Threadweaver stacking | `GW.Simulation` | 5 Threadweavers → +50% production/capture (cap) |
| 16 | Harmonizer capacity | `GW.Simulation` | 1 Harmonizer → maxCapacity += 50 |
| **Phase & Victory** |
| 17 | Phase 2 transition | `GW.Simulation` | At 500 captured → phase changes to 2 |
| 18 | Phase 3 transition | `GW.Simulation` | At 2000 captured + 3 classes → phase 3 |
| 19 | Phase 4 transition | `GW.Simulation` | At 5000 captured + 5 classes → phase 4 |
| 20 | Bottleneck pressure | `GW.Simulation` | Production > capture for 10s → pressure *= 2 |
| 21 | Irradiance in Phase 4 | `GW.Simulation` | Motes have value=2, fadeTime /= 3 |
| **Prestige & Progression** |
| 22 | Retuning reset scope | `GW.Simulation` | Transient fields reset, permanent preserved |
| 23 | Retuning cooldown | `GW.Simulation` | Cannot Retune within `300*(1+retuneCount/10)`s |
| 24 | Victory conditions | `GW.Simulation` | All 5 conditions → `victory = true` |
| **UI & Accessibility** |
| 25 | Reduced motion compliance | `GW.Renderer` | No animations when `reducedMotion=true` |
| 26 | Colorblind modes | `GW.Renderer` | All 3 modes render distinguishable motes |
| 27 | Minimum viewport | `GW.UI` | All controls usable at 360px width |
| 28 | Keyboard navigation | `GW.UI` | All interactive elements focusable via Tab |
| **Edge Cases** |
| 29 | Overflow handling | `GW.Simulation` | Reservoir full + capture → Glim lost |
| 30 | Fade completion | `GW.Simulation` | Mote age >= fadeTime → removed |

**Test Harness Example:**
```js
// Runs all checks; returns { passed: number, failed: number, results: Array }
function runAllAcceptanceChecks() {
  const checks = [
    () => __glimweaveTest.testProductionCaptureIndependence(),
    () => __glimweaveTest.testFadeImpact(),
    // ... all 30 checks
  ];
  return checks.map((check, i) => {
    try {
      const result = check();
      return { id: i + 1, passed: result === true, error: null };
    } catch (e) {
      return { id: i + 1, passed: false, error: e.message };
    }
  });
}
```

---
---
