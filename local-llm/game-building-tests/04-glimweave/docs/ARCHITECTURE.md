# Glimweave — Architecture Contract

---

## 1. Executive Overview

**Glimweave** is a fully offline, single-file browser game implementing a deterministic real-time incremental simulation. It uses **classic JavaScript** (ES5+), **no modules**, **no build step**, and **no dependencies**. All code executes in the `window.GW` namespace. Opening `index.html` directly must start the game.

**Core tenets:**
- Strict separation: **State** owns data, **Simulation** owns logic, **Renderer** owns canvas, **UI** owns DOM.
- Deterministic: Fixed-step simulation + seeded RNG.
- Offline-first: All progress calculated client-side; save/load uses `localStorage`.
- Accessible: Reduced motion, colorblind modes, keyboard navigation, screen reader support.
- Testable: `window.__glimweaveTest` exposes deterministic control for headless verification.

---

---

## 2. File Tree and Boot Sequence

### 2.1 Directory Structure
```
.
├── index.html
├── styles.css
├── data/
│   └── game-data.js          // Defines `window.GW_DATA`
├── src/
│   ├── utils.js              // RNG, formatting, geometry, spatial hash
│   ├── state.js              // GW.State
│   ├── simulation.js         // GW.Simulation
│   ├── render.js             // GW.Renderer
│   └── ui.js                 // GW.UI
└── docs/
    ├── GAME_DESIGN.md
    └── ARCHITECTURE.md
```

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

### 2.3 Load Order Rationale
1. `game-data.js` — Defines `GW_DATA` **before** any module initializes.
2. `utils.js` — Provides shared utilities (RNG, formatting) required by all modules.
3. `state.js` — Defines state shape and serialization; no dependencies beyond `GW_DATA` and `GW.Utils`.
4. `simulation.js` — Depends on `GW.State` and `GW.Utils`.
5. `render.js` — Depends on `GW.Utils`; may query `GW.State`.
6. `ui.js` — Orchestrates modules; depends on all others.
7. Init call — `GW.init()` bootstraps the game loop and UI binding.

---

---

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

## 4. Data Contract: `GW_DATA`

### 4.1 Complete Schema
`window.GW_DATA` is a **plain object** defined in `data/game-data.js`. All string IDs are **case-sensitive** and match the game design exactly.

