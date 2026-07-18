Act as the principal browser-game architect for Glimweave. Using the experiment brief
and completed game design, write `docs/ARCHITECTURE.md` as the single source of truth for
implementation contracts.

The game must run offline by opening `index.html`, using classic ordered JavaScript files
and one global namespace `window.GW`; no modules, fetch, server, dependencies, or build.

Specify:
- complete file tree and ordered script loading;
- exact `GW_DATA` JSON schema and validation invariants;
- exact serializable state schema with field names and types;
- public APIs for `GW.State`, `GW.Simulation`, `GW.Renderer`, and `GW.UI`;
- ownership of mutation, rendering, DOM, time, random numbers, save/load, offline progress;
- fixed-step simulation and seeded deterministic RNG design;
- Glim mote representation, pooling, caps, and reduced-motion behavior;
- event/action protocol between UI and simulation;
- persistence versioning and migration/fallback behavior;
- number formatting and time units;
- `window.__glimweaveTest` API with methods that allow deterministic browser tests for
  purchases, unit effects, upgrades, doctrines, phase progression, Retuning, offline
  progress, save/load, and victory;
- error handling, accessibility requirements, and performance budgets;
- at least 24 concrete automated acceptance checks mapped to owning modules.

Choose interfaces that make incompatible state shapes difficult to express. Include
short JavaScript signature examples, but do not implement the game. Resolve any game
design ambiguity explicitly. Return Markdown only, beginning with
`# Glimweave — Architecture Contract`.
