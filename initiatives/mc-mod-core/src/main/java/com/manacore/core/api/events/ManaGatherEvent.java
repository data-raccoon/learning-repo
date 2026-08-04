package com.manacore.core.api.events;

/**
 * Immutable record representing a mana gather event.
 * Captures center position, radius, and amount of mana gathered.
 */
public record ManaGatherEvent(
    int centerX,
    int centerY,
    int centerZ,
    int radius,
    double amount
) {
    
    /**
     * Creates a new ManaGatherEvent with validation.
     * 
     * @param centerX the x-coordinate of the gather center
     * @param centerY the y-coordinate of the gather center
     * @param centerZ the z-coordinate of the gather center
     * @param radius the gather radius (must be non-negative)
     * @param amount the amount of mana gathered (must be finite and non-negative)
     * @throws IllegalArgumentException if any validation fails
     */
    public ManaGatherEvent {
        if (radius < 0) {
            throw new IllegalArgumentException("Radius must be non-negative");
        }
        if (!Double.isFinite(amount)) {
            throw new IllegalArgumentException("Amount must be finite");
        }
        if (amount < 0) {
            throw new IllegalArgumentException("Amount must be non-negative");
        }
    }
}
