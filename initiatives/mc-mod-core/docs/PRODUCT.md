# Mana Core - Product Document

## Audience and Player Promise

**Target Audience:**
- Mod developers creating magic-themed mods
- Technical players building custom magic systems
- Modpack creators integrating magic mechanics

**Player Promise:**
Mana Core provides a foundational positional mana resource system that enables mods to implement magic mechanics with gradient-based mana flow, gathering, and storage. It handles the complex calculations on the server while providing client-side visualization for players and developers to build upon.

## Core Loop

1. **Mana Exists:** Mana values are maintained at every 3D coordinate in the world
2. **Mana Flows:** Mana automatically moves along gradients from high to low concentration
3. **Mana Gathered:** Consumer blocks and entities collect mana from spherical regions around them
4. **Mana Stored:** Collected mana is stored in finite-capacity containers
5. **Mana Used:** Stored mana powers spells, crafting, or other mod-defined effects
6. **Mana Created:** Creator blocks and events inject new mana into the system

## Controls and Feedback

**Controls:**
- Primary input: None (automatic system)
- Configuration: JSON config files for flow rates, sphere radii
- Commands: `/mana debug` - shows mana values at player position

**Feedback:**
- **Visual:** Particle effects showing mana flow direction and intensity
- **Visual:** Color-coded block overlays indicating mana density
- **Text:** Debug output showing numeric mana values
- **Text:** Chat messages for significant mana events (configurable)

## Progression, Failure, and Restart

**Progression:**
- Mod developers integrate Mana Core API into their mods
- Players experience mana mechanics through integrated mods
- System scales with world size and entity count

**Failure:**
- Invalid coordinates or missing world: Logs error, continues operation
- Overflow storage: Mana is discarded with warning
- Negative mana: Clamped to zero with audit log

**Restart/Recovery:**
- Mana state is NOT persisted across world restarts (v1 limitation - see Out of Scope)
- System recalculates from scratch on world load
- Future versions may add persistence

## MVP Content

### Core Features
- Positional mana storage at 3D coordinates (chunk-based sparse storage)
- Gradient-based mana flow calculation on server tick
- Spherical mana gathering for consumers (configurable radius >= 1)
- Spherical mana injection for creators (configurable radius >= 1)
- Finite mana storage for blocks and entities
- Client-side visualization: particle flow indicators
- Client-side visualization: mana density overlay on blocks
- Example consumer block: Mana Collector
- Example creator block: Mana Generator
- Example storage entity: Mana Crystal
- Debug command: `/mana debug`

### Supporting Features
- Server configuration for flow parameters
- Client configuration for visualization options
- API for mods to register custom consumers/creators
- API for mods to query mana at positions
- API for mods to modify mana at positions

## Explicit Exclusions

Features NOT in v1:
- Persistent mana storage across world restarts
- Complex mana types or colors
- Spell casting system
- Mana network/grid structures
- Configurable flow rates via in-game GUI
- Advanced shaders for mana visualization
- Multi-mod compatibility beyond base API
- Mana decay over time
- Mana regeneration from natural sources
- Mana interaction with fluids or weather

## Representative Gameplay Scenarios

### Scenario 1: First Experience with Mana Generator
1. Player places a Mana Generator block
2. System injects mana in a 3-block radius sphere
3. Player sees particle effects emanating from the generator
4. Player places a Mana Collector 5 blocks away
5. Mana flows along gradient from generator to collector
6. Collector displays stored mana count in its GUI

### Scenario 2: Mana Flow Visualization
1. Player enables debug visualization
2. Player sees color overlays on blocks indicating mana density
3. Player sees directional particles showing flow direction
4. Player identifies "mana rivers" forming between generators and collectors
5. Player places new collector to intercept flow

### Scenario 3: Custom Mod Integration
1. Mod developer adds custom consumer entity
2. Developer registers entity as mana consumer with 5-block radius
3. Developer implements `onManaReceived` callback
4. Entity receives mana from surrounding area on each tick
5. Developer tests with debug commands to verify flow

## Risks and Assumptions

### Technical Risks
- **Risk:** Performance impact from per-coordinate mana calculations
  - **Mitigation:** Use chunk-based sparse storage; only process chunks with active mana; batch calculations
- **Risk:** Network synchronization overhead for visualization
  - **Mitigation:** Send only changed mana regions; use coarse quantization for client display
- **Risk:** Mod API misuse causing mana exploits
  - **Mitigation:** Validate all mod inputs; clamp values; audit suspicious operations

### Design Assumptions
- **Assumption:** Chunk-based processing provides sufficient performance
  - **Validation:** Profile with 100x100 area containing 50 generators and 50 collectors
- **Assumption:** Spherical gathering provides intuitive gameplay
  - **Validation:** Playtest with various radius values; gather developer feedback
- **Assumption:** Server-authoritative model prevents client-side cheating
  - **Validation:** Verify no client classes loaded on dedicated server; test with malicious client

### External Dependencies
- Fabric API 0.154.2+26.2 (networking, events)
- No additional runtime dependencies
