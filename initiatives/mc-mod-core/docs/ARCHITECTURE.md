# Mana Core - Architecture Document

## Module Boundaries

```
┌─────────────────────────────────────────────────────────────────┐
│                        Mana Core Mod                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────────┐    ┌─────────────────────────────────┐ │
│  │   Common (Server)    │    │         Client                   │ │
│  │                     │    │                                     │ │
│  │  ┌───────────────┐  │    │  ┌─────────────────────────────┐ │ │
│  │  │ Mana Storage  │  │    │  │  Mana Visualization Renderer   │ │ │
│  │  │ - ChunkManaMap │  │    │  │  - ParticleManager              │ │ │
│  │  │ - ManaCalc    │  │    │  │  - OverlayRenderer             │ │ │
│  │  └───────────────┘  │    │  └─────────────────────────────┘ │ │
│  │                     │    │                                     │ │
│  │  ┌───────────────┐  │    │  ┌─────────────────────────────┐ │ │
│  │  │ Mana Flow     │  │    │  │  Client Proxy                  │ │ │
│  │  │ - Gradient    │  │    │  │  - NetworkReceiver             │ │ │
│  │  │ - FlowEngine  │  │    │  │  - DebugHUD                   │ │ │
│  │  └───────────────┘  │    │  └─────────────────────────────┘ │ │
│  │                     │    │                                     │ │
│  │  ┌───────────────┐  │    │                                    │ │
│  │  │ API           │  │    │                                    │ │
│  │  │ - ManaAPI     │  │    │                                    │ │
│  │  │ - EventBus    │  │    │                                    │ │
│  │  └───────────────┘  │    │                                    │ │
│  │                     │    │                                    │ │
│  └─────────────────────┘    └─────────────────────────────────┘ │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                    Example Blocks & Entities                   │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐    │ │
│  │  │ ManaGenerator │  │ ManaCollector │  │ ManaCrystal       │    │ │
│  │  │ (Creator)     │  │ (Consumer)    │  │ (Storage Entity) │    │ │
│  │  └──────────────┘  └──────────────┘  └──────────────────┘    │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                     │
└─────────────────────────────────────────────────────────────────┘
```

## Common/Client Source Set Isolation

| Module | Source Path | Loaded On | Dependencies |
|--------|-------------|-----------|--------------|
| Common | `src/main/java/com/manacore/` | Server + Client | Fabric API, Minecraft |
| Client | `src/client/java/com/manacore/client/` | Client only | Common, Fabric Client API |

**Enforcement:**
- Common code MUST NOT import `net.minecraft.client.*`
- Client code MUST be annotated with `@Environment(EnvType.CLIENT)`
- Common initialization uses `ModInitializer`
- Client initialization uses `ClientModInitializer`

## Server Authority

World-scoped state ownership is defined in `docs/STATE_OWNERSHIP.md`.
`ManaAPI` is instantiated once per authoritative logical server world or
dimension; it is not a process-global singleton.

**Server owns:**
- All mana values at every coordinate
- Mana flow calculations
- Mana gathering logic
- Mana creation logic
- Mana storage amounts
- Consumer/creator registration
- All game state changes

**Client owns:**
- Visualization rendering only
- Particle effects
- Block overlays
- Debug HUD display
- Input for debug commands

**Synchronization:**
- Server sends mana visualization data to client via custom payload
- Client never modifies server state
- Server validates all client-supplied positions

## Networking

### Packet Types

| ID | Direction | Purpose | Validation |
|----|-----------|---------|------------|
| `mana:visualization` | S→C | Mana density data for rendering | Bounds check, rate limit |
| `mana:debug` | C→S | Request debug info at position | Position validation |
| `mana:debug_response` | S→C | Debug mana values | None (read-only) |

### Packet Validation

All client-supplied packets validate:
1. **Existence:** Block/Entity exists at position
2. **Range:** Position within loaded chunks
3. **Authority:** Player has permission to query
4. **Rate:** Not exceeding rate limit (configurable)
5. **Format:** Correct packet structure

### Network Implementation

- Uses Fabric API `ServerPlayNetworking` and `ClientPlayNetworking`
- Payload types registered in `ManaNetworking` class
- Packet handlers in `ManaPacketHandler`
- No mixins required - pure Fabric API

## Persistence Schema

### v1 Schema (Non-persistent)

**Current v1:** Mana state is NOT persisted. Recalculates on world load.

This is explicit v1 limitation. Schema reserved for future versions:

