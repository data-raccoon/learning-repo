# Glimweave — Game Design

---

## 1. Core Vision

Glimweave is a **25–40 minute** strategic incremental game about harvesting luminous possibility from the Sky Loom. Players command **Weftlings**—tiny engineers who coax **Glim** (motes of light) from the aurora machine, then race to capture them before they **fade** into nothing. 
Production and retrieval are deliberately separated: you can make Glim faster than you can collect it, forcing constant optimization between generating more and losing less. The game ends in a finite **“Weave the Dawn”** victory after mastering four **Loom phases**, five **Weftling classes**, three **Refraction doctrines**, and a deep **Retuning** prestige system.

---

## 2. First-Completion Arc

| Beat | Target Time | Goal | Pacing Guardrail |
|------|-------------|------|------------------|
| Tutorial Start | 0:00 | First Glim mote appears; player clicks to capture | Must happen within 30 s |
| First Producer | 1:00 | Buy **Glimspinner**; see automatic Glim appear | Cost ≤ 60 Glim |
| Reservoir Pressure | 2:30 | Reservoir hits 80 % capacity; player learns overflow | Capacity starts at 100 |
| Drift Crisis | 4:00 | Uncaptured Glim visibly piles up; player buys **Driftcatcher** | ≥ 20 motes on screen |
| Phase 1 → 2 | 5:00 | Capture 500 total Glim to unlock Phase 2 | Must be reachable in ≤ 8 min |
| Class Unlock | 10:00 | All 5 Weftling classes available | Each gated by Phase + cost |
| Doctrine Choice | 12:00 | Player commits to one of three **Refraction doctrines** | Cannot be undone |
| Phase 3 | 18:00 | Reach Convergence mechanics | Requires class diversity |
| Phase 4 | 22:00 | Final mechanics and victory condition appear | Requires 5,000 captured |
| Weave the Dawn | 25–40:00 | Finite win | Must be possible in < 60 min |

---

## 3. Loom Phases

### Overview
The Sky Loom cycles through four phases. Each phase introduces new mechanics, Weftling classes, and **pressure** rules. Phase transitions are triggered by **cumulative Glim captured** and **class diversity**.

| Phase | Name | Unlock Condition | New Mechanics | Weftling Unlocks |
|-------|------|------------------|---------------|-------------------|
| 1 | **Awakening** | Start | Basic production, fade, capture | Glimspinner (start), Driftcatcher (50 Glim captured) |
| 2 | **Resonance** | 500 Glim captured | **Pressure** (uncaptured Glim slows production), Bottleneck visible | Threadweaver, Harmonizer |
| 3 | **Convergence** | 2,000 Glim captured + 3 classes owned | **Overflow acceleration** (overflow rate scales with pressure), Fade acceleration at high pressure | Loomguard |
| 4 | **Radiance** | 5,000 Glim captured + all 5 classes owned | **Irradiance** (Glim motes spawn with 2× value but fade 3× faster), Victory condition active | – |

> **Pressure Formula** (Phase 2+):
> `pressure = min(1, uncapturedGlimCount / pressureThreshold)`
> `pressureThreshold = 50 + (50 * phase)`
> `productionMultiplier = 1 - (pressure * 0.5)`
> *At 100 pressure in Phase 2, production drops to 75 %.*

> **Overflow Acceleration** (Phase 3+):
> `overflowLoss = capturedGlim * min(1, (uncapturedGlimCount / 100) * 0.5)`
> *At 200 uncaptured, you lose 100 % of captured Glim to overflow.*

> **Fade Acceleration** (Phase 3+):
> `effectiveFadeRate = baseFadeRate * (1 + pressure * 2)`
> *At 100 pressure, fade time halves.*

---

## 4. Weftling Classes

Five classes, each with a unique role. All are purchased with **Glim** from the Reservoir.

| Class | Role | Base Stat | Unlock Condition | Cost | Max Owned | Notes |
|-------|------|-----------|------------------|------|-----------|-------|
| **Glimspinner** | Primary producer | 1 Glim / s | Start | 60 | 50 | Spawns Glim at its position |
| **Driftcatcher** | Primary capturer | 0.5 Glim / s capture radius | Capture 50 Glim | 75 | 50 | Captures drifting Glim in range (radius = 100 px) |
| **Threadweaver** | Support | +10 % production & capture to Weftlings in radius 150 px | Phase 2 | 100 | 25 | Stacks additively up to +50 % |
| **Harmonizer** | Reservoir | +50 base capacity | Phase 2 + 200 Glim spent on capacity | 125 | 20 | Capacity bonus is permanent while owned |
| **Loomguard** | Fade protection | Extends fade timer by 50 % for Glim in radius 120 px | Phase 3 | 150 | 20 | Multiplicative with other fade extensions |

