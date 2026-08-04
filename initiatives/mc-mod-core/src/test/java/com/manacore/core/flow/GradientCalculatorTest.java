package com.manacore.core.flow;

import com.manacore.core.storage.ChunkManaMap;

/**
 * Executable test for GradientCalculator.
 * No dependencies other than the pure Java classes under test.
 * Tests cover axis-aligned, diagonal, reversed arguments, equal values, sparse values, and negative coordinates.
 */
public class GradientCalculatorTest {

    private static int passed = 0;
    private static int failed = 0;

    public static void main(String[] args) {
        System.out.println("Running GradientCalculator tests...");

        testAxisAlignedPositiveDirection();
        testAxisAlignedNegativeDirection();
        testDiagonalDirection();
        testReversedArguments();
        testEqualValues();
        testSparseValues();
        testNegativeCoordinates();
        testZeroManaPositions();
        testLargeCoordinateRange();
        testGradientRecordValidation();
        testGradientRecordMethods();

        System.out.println("\nTest Results:");
        System.out.println("Passed: " + passed);
        System.out.println("Failed: " + failed);

        if (failed > 0) {
            System.exit(1);
        }
    }

    private static void testAxisAlignedPositiveDirection() {
        ChunkManaMap map = new ChunkManaMap();
        map.set(0, 0, 0, 100.0);
        map.set(5, 0, 0, 50.0);

        GradientCalculator.Gradient gradient = GradientCalculator.calculate(map, 0, 0, 0, 5, 0, 0);

        assert gradient.dx() == 1 : "Expected dx=1 for flow from (0,0,0) to (5,0,0)";
        assert gradient.dy() == 0 : "Expected dy=0";
        assert gradient.dz() == 0 : "Expected dz=0";
        assert gradient.magnitude() == 50.0 : "Expected magnitude=50.0";
        passed++;
    }

    private static void testAxisAlignedNegativeDirection() {
        ChunkManaMap map = new ChunkManaMap();
        map.set(10, 0, 0, 25.0);
        map.set(5, 0, 0, 75.0);

        GradientCalculator.Gradient gradient = GradientCalculator.calculate(map, 10, 0, 0, 5, 0, 0);

        assert gradient.dx() == 1 : "Expected dx=1 for flow from higher mana at (5,0,0) to lower mana at (10,0,0)";
        assert gradient.dy() == 0 : "Expected dy=0";
        assert gradient.dz() == 0 : "Expected dz=0";
        assert gradient.magnitude() == 50.0 : "Expected magnitude=50.0";
        passed++;
    }

    private static void testDiagonalDirection() {
        ChunkManaMap map = new ChunkManaMap();
        map.set(0, 0, 0, 100.0);
        map.set(3, 4, 5, 25.0);

        GradientCalculator.Gradient gradient = GradientCalculator.calculate(map, 0, 0, 0, 3, 4, 5);

        assert gradient.dx() == 1 : "Expected dx=1 for positive X difference";
        assert gradient.dy() == 1 : "Expected dy=1 for positive Y difference";
        assert gradient.dz() == 1 : "Expected dz=1 for positive Z difference";
        assert gradient.magnitude() == 75.0 : "Expected magnitude=75.0";
        passed++;
    }

    private static void testReversedArguments() {
        ChunkManaMap map = new ChunkManaMap();
        map.set(0, 0, 0, 100.0);
        map.set(5, 0, 0, 50.0);

        // Same positions as testAxisAlignedPositiveDirection but with arguments reversed
        GradientCalculator.Gradient gradient = GradientCalculator.calculate(map, 5, 0, 0, 0, 0, 0);

        // Direction remains from higher mana at (0,0,0) toward lower mana at (5,0,0).
        assert gradient.dx() == 1 : "Expected argument-order-invariant positive X direction";
        assert gradient.dy() == 0 : "Expected dy=0";
        assert gradient.dz() == 0 : "Expected dz=0";
        assert gradient.magnitude() == 50.0 : "Expected magnitude=50.0";
        passed++;
    }

    private static void testEqualValues() {
        ChunkManaMap map = new ChunkManaMap();
        map.set(0, 0, 0, 50.0);
        map.set(5, 3, 2, 50.0);

        GradientCalculator.Gradient gradient = GradientCalculator.calculate(map, 0, 0, 0, 5, 3, 2);

        assert gradient.isZero() : "Expected zero gradient for equal mana values";
        assert gradient.dx() == 0 : "Expected dx=0";
        assert gradient.dy() == 0 : "Expected dy=0";
        assert gradient.dz() == 0 : "Expected dz=0";
        assert gradient.magnitude() == 0.0 : "Expected magnitude=0.0";
        passed++;
    }

    private static void testSparseValues() {
        ChunkManaMap map = new ChunkManaMap();
        // Only set one position, the other should read as 0
        map.set(10, 20, 30, 75.0);

        GradientCalculator.Gradient gradient = GradientCalculator.calculate(map, 10, 20, 30, 15, 25, 35);

        // Flow from (10,20,30) with mana=75 to (15,25,35) with mana=0
        assert gradient.dx() == 1 : "Expected dx=1";
        assert gradient.dy() == 1 : "Expected dy=1";
        assert gradient.dz() == 1 : "Expected dz=1";
        assert gradient.magnitude() == 75.0 : "Expected magnitude=75.0";
        passed++;
    }

