# Glimweave: Living Loom — Creative Style Guide

## Creative north star

The Sky Loom is a quiet, dark instrument that becomes visibly alive through play. The field should feel like a piece of night sky under tension: fine woven lines, soft luminous currents, and deliberate knots of light. Its beauty must explain the simulation. Every flourish either reveals production, capture, risk, pressure, progression, or player intent.

The interface follows three rules:

1. **Field first.** The living field owns the largest area and strongest contrast.
2. **Meaning before ornament.** Shape, line style, labels, and patterns communicate state before hue or motion.
3. **Calm until consequential.** Ambient treatment is restrained; placement, loss, phase changes, abilities, Retuning, and victory earn the strongest responses.

All visual and audio material is procedural. No external font, image, audio file, runtime download, package, or network access is required.

## Hierarchy and responsive composition

### Priority order

1. Living field and placement cursor
2. Loom Directive: phase, requirement progress, next unlock, Retune state
3. Reservoir, Iridescence, compact actions, active abilities, pause, mute, and settings
4. Weftling shop, upgrades, doctrine, records, and explanatory collections

At desktop size (target 1440×900), the field should occupy at least 60% of the main content width and visually dominate through scale, open space, and luminous events. The Directive remains a compact persistent card beside or above it. Secondary collections live in tabs or collapsible trays.

At 360×640, use one column with a sticky compact resource/action strip, the Directive immediately before the field, and a field no shorter than 300 CSS pixels when placement is active. Confirm and Cancel form a reachable sticky placement bar. Secondary content collapses below the field. The document must never scroll horizontally. Interactive targets are at least 44×44 CSS pixels with 8 CSS pixels of separation where practical.

The viewport, not a fixed pixel layout, determines field bounds. Canvas backing dimensions follow device pixel ratio while all layout, pointer conversion, ranges, and hit testing remain in CSS coordinates.

## Visual language

### Palette roles

`assets/visual-tokens.json` is the canonical creative token source. Runtime code selects one of the exact appearance mode IDs: `default`, `high-contrast`, `deuteranopia`, or `protanopia`. It must apply the selected mode to both Canvas and DOM.

- **Void / surface:** near-black blue backgrounds separate play space from supporting panels.
- **Thread / boundary:** cool, low-energy lines describe geometry without competing with entities.
- **Glim:** the brightest small object, drawn as a diamond with a solid center and halo.
- **Production:** a four-ray star and solid radius line.
- **Capture:** an open crescent and dashed radius line.
- **Support:** a hex-knot and alternating dash-dot radius line.
- **Guard:** a shield and double-ring boundary.
- **Warning:** a downward triangle, diagonal hatch, and text label—never color alone.
- **Valid placement:** a solid ring, center check, and `VALID` label.
- **Invalid placement:** a crossed ring, diagonal hatch, and concise reason.
- **Focus:** a thick outer keyline with a contrasting offset gap.

The default palette uses aurora cyan, mint, violet, amber, and coral over an ink background. High contrast removes translucent ambiguity and uses near-black, white, cyan, yellow, and magenta with thicker strokes. Deuteranopia and protanopia variants move success/capture distinctions to blue, gold, and violet while retaining all shape and pattern codes.

### Typography

Use the system stack declared in the visual tokens; never fetch a web font. Display text uses the same family with stronger weight and slightly expanded tracking. Numeric resource values use tabular numerals. Minimum body size is 14px on compact screens and 15px where space permits. Labels do not use all caps except very short state stamps such as `VALID`, `FULL`, or `READY`.

### Layer order on the field

Render in this deterministic order:

1. void fill and subtle static vignette
2. woven grid and phase atmosphere
3. placement exclusions and obstructions
4. unit ranges and ability zones
5. Glim trails and motes
6. placed Weftlings
7. placement preview/cursor
8. event marks and compact labels
9. keyboard focus and modal dimming

Ranges must remain visible over both quiet and 500-mote fields. Give range fills a low opacity, but keep their outlines opaque enough to read. A selected range receives a second contrasting keyline. Do not use blur as the only edge definition.

## Entity and state coding

Glim states combine silhouettes and internal marks:

- **Drifting:** diamond, solid center, short trailing thread.
- **Endangered/fading:** diamond with an hourglass cutout and a three-segment countdown arc.
- **Captured:** collapsing square-knot mark or, in reduced motion, a static square-knot stamp.
- **Overflowed:** diamond over a broken reservoir bar plus `FULL` label.

Weftling classes use stable glyphs independent of mode:

- **Glimspinner:** four-ray star; production range uses a solid line.
- **Driftcatcher:** crescent; capture range uses long dashes.
- **Threadweaver:** crossed shuttle; routing/support range uses dash-dot.
- **Harmonizer:** hexagonal knot; resonance range uses dots plus cardinal ticks.
- **Loomguard:** shield; protection range uses a double outline.

Unit status is expressed by an outer ring: complete ring for operating, segmented ring for cooldown, broken ring plus `!` for disabled, and a crown-like three-knot cap for upgraded. Textual tooltips and accessible labels name the same state.

## Placement and interaction feedback

Buying a class enters preview; it does not place or charge. Preview presents the class glyph, canonical CSS-coordinate position, relevant range, price, and validity.

- Valid: solid outer ring, check mark, class-shaped range, `VALID — Confirm to place`.
- Invalid: crossed outer ring, diagonal hatch, `INVALID — {reason}`.
- Obstructed: invalid treatment plus the obstruction's boundary emphasized.
- Out of bounds: preview clamps visually to the nearest legal field edge while its true cursor remains invalid and the reason says `Outside Loom field`.
- Confirmed: a knot closes around the unit, one short radial response, and a single status announcement.
- Cancelled: preview disappears without spend; no success sound or field burst.

