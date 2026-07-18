# Deterministic normalizations

## `src/simulation.js`

The `simulation` cloud run returned a complete JavaScript implementation wrapped in two
prose paragraphs and a Markdown code fence. Integration removed only the leading prose,
opening fence, and closing fence. No JavaScript tokens inside the fenced artifact were
changed. The original cloud output hash remains recorded in
`.orchestration/runs/simulation.json`; the runtime file intentionally differs by this
documented transport normalization.
