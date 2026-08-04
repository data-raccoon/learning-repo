# Mana Core - Acceptance Contract

## Automated Release Gates

The trusted gate must pass all four fixed verifier IDs:
1. `compile-common` -> `compileJava`
2. `compile-client` -> `compileClientJava`
3. `unit-tests` -> `test`
4. `build` -> `build`

## Player Journeys

### Journey 1: Server Start and World Load

**ID:** MC-001
**Preconditions:** Dedicated server with Mana Core installed, clean world
**Action:** Server starts with `/mana debug` enabled
**Observable:** Server starts without errors, no client classes loaded
**Verification:** Check server log for `ManaCore initialized` message and absence of `net.minecraft.client` errors
**Authority:** Server
**Evidence:** Server log file, `./gradlew run` output

### Journey 2: Client Connection and Visualization

**ID:** MC-002
**Preconditions:** Server running with Mana Core, client connects
**Action:** Client joins world
**Observable:** Client receives mana visualization packets, no connection errors
**Verification:** Client log shows `Registered ManaCore client`, no NPE or class not found errors
**Authority:** Client
**Evidence:** Client log file, successful connection

### Journey 3: Mana Generator Placement

**ID:** MC-003
**Preconditions:** Player in creative mode, holding Mana Generator block
**Action:** Player places Mana Generator at (10, 64, 10)
**Observable:** 
- Generator block appears in world
- Particle effect emanates from generator (3-block radius sphere)
- Debug HUD shows mana injection at position
**Verification:** 
- Server log: `ManaCreator registered at BlockPos(10,64,10)`
- Client visual: Particles visible to all players
- Debug command: `/mana debug` at (10,64,10) shows mana > 0
**Authority:** Server (placement), Client (visualization)
**Evidence:** Server log, client screenshot, debug output

### Journey 4: Mana Collector Placement and Flow

**ID:** MC-004
**Preconditions:** Mana Generator placed at (10,64,10), player has Mana Collector
**Action:** Player places Mana Collector at (15,64,10)
**Observable:**
- Collector block appears
- Mana particles flow from generator toward collector
- Collector shows stored mana count in GUI (if opened)
**Verification:**
- Server: Mana values decrease at generator sphere, increase at collector
- Flow direction matches gradient (10,64,10) -> (15,64,10)
- Collector storage increases over time
**Authority:** Server
**Evidence:** Server state dump, particle direction screenshot, storage values

### Journey 5: Spherical Gathering at Radius 1

**ID:** MC-005
**Preconditions:** Mana Generator at (10,64,10), Mana Collector at (11,64,10)
**Action:** System processes mana gathering
**Observable:** Collector gathers mana from adjacent position
**Verification:** 
- Collector at (11,64,10) receives mana from (10,64,10) 
- Distance = 1, within minimum radius
- Mana transfer amount matches configuration
**Authority:** Server
**Evidence:** Server log showing mana transfer, collector storage increase

### Journey 6: Spherical Gathering at Radius 3

**ID:** MC-006
**Preconditions:** Mana Generator at (10,64,10), Mana Collector at (13,64,10)
**Action:** System processes mana gathering
**Observable:** Collector gathers mana from 3-block distance
**Verification:**
- Distance = 3, within configurable radius
- Mana flows through intermediate positions (11,64,10), (12,64,10)
- Collector receives reduced mana due to distance/gradient
**Authority:** Server
**Evidence:** Server state showing flow path, collector storage

### Journey 7: Multiple Collectors Competition

**ID:** MC-007
**Preconditions:** One Mana Generator at (10,64,10), two Collectors at (12,64,10) and (14,64,10)
**Action:** System processes mana flow
**Observable:** Mana distributes between collectors based on gradient
**Verification:**
- Both collectors receive mana
- Collector at (12,64,10) receives more than (14,64,10) (closer = stronger gradient)
- Total mana gathered <= mana generated
**Authority:** Server
**Evidence:** Storage values from both collectors, ratio matches distance

### Journey 8: Storage Capacity Limit

**ID:** MC-008
**Preconditions:** Mana Collector with capacity=1000 at (10,64,10)
**Action:** System attempts to add mana when storage is full
**Observable:** Storage stops at 1000, no overflow
**Verification:**
- Storage value = 1000 (capped)
- Server log: `Mana storage full, discarding excess`
- No negative values or wrap-around
**Authority:** Server
**Evidence:** Server log, storage value remains at cap

### Journey 9: Debug Command

**ID:** MC-009
**Preconditions:** Server running, player in world
**Action:** Player executes `/mana debug` at position (x,y,z)
**Observable:** Chat message showing mana value at position
**Verification:**
- Response format: `Mana at (x,y,z): <value>`
- Value matches server state
- No errors for valid coordinates
- Error message for invalid coordinates
**Authority:** Server (data), Client (display)
**Evidence:** Chat output screenshot, server command processing log

### Journey 10: Invalid Position Handling

**ID:** MC-010
**Preconditions:** Server running
**Action:** Mod API queries mana at invalid position (null, out of bounds)
**Observable:** Graceful error handling
**Verification:**
- No NPE or exception thrown
- Return value: 0 mana
- Server log: `Invalid position requested: <details>`
**Authority:** Server
**Evidence:** Server log, mod API returns 0

### Journey 11: Client-Server Isolation

**ID:** MC-011
**Preconditions:** Dedicated server running, client connected
**Action:** Client attempts to modify mana via packet
**Observable:** Server rejects modification attempt
**Verification:**
- No mana state change on server
- Server log: `Rejected client mana modification attempt`
- Client receives no confirmation
**Authority:** Server
**Evidence:** Server state unchanged, rejection log entry

