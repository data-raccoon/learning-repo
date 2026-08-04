package com.manacore.core.api;

import com.manacore.core.config.ManaConfig;
import com.manacore.core.flow.FlowEngine;
import com.manacore.core.gather.SphericalGatherer;
import com.manacore.core.storage.ChunkManaMap;
import java.util.Objects;

/**
 * Pure-Java mana facade owned by one logical server world or dimension.
 *
 * <p>Callers create one instance per authoritative world state. Synchronized
 * instance methods serialize access to the underlying non-thread-safe sparse
 * map without coupling unrelated worlds through process-global state.
 */
public final class ManaAPI {
    private final ChunkManaMap storage;
    private ManaConfig config;

    /** Creates an empty world-scoped mana state with default configuration. */
    public ManaAPI() {
        storage = new ChunkManaMap();
        config = ManaConfig.defaults();
    }

    /** Returns the mana at a position, or zero when the position is unset. */
    public synchronized double getMana(int x, int y, int z) {
        return storage.get(x, y, z);
    }

    /** Sets mana at a position using {@link ChunkManaMap#set} semantics. */
    public synchronized void setMana(int x, int y, int z, double value) {
        storage.set(x, y, z, value);
    }

    /**
     * Adds a delta using the storage implementation and returns the resulting
     * stored value.
     */
    public synchronized double addMana(int x, int y, int z, double delta) {
        storage.add(x, y, z, delta);
        return storage.get(x, y, z);
    }

    /** Gathers mana in deterministic coordinate order from an inclusive sphere. */
    public synchronized double gatherMana(
            int centerX, int centerY, int centerZ, int radius, double maxTotal) {
        return SphericalGatherer.gather(
                storage, centerX, centerY, centerZ, radius, maxTotal);
    }

    /** Transfers mana between two positions without overshooting equalization. */
    public synchronized double flowMana(
            int ax,
            int ay,
            int az,
            int bx,
            int by,
            int bz,
            double maxTransfer) {
        return FlowEngine.flowPair(
                storage, ax, ay, az, bx, by, bz, maxTransfer);
    }

    /** Returns this world's immutable configuration value. */
    public synchronized ManaConfig getConfig() {
        return config;
    }

    /** Replaces this world's validated immutable configuration value. */
    public synchronized void setConfig(ManaConfig replacement) {
        config = Objects.requireNonNull(replacement, "config must not be null");
    }
}
