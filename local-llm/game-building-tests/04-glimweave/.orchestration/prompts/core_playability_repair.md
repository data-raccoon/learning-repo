Repair only Glimweave's clean-boot action wiring and opening economy. Work directly in
`game-building-tests/04-glimweave`. This is an implementation task: inspect the named
production files, edit them, and verify the public path. Do not read architecture/design
documents or unrelated source. Do not edit orchestration evidence.

Allowed production scope:

- `bootstrap.js`
- `src/integration.js`
- `src/ui.js`
- `src/state.js`
- `data/game-data.json` only if balance data truly must change

Confirmed failures:

- `UI.onAction` exists but production boot never registers it, so enabled controls are
  inert.
- fresh state starts with zero Reservoir Glim and no Weftlings while the cheapest producer
  costs 60, so there is no public opening action or passive income.
- disabled/enabled presentation does not reliably correspond to a reachable state change.

Implement one coherent opening loop. Preserve the Glimweave IP, Glim, motes, Weftlings,
and the separation between production and capture. Do not introduce shards, a debug grant,
test-only funding, or a second parallel state path. A clean profile must immediately have
an understandable meaningful action or a visible automatic source that reaches the first
producer quickly. Wire each public action exactly once through the existing integration
layer. Preserve save/load, reset, Retuning, phase, doctrine, and victory semantics.

After editing, use repository tools or targeted inspection to prove:

- production boot registers an action handler;
- a clean state reaches the first producer without test fixtures;
- an enabled public control changes production state exactly once;
- invalid/unaffordable actions remain inert and receive truthful feedback;
- syntax and existing deterministic checks covering these modules still pass.

Return only a concise Markdown report of files changed, behavioral decisions, exact tests
run/results, and remaining issues outside this narrow scope. Do not commit.