> **Bottleneck Rule**: If total production > total capture capacity for > 10 s continuously, **pressure** increases at 2× rate until equilibrium is restored.

---

## 5. Economy: Production → Drift → Capture → Reservoir

### Glim Lifecycle
1. **Production**: A Glimspinner emits a Glim mote every second.
2. **Drift**: Mote moves in a random direction at **2 px / frame (60 FPS)** for **10 s** (base).
3. **Fade**: If not captured within lifetime, mote disappears.
4. **Capture**: Driftcatchers pull motes within their radius at their capture rate.
5. **Storage**: Captured Glim → Reservoir.

### Reservoir
- **Starting Capacity**: 100 Glim
- **Overflow**: Excess captured Glim is **lost forever**.
- **Spending**: Glim is deducted instantly for purchases.

### Key Rules
- **Fade Time Formula**:
  `fadeTime = baseFadeTime * (1 + sumOfFadeExtensions) * (1 - phase3FadePenalty)`
- **Drift Speed Formula**:
  `driftSpeed = baseDriftSpeed * (1 - magneticSlowdown)` (from doctrine)
- **Capture Formula**:
  `effectiveCapture = driftcatcherRate * (1 + threadweaverBonus) * (1 + doctrineBonus)`
- **Pressure Visualization**: Uncaptured motes turn from **pale blue → yellow → red** as they approach fading, and the background **aurora intensity** scales with `uncapturedGlimCount`.

---

## 6. Upgrades

### Global Upgrades (Always Available)
| Name | Effect | Start Cost | Scaling | Cap |
|------|--------|------------|---------|-----|
| **Weftling Efficiency** | +10 % production & capture | 100 | ×1.5 | +200 % |
| **Reservoir Expansion** | +100 capacity | 200 | ×1.8 | +5,000 |
| **Drift Reduction** | -15 % fade speed (multiplicative) | 150 | ×1.6 | -80 % |
| **Basic Training** | +1 max Weftling slot | 50 | ×1.4 | +50 |
| **Field Amplifier** | +5 % production from all sources | 300 | ×1.7 | +100 % |
| **Reinforced Field** | Pressure effects reduced by 20 % | 400 | ×1.7 | -80 % |
| **Swift Current** | Glim drifts 10 % faster | 200 | ×1.55 | +50 % |

### Doctrine of Luminance (Production-Focused)
| Name | Effect | Start Cost | Scaling | Requires |
|------|--------|------------|---------|----------|
| **Enhanced Spindles** | +20 % Glimspinner production | 250 | ×1.6 | Luminance |
| **Radiant Core** | Every 5 s: 2× production for 1 s | 500 | ×1.7 | Enhanced Spindles |
| **Brilliant Synthesis** | 5 % chance to produce **2 Glim** | 400 | ×1.75 | Luminance |
| **Everflow Matrix** | Produced Glim **never fades** | 1,000 | ×1.8 | Radiant Core |
| **Luminous Surge** | +15 % production for 10 s after phase change | 350 | ×1.65 | Luminance |

### Doctrine of Captivation (Capture-Focused)
| Name | Effect | Start Cost | Scaling | Requires |
|------|--------|------------|---------|----------|
| **Grasping Tendrils** | +30 % capture radius | 300 | ×1.65 | Captivation |
| **Vortex Lens** | Captured Glim gives +5 % bonus Glim | 400 | ×1.7 | Grasping Tendrils |
| **Tethered Flight** | On activation: 2× capture for 5 s (30 s cooldown) | 500 | ×1.7 | Captivation |
| **Omni Directional** | Instantly captures **all Glim in Reservoir radius** on activation (60 s cooldown) | 800 | ×1.8 | Vortex Lens |
| **Magnetic Field** | Glim drifts 20 % slower | 250 | ×1.6 | Captivation |

