Implement `src/state.js` for Glimweave from the supplied state contract, real utilities,
and runtime data. Return complete classic JavaScript only, without Markdown or commentary.

Implement every `GW.State` public API and the exact runtime/persistent schemas. Include:
- valid fresh-state construction with all five Weftling counts, upgrades, doctrines,
  phases, transient motes, tutorial, settings, prestige, statistics, and timestamps;
- rigorous invariant validation that accepts every legitimate playing/victory state;
- serialization, deserialization, versioned migration, corrupted-save fallback, save,
  load, clear, and capped offline elapsed-time calculation;
- localStorage key and version exactly as defined by the architecture;
- deterministic reset-for-Retuning that preserves only explicitly permanent fields;
- deep-copy/snapshot behavior that cannot leak mutable state;
- safe handling when localStorage is unavailable under file://.

Use the shared `window.GW` namespace non-destructively. State owns no DOM, render loop,
simulation timers, or gameplay formulas assigned to Simulation. No TODOs or placeholders.
