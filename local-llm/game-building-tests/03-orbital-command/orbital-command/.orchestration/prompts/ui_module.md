Implement `src/ui.js` against the supplied project, DOM, state, engine, and data contracts.
Return JavaScript only without Markdown fences. Use an IIFE and bootstrap on
DOMContentLoaded. Load state, construct the engine, and render every required region.

Use safe DOM creation and textContent, never innerHTML for generated content. Render:
- resource and turn values;
- one module card with build button per module, disabled via engine.canBuild;
- one technology card with research button, progress/complete state, disabled via
  engine.canResearch;
- each crew role with minus/plus buttons and current assignment;
- mission goals with current/target values;
- newest ten log entries;
- pending event dialog with exactly two choice buttons;
- victory/loss banner and appropriate disabled controls.

Use event delegation for data-action controls. After every successful mutation call
OC.saveState(engine.state), rerender, and update #announcer. Advance and reset buttons
must work. Expose exactly `window.__orbitalTest = { engine, render, newGame }`, where
newGame clears the save, replaces the engine with a fresh state, rerenders, and returns
the new engine. No network, eval, imports, exports, or external dependencies.
