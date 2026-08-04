package com.manacore.core.config;

/**
 * Executable tests for ManaConfig validation and defaults.
 */
public class ManaConfigTest {

    private static int passed = 0;
    private static int failed = 0;

    public static void main(String[] args) {
        testDefaults();
        testCustomValues();
        testZeroFlowRate();
        testMinimumGatherRadius();
        testNegativeFlowRateThrows();
        testNonFiniteFlowRateThrows();
        testNaNFlowRateThrows();
        testZeroGatherRadiusThrows();
        testNegativeGatherRadiusThrows();
        testZeroMaxStorageThrows();
        testNegativeMaxStorageThrows();
        testNonFiniteMaxStorageThrows();
        testNaNMaxStorageThrows();
        testImmutability();

        System.out.println("Tests completed: " + passed + " passed, " + failed + " failed");
        if (failed > 0) {
            System.exit(1);
        }
    }

    private static void assertEquals(double expected, double actual, double delta, String message) {
        if (Math.abs(expected - actual) > delta) {
            failed++;
            throw new AssertionError(message + ": expected " + expected + " but was " + actual);
        }
        passed++;
    }

    private static void assertEquals(double expected, double actual, double delta) {
        assertEquals(expected, actual, delta, "Double comparison failed");
    }

    private static void assertEquals(int expected, int actual, String message) {
        if (expected != actual) {
            failed++;
            throw new AssertionError(message + ": expected " + expected + " but was " + actual);
        }
        passed++;
    }

    private static void assertEquals(int expected, int actual) {
        assertEquals(expected, actual, "Int comparison failed");
    }

    private static void assertTrue(boolean condition, String message) {
        if (!condition) {
            failed++;
            throw new AssertionError(message);
        }
        passed++;
    }

    private static void testDefaults() {
        ManaConfig config = ManaConfig.defaults();
        assertEquals(0.25, config.flowRate(), 0.001, "Default flowRate");
        assertEquals(3, config.gatherRadius(), "Default gatherRadius");
        assertEquals(1000.0, config.maxStorage(), 0.001, "Default maxStorage");
    }

    private static void testCustomValues() {
        ManaConfig config = new ManaConfig(0.5, 5, 2000.0);
        assertEquals(0.5, config.flowRate(), 0.001, "Custom flowRate");
        assertEquals(5, config.gatherRadius(), "Custom gatherRadius");
        assertEquals(2000.0, config.maxStorage(), 0.001, "Custom maxStorage");
    }

    private static void testZeroFlowRate() {
        ManaConfig config = new ManaConfig(0.0, 1, 1.0);
        assertEquals(0.0, config.flowRate(), 0.001, "Zero flowRate");
        assertEquals(1, config.gatherRadius(), "Zero flowRate gatherRadius");
        assertEquals(1.0, config.maxStorage(), 0.001, "Zero flowRate maxStorage");
    }

    private static void testMinimumGatherRadius() {
        ManaConfig config = new ManaConfig(0.1, 1, 1.0);
        assertEquals(1, config.gatherRadius(), "Minimum gatherRadius");
    }

    private static void testNegativeFlowRateThrows() {
        try {
            new ManaConfig(-0.1, 1, 1.0);
            failed++;
            throw new AssertionError("Negative flowRate: expected IllegalArgumentException");
        } catch (IllegalArgumentException e) {
            assertTrue(e.getMessage().contains("flowRate must be >= 0"), "Negative flowRate message");
        }
    }

    private static void testNonFiniteFlowRateThrows() {
        try {
            new ManaConfig(Double.POSITIVE_INFINITY, 1, 1.0);
            failed++;
            throw new AssertionError("Non-finite flowRate: expected IllegalArgumentException");
        } catch (IllegalArgumentException e) {
            assertTrue(e.getMessage().contains("flowRate must be finite"), "Non-finite flowRate message");
        }
    }

    private static void testNaNFlowRateThrows() {
        try {
            new ManaConfig(Double.NaN, 1, 1.0);
            failed++;
            throw new AssertionError("NaN flowRate: expected IllegalArgumentException");
        } catch (IllegalArgumentException e) {
            assertTrue(e.getMessage().contains("flowRate must be finite"), "NaN flowRate message");
        }
    }

    private static void testZeroGatherRadiusThrows() {
        try {
            new ManaConfig(0.1, 0, 1.0);
            failed++;
            throw new AssertionError("Zero gatherRadius: expected IllegalArgumentException");
        } catch (IllegalArgumentException e) {
            assertTrue(e.getMessage().contains("gatherRadius must be >= 1"), "Zero gatherRadius message");
        }
    }

    private static void testNegativeGatherRadiusThrows() {
        try {
            new ManaConfig(0.1, -1, 1.0);
            failed++;
            throw new AssertionError("Negative gatherRadius: expected IllegalArgumentException");
        } catch (IllegalArgumentException e) {
            assertTrue(e.getMessage().contains("gatherRadius must be >= 1"), "Negative gatherRadius message");
        }
    }

    private static void testZeroMaxStorageThrows() {
        try {
            new ManaConfig(0.1, 1, 0.0);
            failed++;
            throw new AssertionError("Zero maxStorage: expected IllegalArgumentException");
        } catch (IllegalArgumentException e) {
            assertTrue(e.getMessage().contains("maxStorage must be > 0"), "Zero maxStorage message");
        }
    }

    private static void testNegativeMaxStorageThrows() {
        try {
            new ManaConfig(0.1, 1, -1.0);
            failed++;
            throw new AssertionError("Negative maxStorage: expected IllegalArgumentException");
        } catch (IllegalArgumentException e) {
            assertTrue(e.getMessage().contains("maxStorage must be > 0"), "Negative maxStorage message");
        }
    }

    private static void testNonFiniteMaxStorageThrows() {
        try {
            new ManaConfig(0.1, 1, Double.POSITIVE_INFINITY);
            failed++;
            throw new AssertionError("Non-finite maxStorage: expected IllegalArgumentException");
        } catch (IllegalArgumentException e) {
            assertTrue(e.getMessage().contains("maxStorage must be finite"), "Non-finite maxStorage message");
        }
    }

    private static void testNaNMaxStorageThrows() {
        try {
            new ManaConfig(0.1, 1, Double.NaN);
            failed++;
            throw new AssertionError("NaN maxStorage: expected IllegalArgumentException");
        } catch (IllegalArgumentException e) {
            assertTrue(e.getMessage().contains("maxStorage must be finite"), "NaN maxStorage message");
        }
    }

    private static void testImmutability() {
        ManaConfig config = new ManaConfig(0.25, 3, 1000.0);
        assertEquals(0.25, config.flowRate(), 0.001, "Immutability flowRate");
        assertEquals(3, config.gatherRadius(), "Immutability gatherRadius");
        assertEquals(1000.0, config.maxStorage(), 0.001, "Immutability maxStorage");
    }
}
