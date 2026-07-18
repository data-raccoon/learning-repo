Strengthen only `04-glimweave/smoke.js`. Read it once, then edit it on
the next turn. Preserve every existing deterministic check and compact failure-code style.

Replace the weak final UI existence checks with additional clean-profile production gates:

- canvas `getBoundingClientRect()` has meaningful width/height and is displayed;
- at desktop verifier width, `.left-column` and `.right-column` rectangles leave a central
  horizontal gap of at least 300 CSS pixels that overlaps the canvas rectangle;
- initial visible Reservoir parses as 100;
- locate enabled public purchase buttons by accessible label/text for Glimspinner and
  Driftcatcher; click Glimspinner, re-query the rebuilt DOM, verify displayed Reservoir is
  55; click Driftcatcher and verify displayed Reservoir is 0;
- verify visible owned-count/UI evidence shows both purchases succeeded; do not mutate
  state, call `Simulation.handleAction`, or use funded fixtures for these gates;
- compute a lightweight checksum from sampled canvas pixels before the clicks, then after
  a short timeout that permits rendering, and fail if it does not change;
- always finalize `#smoke-result` within 3000ms, including exceptions.

It is acceptable to wrap the UI journey/pixel portion in a nested timeout while the
existing synchronous deterministic checks run first. Ensure only the final callback writes
PASS. Keep ARIA/CSS checks. Do not touch any other file.

After editing, run
`py -3 04-glimweave/tools/verify_glimweave.py` from the workspace if
available. Return only a short Markdown report with gates and exact result. Do not commit.