### Doctrine of Resilience (Sustain-Focused)
| Name | Effect | Start Cost | Scaling | Requires |
|------|--------|------------|---------|----------|
| **Sturdy Reservoir** | +200 capacity | 400 | ×1.7 | Resilience |
| **Enduring Glow** | +100 % fade time | 350 | ×1.65 | Resilience |
| **Pressure Valve** | +10 % production when Reservoir > 80 % | 600 | ×1.7 | Sturdy Reservoir |
| **Unyielding Foundation** | Max capacity +50 % | 1,000 | ×1.8 | Resilience |
| **Sustained Flow** | -25 % fade rate when Reservoir > 50 % | 500 | ×1.65 | Enduring Glow |
| **Overflow Gate** | On overflow: 20 % of excess redirected to **temporary buffer** (decays over 30 s) | 700 | ×1.75 | Pressure Valve |

> **Doctrine Lock Rule**: Selecting any upgrade from a doctrine **permanently locks** the other two doctrines for that run. The choice is visually irreversible (UI grays out other trees).

---
---
## 7. Retuning Prestige

### Overview
**Retuning** resets **transient** progress to gain **Iridescence**, a permanent currency spent on **eternal upgrades**.

### Trigger Conditions
- **Phase 2+** AND **1,000 total Glim captured this run**
- **OR Phase 4 reached**

### Reset Scope
| Reset | Preserved |
|-------|-----------|
| Glim | Iridescence |
| Reservoir level | Permanent upgrades |
| Weftlings | Highest phase unlocked across all runs |
| Transient upgrades | Tutorial completion flags |
| Current phase | Settings (reduced motion, etc.) |

### Iridescence Reward
> `iridescenceGained = floor(totalGlimCapturedThisRun / 200) + 1`
> *Example: 5,000 captured → 25 + 1 = 26 Iridescence.*

### Anti-Grind
- **Minimum Interval**: `300 s * (1 + retuningCount / 10)` (capped at 3,600 s)
- **Diminishing Returns**: After 10 Retunings, Iridescence gain formula becomes:
  `floor(totalGlimCapturedThisRun / (200 * (1 + retuningCount / 20))) + 1`

### Permanent Upgrades (Bought with Iridescence)
| Name | Effect | Cost | Notes |
|------|--------|------|-------|
| **Weftling Memory** | Start with +1 Weftling slot | 1 | Stacks |
| **Reservoir Blueprint** | Start with +100 capacity | 2 | Stacks |
| **Eternal Glow** | Base fade time +50 % | 3 | Multiplicative |
| **Prismatic Core** | All **doctrine upgrade costs -10 %** | 5 | Permanent discount |
| **Dawn’s Promise** | Start with 1 random doctrine upgrade pre-unlocked | 4 | Random each run |
| **Luminous Legacy** | Glimspinners start at +10 % production | 3 | Stacks |
| **Steady Hand** | Capture radius +10 % | 2 | Stacks |
| **Enduring Design** | Pressure effects reduced by 30 % | 4 | Multiplicative with Reinforced Field |

---
---
## 8. Victory: Weave the Dawn

### Requirements (All must be true simultaneously)
1. **Phase 4** reached
2. **All 5 Weftling classes** owned (at least 1 of each)
3. **Reservoir at maximum capacity** for **60 continuous seconds**
4. **10,000 total Glim captured** in the current run
5. **12+ upgrades purchased** (global + doctrine)

### On Victory
- Game state **freezes**
- **"Weave the Dawn"** animation plays (aurora converges into a sunrise)
- **Final score** displayed:
  > `score = floor(totalGlimCaptured * (1 + iridescence / 100) * (1 + doctrineBonus))`
  - Doctrine Bonus: +0 % Luminance, +5 % Captivation, +10 % Resilience
- **Save slot** is marked as **complete**
- Player can **start a new game** (keeps Iridescence & permanent upgrades)

---
---
## 9. Tutorial

### Beats (Automatic, Non-Skippable First Run)
| # | Trigger | Text | Action Required |
|---|---------|------|-----------------|
| 1 | First Glim mote spawns | *"Click the glowing mote to capture it!"* | Click mote |
| 2 | First capture | *"Glim is stored in your Reservoir. Use it to buy units."* | – |
| 3 | Reservoir ≥ 50 % | *"Your Reservoir is filling. Expand it or spend Glim!"* | – |
| 4 | First Glim fades | *"Uncaptured Glim fades. Build capturers!"* | – |
| 5 | Can afford Glimspinner | *"Buy a Glimspinner to produce Glim automatically."* | Purchase |
| 6 | Can afford Driftcatcher | *"Driftcatchers grab drifting Glim before it fades."* | Purchase |
| 7 | Phase 2 reached | *"New challenges! Uncaptured Glim slows production."* | – |
| 8 | First doctrine choice | *"Choose a Refraction doctrine—this cannot be undone!"* | Select |