```js
window.GW_DATA = {
  // --- Metadata ---
  version: "1.0",               // Schema version for GW_DATA itself

  // --- Enums (string constants for type safety) ---
  phases: {
    AWKENING: "Awakening",
    RESONANCE: "Resonance",
    CONVERGENCE: "Convergence",
    RADIANCE: "Radiance"
  },
  weftlingTypes: {
    GLIMSPINNER: "Glimspinner",
    DRIFTCATCHER: "Driftcatcher",
    THREADWEAVER: "Threadweaver",
    HARMONIZER: "Harmonizer",
    LOOMGUARD: "Loomguard"
  },
  doctrines: {
    LUMINANCE: "Luminance",
    CAPTIVATION: "Captivation",
    RESILIENCE: "Resilience"
  },
  colorblindModes: {
    DEFAULT: "default",
    HIGH_CONTRAST: "high-contrast",
    DEUTERANOPIA: "deuteranopia-protanopia"
  },

  // --- Phase Definitions ---
  phaseThresholds: {
    // phase: { totalGlimCaptured, requiredClassCount }
    2: { totalGlimCaptured: 500, requiredClassCount: null },
    3: { totalGlimCaptured: 2000, requiredClassCount: 3 },
    4: { totalGlimCaptured: 5000, requiredClassCount: 5 }
  },
  phaseConstants: {
    // phase: { pressureThreshold, overflowAccelerationFactor, fadeAccelerationFactor }
    1: { pressureThreshold: 100, overflowAccelerationFactor: 0, fadeAccelerationFactor: 0 },
    2: { pressureThreshold: 100, overflowAccelerationFactor: 0, fadeAccelerationFactor: 0 },
    3: { pressureThreshold: 150, overflowAccelerationFactor: 0.5, fadeAccelerationFactor: 2 },
    4: { pressureThreshold: 200, overflowAccelerationFactor: 0.5, fadeAccelerationFactor: 2 }
  },

  // --- Weftling Definitions ---
  weftlings: {
    // key = weftlingType ID
    Glimspinner: {
      id: "Glimspinner",
      role: "producer",
      baseProduction: 1,          // Glim per second
      baseCaptureRate: 0,
      baseFadeExtension: 0,
      supportRadius: 0,
      unlock: { phase: 1, totalGlimCaptured: 0 },
      baseCost: 60,
      maxOwned: 50,
      description: "Produces 1 Glim every second."
    },
    Driftcatcher: {
      id: "Driftcatcher",
      role: "capturer",
      baseProduction: 0,
      baseCaptureRate: 0.5,       // Glim per second capture rate
      captureRadius: 100,         // px
      baseFadeExtension: 0,
      supportRadius: 0,
      unlock: { phase: 1, totalGlimCaptured: 50 },
      baseCost: 75,
      maxOwned: 50,
      description: "Captures drifting Glim within 100 px at 0.5/s."
    },
    Threadweaver: {
      id: "Threadweaver",
      role: "support",
      baseProduction: 0,
      baseCaptureRate: 0,
      baseFadeExtension: 0,
      supportRadius: 150,         // px
      productionBonus: 0.10,     // +10% per Threadweaver
      captureBonus: 0.10,
      maxStack: 0.50,             // Cap at +50%
      unlock: { phase: 2 },
      baseCost: 100,
      maxOwned: 25,
      description: "Grants +10% production & capture to nearby Weftlings (max +50%)."
    },
    Harmonizer: {
      id: "Harmonizer",
      role: "reservoir",
      baseProduction: 0,
      baseCaptureRate: 0,
      baseFadeExtension: 0,
      supportRadius: 0,
      capacityBonus: 50,          // Flat +50 capacity each
      unlock: { phase: 2, totalGlimSpentOnCapacity: 200 },
      baseCost: 125,
      maxOwned: 20,
      description: "Increases Reservoir capacity by 50."
    },
    Loomguard: {
      id: "Loomguard",
      role: "fadeProtection",
      baseProduction: 0,
      baseCaptureRate: 0,
      baseFadeExtension: 0.50,    // +50% fade time
      supportRadius: 120,         // px
      unlock: { phase: 3 },
      baseCost: 150,
      maxOwned: 20,
      description: "Extends fade timer by 50% for Glim in radius."
    }
  },

  // --- Upgrade Definitions ---
  globalUpgrades: {
    // key = upgrade ID
    WeftlingEfficiency: {
      id: "WeftlingEfficiency",
      name: "Weftling Efficiency",
      effect: "+10% production & capture",
      startCost: 100,
      scaling: 1.5,
      cap: 2.0,                 // +200% total
      category: "global"
    },
    ReservoirExpansion: {
      id: "ReservoirExpansion",
      name: "Reservoir Expansion",
      effect: "+100 capacity",
      startCost: 200,
      scaling: 1.8,
      cap: 5000,                // +5,000 total
      category: "global"
    },
    DriftReduction: {
      id: "DriftReduction",
      name: "Drift Reduction",
      effect: "-15% fade speed (multiplicative)",
      startCost: 150,
      scaling: 1.6,
      cap: 0.80,                // -80% total (i.e., 20% of original)
      category: "global"
    },
    BasicTraining: {
      id: "BasicTraining",
      name: "Basic Training",
      effect: "+1 max Weftling slot",
      startCost: 50,
      scaling: 1.4,
      cap: 50,                  // +50 slots total
      category: "global"
    },
    FieldAmplifier: {
      id: "FieldAmplifier",
      name: "Field Amplifier",
      effect: "+5% production from all sources",
      startCost: 300,
      scaling: 1.7,
      cap: 1.00,                // +100% total
      category: "global"
    },
    ReinforcedField: {
      id: "ReinforcedField",
      name: "Reinforced Field",
      effect: "Pressure effects reduced by 20%",
      startCost: 400,
      scaling: 1.7,
      cap: 0.80,                // -80% total (i.e., 20% of original pressure)
      category: "global"
    },
    SwiftCurrent: {
      id: "SwiftCurrent",
      name: "Swift Current",
      effect: "Glim drifts 10% faster",
      startCost: 200,
      scaling: 1.55,
      cap: 0.50,                // +50% total
      category: "global"
    }
  },

  // --- Doctrine Upgrades ---
  doctrineUpgrades: {
    // key = doctrine ID
    Luminance: [
      {
        id: "EnhancedSpindles",
        name: "Enhanced Spindles",
        effect: "+20% Glimspinner production",
        startCost: 250,
        scaling: 1.6,
        requires: null,
        target: "Glimspinner"
      },
      {
        id: "RadiantCore",
        name: "Radiant Core",
        effect: "Every 5s: 2× production for 1s",
        startCost: 500,
        scaling: 1.7,
        requires: "EnhancedSpindles",
        target: null
      },
      {
        id: "BrilliantSynthesis",
        name: "Brilliant Synthesis",
        effect: "5% chance to produce 2 Glim",
        startCost: 400,
        scaling: 1.75,
        requires: null,
        target: null
      },
      {
        id: "EverflowMatrix",
        name: "Everflow Matrix",
        effect: "Produced Glim never fades",
        startCost: 1000,
        scaling: 1.8,
        requires: "RadiantCore",
        target: null
      },
      {
        id: "LuminousSurge",
        name: "Luminous Surge",
        effect: "+15% production for 10s after phase change",
        startCost: 350,
        scaling: 1.65,
        requires: null,
        target: null
      }
    ],
    Captivation: [
      {
        id: "GraspingTendrils",
        name: "Grasping Tendrils",
        effect: "+30% capture radius",
        startCost: 300,
        scaling: 1.65,
        requires: null,
        target: null
      },
      {
        id: "VortexLens",
        name: "Vortex Lens",
        effect: "Captured Glim gives +5% bonus Glim",
        startCost: 400,
        scaling: 1.7,
        requires: "GraspingTendrils",
        target: null
      },
      {
        id: "TetheredFlight",
        name: "Tethered Flight",
        effect: "On activation: 2× capture for 5s (30s cooldown)",
        startCost: 500,
        scaling: 1.7,
        requires: null,
        target: null,
        cooldown: 30000,
        duration: 5000
      },
      {
        id: "OmniDirectional",
        name: "Omni Directional",
        effect: "Instantly captures all Glim in Reservoir radius on activation (60s cooldown)",
        startCost: 800,
        scaling: 1.8,
        requires: "VortexLens",
        target: null,
        cooldown: 60000
      },
      {
        id: "MagneticField",
        name: "Magnetic Field",
        effect: "Glim drifts 20% slower",
        startCost: 250,
        scaling: 1.6,
        requires: null,
        target: null
      }
    ],
    Resilience: [
      {
        id: "SturdyReservoir",
        name: "Sturdy Reservoir",
        effect: "+200 capacity",
        startCost: 400,
        scaling: 1.7,
        requires: null,
        target: null
      },
      {
        id: "EnduringGlow",
        name: "Enduring Glow",
        effect: "+100% fade time",
        startCost: 350,
        scaling: 1.65,
        requires: null,
        target: null
      },
      {
        id: "PressureValve",
        name: "Pressure Valve",
        effect: "+10% production when Reservoir > 80%",
        startCost: 600,
        scaling: 1.7,
        requires: "SturdyReservoir",
        target: null
      },
      {
        id: "UnyieldingFoundation",
        name: "Unyielding Foundation",
        effect: "Max capacity +50%",
        startCost: 1000,
        scaling: 1.8,
        requires: null,
        target: null
      },
      {
        id: "SustainedFlow",
        name: "Sustained Flow",
        effect: "-25% fade rate when Reservoir > 50%",
        startCost: 500,
        scaling: 1.65,
        requires: "EnduringGlow",
        target: null
      },
      {
        id: "OverflowGate",
        name: "Overflow Gate",
        effect: "On overflow: 20% of excess redirected to temporary buffer (decays over 30s)",
        startCost: 700,
        scaling: 1.75,
        requires: "PressureValve",
        target: null
      }
    ]
  },

  // --- Permanent Upgrades (Iridescence shop) ---
  permanentUpgrades: {
    WeftlingMemory: {
      id: "WeftlingMemory",
      name: "Weftling Memory",
      effect: "Start with +1 Weftling slot",
      cost: 1,
      stackable: true
    },
    ReservoirBlueprint: {
      id: "ReservoirBlueprint",
      name: "Reservoir Blueprint",
      effect: "Start with +100 capacity",
      cost: 2,
      stackable: true
    },
    EternalGlow: {
      id: "EternalGlow",
      name: "Eternal Glow",
      effect: "Base fade time +50%",
      cost: 3,
      stackable: false
    },
    PrismaticCore: {
      id: "PrismaticCore",
      name: "Prismatic Core",
      effect: "All doctrine upgrade costs -10%",
      cost: 5,
      stackable: false
    },
    DawnsPromise: {
      id: "DawnsPromise",
      name: "Dawn's Promise",
      effect: "Start with 1 random doctrine upgrade pre-unlocked",
      cost: 4,
      stackable: false
    },
    LuminousLegacy: {
      id: "LuminousLegacy",
      name: "Luminous Legacy",
      effect: "Glimspinners start at +10% production",
      cost: 3,
      stackable: true
    },
    SteadyHand: {
      id: "SteadyHand",
      name: "Steady Hand",
      effect: "Capture radius +10%",
      cost: 2,
      stackable: true
    },
    EnduringDesign: {
      id: "EnduringDesign",
      name: "Enduring Design",
      effect: "Pressure effects reduced by 30%",
      cost: 4,
      stackable: false
    }
  },

  // --- Constants ---
  constants: {
    baseFadeTime: 10000,        // ms
    baseDriftSpeed: 120,        // px per second (2 px/frame @ 60 FPS)
    baseReservoirCapacity: 100,
    maxMotes: 500,              // Hard cap on visible motes
    offline: {
      maxSeconds: 3600,        // 1 hour cap
      productionMultiplier: 0.5
    },
    retuning: {
      iridescenceFormula: "floor(totalGlimCapturedThisRun / 200) + 1",
      minimumIntervalBase: 300, // 5 minutes base
      diminishingReturnsThreshold: 10
    },
    victory: {
      requirements: [
        "phase === 4",
        "all 5 Weftling classes owned",
        "reservoir === maxCapacity for 60s continuous",
        "totalGlimCaptured >= 10000",
        "upgrades.purchased >= 12"
      ],
      scoreFormula: "floor(totalGlimCaptured * (1 + iridescence / 100) * (1 + doctrineBonus))",
      doctrineBonus: { Luminance: 0, Captivation: 0.05, Resilience: 0.10 }
    },
    tutorial: {
      steps: 8 // As per GAME_DESIGN.md §9
    }
  }
};
```

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

