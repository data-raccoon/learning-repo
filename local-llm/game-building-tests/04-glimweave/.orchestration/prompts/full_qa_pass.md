You are the independent release QA auditor for Glimweave. Perform a full, adversarial QA
pass and write `docs/FULL_QA_REPORT.md`.

Return ONLY the Markdown report. Do not modify code. Do not propose code snippets or
return replacement files. Do not trust prior PASS labels, README claims, model-owned test
helpers, or direct state-fixture progression as evidence of a playable product.

Authority and evidence rules:

1. The attached full-resolution `first-run-1440x900.png` and `FIRST_RUN_EVIDENCE.md`
   are externally captured clean-profile browser evidence and outrank generated tests.
2. Production source is authoritative for tracing likely causes and additional defects.
3. Clearly label each statement OBSERVED, SOURCE-CONFIRMED, INFERRED, or UNTESTED.
4. Inspect the attached PNG directly at full resolution. Distinguish what is visible in
   the screenshot from behavior that requires interaction or runtime instrumentation.
5. A populated DOM, nonzero canvas attribute, or passing helper scenario is not proof of
   usability, visibility, wiring, or reachability.

Audit all of these areas:

- clean first boot with empty storage;
- initialization order and action-handler wiring;
- first actionable step and economy bootstrap (no test funding);
- real public path through first producer, mote, capture, purchase, phase, doctrine,
  Retuning, persistence, reset, and victory prerequisites;
- canvas initialization, CSS/backing dimensions, render loop, z-index, occlusion, and
  whether a distinct play area is reserved;
- desktop 1440×900 and narrow/mobile layout risks;
- enabled/disabled button truthfulness and feedback for unavailable actions;
- tutorial/onboarding ability to explain and enable the first meaningful action;
- save/load/offline/reset behavior through production APIs;
- keyboard navigation, focus, semantic controls, reduced motion, and live announcements;
- runtime/console error capture and whether current smoke coverage could falsely pass;
- performance risks from 100 ms simulation updates, full UI rebuilds, render loop, mote
  cap, and long catalogues;
- contradictions between data, state, simulation, renderer, integration, and UI.

Known report that MUST be reproduced as P0 unless source disproves it:

“The game only displays controls with greyed-out buttons and has no game area otherwise.”

Explicit hypotheses to verify rather than merely repeat:

- fresh state is economically soft-locked at zero Glim with no producer;
- `UI.onAction` is never wired, so public control actions are inert;
- UI z-index/layout occludes the canvas and reserves no play-field region;
- renderer backing dimensions use browser defaults instead of the displayed canvas size;
- old smoke tests passed because they bypassed production boot and checked existence, not
  visibility or public reachability.

For every finding provide:

- stable ID and severity: P0 blocker, P1 major, P2 moderate, or P3 minor;
- evidence class and concise evidence;
- exact reproduction steps beginning from empty storage when applicable;
- affected file(s) and line(s);
- user impact;
- failure class/owner (`bootstrap`, `state`, `simulation`, `renderer`, `ui`, `css`,
  `integration`, `data`, or `test-harness`);
- repair direction without implementation;
- a regression acceptance test using production boot and public interfaces.

Then include:

1. **Release verdict**: FAIL, CONDITIONAL, or PASS. Any P0 forces FAIL.
2. **First 15 minutes journey table**: first load, first action, first producer, first
   visible mote, first capture, first purchase, first phase progress. Mark PASS/FAIL/
   UNTESTED and never invent evidence.
3. **Full path checklist**: phase/doctrine/Retuning/persistence/reset/victory,
   desktop/mobile/keyboard/reduced-motion. Mark PASS/FAIL/UNTESTED.
4. **Repair ordering** by dependency. Put bootstrap/action wiring and economic reachability
   before cosmetic polish.
5. **Replacement QA gates** that would have caught the current failure. Include visible
   play-field geometry/occlusion, at least one reachable first action, public action state
   mutation, canvas pixel/checksum change, and a clean-profile journey without direct
   fixture funding.
6. **Evidence gaps** that require a human or a browser automation harness; do not call
   them passed.

Be concise but complete. Prefer ten well-supported findings over speculative volume.
Do not praise the project. The goal is to prevent another false green release.
