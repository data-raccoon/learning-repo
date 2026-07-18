Implement `src/render.js` for Glimweave from the supplied rendering contract and actual
game modules. Return complete classic JavaScript only, without Markdown or commentary.

Implement every `GW.Renderer` public API. The renderer must:
- initialize and resize `#gameCanvas` with device-pixel-ratio caps and 360px support;
- render an original procedural Sky Loom, Reservoir, five visually distinct Weftling
  classes, drifting/captured/fading Glim, pressure, overflow, and four phase identities;
- derive visuals from simulation/state snapshots without mutating gameplay state;
- interpolate fixed-step state for smooth requestAnimationFrame drawing;
- pool/reuse visual objects and obey mote/draw-call/performance caps;
- provide colorblind palettes and non-color status cues;
- implement reduced-motion mode that preserves information while minimizing movement;
- handle pause, victory, focus loss, zero-size canvas, and missing optional data safely;
- expose the contract's debug metrics and deterministic renderer test hooks.

Use Canvas 2D and generated vector geometry only. No DOM outside the owned canvas, image
assets, fonts, network, storage, game-state mutation, timers, eval, TODOs, or placeholders.
