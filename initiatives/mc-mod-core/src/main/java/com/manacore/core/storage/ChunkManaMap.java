package com.manacore.core.storage;

import java.util.HashMap;
import java.util.Map;

/**
 * Sparse positional chunk storage for mana values.
 * Only stores non-zero mana values to maintain sparsity.
 * Unset positions read as zero; non-positive results are removed so storage remains sparse.
 * Mana values are always non-negative and finite.
 */
public class ChunkManaMap {

    /**
     * Map from chunk keys to chunk data.
     * Chunk key is a long packing chunk X, Y, Z coordinates.
     */
    private final Map<Long, ChunkData> chunks;

    /**
     * Creates a new empty ChunkManaMap.
     */
    public ChunkManaMap() {
        this.chunks = new HashMap<>();
    }

    /**
     * Gets the mana value at the specified world coordinates.
     * Unset positions return 0.
     *
     * @param x the world X coordinate
     * @param y the world Y coordinate
     * @param z the world Z coordinate
     * @return the mana value at the position (0 if unset)
     */
    public double get(int x, int y, int z) {
        long chunkKey = ManaCoordinates.chunkKey(
                ManaCoordinates.getChunkCoord(x),
                ManaCoordinates.getChunkCoord(y),
                ManaCoordinates.getChunkCoord(z));

        ChunkData chunk = chunks.get(chunkKey);
        if (chunk == null) {
            return 0.0;
        }

        short intraChunkKey = ManaCoordinates.intraChunkKey(
                ManaCoordinates.getIntraChunkCoord(x),
                ManaCoordinates.getIntraChunkCoord(y),
                ManaCoordinates.getIntraChunkCoord(z));

        Double value = chunk.positions.get(intraChunkKey);
        return value != null ? value : 0.0;
    }

    /**
     * Sets the mana value at the specified world coordinates.
     * If the value is non-positive (<= 0), the position is removed from storage.
     * If the value is NaN or infinite, it is treated as invalid and the position is removed.
     *
     * @param x the world X coordinate
     * @param y the world Y coordinate
     * @param z the world Z coordinate
     * @param value the mana value to set
     */
    public void set(int x, int y, int z, double value) {
        // Validate and clamp the value
        if (!isValidManaValue(value)) {
            remove(x, y, z);
            return;
        }

        long chunkKey = ManaCoordinates.chunkKey(
                ManaCoordinates.getChunkCoord(x),
                ManaCoordinates.getChunkCoord(y),
                ManaCoordinates.getChunkCoord(z));

        short intraChunkKey = ManaCoordinates.intraChunkKey(
                ManaCoordinates.getIntraChunkCoord(x),
                ManaCoordinates.getIntraChunkCoord(y),
                ManaCoordinates.getIntraChunkCoord(z));

        if (value <= 0) {
            // Remove non-positive values to maintain sparsity
            remove(x, y, z);
            return;
        }

        ChunkData chunk = chunks.computeIfAbsent(chunkKey, k -> new ChunkData());
        chunk.positions.put(intraChunkKey, value);
    }

    /**
     * Adds mana to the specified world coordinates.
     * If the result is non-positive, the position is removed from storage.
     *
     * @param x the world X coordinate
     * @param y the world Y coordinate
     * @param z the world Z coordinate
     * @param delta the mana value to add
     */
    public void add(int x, int y, int z, double delta) {
        // Reject non-finite deltas but allow negative finite values
        if (!Double.isFinite(delta)) {
            return;
        }

        double current = get(x, y, z);
        double result = current + delta;

        // Handle overflow
        if (Double.isInfinite(result)) {
            result = Double.MAX_VALUE;
        }

        set(x, y, z, result);
    }

    /**
     * Removes the mana value at the specified world coordinates.
     * This is a no-op if the position was not set.
     *
     * @param x the world X coordinate
     * @param y the world Y coordinate
     * @param z the world Z coordinate
     */
    public void remove(int x, int y, int z) {
        long chunkKey = ManaCoordinates.chunkKey(
                ManaCoordinates.getChunkCoord(x),
                ManaCoordinates.getChunkCoord(y),
                ManaCoordinates.getChunkCoord(z));

        ChunkData chunk = chunks.get(chunkKey);
        if (chunk == null) {
            return;
        }

        short intraChunkKey = ManaCoordinates.intraChunkKey(
                ManaCoordinates.getIntraChunkCoord(x),
                ManaCoordinates.getIntraChunkCoord(y),
                ManaCoordinates.getIntraChunkCoord(z));

        chunk.positions.remove(intraChunkKey);

        // Clean up empty chunks
        if (chunk.positions.isEmpty()) {
            chunks.remove(chunkKey);
        }
    }

    /**
     * Checks if a mana value is valid (non-negative, finite, and not NaN).
     *
     * @param value the value to check
     * @return true if the value is valid
     */
    private static boolean isValidManaValue(double value) {
        return value > 0 && Double.isFinite(value);
    }

    /**
     * Gets the number of chunks with stored mana values.
     *
     * @return the number of non-empty chunks
     */
    public int getChunkCount() {
        return chunks.size();
    }

    /**
     * Gets the number of positions with stored mana values.
     *
     * @return the number of non-zero positions
     */
    public int getPositionCount() {
        int count = 0;
        for (ChunkData chunk : chunks.values()) {
            count += chunk.positions.size();
        }
        return count;
    }

    /**
     * Clears all mana values from storage.
     */
    public void clear() {
        chunks.clear();
    }

    /**
     * Checks if the storage is empty.
     *
     * @return true if there are no stored mana values
     */
    public boolean isEmpty() {
        return chunks.isEmpty();
    }

    /**
     * Internal class representing the mana data for a single chunk.
     */
    private static final class ChunkData {
        /**
         * Map from intra-chunk position keys to mana values.
         * Only stores non-zero values.
         */
        final Map<Short, Double> positions;

        ChunkData() {
            this.positions = new HashMap<>();
        }
    }
}
