## Sky Loom Priming - Opening Economy Repair

**Opening values chosen:** Starting reservoir = 135 Glim, base capacity = 150

**Files changed:**
- `game-building-tests/04-glimweave/data/game-data.json`: baseReservoirCapacity 100 → 150
- `game-building-tests/04-glimweave/src/state.js`: create() reservoir 0→135, totalGlimCaptured 0→135; resetForRetuning() reservoir 0→135

**Verification:**
- JSON: valid
- State validation: reservoir (135) ≤ maxCapacity (150), totalGlimCaptured (135) ≥ reservoir (135) ✓
- Purchase check: Glimspinner (60) + Driftcatcher (75) = 135 ≤ starting reservoir ✓
- Post-Retuning: reservoir=135, totalGlimCaptured preserved ≥135, iridescence calculation unchanged (totalGlimCapturedThisRun starts at 0)

**Remaining UI-copy work:** Update any tutorial/tooltip text referencing the starting 0 Glim to reflect the new 135 Glim opening endowment.
