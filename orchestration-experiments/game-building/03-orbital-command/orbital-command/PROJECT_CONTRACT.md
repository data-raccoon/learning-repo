# Orbital Command — Project Contract

Orbital Command is an offline, turn-based space-station management game. The player
balances energy, alloys, science, credits, and morale while constructing modules,
researching technologies, assigning crew, resolving events, and completing a campaign.

## Runtime contract

- Runs by opening `index.html`; no server, network, package installation, or build step.
- Plain HTML, CSS, and ordered classic JavaScript files.
- All authored modules share the namespace `window.OC`.
- Declarative content is loaded first as `window.OC_DATA` from `data/content.js`.
- State, engine, and UI are separate modules with explicit public APIs.
- State persists in `localStorage` under `orbital-command-save-v1`.
- The interface must remain usable at 360 CSS pixels and support keyboard focus.

## Game loop

Each turn the player may construct modules, start research, or adjust crew assignments,
then advances the cycle. Production and upkeep resolve, active research progresses, an
event may occur, and mission progress is evaluated. The campaign is won by satisfying
all mission goals and lost if morale or energy remains at zero for two consecutive turns.

## Required modules

- `src/state.js`: create, validate, serialize, save, and load state.
- `src/engine.js`: all game rules and state transitions.
- `src/ui.js`: DOM rendering, accessible controls, event log, and bootstrap.
- `styles.css`: responsive visual system.
- `data/*.json`: independently authored design artifacts.
- `data/content.js`: deterministic integration artifact generated from JSON.

## Completion evidence

The integrated game must pass browser tests for boot, construction, resource changes,
research, crew assignment, turn advancement, event resolution, save/load, reset, and
responsive DOM availability. Passing source-pattern checks alone is insufficient.
