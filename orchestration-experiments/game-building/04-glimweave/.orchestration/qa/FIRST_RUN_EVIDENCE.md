# Clean-Profile First-Run Evidence

## Capture conditions

- Runtime: Microsoft Edge, fresh temporary browser profile and empty local storage.
- Entry: `index.html` directly from the filesystem, with no `?smoke` query.
- Viewport: 1440 × 900 CSS pixels.
- Capture delay: approximately three seconds after navigation.
- Screenshot: `first-run-1440x900.png` in this directory.
- This text is outer-orchestrator evidence. Vibe CLI's `read_file` tool cannot deliver
  binary image pixels, but Vibe Work in the browser can inspect the original PNG upload.

## Human-observed result

- The viewport is almost entirely a control dashboard.
- No distinct Sky Loom or interactive game/play field is visible.
- The top status reads Reservoir `0 / 100`, Production `0.0/s`, Capture `0.0/s`,
  Fade `0.0/s`, and Phase `Awakening (1)`.
- The visible Glimspinner purchase costs 60 Glim and is disabled.
- The visible Driftcatcher purchase costs 75 Glim and is disabled.
- Every visible global-upgrade purchase is disabled.
- Settings controls are visible; they do not provide a way to begin the economy.
- The page is scroll-heavy and the large upgrade catalogue occupies the area where a
  play field would normally be expected.

## Source-correlated observations

These are observations for the auditor to verify, not pre-approved fixes:

1. A fresh state has `reservoir: 0` and an empty `weftlings` array
   (`src/state.js:462`, `src/state.js:466`).
2. The cheapest producer has `baseCost: 60` (`data/game-data.json:74`).
3. The normal simulation loop steps the current state, but no initial producer or passive
   production source is apparent (`src/ui.js:1170–1181`).
4. UI actions call a private `dispatchAction`; it performs work only when
   `actionHandler` has been registered (`src/ui.js:107–110`).
5. `UI.onAction` can register the handler (`src/ui.js:1305–1307`), but a repository-wide
   JavaScript search found no call to `UI.onAction(...)`.
6. The canvas is absolute at z-index 1, while `#uiRoot` is z-index 10 and spans the page
   (`styles.css:150–157`, `styles.css:235–243`). The main control grid uses
   `280px 1fr` (`styles.css:349–353`), reserving no central play-field column.
7. Renderer initialization sizes from the canvas element's width/height attributes
   (`src/render.js:30–35`); the HTML canvas has no explicit dimensions, so browser
   defaults can diverge from its full-screen CSS size.
8. The previous smoke checks only required `#uiRoot` to have children and
   `#gameCanvas.width > 0` (`smoke.js:73–74`). They did not test visibility, occlusion,
   pixel change, an enabled first action, or a public UI-driven state transition.
9. Model-owned smoke scenarios fund states directly and call test helpers, so their unit
   purchase and progression results do not prove that a clean human session can start.

## Required QA interpretation

The user's report is reproduced and is release-blocking. A QA report must not downgrade
it merely because the old smoke suite says PASS. The auditor must find all related and
independent release blockers, distinguish observed facts from source inference, and
propose acceptance tests that use the production boot and public UI/action path.