    private static void testNegativeCoordinates() {
        ChunkManaMap map = new ChunkManaMap();
        map.set(-5, -10, -15, 200.0);
        map.set(-2, -8, -12, 50.0);

        GradientCalculator.Gradient gradient = GradientCalculator.calculate(map, -5, -10, -15, -2, -8, -12);

        // From (-5,-10,-15) to (-2,-8,-12): all coordinates increase
        // Mana flows from higher (200) to lower (50)
        assert gradient.dx() == 1 : "Expected dx=1 for negative coordinates";
        assert gradient.dy() == 1 : "Expected dy=1 for negative coordinates";
        assert gradient.dz() == 1 : "Expected dz=1 for negative coordinates";
        assert gradient.magnitude() == 150.0 : "Expected magnitude=150.0";
        passed++;
    }

    private static void testZeroManaPositions() {
        ChunkManaMap map = new ChunkManaMap();
        // Both positions have zero mana (not set in the map)

        GradientCalculator.Gradient gradient = GradientCalculator.calculate(map, 0, 0, 0, 10, 5, 3);

        assert gradient.isZero() : "Expected zero gradient for both positions having zero mana";
        passed++;
    }

    private static void testLargeCoordinateRange() {
        ChunkManaMap map = new ChunkManaMap();
        map.set(1000, 2000, 3000, 1000.0);
        map.set(-1000, -2000, -3000, 500.0);

        GradientCalculator.Gradient gradient = GradientCalculator.calculate(map, 1000, 2000, 3000, -1000, -2000, -3000);

        // Flow from (1000,2000,3000) with mana=1000 to (-1000,-2000,-3000) with mana=500
        assert gradient.dx() == -1 : "Expected dx=-1 for large negative X difference";
        assert gradient.dy() == -1 : "Expected dy=-1 for large negative Y difference";
        assert gradient.dz() == -1 : "Expected dz=-1 for large negative Z difference";
        assert gradient.magnitude() == 500.0 : "Expected magnitude=500.0";
        passed++;
    }

    private static void testGradientRecordValidation() {
        // Test valid gradient creation
        try {
            GradientCalculator.Gradient valid = new GradientCalculator.Gradient(1, 0, -1, 50.0);
            assert valid.dx() == 1 : "Valid gradient dx";
            assert valid.dy() == 0 : "Valid gradient dy";
            assert valid.dz() == -1 : "Valid gradient dz";
            assert valid.magnitude() == 50.0 : "Valid gradient magnitude";
            passed++;
        } catch (Exception e) {
            fail("Valid gradient creation should not throw: " + e.getMessage());
        }

        // Test invalid dx
        try {
            new GradientCalculator.Gradient(2, 0, 0, 10.0);
            fail("Should have thrown for invalid dx=2");
        } catch (IllegalArgumentException e) {
            passed++;
        }

        // Test invalid dy
        try {
            new GradientCalculator.Gradient(0, -2, 0, 10.0);
            fail("Should have thrown for invalid dy=-2");
        } catch (IllegalArgumentException e) {
            passed++;
        }

        // Test invalid dz
        try {
            new GradientCalculator.Gradient(0, 0, 3, 10.0);
            fail("Should have thrown for invalid dz=3");
        } catch (IllegalArgumentException e) {
            passed++;
        }

        // Test negative magnitude
        try {
            new GradientCalculator.Gradient(0, 0, 0, -1.0);
            fail("Should have thrown for negative magnitude");
        } catch (IllegalArgumentException e) {
            passed++;
        }

        // Test NaN magnitude
        try {
            new GradientCalculator.Gradient(0, 0, 0, Double.NaN);
            fail("Should have thrown for NaN magnitude");
        } catch (IllegalArgumentException e) {
            passed++;
        }

        // Test infinite magnitude
        try {
            new GradientCalculator.Gradient(0, 0, 0, Double.POSITIVE_INFINITY);
            fail("Should have thrown for infinite magnitude");
        } catch (IllegalArgumentException e) {
            passed++;
        }
    }

    private static void testGradientRecordMethods() {
        GradientCalculator.Gradient zero = new GradientCalculator.Gradient(0, 0, 0, 0.0);
        GradientCalculator.Gradient nonZero = new GradientCalculator.Gradient(1, 0, -1, 25.0);

        assert zero.isZero() : "Zero gradient should report isZero=true";
        assert !zero.hasDirection() : "Zero gradient should report hasDirection=false";
        assert !nonZero.isZero() : "Non-zero gradient should report isZero=false";
        assert nonZero.hasDirection() : "Non-zero gradient should report hasDirection=true";
        
        passed++;
    }

    private static void fail(String message) {
        System.err.println("FAIL: " + message);
        failed++;
    }
}
