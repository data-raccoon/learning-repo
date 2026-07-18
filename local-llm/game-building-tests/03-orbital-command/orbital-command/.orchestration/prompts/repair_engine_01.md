Repair the supplied `src/engine.js` and return the complete replacement JavaScript only.
Integration failure: the module currently replaces the shared namespace with an
assignment equivalent to `window.OC = { Engine: ... }`, which erases state functions
such as `OC.loadState` before UI bootstrap.

Preserve the complete simulation behavior and public Engine API from the original
engine prompt. Initialize non-destructively with `window.OC = window.OC || {}` and assign
the class as `window.OC.Engine = Engine`; never replace the shared object. Ensure the
constructor exposes its mutable state as `.state`. No Markdown or commentary.
