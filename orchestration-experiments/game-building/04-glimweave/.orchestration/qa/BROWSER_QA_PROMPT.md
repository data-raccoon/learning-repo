# Glimweave Full Visual and Functional QA

Act as an independent release QA auditor. This upload contains:

- `first-run-1440x900.png`: the ORIGINAL full-resolution clean-profile screenshot. You
  must open and visually inspect it as an image.
- `FIRST_RUN_EVIDENCE.md`: capture conditions and source-correlated observations.
- production HTML, CSS, JavaScript, and game data files.
- the previous smoke harness, included as evidence of what it did and did not test.

Do not edit or rewrite code during this pass. Produce a QA report first. Do not trust the
old PASS result, README claims, model-owned test fixtures, or direct state mutation as
proof of a playable first-run experience.

## Visual inspection is mandatory

Begin the report with `FULL_IMAGE_INSPECTED: YES` and the image's pixel dimensions. If
you cannot actually see the PNG pixels, stop and say so; do not substitute source review.

Describe what occupies the viewport, whether a distinct Sky Loom/play field is visible,
whether controls occlude it, the information hierarchy, disabled-control state, scrolling,
and the apparent first action. Cite concrete regions of the screenshot (top/left/center/
right/below fold).

## Reproduce the user report

Treat this as the primary release-blocking report:

> The game only displays controls with greyed-out buttons, and has no game area otherwise.

Determine from pixels plus source whether the report is reproduced. Prioritize these
hypotheses, but verify them rather than blindly accepting them:

1. A clean state starts with zero Glim and no producer, while the first producer costs 60,
   creating an economic soft lock.
2. UI controls dispatch through `actionHandler`, but no production boot code calls
   `UI.onAction`, making public actions inert even if enabled.
3. The z-index/grid layout puts a full-height control dashboard over the canvas and
   reserves no visible play-field area.
4. The renderer sizes its backing buffer from default canvas attributes rather than the
   displayed CSS dimensions.
5. Old smoke tests passed because they used funded fixtures and checked existence/nonzero
   dimensions rather than visible geometry, pixels, wiring, or first-use reachability.

## Full audit scope

Audit clean boot, initialization and action wiring, first economy step, producer/mote/
capture loop, upgrades, phases, doctrine, Retuning, persistence/offline/reset, canvas and
render loop, desktop and mobile layout, enabled/disabled truthfulness, onboarding,
keyboard/focus/accessibility, reduced motion, runtime errors, and performance risks.

Trace human-reachable production paths only. Generated helpers may explain intent, but
they cannot establish reachability.

## Required finding format

For every finding provide:

- stable ID and P0/P1/P2/P3 severity;
- OBSERVED, SOURCE-CONFIRMED, INFERRED, or UNTESTED evidence class;
- screenshot evidence and/or exact file/line evidence;
- clean reproduction steps;
- user impact and failure owner;
- repair direction without implementation;
- an observable regression test using production boot and public interfaces.

End with:

1. release verdict (any P0 forces FAIL);
2. first-15-minutes journey table marked PASS/FAIL/UNTESTED;
3. full-path checklist for phases, doctrine, Retuning, persistence, reset, victory,
   desktop, mobile, keyboard, and reduced motion;
4. repair order by dependency;
5. replacement QA gates: visible play-field geometry/occlusion, reachable first action,
   public action state mutation, canvas pixel/checksum change, and a clean-profile journey
   without fixture funding;
6. evidence gaps requiring real browser automation or human playtesting.

Prefer a smaller number of fully evidenced findings to generic commentary. Do not praise
the project and do not implement repairs in this pass.