> **Tutorial State**: Saved per-device via `localStorage`. Skipped on subsequent runs with a **"Skip Tutorial"** button.

---
---
## 10. Pacing & Numbers

### Target Ranges
| Metric | Early Game | Mid Game | Late Game |
|--------|------------|----------|-----------|
| Glim Production | 1–5 / s | 20–50 / s | 100–300 / s |
| Capture Rate | 0.5–5 / s | 10–40 / s | 50–200 / s |
| Reservoir Capacity | 100–300 | 500–2,000 | 5,000–20,000 |
| Visible Glim Motes | 10–50 | 50–200 | 100–500 (capped) |
| Fade Time | 8–12 s | 15–30 s | 20–60 s |
| Phase Duration | 3–5 min | 5–10 min | 10–15 min |

### Offline Progress
- **Max Offline Time Counted**: 3,600 s (1 hour)
- **Production Rate**: 50 % of online rate
- **No New Production**: Existing motes fade normally; no new motes spawn
- **Reservoir Still Applies**: Capped at current max capacity
- **Formula**:
  ```js
  effectiveOfflineSeconds = min(actualOfflineSeconds, 3600);
  glimGained = (productionRate * effectiveOfflineSeconds * 0.5);
  glimGained = min(glimGained, currentMaxCapacity - reservoirAtSave);
  ```

### Save/Load
- **Format**: Gzipped JSON
- **Auto-Save**: Every 30 s OR on tab visibility change
- **Manual Save**: Button in settings menu
- **Fields Saved**:
  ```js
  {
    version: "1.0",
    phase: 2,
    glim: 1234,
    reservoir: 500,
    maxCapacity: 800,
    weftlings: [{ type: "Glimspinner", x: 100, y: 200, level: 1 }, ...],
    upgrades: { global: ["Weftling Efficiency"], doctrine: "Luminance", doctrineUpgrades: ["Enhanced Spindles"] },
    totalGlimCaptured: 9876,
    iridescence: 5,
    permanentUpgrades: ["Weftling Memory"],
    lastUpdate: 1718123456789, // Unix ms
    settings: { reducedMotion: false, ... }
  }
  ```
- **Offline Calculation**:
  ```js
  offlineMs = Date.now() - save.lastUpdate;
  glimGained = computeOfflineGlim(save, offlineMs);
  // Apply and display summary: "You gained X Glim while offline."
  ```

---
---
## 11. Accessibility

| Feature | Implementation |
|---------|----------------|
| **Reduced Motion** | Toggle in settings. When ON: Glim motes are **static circles** (no drift animation), aurora background is static gradient, no particle effects. |
| **Colorblind Modes** | 3 presets: Default (aurora), High Contrast (black background, bright colors), Deuteranopia/Protanopia (shape-coded: circles = drifting, squares = captured, triangles = fading). |
| **Keyboard** | Tab/Shift+Tab to navigate, Enter to select, Escape to close menus. All buttons have `focus-visible` styles. |
| **Screen Reader** | All interactive elements have `aria-label`, `aria-live` for dynamic updates (e.g., "Reservoir: 500 / 800"). |
| **Minimum Viewport** | Fully functional at **360 CSS pixels** width. Layout stacks vertically; non-critical info (stats) collapses into expandable section. |
| **Pause** | Spacebar or **Pause** button. Simulation stops; Glim motes freeze mid-animation. |
| **Speed Controls** | 0.5×, 1×, 2×, 4×. Affects simulation tick rate (not rendering FPS). |

> **Reduced Motion Compliance**: No `@keyframes`, `prefers-reduced-motion: reduce` media query respected, all animations use `animation: none` when toggled.

---
---
## 12. Balancing Invariants

| Invariant | Measurement | Target |
|-----------|-------------|--------|
| **Early Viability** | Time to first Glimspinner | ≤ 2 min |
| **Phase 2 Reachability** | Time to 500 Glim captured | ≤ 8 min |
| **Phase 4 Reachability** | Time to 5,000 Glim captured | ≤ 25 min |
| **Fade Impact** | % of Glim that fades in no-capture test | ≥ 95 % within 15 s |
| **Overflow Impact** | Reservoir fills at least once per phase | Must occur in naive play |
| **Bottleneck Visibility** | Pressure > 50 when production > 1.5× capture | Always true |
| **Doctrine Parity** | Victory time difference between best/worst doctrine | ≤ 15 % |
| **Retuning Value** | Effective production post-Retuning vs pre | ≥ +50 % |
| **First Victory Time** | Median across new players | 30–35 min |
| **Expert Victory Time** | Top 10 % players | ≤ 20 min |

