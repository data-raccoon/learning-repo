package com.manacore.core.storage;

import com.manacore.core.ManaMath;

/**
 * No-dependency executable test for ChunkManaMap.
 * Covers get, set, add, remove, sparse cleanup, invalid values, negative coordinates, and chunk boundaries.
 * Run with: java -cp ... com.manacore.core.storage.ChunkManaMapTest
 */
public class ChunkManaMapTest {

    private static int passed = 0;
    private static int failed = 0;

    public static void main(String[] args) {
        System.out.println("Running ChunkManaMapTest...");

        testBasicGetSet();
        testAdd();
        testRemove();
        testSparseCleanup();
        testInvalidValues();
        testNegativeCoordinates();
        testChunkBoundaries();
        testCoordinateUtilities();
        testManaMath();

        System.out.println("\nTest Results:");
        System.out.println("  Passed: " + passed);
        System.out.println("  Failed: " + failed);

        if (failed > 0) {
            System.exit(1);
        }
    }

    private static void testBasicGetSet() {
        System.out.println("\n=== Testing Basic Get/Set ===");

        ChunkManaMap map = new ChunkManaMap();

        // Test unset positions return 0
        assertEquals(0.0, map.get(0, 0, 0), "Unset position should return 0");

        // Test set and get
        map.set(0, 0, 0, 100.0);
        assertEquals(100.0, map.get(0, 0, 0), "Set value should be retrievable");

        // Test overwriting
        map.set(0, 0, 0, 50.0);
        assertEquals(50.0, map.get(0, 0, 0), "Overwritten value should be updated");

        // Test multiple positions
        map.set(1, 0, 0, 200.0);
        map.set(0, 1, 0, 300.0);
        map.set(0, 0, 1, 400.0);
        assertEquals(200.0, map.get(1, 0, 0), "X+1 position should be correct");
        assertEquals(300.0, map.get(0, 1, 0), "Y+1 position should be correct");
        assertEquals(400.0, map.get(0, 0, 1), "Z+1 position should be correct");

        System.out.println("  Basic Get/Set tests passed");
    }

    private static void testAdd() {
        System.out.println("\n=== Testing Add ===");

        ChunkManaMap map = new ChunkManaMap();

        // Test add to unset position
        map.add(0, 0, 0, 50.0);
        assertEquals(50.0, map.get(0, 0, 0), "Add to unset should work");

        // Test add to existing position
        map.add(0, 0, 0, 30.0);
        assertEquals(80.0, map.get(0, 0, 0), "Add to existing should accumulate");

        // Test add with negative delta (should be ignored)
        map.add(0, 0, 0, -10.0);
        assertEquals(70.0, map.get(0, 0, 0), "Add with negative delta should subtract");

        // Test add with zero delta (should be ignored)
        map.add(0, 0, 0, 0.0);
        assertEquals(70.0, map.get(0, 0, 0), "Add with zero delta should be no-op");

        // Test add that results in non-positive value
        map.add(0, 0, 0, -100.0);
        assertEquals(0.0, map.get(0, 0, 0), "Add resulting in negative should remove position");

        System.out.println("  Add tests passed");
    }

    private static void testRemove() {
        System.out.println("\n=== Testing Remove ===");

        ChunkManaMap map = new ChunkManaMap();

        // Test remove non-existent position
        map.remove(0, 0, 0);
        assertEquals(0.0, map.get(0, 0, 0), "Remove non-existent should be no-op");

        // Test remove existing position
        map.set(0, 0, 0, 100.0);
        map.remove(0, 0, 0);
        assertEquals(0.0, map.get(0, 0, 0), "Remove existing should clear position");

        // Test remove with set to non-positive
        map.set(1, 0, 0, 50.0);
        map.set(1, 0, 0, -10.0);
        assertEquals(0.0, map.get(1, 0, 0), "Set to negative should remove position");

        System.out.println("  Remove tests passed");
    }

