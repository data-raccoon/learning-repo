Implement `src/ui.js`, the Glimweave integration and interface layer, against the supplied
UI contract, fixed HTML shell, runtime data, and actual generated modules. Return complete
classic JavaScript only, without Markdown or commentary.

Implement every `GW.UI` public API and the top-level `GW.init()` bootstrap. The UI must:
- create all interface DOM safely inside `#uiRoot` using DOM methods and textContent;
- show stored/loose Glim, production/capture/fade/overflow rates, pressure, capacity,
  phase, unit counts, costs, upgrades, doctrine choice/locking, Retuning, permanent
  upgrades, tutorial, settings, offline report, and victory;
- dispatch only contract-defined Simulation actions and rerender from state snapshots;
- run the fixed-step simulation accumulator and requestAnimationFrame renderer without
  double-starting loops; pause on visibility loss and save at required intervals;
- wire purchase, upgrade, doctrine, Retune, speed, pause, reset, export/import if defined,
  colorblind, sound/motion settings, and keyboard shortcuts;
- bootstrap save loading, migration fallback, capped offline progress, renderer init,
  autosave, unload save, and error recovery;
- expose the exact `window.__glimweaveTest` deterministic API from the architecture,
  including safe methods to create fresh state, step time, grant resources, purchase,
  select doctrine, Retune, save/load round-trip, force phases, and reach victory;
- update `#announcer`, focus, disabled states, progress semantics, and tooltips accessibly;
- remain usable at 360px and with reduced motion.

Do not duplicate simulation formulas, mutate state outside Simulation/State APIs, use
innerHTML with generated content, access network, eval code, or leave TODOs/placeholders.
