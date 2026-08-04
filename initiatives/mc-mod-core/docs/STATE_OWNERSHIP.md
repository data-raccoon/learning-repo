# Mana state ownership

## Decision

`ManaAPI` is an instance-owned facade. The Fabric integration layer must create
one instance for each authoritative logical server world or dimension and bind
that instance to the corresponding lifecycle.

There is no process-global mana map or configuration singleton. Two worlds in
the same dedicated-server process must never observe or mutate each other's
mana coordinates or configuration.

## Lifecycle

1. Create `ManaAPI` when the logical server world becomes available.
2. Route server-authoritative tick, block, entity, command, and packet handlers
   to that world's instance.
3. Never expose the mutable instance as client authority.
4. Discard the instance when the world unloads. Mana Core v1 intentionally does
   not persist positional mana across reloads.

The eventual Fabric binding owns the mapping from the current 26.2 world type
to `ManaAPI`; the pure-Java core does not import Minecraft or Fabric classes.

## Concurrency

Each facade synchronizes its public operations because `ChunkManaMap` is not
thread-safe. Synchronization is per world, so unrelated dimensions do not share
a process-wide lock.

## Integration gate

Before Fabric integration is accepted, an independent test must create at
least two logical-world bindings and prove storage and configuration isolation.