    private static void testSparseCleanup() {
        System.out.println("\n=== Testing Sparse Cleanup ===");

        ChunkManaMap map = new ChunkManaMap();

        // Add multiple positions in same chunk
        map.set(0, 0, 0, 100.0);
        map.set(1, 0, 0, 200.0);
        map.set(0, 1, 0, 300.0);

        assertEquals(1, map.getChunkCount(), "Should have 1 chunk");
        assertEquals(3, map.getPositionCount(), "Should have 3 positions");

        // Remove all positions in chunk
        map.remove(0, 0, 0);
        map.remove(1, 0, 0);
        map.remove(0, 1, 0);

        assertEquals(0, map.getChunkCount(), "Empty chunk should be cleaned up");
        assertEquals(0, map.getPositionCount(), "Should have 0 positions");

        // Test clear
        map.set(0, 0, 0, 100.0);
        map.set(16, 0, 0, 200.0); // Different chunk
        assertEquals(2, map.getChunkCount(), "Should have 2 chunks");

        map.clear();
        assertEquals(0, map.getChunkCount(), "Clear should remove all chunks");
        assertTrue(map.isEmpty(), "Map should be empty after clear");

        System.out.println("  Sparse Cleanup tests passed");
    }

    private static void testInvalidValues() {
        System.out.println("\n=== Testing Invalid Values ===");

        ChunkManaMap map = new ChunkManaMap();

        // Test NaN
        map.set(0, 0, 0, Double.NaN);
        assertEquals(0.0, map.get(0, 0, 0), "NaN should be rejected");

        // Test positive infinity
        map.set(0, 0, 0, Double.POSITIVE_INFINITY);
        assertEquals(0.0, map.get(0, 0, 0), "Positive infinity should be rejected");

        // Test negative infinity
        map.set(0, 0, 0, Double.NEGATIVE_INFINITY);
        assertEquals(0.0, map.get(0, 0, 0), "Negative infinity should be rejected");

        // Test negative value
        map.set(0, 0, 0, -100.0);
        assertEquals(0.0, map.get(0, 0, 0), "Negative value should be rejected");

        // Test zero
        map.set(0, 0, 0, 0.0);
        assertEquals(0.0, map.get(0, 0, 0), "Zero should be rejected");

        // Test very small positive value
        map.set(0, 0, 0, 1e-100);
        assertEquals(1e-100, map.get(0, 0, 0), "Very small positive should be accepted");

        // Test very large positive value
        map.set(1, 0, 0, Double.MAX_VALUE);
        assertEquals(Double.MAX_VALUE, map.get(1, 0, 0), "MAX_VALUE should be accepted");

        System.out.println("  Invalid Values tests passed");
    }

    private static void testNegativeCoordinates() {
        System.out.println("\n=== Testing Negative Coordinates ===");

        ChunkManaMap map = new ChunkManaMap();

        // Test negative coordinates
        map.set(-1, -2, -3, 100.0);
        assertEquals(100.0, map.get(-1, -2, -3), "Negative coordinates should work");

        // Test mixed positive/negative
        map.set(-10, 5, -15, 200.0);
        assertEquals(200.0, map.get(-10, 5, -15), "Mixed coordinates should work");

        // Test chunk boundaries with negative coordinates
        // -17 should be in chunk -2 (floor(-17/16) = -2)
        // -16 should be in chunk -1 (floor(-16/16) = -1)
        // -1 should be in chunk -1 (floor(-1/16) = -1)
        // 0 should be in chunk 0
        map.set(-17, 0, 0, 100.0);
        map.set(-16, 0, 0, 200.0);
        map.set(-1, 0, 0, 300.0);
        map.set(0, 0, 0, 400.0);

        assertEquals(100.0, map.get(-17, 0, 0), "Coordinate -17 should work");
        assertEquals(200.0, map.get(-16, 0, 0), "Coordinate -16 should work");
        assertEquals(300.0, map.get(-1, 0, 0), "Coordinate -1 should work");
        assertEquals(400.0, map.get(0, 0, 0), "Coordinate 0 should work");

        System.out.println("  Negative Coordinates tests passed");
    }

