Create the complete contents of `src/smoke-scenarios.js`, a smoke-only scenario layer for Glimweave.

Return ONLY plain JavaScript, no Markdown or commentary. Keep it concise (target under 250 lines), ES5-compatible, dependency-free, and isolated in an IIFE.

Runtime context:

- This file loads only after the Mistral-authored simulation test API has been restored to `window.__glimweaveTest`.
- It must immediately return unless the URL query contains `smoke` and the test API exists.
- Preserve every existing helper on that API.
- Replace the eleven `test*` scenario functions called by the attached `smoke.js` with contract-valid scenarios: production/capture independence, fade impact, overflow, unit purchase, upgrade purchase, doctrine lock, phase progression, Retuning, victory, offline progress, and save/load.
- Use the existing test API helpers and `window.GW_DATA`; do not change production runtime modules.
- Every state must satisfy `GW.State.validate` before any helper that validates or persists it. Directly seeded reservoir funds require consistent `maxCapacity`, `totalGlimCaptured`, and `totalGlimCapturedThisRun`. Directly seeded Weftlings require the correct unique `ownedClassCount`. Phase/highestPhaseUnlocked, upgrades, and other derived fields must likewise remain consistent.
- Add a small local funding/setup helper if useful. Call `assertStateInvariants` at meaningful setup boundaries so scenarios genuinely test the contracts.
- Scenario methods must return strict booleans and test real behavior, never unconditional success.
- Keep the established purchase action interface indirectly through `test.buyWeftling(state, type, x, y)`.
- Use valid IDs/values from `GW_DATA`, not invented placeholders.
- Do not weaken validation, swallow unexpected exceptions, or redefine normal game rules. The doctrine-lock scenario may catch only the expected rejection of a second doctrine.
- Ensure setup resource amounts do not exceed capacity and purchases have sufficient legal funds.
- For fade behavior, create Glim through actual stepping rather than invalid mote literals.
- For victory, create a fully contract-valid late-game state using valid unique upgrade IDs and all required Weftling classes, then invoke simulation stepping/checking through the test helpers.

The attached current state and simulation modules are authoritative. The current built-in scenario implementations near the bottom of simulation.js are examples of intent but contain invalid direct setup; do not copy those mistakes.