## 6. Module Public APIs

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

### 6.2 `GW.Simulation`
Owns **all game logic**, fixed-step updates, and deterministic RNG.

```js
GW.Simulation = {
  // --- Constants ---
  TICK_MS: 100,   // Fixed simulation step (10 FPS)

  // --- Lifecycle ---
  /**
   * Initializes simulation with a state.
   * @param {Object} state - Runtime state.
   */
  init: function(state: Object): void,

  /**
   * Advances simulation by one fixed tick.
   * @param {Object} state - Runtime state (MUTATED IN PLACE).
   * @param {number} deltaMs - Time to advance (default: TICK_MS).
   */
  step: function(state: Object, deltaMs: number = GW.Simulation.TICK_MS): void,

  // --- Actions (UI → Simulation) ---
  /**
   * Handles an action, mutating state if valid.
   * @param {Object} state - Runtime state (MUTATED).
   * @param {Object} action - Action object (see §10.1).
   * @returns {Object} New state (same object, mutated).
   * @throws {Error} If action is invalid (e.g., insufficient Glim).
   */
  handleAction: function(state: Object, action: Object): Object,

  // --- Queries ---
  /**
   * @param {Object} state
   * @returns {number} Current production rate in Glim/s.
   */
  getProductionRate: function(state: Object): number,

  /**
   * @param {Object} state
   * @returns {number} Current capture rate in Glim/s.
   */
  getCaptureRate: function(state: Object): number,

  /**
   * @param {Object} state
   * @returns {number} Current pressure (0-1).
   */
  getPressure: function(state: Object): number,

  /**
   * @param {Object} state
   * @returns {boolean} True if all victory conditions are met.
   */
  checkVictory: function(state: Object): boolean,

  /**
   * @param {Object} state
   * @returns {Array<Object>} All active motes.
   */
  getMotes: function(state: Object): Array<Object>,

  /**
   * @param {Object} state
   * @returns {number} Current phase (1-4).
   */
  getPhase: function(state: Object): number,

  // --- Mote Management ---
  /**
   * Spawns a new Glim mote at (x, y) with given value.
   * @param {Object} state - Runtime state.
   * @param {number} x - Spawn x position (px).
   * @param {number} y - Spawn y position (px).
   * @param {number} [value=1] - Mote value (1 or 2).
   * @returns {Object|null} The spawned mote, or null if cap reached.
   */
  spawnMote: function(state: Object, x: number, y: number, value: number = 1): Object | null,

  /**
   * Removes a mote by ID.
   * @param {Object} state - Runtime state.
   * @param {string} moteId - ID of mote to remove.
   */
  removeMote: function(state: Object, moteId: string): void,

  // --- Phase Management ---
  /**
   * Attempts to advance to the next phase.
   * @param {Object} state - Runtime state.
   * @returns {boolean} True if phase changed.
   */
  tryAdvancePhase: function(state: Object): boolean,

  // --- Prestige ---
  /**
   * Performs Retuning if conditions are met.
   * @param {Object} state - Runtime state (MUTATED).
   * @returns {Object} { success: boolean, iridescenceGained: number }
   * @throws {Error} If Retuning conditions not met.
   */
  retune: function(state: Object): Object
};
```