    private static void testChunkBoundaries() {
        System.out.println("\n=== Testing Chunk Boundaries ===");

        ChunkManaMap map = new ChunkManaMap();

        // Test positions at chunk boundaries
        // Chunk 0: positions 0-15
        // Chunk 1: positions 16-31

        // Set values at chunk boundaries
        map.set(15, 0, 0, 100.0);  // Last position in chunk 0
        map.set(16, 0, 0, 200.0);  // First position in chunk 1
        map.set(31, 0, 0, 300.0);  // Last position in chunk 1
        map.set(32, 0, 0, 400.0);  // First position in chunk 2

        assertEquals(100.0, map.get(15, 0, 0), "Position 15 should be in chunk 0");
        assertEquals(200.0, map.get(16, 0, 0), "Position 16 should be in chunk 1");
        assertEquals(300.0, map.get(31, 0, 0), "Position 31 should be in chunk 1");
        assertEquals(400.0, map.get(32, 0, 0), "Position 32 should be in chunk 2");

        // Test that positions in different chunks don't interfere
        assertEquals(3, map.getChunkCount(), "Should have 3 chunks (0, 1, 2)");

        // Test all 3D boundaries
        map.set(0, 15, 0, 500.0);  // Y boundary
        map.set(0, 16, 0, 600.0);
        map.set(0, 0, 15, 700.0);  // Z boundary
        map.set(0, 0, 16, 800.0);

        assertEquals(500.0, map.get(0, 15, 0), "Y=15 should work");
        assertEquals(600.0, map.get(0, 16, 0), "Y=16 should work");
        assertEquals(700.0, map.get(0, 0, 15), "Z=15 should work");
        assertEquals(800.0, map.get(0, 0, 16), "Z=16 should work");

        System.out.println("  Chunk Boundaries tests passed");
    }

    private static void testCoordinateUtilities() {
        System.out.println("\n=== Testing Coordinate Utilities ===");

        // Test floor division
        assertEquals(0, ManaCoordinates.floorDiv(0, 16), "floorDiv(0, 16) should be 0");
        assertEquals(1, ManaCoordinates.floorDiv(16, 16), "floorDiv(16, 16) should be 1");
        assertEquals(0, ManaCoordinates.floorDiv(15, 16), "floorDiv(15, 16) should be 0");
        assertEquals(-1, ManaCoordinates.floorDiv(-1, 16), "floorDiv(-1, 16) should be -1");
        assertEquals(-1, ManaCoordinates.floorDiv(-16, 16), "floorDiv(-16, 16) should be -1");
        assertEquals(-2, ManaCoordinates.floorDiv(-17, 16), "floorDiv(-17, 16) should be -2");

        // Test floor modulus
        assertEquals(0, ManaCoordinates.floorMod(0, 16), "floorMod(0, 16) should be 0");
        assertEquals(0, ManaCoordinates.floorMod(16, 16), "floorMod(16, 16) should be 0");
        assertEquals(15, ManaCoordinates.floorMod(15, 16), "floorMod(15, 16) should be 15");
        assertEquals(15, ManaCoordinates.floorMod(-1, 16), "floorMod(-1, 16) should be 15");
        assertEquals(0, ManaCoordinates.floorMod(-16, 16), "floorMod(-16, 16) should be 0");
        assertEquals(15, ManaCoordinates.floorMod(-17, 16), "floorMod(-17, 16) should be 15");

        // Test chunk coordinate calculation
        assertEquals(0, ManaCoordinates.getChunkCoord(0), "Chunk coord of 0 should be 0");
        assertEquals(0, ManaCoordinates.getChunkCoord(15), "Chunk coord of 15 should be 0");
        assertEquals(1, ManaCoordinates.getChunkCoord(16), "Chunk coord of 16 should be 1");
        assertEquals(-1, ManaCoordinates.getChunkCoord(-1), "Chunk coord of -1 should be -1");
        assertEquals(-1, ManaCoordinates.getChunkCoord(-16), "Chunk coord of -16 should be -1");
        assertEquals(-2, ManaCoordinates.getChunkCoord(-17), "Chunk coord of -17 should be -2");

        // Test intra-chunk coordinate calculation
        assertEquals(0, ManaCoordinates.getIntraChunkCoord(0), "Intra coord of 0 should be 0");
        assertEquals(15, ManaCoordinates.getIntraChunkCoord(15), "Intra coord of 15 should be 15");
        assertEquals(0, ManaCoordinates.getIntraChunkCoord(16), "Intra coord of 16 should be 0");
        assertEquals(15, ManaCoordinates.getIntraChunkCoord(-1), "Intra coord of -1 should be 15");

        // Test chunk key round-trip
        long key = ManaCoordinates.chunkKey(1, 2, 3);
        assertEquals(1, ManaCoordinates.getChunkX(key), "Chunk X should round-trip");
        assertEquals(2, ManaCoordinates.getChunkY(key), "Chunk Y should round-trip");
        assertEquals(3, ManaCoordinates.getChunkZ(key), "Chunk Z should round-trip");

        // Test intra-chunk key round-trip
        short intraKey = ManaCoordinates.intraChunkKey(1, 2, 3);
        assertEquals(1, ManaCoordinates.getIntraChunkX(intraKey), "Intra X should round-trip");
        assertEquals(2, ManaCoordinates.getIntraChunkY(intraKey), "Intra Y should round-trip");
        assertEquals(3, ManaCoordinates.getIntraChunkZ(intraKey), "Intra Z should round-trip");

        System.out.println("  Coordinate Utilities tests passed");
    }

