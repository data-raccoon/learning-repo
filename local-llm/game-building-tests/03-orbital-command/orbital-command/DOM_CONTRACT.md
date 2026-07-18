# Orbital Command DOM Contract

The fixed `index.html` provides these elements:

- `#turn`, and resource values `#energy`, `#alloys`, `#science`, `#credits`, `#morale`
- lists `#module-list`, `#tech-list`, `#crew-list`, `#mission-list`, and `#event-log`
- buttons `#advance-turn` and `#reset-game`
- modal `#event-modal`, text `#event-title`, `#event-text`, choices `#event-choices`
- banner `#game-banner` and live region `#announcer`

Generated list controls use `data-action` (`build`, `research`, or `crew`) and `data-id`.
Crew controls additionally use `data-delta` with `-1` or `1`.

`src/ui.js` must bootstrap on `DOMContentLoaded`, load state through `OC.loadState`,
construct `new OC.Engine(OC_DATA, state)`, render all regions, save after mutations, and
expose `window.__orbitalTest = { engine, render, newGame }` for browser verification.
