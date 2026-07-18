Repair the supplied `src/state.js` and return the complete replacement JavaScript only.
Browser failure: `OC.loadState is not a function` when `src/ui.js` bootstraps.

Ensure the IIFE initializes the shared global namespace with `window.OC = window.OC || {}`
and assigns all five public functions directly onto that exact object:
`OC.createInitialState`, `OC.validateState`, `OC.saveState`, `OC.loadState`, and
`OC.clearSave`. Preserve every state-shape, validation, persistence-key, and fallback
requirement from the original state-module prompt. Do not use a block-local namespace
that other classic scripts cannot see. No Markdown or commentary.