```json
{
  "schema_version": 1,
  "world_id": "uuid",
  "mana_chunks": {
    "<chunk_key>": {
      "version": 1,
      "coordinates": {
        "<local_x>,<local_y>,<local_z>": <mana_value>
      }
    }
  },
  "stored_mana": {
    "<block_entity_id>": <amount>,
    "<entity_uuid>": <amount>
  }
}
```

### Migration Strategy

- v0 (current): No persistence
- v1 (future): Chunk-based sparse storage
- Migration: On first load with v1, initialize empty state
- Corruption: Discard corrupted chunk data, log warning
- Missing data: Treat as zero mana

## Resource Layout

```
src/
├── main/
│   ├── java/com/manacore/
│   │   ├── ManaCore.java                 # Mod entrypoint
│   │   ├── api/
│   │   │   ├── ManaAPI.java              # Public API
│   │   │   ├── events/
│   │   │   │   ├── ManaFlowEvent.java
│   │   │   │   ├── ManaGatherEvent.java
│   │   │   │   └── ManaStoreEvent.java
│   │   │   └── types/
│   │   │       ├── ManaConsumer.java     # Interface
│   │   │       ├── ManaCreator.java      # Interface
│   │   │       └── ManaStorage.java      # Interface
│   │   ├── core/
│   │   │   ├── storage/
│   │   │   │   ├── ChunkManaMap.java      # Sparse chunk storage
│   │   │   │   └── ManaCoordinates.java   # Coordinate utilities
│   │   │   ├── flow/
│   │   │   │   ├── GradientCalculator.java
│   │   │   │   └── FlowEngine.java
│   │   │   ├── gather/
│   │   │   │   └── SphericalGatherer.java
│   │   │   └── ManaMath.java            # Math utilities
│   │   ├── networking/
│   │   │   ├── ManaNetworking.java      # Packet registration
│   │   │   └── ManaPacketHandler.java   # Packet processing
│   │   └── config/
│   │       └── ManaConfig.java
│   └── resources/
│       ├── fabric.mod.json
│       └── assets/manacore/
│           └── lang/
│               └── en_us.json
└── client/
    └── java/com/manacore/client/
        ├── ManaCoreClient.java          # Client entrypoint
        ├── visualization/
        │   ├── particle/
        │   │   └── ManaFlowParticle.java
        │   ├── overlay/
        │   │   └── ManaOverlay.java
        │   └── ParticleManager.java
        ├── hud/
        │   └── DebugHUD.java
        └── networking/
            └── ClientManaPacketHandler.java

tests/
└── src/test/java/com/manacore/
    ├── core/
    │   ├── storage/
    │   │   └── ChunkManaMapTest.java
    │   └── flow/
    │       └── GradientCalculatorTest.java
    └── TestManaCore.java
```

## Test Seams

### Unit Test Boundaries

| Component | Test Strategy | Seam Location |
|-----------|---------------|---------------|
| ChunkManaMap | Direct instantiation | Constructor |
| GradientCalculator | Pure function | Static methods |
| FlowEngine | Mock dependencies | Interface injection |
| SphericalGatherer | Parameterized tests | Public methods |
| ManaAPI | Integration tests | Public API |

### Automated Test Coverage

**Required tests:**
- `ChunkManaMapTest`: Add, get, remove mana at coordinates
- `ChunkManaMapTest`: Sparse storage behavior
- `GradientCalculatorTest`: Correct gradient direction
- `GradientCalculatorTest`: Edge cases (equal values, boundaries)
- `SphericalGathererTest`: Correct sphere collection
- `SphericalGathererTest`: Radius configuration
- `FlowEngineTest`: Mana movement logic
- `FlowEngineTest`: Performance with many coordinates

### Manual Test Points

- Server start without client classes
- Client connection to server
- Mana flow visualization accuracy
- Debug command output
- Multiple generators/collectors interaction

## Build and Runtime

### Gradle
- `build.gradle`: Fabric Loom 1.17-SNAPSHOT
- `settings.gradle`: Mod configuration
- `gradle.properties`: Version pins
- Wrapper: Gradle 9.5.1

### Java
- Java 25 required
- Source compatibility: Java 25
- Target compatibility: Java 25

### Mod Metadata
- mod_id: `manacore`
- version: `1.0.0`
- name: `Mana Core`
- description: `Foundational mana resource system for Fabric mods`
- authors: `["AI-Learn"]`
- license: `MIT`
- environment: `server` and `client`
- entrypoints:
  - main: `com.manacore.ManaCore`
  - client: `com.manacore.client.ManaCoreClient`
- mixins: `[]` (none in v1)
- depends: `fabric-api:0.154.2+26.2`
