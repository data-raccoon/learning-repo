Return ONLY the complete corrected `src/smoke-scenarios.js` as plain JavaScript. Preserve everything already working and change only these two browser-smoke defects:

1. Doctrine actions use enum IDs (the keys of `GW_DATA.doctrines`), not display values. In `testDoctrineLock`, call `test.chooseDoctrine` with `'LUMINANCE'`, then attempt `'CAPTIVATION'`. Catch only the expected second-choice rejection and return a strict boolean. The normal UI also sends these keys.
2. The fade scenario currently keeps the Glimspinner active during the long fade step, so newly produced motes replace expired motes and total count does not prove fading. After confirming the initial mote count is positive, remove production for this isolated fixture by setting `state.weftlings = []` and synchronizing `state.ownedClassCount = 0`; validate, then step longer than base fade time and require the remaining mote count to be lower (ideally zero). Do not inject motes or bypass validation.

Keep the file smoke-only, ES5-compatible, concise, and dependency-free. Do not alter any other scenario semantics or production modules. No Markdown or commentary.
