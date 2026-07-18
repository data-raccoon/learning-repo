Repair the supplied `src/engine.js` and return the complete replacement JavaScript only.
Browser failure in construction: `TypeError: cannot read properties of undefined
(reading find)`. The integrated data keys are exactly `data.world`, `data.modules`,
`data.technologies`, `data.events`, and `data.copy`.

Use `data.modules.find(...)` for module lookup and `data.technologies.find(...)` for
technology lookup everywhere. Use `data.events` for events. Preserve the non-destructive
`window.OC.Engine = Engine` namespace fix, `.state`, every public method, and all original
simulation rules. Defensively return false for unknown IDs instead of throwing.
No Markdown or commentary.