Keyboard placement uses a high-contrast field cursor, an always-visible coordinate/range summary, arrow keys for movement, Enter/Space to confirm, and Escape to cancel. Pointer, touch, and keyboard all dispatch through the same canonical confirmation path.

Distinct event marks persist long enough to read:

| Event | Field response | Static/reduced-motion substitute |
|---|---|---|
| Manual capture | square knot at target plus `+Glim` | knot stamp and label |
| Automatic capture | dashed tether to catcher | tether shown for a fixed, non-animated interval |
| Fade | hourglass closes, broken-thread mark | broken-thread stamp and `FADED` |
| Overflow | reservoir-edge chevrons and broken bar | hatched bar, triangle, and `FULL` |
| Pressure | perimeter tightens and gains ticks | thicker ticked perimeter with numeric pressure |
| Phase transition | aurora band crosses the field | new phase keyline and persistent phase plaque |
| Ability | ability-specific zone and glyph | zone outline, glyph, and remaining duration |
| Retune | threads gather toward the Loom | static concentric weave and reset summary |
| Victory | five threads form a dawn fan | dawn fan, five checks, and victory plaque |

Do not announce or visually stamp every economy tick. Aggregate repeated fade/overflow messages into a short count window.

## Directive, abilities, and progression

The Directive always displays the exact phase names and subtitles:

- Awakening — “Wake the Loom”
- Resonance — “Find the Pattern”
- Convergence — “Bind Every Thread”
- Radiance — “Weave the Dawn”

Use a four-knot phase thread with completed knots filled, the current knot double-outlined, and future knots open. Requirement rows include a glyph, label, exact current/target values, and a real progress element. Do not hide unmet requirements behind hover. The next unlock and Retune eligibility/reason remain visible.

Ability controls display glyph, name, unique binding, and a state word. Ready uses a complete outline; active uses a filled duration track; cooldown uses a segmented numeric/progress track; unavailable uses a broken outline and visible reason. Color is supplementary.

Doctrine commitment uses three visually equal cards. Selection is marked by a physical thread motif and a confirmation summary, not only a colored border. Unselected doctrines become visibly locked after commitment and state why.

## Motion

Motion is brief, interruptible, and never required to decode state. The timing tokens define four durations; simulation time does not depend on these animations. Ambient drift and aurora breathing use small displacement and opacity ranges. Placement confirmation, capture, and warning responses finish within 520ms. Phase and victory moments may last longer but must not block input or state updates.

`prefers-reduced-motion` initializes the preference only when no saved choice exists. With reduced motion enabled:

- disable ambient drift, parallax, particles, shaking, and animated transitions;
- render event stamps immediately and hold them for the tokenized static duration;
- replace moving cooldown sweeps with numeric time and a non-animated progress fill;
- replace phase, Retune, and victory travel with static keylines and plaques;
- keep all simulation, placement, and input behavior unchanged.

## Accessibility

- Every essential distinction uses at least two of: shape, line/pattern, label, position, or color.
- DOM controls use native elements, accessible names, logical order, and the tokenized `:focus-visible` treatment.
- Canvas actions have keyboard-operable equivalents and live textual summaries.
- The polite live region reports threshold crossings and meaningful actions, not continuous values.
- Dialogs have labeled native/modal semantics, trapped focus, Escape behavior appropriate to the top surface, and focus restoration.
- Never place body copy directly on a moving aurora without an opaque surface behind it.
- High-contrast mode disables soft-only shadows and translucency as a meaning carrier.
- Mute is visible, immediate, persistent, and reflected in its accessible name.

Contrast should be physically inspected in every appearance mode; tokens are design inputs, not a claim of audited WCAG compliance.

## Procedural audio language

`assets/audio-cues.json` describes conservative Web Audio recipes. The sound world is glass thread and soft tension: sine/triangle oscillators, very short filtered noise only for warnings, and low master gain. No sample, decoding, file request, continuous drone, or downloaded media is used.

Audio starts muted and no `AudioContext` is created until a user gesture and an explicit unmuted state allow it. Mute stops active cue nodes and prevents future cue creation. Autoplay rejection is silent and leaves visual/text feedback intact.

Semantic families are deliberately distinct:

- purchase/placement: short rising paired thread tones;
- manual/automatic capture: compact bright plucks with different pitch and weight;
- warning/overflow/pressure: low descending or noisy pulses with strict throttles;
- phase: three ascending woven tones;
- ability: a centered shimmer with one cue per accepted activation;
- Retune: descending then resolving interval;
- victory: five-note dawn fan.

The cue definitions include per-cue cooldown and polyphony limits to prevent a 500-mote field from becoming continuous noise. Repeated captures are aggregated; cooldown rejection and ordinary ticks are silent. Sound never carries exclusive information.

## Placeholder and provenance policy

There are no bitmap, vector-file, font, or audio-file placeholders in this Creative package. Shapes, patterns, gradients, oscillator envelopes, and noise buffers are generated at runtime from the checked-in JSON definitions. The asset manifest records each Creative path, author/generator, provenance, license, placeholder status, and intended integration.

If future production replaces a procedural element, it must be added to the manifest before integration with a known author/source, explicit usage license, and a documented no-network loading path. Unknown or search-sourced media is not acceptable.

## Engineering integration notes

- Parse token files once at boot or mirror them into deterministic checked-in configuration if direct `file://` JSON fetch is unavailable; do not add a runtime network request.
- Use exact mode IDs and semantic token keys rather than copying raw colors into UI formulas.
- Canvas patterns should be created procedurally and cached by appearance mode and DPR.
- Audio cue IDs are events, not gameplay actions. Emit them only after canonical state accepts the corresponding action.
- Failure to initialize audio must never interrupt boot, simulation, input, saving, or visual feedback.

