# Glimweave — State Implementation Contract

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


## 5. Serializable State Contract

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

### 5.2 Persistent State Schema (Saved to `localStorage`)
A **subset** of the runtime state, excluding transient simulation data. Serialized as a **plain object** via `JSON.stringify()`.

```js
{
  version: "1.0",
  rngSeed: number,
  lastUpdate: number,

  phase: number,
  highestPhaseUnlocked: number,
  totalGlimCaptured: number,
  totalGlimCapturedThisRun: number,

  reservoir: number,
  iridescence: number,
  maxCapacity: number,
  baseCapacity: number,

  weftlings: [
    { id: string, type: string, x: number, y: number }
  ],
  ownedClassCount: number,

  upgrades: {
    global: [string],
    doctrine: string | null,
    doctrineUpgrades: [string]
  },
  permanentUpgrades: [string],

  retuningCount: number,
  lastRetuningTime: number | null,

  settings: {
    reducedMotion: boolean,
    colorblindMode: string,
    speed: number,
    paused: boolean,
    tutorialComplete: boolean,
    audioEnabled: boolean
  },

  tutorialStep: number
}
```

**Excluded from persistence (recomputed on load):**
- `motes` (recreated from simulation state)
- `pressure`, `bottleneckTimer`, `irradianceActive` (recomputed)
- `victory`, `victoryTime` (rechecked on load)

### 5.3 State Invariants
A valid state **MUST** satisfy all of the following. `GW.State.validate(state)` enforces these and throws on violation.

| Invariant | Field | Rule |
|-----------|-------|------|
| **Version** | `version` | Non-empty string |
| **Phase Range** | `phase` | Integer 1-4 |
| **Highest Phase** | `highestPhaseUnlocked` | Integer 1-4, ≥ `phase` |
| **Non-Negative Glim** | `reservoir` | ≥ 0 |
| **Capacity Bound** | `reservoir` | ≤ `maxCapacity` |
| **Non-Negative Totals** | `totalGlimCaptured`, `totalGlimCapturedThisRun` | ≥ 0 |
| **Monotonic Totals** | `totalGlimCaptured` | ≥ `reservoir` |
| **Iridescence** | `iridescence` | ≥ 0 |
| **Capacity Minimum** | `maxCapacity`, `baseCapacity` | ≥ 100 |
| **Weftling Positions** | `weftlings[].x`, `weftlings[].y` | ≥ 0 |
| **Weftling Types** | `weftlings[].type` | Valid ID in `GW_DATA.weftlings` |
| **Unique Weftling IDs** | `weftlings[].id` | All unique |
| **Owned Class Count** | `ownedClassCount` | = number of unique `weftlings[].type` |
| **Doctrine Consistency** | `upgrades.doctrine` | Null or valid doctrine ID |
| **Doctrine Upgrades** | `upgrades.doctrineUpgrades` | All IDs valid for chosen doctrine |
| **Global Upgrades** | `upgrades.global` | All IDs valid in `GW_DATA.globalUpgrades` |
| **Permanent Upgrades** | `permanentUpgrades` | All IDs valid in `GW_DATA.permanentUpgrades` |
| **Retuning Count** | `retuningCount` | ≥ 0 |
| **Mote Cap** | `motes.length` | ≤ `GW.MAX_MOTES` (500) |
| **Mote Age** | `motes[].age` | ≥ 0, ≤ `motes[].fadeTime` |
| **Mote Value** | `motes[].value` | 1 or 2 |
| **Pressure Range** | `pressure` | 0 ≤ pressure ≤ 1 |
| **Settings Speed** | `settings.speed` | One of [0.5, 1, 2, 4] |
| **Tutorial Step** | `tutorialStep` | Integer 0-8 |

**Validation Method:**
```js
// Signature
GW.State.validate(state: Object): void;
// Throws `Error` with descriptive message if any invariant fails.
// Called on state creation, deserialization, and after every mutation.
```

### 5.4 State Serialization Rules
- **Format**: Plain JSON object (no classes, no functions).
- **No `Date` objects**: All timestamps are Unix ms (numbers).
- **No `undefined`**: All fields are explicitly `null` or omitted if unnecessary.
- **Deterministic**: Serializing the same state twice produces identical JSON.
- **Gzip**: Before saving to `localStorage`, the JSON string is **gzipped** (via `pako` or similar, but since we have no dependencies, we use a pure-JS gzip implementation or skip compression if size permits).
  - **Fallback**: If compression fails, save uncompressed (with `localStorage` 5MB limit, this is safe).

