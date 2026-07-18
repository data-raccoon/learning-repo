Create the complete contents of a small browser JavaScript file `src/test-bridge.js` for Glimweave.

Return ONLY plain JavaScript, without Markdown fences or commentary. Keep it under 80 lines, ES5-compatible, dependency-free, and wrapped to avoid leaking temporary names.

Context and required architecture:

- `src/simulation.js` installs the authoritative, valid `window.__glimweaveTest` API.
- A later legacy `src/ui.js` accidentally replaces that global with inferior scenario setup code.
- This bridge will be included twice by the deterministic HTML assembler: once immediately after `simulation.js`, and again immediately after `ui.js`.
- On its first execution, preserve the authoritative test API under a clearly named private property on `window.GW`.
- On its second execution, restore the preserved API to `window.__glimweaveTest`.
- Do absolutely nothing unless the page query string contains the `smoke` parameter. The production game must be unaffected.
- Be idempotent and robust if a module is unexpectedly absent. Do not throw during normal production or smoke startup.
- Do not implement or duplicate test scenarios. This is an integration seam only.

The attached smoke harness shows the expected global. Produce the minimal bridge.
