# Experiment 04 — Glimweave

## Goal

Use Mistral Cloud `mistral-medium-3.5` to build and verify an original, ambitious
strategic incremental browser game with a finite campaign and expressive simulation.

## Original IP

**Glimweave** takes place around a living aurora machine called the Sky Loom. Tiny
engineers called **Weftlings** coax luminous motes of possibility—**Glim**—from the Loom.
Loose Glim drifts through the air and fades unless capture units guide it into the
Reservoir. Stored Glim funds new units, Loom structures, and mutually exclusive
Refraction doctrines.

The strategic inspiration is limited to one abstract relationship: producing a resource
and retrieving it are separate optimization problems. Glimweave must not use GNORP
names, characters, prose, art, rocks, shards, mining, exact units, balance, or progression.

## Ambition

- Real-time production, drift, capture, fading, and Reservoir capacity simulation
- A visible field containing many independently moving Glim motes
- Five original Weftling classes with distinct production, transport, and support roles
- At least 18 upgrades across three mutually exclusive Refraction doctrines
- Synergies that support several viable builds rather than one linear upgrade path
- Four Loom phases with new mechanics and a finite “Weave the Dawn” victory
- **Retuning** prestige that resets transient progress and awards permanent Iridescence
- Save/load and capped offline progress
- Pause, simulation-speed controls, compact-number formatting, reduced motion, and
  keyboard-accessible controls
- Original procedural vector/canvas presentation with no external assets

## Technical Shape

- Offline HTML/CSS/classic JavaScript; open `index.html` directly
- Separate state, simulation, rendering, UI, and data modules
- One recorded Vibe process per cloud generation or repair job
- Cloud artifacts written directly to disk; only compact evidence returned externally
- Headless Edge integration tests plus deterministic simulation checks
- Maximum cloud price per job: USD 2.00
- At most two repairs per failure class before an architectural change

## Acceptance Tests

- Production and capture rates are independently measurable.
- Glim can fade or overflow, making retrieval and capacity strategically meaningful.
- Every unit class and representative upgrades cause observable state changes.
- Doctrine choice locks competing branches and materially alters a build.
- Retuning preserves Iridescence while resetting transient factory state.
- Offline progress is capped, applied safely, and explained to the player.
- Save/load round-trips a valid campaign.
- The exposed test API can drive a fresh state through all four phases to victory.
- The interface remains usable at 360 CSS pixels and with reduced motion.
- The final browser suite has no boot, runtime, or contract failures.

## Artifact Ownership

| Artifact | Writer |
| --- | --- |
| `docs/GAME_DESIGN.md`, `docs/ARCHITECTURE.md` | Mistral Cloud architecture run |
| `data/game-data.json` | Mistral Cloud systems-design run |
| `src/state.js` | Mistral Cloud state run |
| `src/simulation.js` | Mistral Cloud simulation run |
| `src/render.js` | Mistral Cloud rendering run |
| `src/ui.js` | Mistral Cloud UI run |
| `styles.css` | Mistral Cloud visual-design run |
| `README.md` | Mistral Cloud documentation run after verification |
| Runner, fixed HTML shell, tests, normalization, provenance | Outer orchestrator |

The user explicitly approved Mistral Cloud usage for this experiment. Credentials remain
outside the repository and are never included in prompts or artifacts.