**Fixed-Step Design:**
- Simulation logic runs at **10 FPS** (`TICK_MS = 100`).
- Each `step()` advances the world by exactly `deltaMs` (default 100ms).
- Rendering runs at **60 FPS** independently (via `requestAnimationFrame`).
- When `settings.paused` is true, `step()` is a no-op.
- When `settings.speed` is set, `deltaMs` passed to `step()` is scaled (e.g., `speed=2` → `deltaMs=200`).

**Seeded RNG (`GW.Utils.RNG`):**
- **Algorithm**: Mulberry32 (simple, fast, deterministic).
- **Seed**: Stored in `state.rngSeed` (integer).
- **Usage**: All randomness (mote spawn positions, drift directions) uses `GW.Utils.RNG.random()`.
- **Initialization**:
  - New game: `seed = hashCode(Date.now().toString())`.
  - Loaded game: `seed = state.rngSeed`.
  - Test: `seed` passed explicitly to `GW.State.create(seed)`.

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

### 6.4 `GW.UI`
Owns **all DOM manipulation**, event handling, and user input.

```js
GW.UI = {
  // --- Lifecycle ---
  /**
   * Initializes UI with root DOM element.
   * @param {HTMLElement} root
   */
  init: function(root: HTMLElement): void,

  /**
   * Updates all UI elements to reflect current state.
   * @param {Object} state - Runtime state.
   */
  update: function(state: Object): void,

  // --- Event Binding ---
  /**
   * Binds a callback for game actions.
   * @param {Function} handler - (action) => void
   */
  onAction: function(handler: Function): void,

  // --- Tutorial ---
  /**
   * Shows a tutorial step.
   * @param {number} stepId - 0-8 (see GAME_DESIGN.md §9).
   */
  showTutorialStep: function(stepId: number): void,

  /**
   * Hides the tutorial overlay.
   */
  hideTutorial: function(): void,

  // --- Modals ---
  /**
   * Shows a modal dialog.
   * @param {string} title
   * @param {string} message
   * @param {Array<{text: string, callback: Function}>} buttons
   */
  showModal: function(title: string, message: string, buttons: Array<Object>): void,

  /**
   * Hides the active modal.
   */
  hideModal: function(): void,

  // --- Notifications ---
  /**
   * Shows a transient notification.
   * @param {string} message
   * @param {string} [type="info"] - "info" | "success" | "warning" | "error"
   */
  showNotification: function(message: string, type: string = "info"): void
};
```

