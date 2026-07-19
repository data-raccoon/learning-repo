# Acceptance Contract — Glimweave: Living Loom

Release requires all automated gates to pass and all physical, visual, and timed evidence below to be recorded. Test-only state mutation may prepare isolated deterministic cases, but it cannot substitute for the clean-profile public journey, native-input checks, or balance trajectories.

## Public player journeys

### Clean-profile learn-by-doing journey

From cleared game storage, launch `index.html` directly with networking unavailable at 360×640 and again at desktop size. Using only visible controls and physical input:

1. Dismiss the welcome without completing any action-gated tutorial step.
2. Manually catch a real mote and observe a distinct field response, a correct capacity-aware Reservoir change, and contextual coaching advancement.
3. Earn enough Glim, buy a Glimspinner, preview its meaningful placement information, place it on a valid field coordinate, and observe exactly one charge and one placed producer.
4. Observe a real fade or overflow event and its explanation.
5. Buy and place a Driftcatcher, observe its capture range and an automatic capture, and see the production-versus-retrieval lesson complete from those real events.
6. Read a persistent directive that names the current phase, exact remaining requirement(s), progress, and next unlock.

Record input type, viewport, elapsed time, screenshots before and after each placement, and the final directive. Perform the journey with a mouse and separately with native keyboard controls; perform placement, confirm, cancel, and manual capture with touch emulation or a touch device. No console API or test bridge may advance it.

### Full progression and restart journey

Public or accelerated-but-canonical play must demonstrate organic acquisition of Glimspinner, Driftcatcher, Threadweaver, Harmonizer, and Loomguard; all four named directives; a doctrine commitment; an active ability; Retune preview/confirmation; and all five simultaneous victory conditions. The Harmonizer must unlock without already owning or spending on a Harmonizer. The victory panel shows the five satisfied conditions, final score, and recap. Starting a new run preserves Iridescence, permanent upgrades, settings, tutorial completion, recap/history, and per-doctrine records while clearing the per-run doctrine and transient run state.

### Doctrine and pacing journeys

Run representative deterministic trajectories for Luminance, Captivation, and Resilience, plus a public first 10–15 minute clean-profile journey. Record seed, actions, elapsed simulated/real time, phase times, produced/captured/faded/overflowed totals, doctrine, Retunes, victory time, and score. Evidence must support or candidly reject a 25–40 minute first victory target and report fastest-versus-slowest doctrine completion-time variance. Unit tests alone cannot support a balance or fun claim.

## Boot and runtime correctness

- Opening `index.html` from the filesystem starts a playable game without a server, build step, install, dependency, module loader, downloaded resource, or network request. Existing root runtime files load in deterministic order and produce no uncaught boot/runtime errors.
- The field remains the dominant interactive surface at 1440×900 and usable at 360×640. Secondary controls collapse or tab without hiding essential directive, resource, placement, ability, pause, mute, or settings access.
- The simulation uses deterministic fixed-step seams for verification. Renderer timing cannot change economy results. Pausing halts simulation; speed controls apply once; victory freezes gameplay except explicitly safe settings/new-run actions.
- The checked-in runtime is the verified runtime. `tools/assemble_runtime.py` is not run by the build or verifier and does not overwrite approved artifacts.

## Input and physical interaction

- Buying any Weftling starts placement rather than immediately creating it. Pointer, touch, and keyboard can preview and change the coordinate, see class-relevant ranges and validity, confirm, and cancel.
- Preview and cancel spend zero. One valid confirmation creates exactly one entity at the previewed canonical field coordinate and charges the canonical displayed price exactly once. Invalid, out-of-bounds, obstructed, repeated, pointer-plus-key, and double-click/double-tap confirmations cannot charge or dispatch twice and expose a concise disabled reason.
- Manual capture targets the intended live mote, respects current Reservoir capacity, reports overflow correctly, cannot recapture a removed mote, and works at device pixel ratios 1 and 2 without coordinate drift.
- Native keyboard interaction uses normal focus order and control activation; no synthetic click-only shortcut is accepted as keyboard evidence. Escape cancels placement and closes only the top dismissible surface. Modal actions dispatch once.
- Every implemented active ability has a visible control, documented unique binding, availability prerequisite, disabled reason, activation/active feedback, and numeric or progress cooldown. Holding or combining input cannot activate twice. Deterministic tests cover activation, effect duration, cooldown rejection, and reactivation when ready.
- Manual capture, automatic capture, fading, overflow, pressure, purchase/placement, phase transition, doctrine commitment, Retuning, and victory each produce observable, distinguishable feedback. Reduced motion substitutes a static pulse, outline, label, or other non-motion field response.

## State, progression, failure, and restart

