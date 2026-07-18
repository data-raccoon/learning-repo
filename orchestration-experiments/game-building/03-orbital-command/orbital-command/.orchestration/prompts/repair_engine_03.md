Repair the supplied `src/engine.js` and return the complete replacement JavaScript only.
Current browser failures: no starting module is considered affordable; construction does
not add a module; research throws while reading `.find` from undefined.

Use these exact interfaces everywhere:
- `state.modules` is an array of module ID strings.
- `state.completedTech` is an array of technology ID strings.
- `state.activeResearch` is null or one technology ID; `state.researchProgress` is numeric.
- Module definitions are `data.modules`; cost has `alloys` and `credits`; production has
  energy, alloys, science, credits, morale; prerequisite field is `required_tech`.
- Technology definitions are `data.technologies`; prerequisite field is `prerequisite`.

`canBuild` must find the definition, check `required_tech` against completedTech, and
compare only each listed cost key to `state.resources[key]`. `build` deducts those keys and
pushes the ID string. `canResearch` must not access `state.technologies`; it checks the
definition, completedTech, activeResearch, prerequisite, and available science if needed.
`research` sets activeResearch and progress. Production maps each stored module ID back
through `data.modules.find`. Technology completion pushes its ID into completedTech.
Preserve the namespace fix, `.state`, events, crew rules, victory/loss, and public API.
Unknown IDs return false. No Markdown or commentary.
