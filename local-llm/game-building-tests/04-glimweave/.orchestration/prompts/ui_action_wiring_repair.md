Fix exactly one defect in `game-building-tests/04-glimweave/src/ui.js`: production UI
actions are dispatched through the private `actionHandler`, but `UI.init` never installs a
handler. This localized task explicitly overrides the default end-to-end read requirement:
use `read_file` once with an offset/limit covering approximately lines 1250-1320, then use
`edit` on the next turn. Do not read the rest of this 1500-line file.

Install one production handler after state has loaded/been created and before gameplay
loops begin. It must call the existing `Simulation.handleAction(state, action)` exactly
once. That API mutates `state` in place and may return a non-state result for Retuning, so
do not replace `state` from its return value. After every successful action, persist the
mutated state and update the visible UI. Turn rejected actions into concise accessible
player feedback rather than uncaught errors. A draft handler may already be present from a
stopped run; correct it rather than duplicating it. Do not create a parallel action system,
test hook, starting-resource grant, or unrelated layout change. Preserve keyboard actions,
save/load, Retuning, and the existing public `UI.onAction` API. Avoid double registration
across repeated initialization.

After editing, inspect the changed region and run a JavaScript syntax check if available.
Return only a short Markdown report with the exact change and verification result. Do not
commit and do not read unrelated files.