---
---
## 13. Acceptance Scenarios (Measurable)

| # | Scenario | Success Criteria |
|---|----------|------------------|
| 1 | **Production-Capture Independence** | With 10/s production and 5/s capture, Reservoir gains ~50 Glim in 10 s, and ~50 Glim fades. |
| 2 | **Fade Impact** | With 0 capture, 100 produced Glim → 100 % fade within 15 s. |
| 3 | **Overflow Impact** | Capacity=100, Reservoir=100. Capture 50 → Reservoir stays 100, 50 lost. |
| 4 | **Unit Impact** | Adding 1 Driftcatcher (0.5/s) → total capture increases by exactly 0.5/s. |
| 5 | **Doctrine Lock** | Choose Luminance → Captivation/Resilience upgrades are **purchasable: false**. |
| 6 | **Retuning Effect** | Pre-Retuning: Glim=5,000, Iridescence=0. Post-Retuning: Glim=0, Iridescence≥10, permanent upgrades unchanged. |
| 7 | **Offline Cap** | Offline for 7,200 s → only 3,600 s progress counted. |
| 8 | **Save/Load Round-Trip** | Save state A → load state A → all numeric values match exactly. |
| 9 | **Victory Trigger** | Meet all 5 victory conditions → `gameState.victory = true`, simulation halts. |
| 10 | **Accessibility** | Viewport=360px + reducedMotion=ON → no animated elements, all buttons clickable. |
| 11 | **Bottleneck Pressure** | Production=20/s, Capture=10/s → pressure > 0.5 within 5 s. |
| 12 | **Phase Transition** | At 500 captured → phase changes to 2, new mechanics activate. |

---
---
## 14. Player-Facing Explanations

### Glossary (Tooltips)
| Term | Explanation |
|------|-------------|
| **Glim** | Luminous motes of possibility, the raw output of the Sky Loom. |
| **Fade** | Glim motes dissolve after 10 seconds unless captured. |
| **Overflow** | When your Reservoir is full, new Glim is lost forever. |
| **Pressure** | Too many uncaptured motes slow down production. |
| **Bottleneck** | Producing more than you can capture causes Glim to pile up and fade. |
| **Capacity** | How much Glim your Reservoir can hold. |
| **Reservoir** | Stored Glim, used to buy Weftlings and upgrades. |
| **Retuning** | Reset your factory to gain Iridescence, a permanent resource. |
| **Iridescence** | Earned from Retuning; spent on upgrades that persist forever. |
| **Refraction Doctrine** | A philosophy of Glim handling. Choosing one locks the others. |
| **Weave the Dawn** | The ultimate victory: prove mastery of the Sky Loom. |

### UI Tooltips (Examples)
- **Glimspinner**: *"Produces 1 Glim every second. Cost: 60 Glim."*
- **Driftcatcher**: *"Captures drifting Glim within 100 px at 0.5/s. Cost: 75 Glim."*
- **Reservoir Expansion**: *"Increases max capacity by 100. Cost: 200 Glim (×1.8 each purchase)."*
- **Pressure**: *"75 uncaptured Glim (35 % pressure) → Production at 82.5 %."*

---
---
## 15. Implementation Notes for Modules

> *These are **non-binding** guidelines for the engineering team, but included for completeness.*

- **`data/game-data.json`** must contain:
  - All Weftling definitions (stats, costs, unlocks)
  - All upgrade definitions (effects, startCosts, scalings)
  - Doctrine trees and lock rules
  - Phase thresholds and mechanics
- **Simulation**:
  - Tick rate: 60 FPS for rendering, 10 FPS for logic (Glim spawning, fade, capture)
  - Glim motes: Array of `{ x, y, vx, vy, age, value }`
  - Capture: Spatial hash grid for O(1) Driftcatcher lookups
- **Rendering**:
  - Canvas-based; Glim motes = gradient circles with glow
  - Aurora background: Procedural noise + time-based color shifts
  - Reduced motion: Skip all `requestAnimationFrame` updates for Glim positions
- **State**:
  - Serialization must be deterministic (no `Date.now()` in saved data)
  - Offline progress uses saved timestamp

---
**Document Version**: 1.0  
**Last Updated**: 2026-07-18  
**Status**: Implementation-ready
