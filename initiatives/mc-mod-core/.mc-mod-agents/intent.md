# Mod Intent

Project ID: `mana-core`

Describe the desired player experience and the smallest enjoyable release. Replace every bracketed prompt before packing the Architect task.

## Intent
A foundational magic mod providing mana as a positional resource that flows along gradients, with consumer/producer blocks and entities, and client-side visualization. Designed as a library for other mods to implement specific in-game objects.

## Audience and Session

- Primary audience: Mod developers and technical players
- Multiplayer expectation: both (dedicated server + client)

## Pinned Platform

- Minecraft Java Edition: 26.2
- Loader: Fabric 0.19.3
- Fabric API: 0.154.2+26.2
- Fabric Loom: 1.17-SNAPSHOT
- Gradle: 9.5.1 through the checked-in wrapper
- Java: 25

## Constraints

- Server authoritative for all mana calculations, flow, and storage
- Client provides visualization and example blocks/entities only
- Must start and operate on dedicated server without loading client classes
- Mana represented as values at 3D coordinates
- Flow follows gradient-based movement
- Consumers gather mana in spherical regions (>=1 coordinate radius)
- Creators inject mana in spherical regions (>=1 coordinate radius)
- Entities and blocks can store finite mana amounts
- No external runtime dependencies beyond Fabric API unless the human approves them
- No mixins in v1 unless the architecture explains why a public API is insufficient
- Assets must be original, procedural, or clearly marked placeholders with provenance

## Inspirations

- BuildCraft energy networks (gradient flow)
- Botanica mana systems (positional resource)
- Thermal series RF/ME (producer/consumer patterns)

## Out of Scope for v1

- Complex mana types or colors
- Spell casting system
- Mana network/grid structures
- Configurable flow rates via GUI
- Persistent world mana storage across restarts
- Advanced shaders for mana visualization
- Multi-mod compatibility beyond base API