**Save Key:** `"glimweave_save_v1"`

**Auto-Save:**
- Triggered every **30 seconds** of simulation time (not real time).
- Triggered on **tab visibility change** (using `document.visibilityState`).
- Manual save via `GW.State.save(state)` (called by UI).

---

---


### 6.1 `GW.State`
Owns **all state data**, serialization, migration, and offline progress.

```js
GW.State = {
  // --- Lifecycle ---
  /**
   * Creates a new initial game state.
   * @param {number} [seed] - Optional RNG seed. If omitted, uses timestamp hash.
   * @returns {Object} New runtime state.
   */
  create: function(seed?: number): Object,

  /**
   * Validates a state object against all invariants.
   * @param {Object} state - Runtime state.
   * @throws {Error} If any invariant fails.
   */
  validate: function(state: Object): void,

  // --- Serialization ---
  /**
   * Serializes runtime state to persistent state (removes transient fields).
   * @param {Object} state - Runtime state.
   * @returns {Object} Persistent state (plain object).
   */
  toPersistent: function(state: Object): Object,

  /**
   * Deserializes persistent state to runtime state.
   * @param {Object} persistentState - Saved state from localStorage.
   * @returns {Object} Runtime state.
   */
  fromPersistent: function(persistentState: Object): Object,

  /**
   * Applies offline progress to a deserialized state.
   * @param {Object} state - Runtime state (after fromPersistent).
   * @param {number} offlineMs - Milliseconds offline.
   * @returns {Object} Updated runtime state.
   */
  applyOfflineProgress: function(state: Object, offlineMs: number): Object,

  /**
   * Saves current state to localStorage (compressed).
   * @param {Object} state - Runtime state.
   */
  save: function(state: Object): void,

  /**
   * Loads state from localStorage.
   * @returns {Object|null} Runtime state, or null if no save exists.
   */
  load: function(): Object | null,

  /**
   * Deletes saved state from localStorage.
   */
  deleteSave: function(): void,

  // --- Migration ---
  /**
   * Migrates a state from an older version to current.
   * @param {Object} state - Persistent state of older version.
   * @returns {Object} Migrated persistent state.
   */
  migrate: function(state: Object): Object,

  /**
   * Gets the current state schema version.
   * @returns {string}
   */
  getVersion: function(): string
};
```

**Offline Progress Calculation (Normative):**
```js
function applyOfflineProgress(state, offlineMs) {
  const cappedMs = Math.min(offlineMs, GW.DATA.constants.offline.maxSeconds * 1000);
  const productionRate = GW.Simulation.getProductionRate(state); // Glim/s
  const glimGained = productionRate * (cappedMs / 1000) * GW.DATA.constants.offline.productionMultiplier;
  const headroom = state.maxCapacity - state.reservoir;
  const actualGlim = Math.min(glimGained, headroom);

  // Update state
  state.reservoir = Math.min(state.reservoir + actualGlim, state.maxCapacity);
  state.lastUpdate = Date.now(); // Reset timestamp

  // Return summary for UI display
  return { glimGained: actualGlim, seconds: cappedMs / 1000 };
}
```


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


## 10. Persistence and Versioning

### 10.1 Save Format
- **Storage**: `localStorage.setItem("glimweave_save_v1", gzippedJSON)`.
- **Fallback**: If compression fails, store uncompressed.
- **Key**: Includes version for future migrations.

### 10.2 Migration Rules
- **Current Version**: `"1.0"`.
- **Migration Function**: `GW.State.migrate(state)`.
- **Strategy**:
  1. Check `state.version`.
  2. If `version < "1.0"`, apply migrations sequentially.
  3. If `version > "1.0"`, show warning and attempt load (ignore unknown fields).
- **Example Migration (hypothetical 0.9 → 1.0):**
  ```js
  if (state.version === "0.9") {
    state.ownedClassCount = new Set(state.weftlings.map(w => w.type)).size;
    state.version = "1.0";
  }
  ```

### 10.3 Offline Progress on Load
1. On `GW.State.load()`:
   - Read `lastUpdate` from saved state.
   - Compute `offlineMs = Date.now() - lastUpdate`.
   - Call `GW.State.applyOfflineProgress(state, offlineMs)`.
2. Display summary: `"You gained X Glim while offline."` (via `GW.UI.showNotification`).

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
