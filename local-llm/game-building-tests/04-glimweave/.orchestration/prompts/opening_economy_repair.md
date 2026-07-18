Repair Glimweave's clean-profile and post-Retuning economic softlock. Work only in:

- `game-building-tests/04-glimweave/src/state.js`
- `game-building-tests/04-glimweave/data/game-data.json`

This localized task overrides end-to-end reading: inspect the initial-state and
`resetForRetuning` regions around the `reservoir` fields in `state.js`, plus only the
Glimspinner and Driftcatcher definitions in the JSON. Then edit on following turns.

Current fresh and Retuned runs start at zero Glim with zero Weftlings. A Glimspinner costs
60 and a Driftcatcher costs 75. Production creates loose motes while capture stores them,
so the opening must make both roles reachable without test fixtures, debug grants, long
idle waiting, or violating the base Reservoir capacity.

Design a deliberate "Sky Loom priming" opening endowment and, if needed, rebalance only
the first producer/capturer costs so a player can buy both roles in an understandable short
opening. Keep the resource named Glim; do not add shards. Maintain state validation,
including total-captured counters relative to Reservoir value. Apply the same viable
opening after Retuning while preserving Iridescence, permanent upgrades, and cumulative
campaign totals. Do not add a second economy path or alter later units/upgrades.

Verify JSON parsing and JavaScript syntax if runtimes are available, and inspect the exact
changed regions. Return only a concise Markdown report with the chosen opening values,
files changed, tests/results, and remaining UI-copy work. Do not commit.
