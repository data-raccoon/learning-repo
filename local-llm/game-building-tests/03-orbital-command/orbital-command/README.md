# Orbital Command

**A turn-based space-station management game** where you balance resources, morale, and technology to survive and thrive in the void.

---

## **Overview**
Orbital Command is an offline, turn-based game where you manage **Aurora-9**, humanity’s first orbital outpost. You must construct modules, research technologies, assign crew, resolve events, and meet mission goals—all while avoiding collapse.

The game runs entirely offline, requiring only an HTML file (`index.html`) and no dependencies.

---

## **Objective**
Complete the campaign by:
- Maintaining **energy, morale, and science** above thresholds.
- Unlocking **advanced technologies** to boost production.
- Managing **crew assignments** to maximize efficiency.
- Surviving **random events** (e.g., system failures, morale crises).

**Win:** Reach all mission goals.
**Lose:** Drop below **0 energy or morale** for two turns.

---

## **Resources & Construction**
### **Starting Resources**
- **Energy:** 20
- **Alloys:** 16
- **Science:** 0
- **Credits:** 12
- **Morale:** 70

### **Modules**
Build modules to generate resources, unlock tech, or improve morale. Costs vary by module type.

### **Research**
Unlock technologies to boost production, morale, or unlock new modules.

---

## **Crew Assignment**
Assign crew to roles:
- **Engineering** (maintains systems, repairs)
- **Science** (researches, analyzes data)
- **Operations** (coordinates, manages morale)

---

## **Events**
Random events occur each turn, such as:
- System failures
- Morale drops
- Resource shortages

---

## **Victory/Loss Conditions**
- **Win:** All mission goals (energy ≥ 60, science ≥ 45, morale ≥ 85) are met.
- **Lose:** Energy or morale drops to **0** for two consecutive turns.

---

## **Saving & Resetting**
- **Auto-save:** State persists in `localStorage` under `orbital-command-save-v1`.
- **Reset:** Delete saved data to start fresh.

---

## **How to Launch**
1. Open `index.html` in a browser.
2. No installation or build steps required.

---

## **Project File Map**
```
src/
├── state.js          # State management (serialization, validation)
├── engine.js         # Game rules & state transitions
├── ui.js             # DOM rendering & controls
styles.css           # Visual system
data/
├── world.json        # Campaign world & settings
├── economy.json      # Module costs & production
├── technology.json   # Researchable tech
├── copy.json         # Localized strings
├── content.js        # Deterministically generated from JSON
```

---

## **Orchestration Provenance**
### **Design & Content**
- **Mistral independently authored** all campaign data (`world.json`, `economy.json`, `technology.json`, `copy.json`).
- **Visual system** (`styles.css`) was also authored by Mistral.

### **Engineering & Integration**
- **Original engine (`src/engine.js`)** failed deterministic integration checks due to schema mismatches (e.g., namespace conflicts, incorrect state handling).
- **Three repair runs** were attempted, but integration remained unstable.
- **Final engine** is a deterministic manifest interpreter (not model-authored).
- **State & UI adapters** were added to resolve binding issues, mutated DOM, and incorrect data paths.
- **All generated code (state/engine/UI)** failed integration checks and was replaced with deterministic adapters.
- **Integration decisions** preserved in `.orchestration/INTEGRATION_DECISIONS.md`.

### **Runtime Notes**
- **No runtime files were fully model-authored**—only deterministic adapters remain.
- **All authored modules** share the `window.OC` namespace.
- **Declarative content** (`window.OC_DATA`) is loaded first via `data/content.js`.

---