**DOM Ownership:**
- `GW.UI` **exclusively** creates/modifies DOM elements.
- `GW.Renderer` **only** uses `<canvas>` (never DOM).
- All interactive elements have:
  - `tabindex` for keyboard focus.
  - `aria-label` for screen readers.
  - `focus-visible` styles for keyboard navigation.

**Keyboard Bindings:**
| Key | Action |
|-----|--------|
| `Space` | Toggle pause |
| `1-4` | Set simulation speed (1=1×, 2=2×, 3=4×, 4=0.5×) |
| `T` | Toggle tutorial (if not complete) |
| `M` | Toggle reduced motion |
| `C` | Cycle colorblind mode |
| `Escape` | Close active modal / menu |

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

## 8. Simulation Design

### 8.1 Fixed-Step Architecture
- **Simulation Tick**: 100ms (10 FPS).
- **Render Frame**: ~16.67ms (60 FPS).
- **Decoupling**: Simulation and rendering run independently.
- **Accumulator Pattern**: Simulation accumulates time and steps in fixed increments.

**Simulation Loop:**
```js
let accumulator = 0;
const fixedDelta = GW.Simulation.TICK_MS;

function simulationLoop() {
  const now = performance.now();
  const delta = now - lastTime;
  lastTime = now;

  if (!state.settings.paused) {
    accumulator += delta * state.settings.speed;
    while (accumulator >= fixedDelta) {
      GW.Simulation.step(state, fixedDelta);
      accumulator -= fixedDelta;
    }
  }

  requestAnimationFrame(simulationLoop);
}
```

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

### 8.3 Weftling Effects
All Weftling stats are **derived from their type + upgrades** at runtime (not stored per-instance).

**Glimspinner:**
- Production: `baseProduction * (1 + WeftlingEfficiency * count) * (1 + FieldAmplifier * count) * doctrineBonuses`
- Spawns motes at its `(x, y)` position.

**Driftcatcher:**
- Capture rate: `baseCaptureRate * (1 + WeftlingEfficiency * count) * (1 + ThreadweaverBonus) * doctrineBonuses`
- Capture radius: `baseCaptureRadius * (1 + GraspingTendrils * count)`

**Threadweaver:**
- Bonuses: `productionBonus * count` (capped at `maxStack`) to all Weftlings in `supportRadius`.
- Same for `captureBonus`.

**Harmonizer:**
- Capacity: `baseCapacity + (capacityBonus * count)`

