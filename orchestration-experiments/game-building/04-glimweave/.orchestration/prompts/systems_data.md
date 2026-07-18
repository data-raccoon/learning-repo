Act as Glimweave's senior economy and systems designer. Using the supplied game design
and architecture contract, produce the complete runtime data artifact for
`data/game-data.json`.

Requirements:
- follow the architecture's exact `GW_DATA` schema and identifiers;
- include all five Weftling classes, every phase, at least 18 general upgrades, all three
  Refraction doctrines with at least four doctrine upgrades each, permanent Iridescence
  upgrades, tutorial beats, achievements/milestones if specified, and all balance caps;
- use concrete numeric costs, effects, unlock thresholds, scaling factors, visual labels,
  descriptions, and formulas represented as supported data fields—not executable code;
- preserve the 20–40 minute first-completion target and multiple viable builds;
- ensure starting state can buy its first meaningful action quickly;
- ensure every referenced ID exists and prerequisites are acyclic;
- avoid placeholder text, TODOs, comments, trailing commas, NaN, and Infinity.

Return one valid JSON object only, with no Markdown fence or commentary.