    private static void testManaMath() {
        System.out.println("\n=== Testing Mana Math ===");

        // Test clampNonNegative
        assertEquals(0.0, ManaMath.clampNonNegative(-1.0), "Negative should clamp to 0");
        assertEquals(0.0, ManaMath.clampNonNegative(0.0), "Zero should stay 0");
        assertEquals(5.0, ManaMath.clampNonNegative(5.0), "Positive should stay positive");

        // Test isValidMana
        assertTrue(ManaMath.isValidMana(0.0), "Zero should be valid");
        assertTrue(ManaMath.isValidMana(100.0), "Positive should be valid");
        assertFalse(ManaMath.isValidMana(-1.0), "Negative should be invalid");
        assertFalse(ManaMath.isValidMana(Double.NaN), "NaN should be invalid");
        assertFalse(ManaMath.isValidMana(Double.POSITIVE_INFINITY), "Infinity should be invalid");

        // Test safe operations
        assertEquals(0.0, ManaMath.safeAdd(-1.0, 5.0), "Safe add with negative should return 0");
        assertEquals(0.0, ManaMath.safeAdd(5.0, -1.0), "Safe add with negative should return 0");
        assertEquals(6.0, ManaMath.safeAdd(3.0, 3.0), "Safe add should work");

        assertEquals(0.0, ManaMath.safeSubtract(5.0, 10.0), "Safe subtract resulting in negative should return 0");
        assertEquals(2.0, ManaMath.safeSubtract(5.0, 3.0), "Safe subtract should work");

        assertEquals(0.0, ManaMath.safeMultiply(-1.0, 5.0), "Safe multiply with negative should return 0");
        assertEquals(6.0, ManaMath.safeMultiply(2.0, 3.0), "Safe multiply should work");

        assertEquals(0.0, ManaMath.safeDivide(5.0, 0.0), "Safe divide by zero should return 0");
        assertEquals(2.5, ManaMath.safeDivide(5.0, 2.0), "Safe divide should work");

        // Test lerp
        assertEquals(0.0, ManaMath.lerp(0.0, 10.0, 0.0), "Lerp at 0 should be first value");
        assertEquals(10.0, ManaMath.lerp(0.0, 10.0, 1.0), "Lerp at 1 should be second value");
        assertEquals(5.0, ManaMath.lerp(0.0, 10.0, 0.5), "Lerp at 0.5 should be midpoint");

        System.out.println("  Mana Math tests passed");
    }

    // Assertion helpers

    private static void assertEquals(double expected, double actual, String message) {
        if (Math.abs(expected - actual) > 1e-10) {
            System.err.println("FAIL: " + message);
            System.err.println("  Expected: " + expected);
            System.err.println("  Actual: " + actual);
            failed++;
        } else {
            passed++;
        }
    }

    private static void assertEquals(int expected, int actual, String message) {
        if (expected != actual) {
            System.err.println("FAIL: " + message);
            System.err.println("  Expected: " + expected);
            System.err.println("  Actual: " + actual);
            failed++;
        } else {
            passed++;
        }
    }

    private static void assertTrue(boolean condition, String message) {
        if (!condition) {
            System.err.println("FAIL: " + message);
            failed++;
        } else {
            passed++;
        }
    }

    private static void assertFalse(boolean condition, String message) {
        assertTrue(!condition, message);
    }
}