- One canonical simulation/state API owns and exposes displayed and charged Weftling and upgrade prices, all discounts/scaling/caps, unlock conditions, purchase eligibility and reasons, doctrine identifiers/lock, action names, phase requirements, ability readiness, Retune requirements/reward/reset preview, and victory progress. UI modules consume these results and contain no competing formulas.
- The eighteen global upgrades and all retained doctrine/permanent upgrades obey canonical caps, prerequisites, discounts, and mutual-exclusion rules. The shown cost equals the deducted amount for every purchase case, including permanent discounts.
- Every declared global upgrade, doctrine upgrade or active ability, and permanent upgrade must have a deterministic test that activates or purchases it through the canonical API and observes its promised gameplay effect at the relevant boundary; testing only price, ownership, or serialization is insufficient. This gate explicitly includes the currently inert identifiers `BasicTraining`, `ReinforcedField`, `MoteLongevity`, `ProductionSurge`, `StabilityMatrix`, `OverflowPrevention`, `PhaseAccelerator`, `WeftlingEndurance`, `OverflowGate`, `WeftlingMemory`, and `DawnsPromise`. Before approval, each declared item must either pass an observable-effect test or be removed from canonical configuration and all player-facing surfaces, or be explicitly labeled non-functional in both configuration and UI so it cannot be bought, activated, or counted toward progression or victory. Silent inert purchases and abilities are release blockers.
- Harmonizer has one canonical, non-circular unlock rule shared by UI and simulation. A deterministic clean-state trajectory reaches all five classes, Phase 4, and victory without forbidden mutation. Tests cover each phase boundary immediately below, at, and above its requirements.
- The Loom Directive uses the exact names Awakening—“Wake the Loom,” Resonance—“Find the Pattern,” Convergence—“Bind Every Thread,” and Radiance—“Weave the Dawn.” It always shows current phase, exact next requirements and progress, next unlock, Retune eligibility/reason, and access to all five victory conditions. Values update from canonical state after every relevant action.
- Tutorial progression is contextual: welcome dismissal advances no action milestone; manual capture, producer placement, first fade or overflow observation, capturer placement, and production/retrieval comprehension advance only from their corresponding real events. Closing or reopening help neither fabricates nor loses progress. Tests cover event ordering, repeated events, reload, and skip behavior.
- Victory requires simultaneously: Phase 4; all five classes; at least 10,000 Glim captured this run; at least 12 purchased transient upgrades; and Reservoir exactly full for 60,000 continuous simulation milliseconds. The hold begins only when full, cannot use wall-clock jumps or accumulated prior intervals, remains incomplete at 59,999 ms, completes at 60,000 ms, and resets to zero immediately on any below-full tick before a new uninterrupted hold.
- Retune eligibility, reward, and confirmation preview agree. Retuning clears current Glim/Reservoir, placed Weftlings, transient upgrades, current phase, run counters, victory/hold state, and per-run doctrine; it preserves Iridescence, permanent upgrades, promised highest progress, preferences, tutorial completion, recaps, and doctrine bests. Tests cover each field and multiple Retunes.
- Victory/New Run uses the same permanence contract and cannot silently delete Iridescence or permanent upgrades. Each finished run records duration, captured, faded, doctrine (or explicit neutral value), and score; best score and best time update only when improved and remain partitioned by doctrine.

## Persistence and invalid-state handling

- The canonical save envelope has an explicit version and deterministic serialized state. Exported text is that actual envelope, not placeholder or stale content. Import parses the supplied text, validates schema, enum values, numeric bounds, IDs, and invariants, migrates only explicitly supported legacy version(s), then atomically installs the result.
- Export→clear→import round-trip preserves all contracted gameplay state, coordinates, settings, tutorial progress, cooldown-safe timestamps, Iridescence/permanent progress, run recaps, and doctrine records. The import UI confirms the loaded version and result.
- Empty, malformed, truncated, unknown-version, impossible, and maliciously oversized inputs fail safely with a useful message. They do not execute content, crash, mutate the current in-memory state, or overwrite the last valid local save. The documented legacy policy is either a tested migration for named versions or an explicit safe rejection; silent best-effort parsing is forbidden.
- Autosave/manual save records the timestamp used for offline progress. Load retains that saved timestamp until `offlineMs = nowMs - savedTimestamp` is calculated, rejects negative/non-finite elapsed time, passes milliseconds to the state API, applies the one-hour cap exactly once, applies the 50% offline multiplier once, respects Reservoir capacity, and does not spawn offline motes.
- Deterministic tests cover 0 ms, sub-second time, exact cap, beyond cap, negative time, empty capacity, and near-full capacity. The player sees actual elapsed/capped duration, Glim gained, and any capacity-limited loss; the report appears once per load.
- Reduced-motion, colorblind/high-contrast, and mute preferences persist through autosave, export/import, Retune, and New Run. Canonical stored enum values match renderer input exactly.

