package com.manacore.core.config;

/**
 * Immutable configuration record for mana system parameters.
 * Defines flow rate, gather radius, and maximum storage with validation.
 */
public record ManaConfig(
    double flowRate,
    int gatherRadius,
    double maxStorage
) {

    /**
     * Creates a new ManaConfig with validation.
     *
     * @param flowRate the mana flow rate (must be finite and >= 0)
     * @param gatherRadius the gather radius (must be >= 1)
     * @param maxStorage the maximum storage (must be finite and > 0)
     * @throws IllegalArgumentException if any validation fails
     */
    public ManaConfig {
        if (!Double.isFinite(flowRate)) {
            throw new IllegalArgumentException("flowRate must be finite");
        }
        if (flowRate < 0) {
            throw new IllegalArgumentException("flowRate must be >= 0");
        }
        if (gatherRadius < 1) {
            throw new IllegalArgumentException("gatherRadius must be >= 1");
        }
        if (!Double.isFinite(maxStorage)) {
            throw new IllegalArgumentException("maxStorage must be finite");
        }
        if (maxStorage <= 0) {
            throw new IllegalArgumentException("maxStorage must be > 0");
        }
    }

    /**
     * Returns the default ManaConfig with predefined values.
     *
     * @return new ManaConfig(0.25, 3, 1000.0)
     */
    public static ManaConfig defaults() {
        return new ManaConfig(0.25, 3, 1000.0);
    }
}
