# Auditable Mistral Task Graph

Every numbered generation node is one operating-system process and exactly one local
Mistral inference request. Each produces a durable artifact and a run record under
`.orchestration/runs/` containing timestamps, input hashes, output hash, byte count, and
reported token usage.

1. `world` → `data/world.json`
2. `economy` → `data/economy.json`
3. `technology` → `data/technology.json`
4. `events` → `data/events.json`
5. `copy` → `data/copy.json`
6. Deterministic schema validation and `data/content.js` assembly
7. `state_module` → `src/state.js`
8. `engine_module` → `src/engine.js`
9. `ui_module` → `src/ui.js`
10. `visual_system` → `styles.css`
11. Deterministic HTML and browser smoke-test assembly
12. Targeted repair jobs, only if a browser failure maps to a generated module
13. `documentation` → `README.md`, after the implementation passes

Data jobs may run independently. Code jobs consume the project contract, schemas, and
integrated content. The UI job additionally consumes the state and engine APIs.
