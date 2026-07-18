# Glimweave — Utils Implementation Contract

Extracted verbatim by heading from `docs/ARCHITECTURE.md`.

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


### 4.2 Validation Invariants
All `GW_DATA` entries **MUST** satisfy these at load time (validated by `GW.Utils.validateGameData()`):

| Invariant | Applies To | Rule |
|-----------|------------|------|
| **Unique IDs** | All definitions | `id` is unique within its category (weftlings, upgrades, etc.) |
| **Valid Phase** | `phaseThresholds` | Phase keys are 2, 3, or 4 |
| **Monotonic Thresholds** | `phaseThresholds` | `totalGlimCaptured` increases with phase |
| **Positive Costs** | All upgrades | `startCost > 0` |
| **Valid Scaling** | All upgrades | `scaling > 1.0` |
| **Non-Negative Caps** | All upgrades | `cap >= 0` (0 = no cap) |
| **Doctrine Consistency** | `doctrineUpgrades` | Each upgrade's `requires` (if set) references another upgrade in the same doctrine |
| **Weftling Unlocks** | `weftlings` | `unlock.phase` is 1-4; if `totalGlimCaptured` exists, it is > 0 |
| **Permanent Upgrade Costs** | `permanentUpgrades` | `cost >= 1` |
| **Colorblind Modes** | `colorblindModes` | Exactly 3 modes defined |

**Validation Method:**
```js
// Signature
GW.Utils.validateGameData(): void;
// Throws `Error` if any invariant fails.
// Called once at startup after GW_DATA is loaded.
```

---

---


### 6.5 `GW.Utils`
Shared utilities with **no state**.

```js
GW.Utils = {
  // --- Random Number Generation ---
  RNG: {
    /**
     * Seeds the RNG.
     * @param {number|string} seed
     */
    seed: function(seed: number | string): void,

    /**
     * @returns {number} Pseudo-random float in [0, 1).
     */
    random: function(): number,

    /**
     * @param {number} min - Inclusive.
     * @param {number} max - Exclusive.
     * @returns {number} Pseudo-random integer in [min, max).
     */
    integer: function(min: number, max: number): number,

    /**
     * @param {Array} array
     * @returns {*} Random element from array.
     */
    choice: function(array: Array): any
  },

  // --- Formatting ---
  /**
   * Formats a number with compact notation (e.g., 1500 → "1.5K").
   * @param {number} value
   * @param {number} [precision=1] - Decimal places.
   * @returns {string}
   */
  formatNumber: function(value: number, precision: number = 1): string,

  /**
   * Formats Glim value (alias for formatNumber).
   * @param {number} value
   * @returns {string}
   */
  formatGlim: function(value: number): string,

  /**
   * Formats duration in seconds to "MM:SS" or "H:MM:SS".
   * @param {number} seconds
   * @returns {string}
   */
  formatTime: function(seconds: number): string,

  // --- Geometry ---
  /**
   * Euclidean distance between two points.
   * @param {number} x1
   * @param {number} y1
   * @param {number} x2
   * @param {number} y2
   * @returns {number}
   */
  distance: function(x1: number, y1: number, x2: number, y2: number): number,

  /**
   * Clamps a value to [min, max].
   * @param {number} value
   * @param {number} min
   * @param {number} max
   * @returns {number}
   */
  clamp: function(value: number, min: number, max: number): number,

  // --- Spatial Hashing (for mote capture optimization) ---
  /**
   * Creates a spatial hash grid.
   * @param {number} cellSize - Grid cell size in px.
   * @returns {Object} Hash grid with { insert, query, clear }.
   */
  createSpatialHash: function(cellSize: number): Object,

  // --- Validation ---
  /**
   * Validates GW_DATA against all invariants (§4.2).
   * @throws {Error} If any invariant fails.
   */
  validateGameData: function(): void,

  /**
   * Generates a UUIDv4.
   * @returns {string}
   */
  uuid: function(): string,

  /**
   * Simple hash function for strings.
   * @param {string} str
   * @returns {number}
   */
  hashCode: function(str: string): number
};
```

**Spatial Hash Usage (Example):**
```js
const grid = GW.Utils.createSpatialHash(200); // 200px cells
grid.insert(mote.x, mote.y, mote);
const nearby = grid.query(mote.x, mote.y, 100); // Radius 100px
```

---

---


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


## 13. Error Handling

### 13.1 Validation Layers
| Layer | Responsibility | Example |
|-------|----------------|---------|
| **Input Validation** | Modules validate their inputs | `GW.Simulation.handleAction()` checks action type |
| **Invariant Checks** | State is valid after every mutation | `GW.State.validate(state)` after `step()` |
| **Game Data Validation** | `GW_DATA` is structurally sound | `GW.Utils.validateGameData()` at startup |
| **Type Safety** | Use of string constants (e.g., `GW_DATA.weftlingTypes.GLIMSPINNER`) |

### 13.2 Error Behavior
- **Development**: Throw `Error` with descriptive message.
- **Production**: Catch errors, log to console, and display user-friendly message via `GW.UI.showModal()`.
- **Critical Errors** (e.g., save corruption): Show error modal with option to reset game.

**Example:**
```js
try {
  GW.Simulation.handleAction(state, action);
} catch (e) {
  GW.UI.showModal("Error", e.message, [{ text: "OK" }]);
}
```

### 13.3 Invariant Enforcement
- **Hard Invariants**: Enforced by validation (e.g., `reservoir <= maxCapacity`).
- **Soft Invariants**: Logged but not enforced (e.g., "production should be > 0").
- **Assertions**: In development, use `console.assert()`; in production, no-op.

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

## 18. Implementation Notes

### 18.1 Mandatory Patterns
- **String Constants**: Always use `GW_DATA.weftlingTypes.GLIMSPINNER` (not `"Glimspinner"`).
- **State Mutation**: Only via `GW.Simulation.handleAction()` or `GW.Simulation.step()`.
- **Validation**: Call `GW.State.validate(state)` after **every** mutation.
- **Error Messages**: Include **field names** and **expected/actual values**.
- **No `Date.now()` in State**: Timestamps use Unix ms but are **not** generated during serialization.

### 18.2 Prohibited Patterns
- ❌ **`fetch` or `XMLHttpRequest`** — No network access.
- ❌ **`import`/`export`** — No modules.
- ❌ **`eval`** — No dynamic code execution.
- ❌ **`setTimeout`/`setInterval` for simulation** — Use fixed-step loop.
- ❌ **Modifying `GW_DATA` at runtime** — Treat as read-only.
- ❌ **Direct DOM access outside `GW.UI`** — Use `GW.UI` methods.
- ❌ **Floating-point for Glim** — Use integers (cents pattern if decimals needed).

### 18.3 Recommended Optimizations
- **Spatial Hash**: Use for `Driftcatcher` capture lookups (O(1) per mote).
- **Object Pooling**: Reuse mote objects (reset `age`, `x`, `y` instead of allocating).
- **Dirty Flag**: Only re-render UI when state changes (not every frame).
- **Canvas Layers**: Use separate canvases for static (aurora) and dynamic (motes) elements.

---
---
