package com.manacore.core.storage;

/**
 * Coordinate utilities for mana storage system.
 * Handles negative coordinates and chunk boundaries using floor division/modulus semantics.
 */
public final class ManaCoordinates {

    /**
     * Chunk size in blocks (Minecraft standard).
     */
    public static final int CHUNK_SIZE = 16;

    /**
     * Chunk size in bits for bit shifting operations.
     */
    public static final int CHUNK_SIZE_BITS = 4;

    /**
     * Mask for extracting intra-chunk coordinates (0-15).
     */
    public static final int CHUNK_MASK = CHUNK_SIZE - 1;

    private ManaCoordinates() {
        // Utility class - no instantiation
    }

    /**
     * Gets the chunk coordinate for a given world coordinate using floor division.
     * Handles negative coordinates correctly (floor division rounds toward negative infinity).
     *
     * @param coord the world coordinate
     * @return the chunk coordinate
     */
    public static int getChunkCoord(int coord) {
        return floorDiv(coord, CHUNK_SIZE);
    }

    /**
     * Gets the intra-chunk coordinate (0-15) for a given world coordinate.
     * Uses floor modulus to ensure positive results even for negative coordinates.
     *
     * @param coord the world coordinate
     * @return the intra-chunk coordinate (0-15)
     */
    public static int getIntraChunkCoord(int coord) {
        return floorMod(coord, CHUNK_SIZE);
    }

    /**
     * Gets the world coordinate from chunk coordinate and intra-chunk coordinate.
     *
     * @param chunkCoord the chunk coordinate
     * @param intraCoord the intra-chunk coordinate (0-15)
     * @return the world coordinate
     */
    public static int getWorldCoord(int chunkCoord, int intraCoord) {
        return (chunkCoord * CHUNK_SIZE) + intraCoord;
    }

    /**
     * Floor division that rounds toward negative infinity.
     * Java's / operator rounds toward zero, so we need to adjust for negative numbers.
     *
     * @param a the dividend
     * @param b the divisor (must be positive)
     * @return the floor division result
     */
    public static int floorDiv(int a, int b) {
        int result = a / b;
        // If the result is negative and there's a remainder, subtract 1
        if (a % b != 0 && ((a < 0) != (b < 0))) {
            result--;
        }
        return result;
    }

    /**
     * Floor modulus that always returns a non-negative result.
     *
     * @param a the dividend
     * @param b the divisor (must be positive)
     * @return the floor modulus result (0 <= result < |b|)
     */
    public static int floorMod(int a, int b) {
        return ((a % b) + b) % b;
    }

    /**
     * Creates a chunk key from chunk coordinates.
     *
     * @param chunkX the chunk X coordinate
     * @param chunkY the chunk Y coordinate
     * @param chunkZ the chunk Z coordinate
     * @return a unique long key for the chunk
     */
    public static long chunkKey(int chunkX, int chunkY, int chunkZ) {
        // Use bit shifting to pack coordinates into a long
        // Each coordinate gets 21 bits (enough for +/- 1 million)
        return ((long) chunkX & 0x1FFFFF) << 42
                | ((long) chunkY & 0x1FFFFF) << 21
                | ((long) chunkZ & 0x1FFFFF);
    }

    /**
     * Extracts chunk X coordinate from a chunk key.
     *
     * @param key the chunk key
     * @return the chunk X coordinate
     */
    public static int getChunkX(long key) {
        return (int) ((key >> 42) & 0x1FFFFF);
    }

    /**
     * Extracts chunk Y coordinate from a chunk key.
     *
     * @param key the chunk key
     * @return the chunk Y coordinate
     */
    public static int getChunkY(long key) {
        return (int) ((key >> 21) & 0x1FFFFF);
    }

    /**
     * Extracts chunk Z coordinate from a chunk key.
     *
     * @param key the chunk key
     * @return the chunk Z coordinate
     */
    public static int getChunkZ(long key) {
        return (int) (key & 0x1FFFFF);
    }

    /**
     * Creates an intra-chunk position key from intra-chunk coordinates.
     *
     * @param x the intra-chunk X coordinate (0-15)
     * @param y the intra-chunk Y coordinate (0-15)
     * @param z the intra-chunk Z coordinate (0-15)
     * @return a unique short key for the intra-chunk position
     */
    public static short intraChunkKey(int x, int y, int z) {
        return (short) ((x & 0xF) << 8 | (y & 0xF) << 4 | (z & 0xF));
    }

    /**
     * Extracts intra-chunk X coordinate from an intra-chunk position key.
     *
     * @param key the intra-chunk position key
     * @return the intra-chunk X coordinate (0-15)
     */
    public static int getIntraChunkX(short key) {
        return (key >> 8) & 0xF;
    }

    /**
     * Extracts intra-chunk Y coordinate from an intra-chunk position key.
     *
     * @param key the intra-chunk position key
     * @return the intra-chunk Y coordinate (0-15)
     */
    public static int getIntraChunkY(short key) {
        return (key >> 4) & 0xF;
    }

    /**
     * Extracts intra-chunk Z coordinate from an intra-chunk position key.
     *
     * @param key the intra-chunk position key
     * @return the intra-chunk Z coordinate (0-15)
     */
    public static int getIntraChunkZ(short key) {
        return key & 0xF;
    }
}
