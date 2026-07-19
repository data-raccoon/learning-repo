# Game Brief — Glimweave: Living Loom

## Audience and player promise

Living Loom is a 25–40 minute, finite first campaign for players who enjoy compact spatial strategy, incremental optimization, readable systems, and expressive procedural presentation. It upgrades Glimweave without replacing its identity: the Sky Loom produces Glim, Weftlings retrieve it, and success depends on understanding that production and capture are separate problems.

The promise is: **place a tiny luminous workforce directly onto a living field, see why Glim is being caught or lost, and always understand the next meaningful decision on the path to weaving the Dawn.** The canvas is the primary play surface; panels support it rather than compete with it.

## Core loop

1. Observe Glim entering the Loom field, manually catch early motes, and read fading, overflow, and pressure directly from field feedback.
2. Buy a Weftling, preview its position and relevant production, capture, or support range, then confirm a valid placement. Currency is charged once on confirmation and never on preview or cancel.
3. Balance Glim production against retrieval, spend stored Glim on Weftlings and upgrades, and respond to phase pressure.
4. Follow the compact Loom Directive for the current requirement and next unlock: Awakening—“Wake the Loom”; Resonance—“Find the Pattern”; Convergence—“Bind Every Thread”; Radiance—“Weave the Dawn.”
5. Commit to exactly one Refraction doctrine per run, use unlocked active abilities, and experiment with another doctrine after Retuning.
6. Satisfy all five Radiance conditions at once, including holding a genuinely full Reservoir continuously for 60 seconds, to weave the Dawn and record the run.

There is no conventional death state. Poor layouts lose Glim to fading or overflow and increase pressure, slowing progress while leaving recovery possible. Retuning is the deliberate restart loop; victory offers a new run. Both explain what resets and preserve Iridescence, permanent upgrades, preferences, records, and other promised permanent progress.

## Controls and feedback

- Pointer and touch: select visible controls, manually catch motes, preview placement on the field, confirm a valid position, or cancel.
- Keyboard: native Tab/Shift+Tab navigation, Enter/Space activation, Escape to cancel placement or close the top modal, visible focus, and documented shortcuts for every active ability. Keyboard placement exposes an understandable field cursor and moves it without requiring a pointer.
- Placement previews show validity and the selected class’s meaningful radius before commitment. Invalid positions explain why they cannot be used.
- Every player ability is visible when relevant and shows its binding, ready/active/cooldown state, remaining cooldown, and disabled reason. Activation produces field feedback that remains legible with reduced motion enabled.
- Manual capture, automatic capture, fading, overflow, pressure, purchase, placement, phase changes, doctrine commitment, Retuning, and victory each have distinct visual feedback and concise, non-spamming live announcements where state changes matter.
- Procedural audio cues may reinforce these events, but play begins safely without audio, includes a persistent mute control, and never depends on audio alone.
- Pause and existing speed controls remain available; hidden-tab behavior prevents accidental time jumps or duplicate simulation work.

## Progression, failure, and restart

The four phases and directive names are fixed:

1. Awakening — “Wake the Loom”
2. Resonance — “Find the Pattern”
3. Convergence — “Bind Every Thread”
4. Radiance — “Weave the Dawn”

The Directive always shows the exact next requirements, current progress, next unlock, Retune eligibility, and—in Radiance or an expandable summary—the five victory requirements. One canonical simulation/state contract determines phases, unlocks, prices, discounts, caps, eligibility, doctrine IDs, action names, Retune rules, and victory; the UI does not reimplement those formulas.

All five Weftling classes must be organically obtainable. The Harmonizer uses one non-circular unlock rule that does not require owning or spending on a Harmonizer. Phase 4 and victory must therefore be reachable from a clean profile through public play.

The first-run tutorial is learn-by-doing. A short dismissible welcome may be modal; later coaching is non-blocking and advances only from verified actions: manually capture a mote, place a producer, observe fading or overflow, place a capturer, and recognize the production-versus-retrieval tension. Closing help does not mark action steps complete, and completed tutorial progress persists.

Retuning resets current Glim, the run’s placed Weftlings, transient upgrades, current phase, per-run doctrine, and other declared transient counters. It preserves Iridescence, permanent upgrades, highest permanent progress promised by the existing contract, preferences, tutorial completion, and run records. A confirmation preview names both lists. New Run after victory follows the same permanence promise and never silently deletes permanent progress.

Each completed run stores a compact recap with at least duration, captured, faded, doctrine, and score. Best score and best completion time are tracked per doctrine. A run without a doctrine records an explicit neutral value rather than an invalid doctrine ID.

## MVP content

- Existing Glimweave identity and deterministic mechanics: Sky Loom, Glim, five Weftling classes, four phases, three mutually exclusive doctrines, eighteen global upgrades, doctrine upgrades, Retuning, Iridescence, and the five-condition victory.
- A dominant, responsive living field with direct placement and class ranges.
- A compact persistent Loom Directive and collapsible or tabbed secondary panels.
- Contextual first-run coaching tied to real player actions.
- Visible active-ability controls and feedback.
- Procedural visual tokens and procedural audio cue definitions with provenance; no downloaded media.
- Versioned local persistence, real export/import, capped offline progress summary, saved accessibility/audio preferences, run recap, and per-doctrine records.
- Deterministic test seams and representative doctrine/public-journey trajectory evidence.
- Direct local `index.html` launch with no network, dependency, package, module loader, or build step.

## Explicit exclusions

Online accounts, multiplayer, monetization, live services, analytics, downloaded media, external fonts, packages, frameworks, build systems, a new engine, broad lore expansion, and new economy layers are excluded. Legacy `data/` is immutable; the approved implementation may move canonical definitions into `config/`. The stale `tools/assemble_runtime.py` is not part of the worker build and must not overwrite the checked-in runtime.

## Risks and assumptions

- Spatial placement can become frustrating on small screens; generous valid areas, clear snap/cursor behavior, cancelability, and 360×640 physical tests are required.
- A richer field can obscure system meaning; shape, contrast, range, and textual state must carry the same information without relying on color or animation.
- A 25–40 minute victory and doctrine parity are balance claims, not unit-test results. They require deterministic trajectories plus timed public play evidence, with observed variance reported rather than hidden.
- Save migration is risky. The new versioned format must define accepted legacy input, reject unknown/corrupt input without damaging the current save, and preserve an existing valid save until import succeeds.
- Procedural audio may be limited by browser autoplay policy; the first user gesture may initialize audio, mute must remain authoritative, and all information must remain available visually and textually.

