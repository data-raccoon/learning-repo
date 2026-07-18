# Strong-Model Takeover Prompt

You are the senior diagnosis and implementation owner for the remaining Glimweave release
blockers. Work directly in `04-glimweave`.

Start from `.orchestration/REPAIR_HANDOFF.md` and the current working tree. Independently
diagnose these externally reproduced gates:

`RESERVOIR_AFTER_DRIFTCATCHER_55_ACTION_MESSAGE_TUTORIAL_STEP_0`,
`ANNOUNCER_REJECTED_ACTION`, and `CANVAS_PIXEL_CHANGED`.

Do not inherit a proposed patch. Trace each assertion through the public browser action,
production state transition, UI feedback, tutorial update, and renderer. Decide whether the
failures share a cause before editing. Existing changes belong to the experiment; preserve
them and avoid wholesale rewrites.

Constraints:

- Do not weaken the independent verifier or change an assertion merely to get green.
- Fix production behavior, unless evidence proves the test contradicts the product contract.
- Keep the game offline, dependency-free, directly runnable from `index.html`, and multi-file.
- Preserve one authoritative runtime and avoid duplicated state or data ownership.
- Make the smallest coherent correction and inspect every changed region.

Verification:

Run `tools/verify_glimweave.py --json` in an unrestricted environment. A successful repair
requires exact external `PASS`, not a prose claim. Save the final causal explanation,
changed files, exact result, and remaining uncertainty in `.orchestration/REPAIR_STATE.md`
and `.orchestration/REPAIR_HANDOFF.md`.
