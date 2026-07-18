Implement `src/simulation.js`, the authoritative Glimweave game engine, from the supplied
simulation contract, runtime data, utilities, and state module. Return complete classic
JavaScript only, without Markdown or commentary.

Implement every `GW.Simulation` public API and all specified action types. The module must:
- run a deterministic fixed 100 ms step using the seeded RNG and caller-owned state;
- model Glim production, individual pooled motes, drift, capture, fading, overflow,
  Reservoir capacity, Loom pressure, and phase-specific mechanics;
- implement all five Weftling class effects, purchases, scaled costs, 18+ global upgrades,
  doctrine selection/locking and doctrine upgrades, permanent upgrades, and prerequisites;
- calculate rates and derived values from data rather than hard-coded duplicate balance;
- implement phase transitions, tutorial triggers, achievements if present, Retuning with
  Iridescence award, permanent progression, and “Weave the Dawn” victory;
- support exact deterministic aggregate offline progress capped by the state/data contract;
- expose action dispatch, selectors, snapshots, rate calculations, debug/test hooks, and
  error results exactly as specified;
- keep all state mutations inside Simulation and preserve State invariants after actions;
- cap mote arrays and numeric values according to performance and safety limits.

No DOM, canvas, storage, requestAnimationFrame, setInterval, network, eval, TODOs, or
placeholder branches. Unknown actions and IDs must fail without partial mutation.
