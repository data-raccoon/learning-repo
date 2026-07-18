Create the complete contents of a new small production module `src/integration.js` for Glimweave. Return ONLY plain ES5-compatible JavaScript, no Markdown/commentary. Target under 180 lines, dependency-free, in an IIFE, idempotent.

This module loads after `data`, `state`, and `simulation`, but before UI. It must repair two cross-module integration seams without replacing or duplicating the simulation.

1. Doctrine ID normalization

- `GW_DATA.doctrines` maps stable enum keys (`LUMINANCE`, `CAPTIVATION`, `RESILIENCE`) to stored/display values (`Luminance`, `Captivation`, `Resilience`).
- UI correctly dispatches the stable key, while simulation effects and `doctrineUpgrades` use the display/stored value.
- Add non-enumerable lookup aliases on `GW_DATA.doctrines` for each display value so State validation accepts stored display values without adding duplicate UI entries to `Object.keys`.
- Wrap `GW.Simulation.handleAction`. For `CHOOSE_DOCTRINE`, copy the action and translate a stable key to its display/stored value before delegating to the original handler. Do not mutate the caller's action.
- Existing display values should also work. Invalid values must still be rejected by the original handler.

2. Permanent upgrade routing

- Current UI dispatches `{type:'BUY_UPGRADE', upgradeId:<permanent id>}` for entries in `GW_DATA.permanentUpgrades`, but the simulation global-upgrade handler rejects them.
- In the wrapper, intercept only that exact case when the ID exists in `GW_DATA.permanentUpgrades`.
- Validate state first. Enforce finite sufficient `state.iridescence`, the configured integer cost, and `stackable`; a non-stackable already-owned upgrade must throw. On success subtract cost, append the ID, apply immediate derived effects, validate again, and return state.
- For `ReservoirBlueprint`, recompute its immediate capacity contribution as +100 per owned copy while preserving other existing derived capacity contributions. Do not reduce capacity or allow reservoir > maxCapacity.
- For other permanent upgrades, preserve their existing simulation-based effects.
- Wrap a successful `RETUNE` result as well: since permanent upgrades survive Retuning, ensure every owned ReservoirBlueprint contributes +100 capacity immediately after reset, then validate. Preserve and return the original Retuning result.

Architecture/safety:

- Preserve the original handler for every other action and exception.
- Do not weaken validation, alter prices/data, touch DOM, add globals other than a small `GW.Integration` status/API object, or affect the smoke test bridge.
- Avoid double wrapping; expose `GW.Integration.installed === true`.
- Work with old saves missing optional runtime-only fields.

The attached current state/simulation/data snippets are authoritative enough to reconcile field names. Return the minimal complete module.