### Journey 12: Visualization Accuracy

**ID:** MC-012
**Preconditions:** Generator at (10,64,10), Collector at (15,64,10)
**Action:** Player observes flow with visualization enabled
**Observable:** Particles flow from generator to collector
**Verification:**
- Particle direction vector points from high to low mana
- Particle count proportional to mana flow rate
- Particles visible within render distance
**Authority:** Client
**Evidence:** Screenshot showing directional particles

## Client and Dedicated-Server Gates

### Gate C-001: Client Start
**Preconditions:** Clean Minecraft installation with Mana Core
**Action:** Launch client with `runClient`
**Result:** Client starts without crash, registries complete
**Evidence:** Client log, no exceptions

### Gate C-002: World Load
**Preconditions:** Client started
**Action:** Load or create world
**Result:** World loads without registry or resource errors
**Evidence:** Client log, world renders correctly

### Gate C-003: Primary Journey
**Preconditions:** World loaded
**Action:** Complete Journey MC-003 (place generator)
**Result:** Feature works as described
**Evidence:** Screenshot, log output

### Gate S-001: Dedicated Server Start
**Preconditions:** Dedicated server with Mana Core
**Action:** Start server
**Result:** Server starts without loading client classes
**Evidence:** Server log, `net.minecraft.client` not in loaded classes

### Gate S-002: Player Connection
**Preconditions:** Server running
**Action:** Client connects to server
**Result:** Player connects, feature works with server authority
**Evidence:** Connection log, successful join

### Gate S-003: Feature Authority
**Preconditions:** Server running, client connected
**Action:** Execute Journey MC-004
**Result:** Feature works with server owning state
**Evidence:** Server state changes, client displays correctly

## Persistence Gates

### Gate P-001: New Save Defaults
**Preconditions:** v1 with no persistence
**Action:** Create new world
**Result:** Mana state initialized empty
**Evidence:** All mana values = 0 at start

### Gate P-002: Missing Data
**Preconditions:** v1 with no persistence
**Action:** Query mana at uninitialized position
**Result:** Returns 0 (no crash)
**Evidence:** API returns 0, no exceptions

## Accessibility and Usability Gates

### Gate A-001: Visual Feedback
**Preconditions:** Player with color vision deficiency
**Action:** Observe mana visualization
**Result:** Flow direction indicated by particle motion, not just color
**Evidence:** Particle system uses motion + color

### Gate A-002: Text Alternatives
**Preconditions:** Player using screen reader
**Action:** Use debug command
**Result:** All information available in text format
**Evidence:** `/mana debug` outputs text to chat

### Gate A-003: Control Remapping
**Preconditions:** Player with custom keybinds
**Action:** Use debug command
**Result:** Command works regardless of keybind configuration
**Evidence:** Command is text-based, not keybind-dependent

## Performance and Network Budgets

### Budget PERF-001: CPU
**Test Environment:** Intel i7-12700, 32GB RAM, SSD
**Workload:** 100x100 area, 50 generators, 50 collectors, 100 entities
**Baseline:** Empty world tick time
**Threshold:** < 50ms per tick (server)
**Measurement:** Average tick time over 60 seconds
**Evidence:** `/forge tps` or equivalent timing log

### Budget PERF-002: Memory
**Test Environment:** Same as PERF-001
**Workload:** Same as PERF-001
**Baseline:** Empty world memory usage
**Threshold:** < 512MB additional memory
**Measurement:** Heap usage via JMX or profiler
**Evidence:** Memory profiler output

### Budget PERF-003: Frame Time
**Test Environment:** RTX 3080, 1080p, high settings
**Workload:** 50 visible generators, 50 collectors, max particles
**Baseline:** Vanilla frame time
**Threshold:** < 5ms additional frame time
**Measurement:** F3 debug screen average
**Evidence:** Screenshot of F3 screen, frame time log

### Budget NET-001: Packet Size
**Test Environment:** Local LAN
**Workload:** Single player with max visualization range
**Baseline:** Vanilla packet size
**Threshold:** < 1KB per visualization update
**Measurement:** Packet size via network profiler
**Evidence:** Wireshark or equivalent capture

### Budget NET-002: Packet Frequency
**Test Environment:** Same as NET-001
**Workload:** Same as NET-001
**Baseline:** Vanilla packet frequency
**Threshold:** < 10 packets per second per player
**Measurement:** Packet count over 60 seconds
**Evidence:** Network profiler count

## Assets and Packaging

### Gate ASSET-001: Creative Artifacts
**Preconditions:** All creative artifacts declared
**Action:** Verify each file exists
**Result:** Every file in `creative_artifacts` list exists at exact path
**Evidence:** File system check, asset manifest

### Gate ASSET-002: Provenance
**Preconditions:** All creative artifacts exist
**Action:** Verify provenance manifest
**Result:** Every artifact has SHA-256 and provenance in manifest
**Evidence:** assets/asset-manifest.json

### Gate ASSET-003: Resolution
**Preconditions:** Client running
**Action:** Load all resources
**Result:** All resource references resolve without errors
**Evidence:** Client log, no missing resource warnings

### Gate ASSET-004: Built JAR
**Preconditions:** Build completed
**Action:** Inspect built JAR
**Result:** Contains fabric.mod.json, common classes, client classes, resources
**Evidence:** JAR contents listing

## Evidence Retention

**Retained for each release:**
- Trusted gate JSON output from harness
- Automated test reports
- Client/server smoke test logs
- Screenshots for visual verification (Journeys MC-003, MC-004, MC-012)
- QA report (future phase)
- Approval hashes
- Git diff of release candidate
