# Game Intent

Project ID: `glimweave`

Describe the desired player, fantasy, genre, target platform, session length, constraints, inspirations, and anything explicitly out of scope.

## Intent

Elevate the existing offline browser game Glimweave into **Living Loom**, a
playfield-first spatial strategy experience that preserves its original identity:
production and retrieval are separate optimization problems around a living aurora
machine. The intended player enjoys compact strategic incremental games, readable
systems, expressive procedural visuals, and a finite 25–40 minute first campaign
with replayable doctrine choices.

This is an upgrade of the checked-in game, not a rewrite and not a new IP. Preserve
the Sky Loom, Glim, Weftlings, the four phases, five classes, three mutually exclusive
Refraction doctrines, eighteen upgrades, Retuning, Iridescence, offline-first classic
HTML/CSS/JavaScript, direct `index.html` launch, procedural rendering, no network,
no dependencies, and deterministic verification seams.

The player promise is: **place a tiny luminous workforce directly onto a living field,
see why Glim is being caught or lost, and always understand the next meaningful
decision on the path to weaving the Dawn.** The canvas should become the dominant
interactive surface instead of a passive backdrop to dense dashboard panels.

### Required product direction

1. Buying a Weftling enters an intentional placement flow on the canvas. Pointer,
   touch, and keyboard users can preview position and relevant ranges, confirm or
   cancel, and spend currency exactly once only after a valid placement.
2. The opening becomes learn-by-doing. A short welcome may be modal, but subsequent
   coaching is non-blocking and advances from real actions: manually capture a mote,
   place a producer, observe fading/overflow, place a capturer, and understand the
   production-versus-retrieval tension. Closing help must not falsely complete steps.
3. Add a persistent, compact Loom Directive surface showing the current phase,
   exact next requirements, progress, next unlock, Retune eligibility, and the five
   final victory conditions. Use these narrative directive names: Awakening—“Wake
   the Loom”; Resonance—“Find the Pattern”; Convergence—“Bind Every Thread”;
   Radiance—“Weave the Dawn.”
4. Surface every implemented player ability with visible cooldown, keyboard binding,
   disabled reason, and reduced-motion-compatible field feedback.
5. Improve game feel for manual capture, automatic capture, fading, overflow,
   pressure, purchase/placement, phase transitions, doctrine commitment, Retuning,
   and victory. Keep all visuals and any audio procedural; include mute and reduced
   motion behavior. Secondary panels may collapse or use tabs so the field remains
   legible at desktop and 360 CSS pixels.
6. Retuning should enable doctrine experimentation on later runs and clearly preview
   what resets and what remains. Victory/new-run actions must honor that promise.
   Record a compact per-run recap (at minimum duration, captured, faded, doctrine,
   score) and best score/time per doctrine if compatible with the approved state
   contract.

### Mandatory integrity repairs

The Director must make these release-blocking defects explicit acceptance items:

- Remove the circular Harmonizer unlock that makes organic acquisition of all five
  classes, Phase 4, and victory unreachable. Use one canonical unlock rule in UI and
  simulation.
- Correct the full-Reservoir victory condition so it requires a genuine continuous
  60-second hold; reset the timer when the reservoir drops below full and test timing.
- Fix exported/imported saves: exported content must be the actual serialized state,
  imported content must be parsed instead of ignored, corrupt input must fail safely,
  and the save format must be versioned with an explicit legacy policy.
- Correct offline progress ordering and units. Preserve the saved timestamp until
  offline elapsed time is calculated, pass milliseconds to the state API, apply the
  cap once, and explain the result to the player.
- Unify displayed and charged Weftling/upgrade prices, discounts, caps, unlocks,
  eligibility, doctrine identifiers, action names, and Retune requirements behind
  canonical simulation/state APIs. Eliminate duplicated UI formulas and prevent
  double-dispatched modal actions.
- Wire colorblind and reduced-motion settings to the renderer using canonical enum
  values. Preserve preferences across saves and ensure all settings visibly work.
- Retuning must reset the per-run doctrine while preserving Iridescence/permanent
  progress. Starting a new run after victory must not silently delete promised
  permanent progress.

### Acceptance and evidence expectations

- A clean-profile physical-interaction journey must demonstrate tutorial dismissal,
  manual mote capture, one producer placement, one capturer placement, and a clearly
  legible next directive without test-only state mutation.
- Deterministic tests must cover placement coordinates and spend-once behavior,
  manual capture and capacity, contextual tutorial progression, ability activation
  and cooldown, canonical pricing/eligibility, Harmonizer reachability, each phase
  transition, genuine 60-second victory hold/reset, Retune invariants, versioned save
  round-trip/import/corruption, offline progress, settings-to-renderer wiring, and
  modal single dispatch.
- Run representative trajectories for all three doctrines and a public first 10–15
  minute journey. Record evidence for the intended 25–40 minute first victory and
  doctrine completion-time variance; do not claim balance from unit tests alone.
- Verify mouse, native keyboard, and touch interaction; focus visibility, modal focus
  trap/restore, live announcements without spam, 360x640 usability, 1440x900 visual
  composition, reduced motion, high contrast/colorblind modes, device-pixel-ratio
  canvas behavior, hidden-tab handling, and a 500-mote performance budget.
- Preserve existing deterministic mechanics and no-network constraints. Do not use
  downloaded media, unclear licenses, frameworks, packages, build systems, or external
  services.

### Ownership and implementation constraints

Use the gaming-agents Director → explicit human hash approval → Creative → Engineering
→ read-only QA workflow. Creative owns only `assets/` and `docs/style-guide.md` and
must document provenance for procedural visual/audio tokens. Engineering owns declared
root runtime files plus modules under `src/`, `tests/`, and `config/`; leave legacy
`data/` immutable unless the approved spec migrates its source of truth into `config/`.
The independent root verifier remains `tools/verify_glimweave.py`. The current
`tools/assemble_runtime.py` is stale and must not overwrite upgraded runtime artifacts
after the build; verification should exercise checked-in files directly or the root
must separately revise that tool outside worker ownership.

Explicitly out of scope: online accounts, multiplayer, monetization, live services,
downloaded assets, broad lore expansion, a new engine, or adding more economy systems
before the existing loop is reachable, legible, and satisfying.