**Loomguard:**
- Fade extension: `baseFadeExtension * count` to all motes in `supportRadius`.

### 8.4 Phase Mechanics
| Phase | Mechanics | Formula |
|-------|-----------|---------|
| 1 (Awakening) | Base production, fade, capture | — |
| 2 (Resonance) | **Pressure**: `pressure = min(1, uncapturedMotes / pressureThreshold)` | `pressureThreshold = GW_DATA.phaseConstants[phase].pressureThreshold` |
| | **Production Multiplier**: `1 - pressure * 0.5` | |
| 3 (Convergence) | **Overflow Acceleration**: `overflowLoss = capturedGlim * min(1, uncapturedMotes / 100 * 0.5)` | |
| | **Fade Acceleration**: `effectiveFadeRate = baseFadeRate * (1 + pressure * 2)` | |
| | **Bottleneck**: If `production > capture` for >10s, `pressure *= 2` | |
| 4 (Radiance) | **Irradiance**: Motes spawn with `value=2` but `fadeTime /= 3` | |

**Phase Transition:**
- Checked in `GW.Simulation.step()`.
- Conditions:
  - Phase 2: `totalGlimCaptured >= 500`
  - Phase 3: `totalGlimCaptured >= 2000 && ownedClassCount >= 3`
  - Phase 4: `totalGlimCaptured >= 5000 && ownedClassCount >= 5`

### 8.5 Retuning (Prestige)
**Trigger Conditions:**
- `(phase >= 2 && totalGlimCapturedThisRun >= 1000) || phase >= 4`

**Reset Scope:**
| Field | Preserved | Reset |
|-------|-----------|-------|
| `reservoir` | ❌ | 0 |
| `maxCapacity` | ❌ | `baseCapacity` |
| `weftlings` | ❌ | Empty |
| `upgrades.global` | ❌ | Empty |
| `upgrades.doctrine` | ❌ | `null` |
| `upgrades.doctrineUpgrades` | ❌ | Empty |
| `phase` | ❌ | 1 |
| `totalGlimCapturedThisRun` | ❌ | 0 |
| `iridescence` | ✅ | — |
| `permanentUpgrades` | ✅ | — |
| `highestPhaseUnlocked` | ✅ | — |
| `retuningCount` | ✅ | Incremented |
| `settings` | ✅ | — |
| `tutorialComplete` | ✅ | — |

**Iridescence Reward:**
```js
const baseReward = Math.floor(state.totalGlimCapturedThisRun / 200) + 1;
const retuneCount = state.retuningCount;
if (retuneCount >= 10) {
  const divisor = 200 * (1 + retuneCount / 20);
  return Math.floor(state.totalGlimCapturedThisRun / divisor) + 1;
}
return baseReward;
```

**Cooldown:**
- Minimum interval: `300 * (1 + retuningCount / 10)` seconds (capped at 3600s).
- Enforced in `GW.Simulation.retune()`.

### 8.6 Victory: "Weave the Dawn"
**Conditions (ALL must be true simultaneously):**
1. `phase === 4`
2. `ownedClassCount === 5` (all Weftling classes owned)
3. `reservoir === maxCapacity` for **60 continuous seconds**
4. `totalGlimCaptured >= 10000`
5. `upgrades.global.length + upgrades.doctrineUpgrades.length >= 12`

**On Victory:**
1. Set `state.victory = true`.
2. Freeze simulation (`paused = true` implicitly).
3. Play aurora convergence animation (canvas-only).
4. Compute score:
   ```js
   const doctrineBonus = GW.DATA.constants.victory.doctrineBonus[state.upgrades.doctrine] || 0;
   const score = Math.floor(
     state.totalGlimCaptured *
     (1 + state.iridescence / 100) *
     (1 + doctrineBonus)
   );
   ```
5. Mark save slot as complete (stored in `localStorage` as `"glimweave_victory_v1"`).

---

---

## 9. Event and Action Protocol

### 9.1 Action Types (UI → Simulation)
All actions are **plain objects** with a `type` field. Dispatched via `GW.UI.onAction(action)` → `GW.Simulation.handleAction(state, action)`.

| Action Type | Fields | Effect |
|-------------|--------|--------|
| `BUY_WEFTLING` | `{ type, x, y }` | Purchases a Weftling if affordable and unlocked. |
| `BUY_UPGRADE` | `{ upgradeId }` | Purchases a global or doctrine upgrade if affordable and available. |
| `CHOOSE_DOCTRINE` | `{ doctrineId }` | Locks in a doctrine; cannot be undone. |
| `RETUNE` | `{}` | Resets transient progress if conditions met. |
| `PAUSE` | `{}` | Toggles `state.settings.paused`. |
| `SET_SPEED` | `{ speed }` | Sets simulation speed (0.5, 1, 2, 4). |
| `SET_REDUCED_MOTION` | `{ enabled }` | Toggles reduced motion. |
| `SET_COLORBLIND_MODE` | `{ mode }` | Sets colorblind mode. |
| `SKIP_TUTORIAL` | `{}` | Skips tutorial (only on first run). |
| `ACTIVATE_ABILITY` | `{ abilityId }` | Activates a doctrine ability (e.g., `TetheredFlight`). |

