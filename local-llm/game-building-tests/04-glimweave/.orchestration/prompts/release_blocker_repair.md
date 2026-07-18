You are the senior implementation owner for Glimweave. Repair the actual game in
`game-building-tests/04-glimweave` until a clean-profile player can see, understand, and
play it. You have the full-resolution pre-repair screenshot and the independent QA report.

Work directly on the production files and tests. Do not edit the audit report, experiment
brief, orchestration files, or captured evidence. Do not merely describe fixes. Use file
tools to inspect the current on-disk versions before editing them, because they are the
authority. Keep the game offline, dependency-free, and runnable from `index.html`.

Repair in dependency order:

1. Wire the public UI action path to the production action handler. Every enabled button
   must invoke exactly one valid state transition and produce truthful feedback.
2. Remove the clean-profile economic softlock with a deliberate, understandable opening
   loop. A new player must have a meaningful reachable action immediately or a clearly
   visible automatic resource source that reaches the first purchase quickly. Preserve
   the Glimweave IP and Glim/mote terminology; do not introduce shards or clone GNORP.
3. Re-architect the page so a large, distinct animated playfield is unmistakably visible.
   Desktop must reserve meaningful central space for it; narrow/mobile must retain a
   usable playfield and controls without complete occlusion.
4. Make canvas CSS and backing dimensions agree using the displayed size and device pixel
   ratio. Rendering and hit geometry must remain correct after resize.
5. Repair onboarding and disabled-state explanations so the first producer, first mote,
   capture, first purchase, phase progress, doctrine, Retuning, persistence, reset, and
   victory prerequisites form a coherent public path.
6. Replace false-green smoke coverage. Tests must boot the production entry point from
   empty storage and exercise public controls. Add gates for visible/non-occluded playfield
   geometry, a reachable first action, public state mutation, canvas pixel/checksum change,
   and early progression without direct fixture funding. Retain useful deterministic unit
   scenarios, but never use them as proof of first-run playability.
7. Address straightforward P1/P2 findings in the report when safe, including duplicate
   loading, unnecessary full UI rebuild work, hidden-canvas rendering, keyboard focus,
   reduced motion, and accessible live feedback. Do not destabilize core progression for
   speculative optimization.

Acceptance requirements:

- no enabled control is inert;
- a fresh profile is not economically stuck at zero;
- the playfield is visibly distinct at 1440x900 and usable at 360x800;
- at least one visible mote and a changing canvas can be reached through public gameplay;
- reset and reload use production APIs and do not depend on test-only globals;
- existing verification plus the new clean-profile regression checks pass;
- source modules keep clear ownership rather than accumulating a second parallel game;
- no external dependencies, build step, server, or network access are introduced.

Run the strongest relevant verification available from the repository after editing.
Inspect every changed file once more for integration mistakes. Return only a concise
Markdown repair report containing changed files, behavioral changes, tests run with exact
results, and any genuinely unverified browser-only checks. Do not claim visual proof of
the repaired state because the attached screenshot is pre-repair evidence.