## Accessibility and responsive behavior

- All controls have accessible names, native semantics, visible `:focus-visible` treatment, and a logical focus order. Canvas-only actions have equivalent keyboard-operable controls/instructions. No essential information relies only on color, animation, position, hover, or sound.
- Welcome, settings, doctrine, Retune, import, and victory dialogs use correct dialog labeling, trap focus while modal, close appropriately, and restore focus to the invoking control. Non-blocking tutorial coaching never steals field focus.
- A polite live region announces meaningful resource thresholds, placement result/error, tutorial milestones, phase changes, ability readiness, Retune, and victory without announcing every simulation tick or mote.
- At 360×640 CSS pixels, no essential control is clipped or requires horizontal page scrolling; touch targets are at least 44×44 CSS pixels; the field remains large enough to place units; directive, placement confirm/cancel, pause, mute, and ability controls remain reachable. At 1440×900 the field visually dominates and text remains readable.
- `prefers-reduced-motion` initializes the setting unless a saved preference overrides it. Reduced motion stops decorative drift, parallax, particles, and animated transitions without pausing the economy or disabling input; all event feedback has a static alternative.
- Default, high-contrast, and deuteranopia/protanopia modes visibly change the actual canvas and DOM using the canonical enum values. Shape/pattern coding distinguishes drifting, endangered/fading, capture/range, invalid placement, and pressure states. Contrast and focus are inspected in each mode.
- Device-pixel-ratio 1 and 2 render crisply and preserve CSS-to-canvas hit coordinates. Tab hiding pauses or accounts for elapsed time exactly once on resume, avoids giant deltas and duplicate loops, and does not bypass the offline cap.

## Visual and audio evidence

- Creative output is procedural and defined by `assets/visual-tokens.json` and `assets/audio-cues.json`, with provenance documented in `docs/style-guide.md`. No network-fetched or license-unclear media is present.
- Capture desktop 1440×900 and mobile 360×640 evidence for opening play, producer placement preview, capturer placement/range, high pressure/fading/overflow, each phase directive, doctrine commitment, Retune preview, and victory. Capture default, reduced-motion, high-contrast, and deuteranopia/protanopia variants.
- Screenshots must show a legible hierarchy: living field first, Directive second, compact resources/actions next, secondary collections last. Placement validity and ranges remain readable over both quiet and 500-mote fields.
- Procedural audio cues distinguish at least purchase/placement, capture, warning/overflow, phase transition, ability, Retune, and victory without becoming continuous noise. Mute is visible, immediate, persistent, and prevents future cue creation; browser autoplay restrictions produce no error. Audio is supplementary, and QA records either audible physical evidence or deterministic audio-event logs plus a manual listening check.

## Performance and engine-specific gates

- Deterministic tests cover: placement coordinates and spend-once semantics; manual capture/capacity/overflow; contextual tutorial events; every active ability and cooldown; canonical price/discount/cap/unlock/eligibility/action/Retune surfaces; Harmonizer reachability; all phase transitions; the 60-second full-hold boundary and reset; Retune/New Run invariants; save version round-trip/import/corruption/legacy behavior; offline ordering/units/cap; settings-to-renderer enums; hidden-tab behavior; and modal single dispatch.
- At 500 simultaneous motes on the 1440×900 and 360×640 paths, interaction remains responsive, placement previews remain aligned, no entity exceeds the hard cap, and the simulation avoids unbounded allocation or duplicate loops. Record browser, hardware, DPR, median and worst frame time over at least 30 seconds, simulation-step time, and long-task count. Release target: median frame time ≤16.7 ms, 95th percentile ≤33.3 ms, no individual simulation step >50 ms, and no sustained input latency >100 ms.
- Run the independent verifier exactly as `['{python}', 'tools/verify_glimweave.py', '--json']`. It must return exit code 0 and one JSON object with `status: "pass"`, `result: "PASS"`, a present smoke result, no boot error evidence, and paths to retained DOM/stderr/screenshot evidence. Verification exercises checked-in files directly.
- Static inspection confirms no `http:`/`https:` runtime fetch, external resource, package manifest, generated dependency directory, module import, or dynamic remote code path.

## Explicitly untested quality dimensions

Automated evidence cannot prove delight, long-term replayability, musical taste, comfort for every disability, doctrine fairness across the full strategy space, or a population median completion time. The required trajectories and physical playtests provide bounded evidence only. Any unrun browser, device, assistive technology, or doctrine strategy is reported as a limitation rather than implied to pass.