**Action Validation:**
- `BUY_WEFTLING`: Weftling type must be unlocked for current phase, and `reservoir >= cost`.
- `BUY_UPGRADE`: Upgrade must be purchasable (not already owned, doctrine matches, prerequisites met), and `reservoir >= cost`.
- `CHOOSE_DOCTRINE`: `upgrades.doctrine === null`.
- `RETUNE`: Conditions in §8.5 must be met, and cooldown must have elapsed.
- All actions **throw** if validation fails.

### 9.2 State Change Notifications
- **Polling Model**: `GW.UI.update(state)` is called by the main loop after each `step()`.
- **No Event Emitters**: To avoid dependencies, modules **read state directly** and react accordingly.
- **Tutorial Integration**: `GW.Simulation.step()` checks for tutorial triggers (e.g., first mote spawn) and calls `GW.UI.showTutorialStep(step)`.

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
## 17. Resolved Design Ambiguities

| Ambiguity | Resolution |
|-----------|------------|
| **`glim` vs `reservoir` in save format** | `reservoir` = current stored Glim; `totalGlimCaptured` = lifetime total. The `glim` field in the example is a typo and **not used**. |
| **Mote value in Phase 4** | Irradiance motes have `value=2` **and** `fadeTime /= 3`. |
| **Bottleneck timer reset** | Resets to 0 when `production <= capture`. |
| **Overflow Gate buffer** | Temporary buffer is **not persisted** (decays over 30s in-memory). |
| **Doctrine upgrade prerequisites** | Prerequisites are **checked at purchase time** (not at doctrine selection). |
| **Retuning and highestPhaseUnlocked** | `highestPhaseUnlocked` is the **maximum phase reached across all runs** (never resets). |
| **Tutorial on subsequent runs** | Skipped if `settings.tutorialComplete === true`. |
| **Save compression** | Gzip if available; **fallback to uncompressed** if not. |
| **RNG for mote spawns** | Seeded from `state.rngSeed`; **deterministic per save**. |
| **Pressure threshold formula** | `pressureThreshold = GW_DATA.phaseConstants[phase].pressureThreshold` (explicit per-phase values). |
| **Weftling level** | All Weftlings are **level 1**; stats come from upgrades. |
| **Glimspinner spawn position** | Spawns motes at its `(x, y)` position. |
| **Driftcatcher capture** | Captures motes **instantly** when in range (no travel time). |
| **Victory score doctrine bonus** | +0% Luminance, +5% Captivation, +10% Resilience. |

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
## 19. Appendix: Formulas Reference

### 19.1 Production Rate
```js
let rate = weftlings
  .filter(w => w.type === GW_DATA.weftlingTypes.GLIMSPINNER)
  .length * GW_DATA.weftlings.Glimspinner.baseProduction;

// Global upgrades
const weftlingEfficiency = state.upgrades.global.filter(id => id === "WeftlingEfficiency").length;
const fieldAmplifier = state.upgrades.global.filter(id => id === "FieldAmplifier").length;
rate *= (1 + weftlingEfficiency * 0.10); // WeftlingEfficiency: +10% each
rate *= (1 + fieldAmplifier * 0.05);    // FieldAmplifier: +5% each

// Doctrine upgrades
if (state.upgrades.doctrine === GW_DATA.doctrines.LUMINANCE) {
  const enhancedSpindles = state.upgrades.doctrineUpgrades.filter(id => id === "EnhancedSpindles").length;
  rate *= (1 + enhancedSpindles * 0.20); // +20% each
  if (state.upgrades.doctrineUpgrades.includes("RadiantCore")) {
    // Every 5s: 2× production for 1s (handled in step())
  }
  if (state.upgrades.doctrineUpgrades.includes("BrilliantSynthesis")) {
    // 5% chance per mote to be value=2 (handled at spawn)
  }
}

// Pressure (Phase 2+)
const phase = state.phase;
if (phase >= 2) {
  const pressure = GW.Simulation.getPressure(state);
  rate *= (1 - pressure * 0.5);
}

// Pressure Valve (Resilience doctrine)
if (state.reservoir / state.maxCapacity > 0.8 &&
    state.upgrades.doctrine === GW_DATA.doctrines.RESILIENCE &&
    state.upgrades.doctrineUpgrades.includes("PressureValve")) {
  rate *= 1.10; // +10%
}

// Luminous Legacy (permanent)
const luminousLegacy = state.permanentUpgrades.filter(id => id === "LuminousLegacy").length;
rate *= (1 + luminousLegacy * 0.10); // +10% per purchase
```

