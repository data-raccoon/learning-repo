Repair the supplied `src/state.js` and return the complete replacement JavaScript only.
Bootstrap failure: `ReferenceError: Cannot access 'crew' before initialization` at line
13 inside initial-state creation.

In `createInitialState(data)`, calculate `crewTotal`, engineering, science, operations,
and the final `crew` object in declaration order before constructing or returning the
state object. Do not shadow `crew`, reference it in its own initializer, or place required
declarations after a return. Preserve the exact crew-total invariant, shared namespace,
five public functions, save key, validation, and safe fallback behavior. No Markdown.