### 19.2 Capture Rate
```js
let rate = 0;
const threadweaverCount = weftlings.filter(w => w.type === GW_DATA.weftlingTypes.THREADWEAVER).length;
const threadweaverBonus = Math.min(threadweaverCount * 0.10, 0.50); // Cap at +50%

for (const w of weftlings) {
  if (w.type !== GW_DATA.weftlingTypes.DRIFTCATCHER) continue;
  let captureRate = GW_DATA.weftlings.Driftcatcher.baseCaptureRate;
  captureRate *= (1 + threadweaverBonus); // Threadweaver support

  // Doctrine upgrades
  if (state.upgrades.doctrine === GW_DATA.doctrines.CAPTIVATION) {
    const graspingTendrils = state.upgrades.doctrineUpgrades.filter(id => id === "GraspingTendrils").length;
    // GraspingTendrils increases radius, not rate
    if (state.upgrades.doctrineUpgrades.includes("VortexLens")) {
      captureRate *= 1.05; // +5% bonus Glim on capture (handled separately)
    }
  }

  // Steady Hand (permanent)
  const steadyHand = state.permanentUpgrades.filter(id => id === "SteadyHand").length;
  captureRate *= (1 + steadyHand * 0.10); // +10% per purchase

  rate += captureRate;
}

// Weftling Efficiency
const weftlingEfficiency = state.upgrades.global.filter(id => id === "WeftlingEfficiency").length;
rate *= (1 + weftlingEfficiency * 0.10);
```

### 19.3 Pressure
```js
function getPressure(state) {
  if (state.phase < 2) return 0;
  const threshold = GW_DATA.phaseConstants[state.phase].pressureThreshold;
  return Math.min(1, state.motes.length / threshold);
}
```

### 19.4 Fade Time
```js
function computeFadeTime(state, x, y) {
  let fadeTime = GW_DATA.constants.baseFadeTime;

  // Loomguard (support radius)
  for (const w of state.weftlings) {
    if (w.type !== GW_DATA.weftlingTypes.LOOMGUARD) continue;
    if (GW.Utils.distance(w.x, w.y, x, y) <= GW_DATA.weftlings.Loomguard.supportRadius) {
      fadeTime *= (1 + GW_DATA.weftlings.Loomguard.baseFadeExtension);
    }
  }

  // Drift Reduction (global upgrade)
  const driftReduction = state.upgrades.global.filter(id => id === "DriftReduction").length;
  fadeTime *= Math.pow(1 - 0.15, driftReduction); // -15% each, multiplicative

  // Enduring Glow (doctrine)
  if (state.upgrades.doctrine === GW_DATA.doctrines.RESILIENCE &&
      state.upgrades.doctrineUpgrades.includes("EnduringGlow")) {
    fadeTime *= 2; // +100%
  }

  // Sustained Flow (doctrine)
  if (state.upgrades.doctrine === GW_DATA.doctrines.RESILIENCE &&
      state.upgrades.doctrineUpgrades.includes("SustainedFlow") &&
      state.reservoir / state.maxCapacity > 0.5) {
    fadeTime *= 0.75; // -25%
  }

  // Eternal Glow (permanent)
  if (state.permanentUpgrades.includes("EternalGlow")) {
    fadeTime *= 1.5; // +50%
  }

  // Phase 3+ fade acceleration
  if (state.phase >= 3) {
    const pressure = GW.Simulation.getPressure(state);
    fadeTime *= (1 - pressure * GW_DATA.phaseConstants[state.phase].fadeAccelerationFactor);
  }

  // Everflow Matrix (doctrine): Produced Glim never fades
  if (state.upgrades.doctrine === GW_DATA.doctrines.LUMINANCE &&
      state.upgrades.doctrineUpgrades.includes("EverflowMatrix")) {
    fadeTime = Infinity;
  }

  // Irradiance (Phase 4): fade 3× faster
  if (state.phase === 4) {
    fadeTime /= 3;
  }

  return fadeTime;
}
```

---
---
**Document Version:** 1.0  
**Last Updated:** 2026-07-18  
**Status:** Implementation-ready  
**Author:** Mistral Vibe (Architect)  
**Generated by Mistral Vibe.**  
**Co-Authored-By: Mistral Vibe <vibe@mistral.ai>**
