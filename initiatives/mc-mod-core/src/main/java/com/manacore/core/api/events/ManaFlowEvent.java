package com.manacore.core.api.events;

/**
 * Immutable record representing a mana flow event.
 * Captures source position, target position, amount, and direction of mana flow.
 */
public record ManaFlowEvent(
    int sourceX,
    int sourceY,
    int sourceZ,
    int targetX,
    int targetY,
    int targetZ,
    double amount,
    int directionX,
    int directionY,
    int directionZ
) {
    
    /**
     * Creates a new ManaFlowEvent with validation.
     * 
     * @param sourceX the x-coordinate of the source
     * @param sourceY the y-coordinate of the source
     * @param sourceZ the z-coordinate of the source
     * @param targetX the x-coordinate of the target
     * @param targetY the y-coordinate of the target
     * @param targetZ the z-coordinate of the target
     * @param amount the amount of mana to flow (must be finite and non-negative)
     * @param directionX the x-component of direction (-1, 0, or 1)
     * @param directionY the y-component of direction (-1, 0, or 1)
     * @param directionZ the z-component of direction (-1, 0, or 1)
     * @throws IllegalArgumentException if any validation fails
     */
    public ManaFlowEvent {
        if (!Double.isFinite(amount)) {
            throw new IllegalArgumentException("Amount must be finite");
        }
        if (amount < 0) {
            throw new IllegalArgumentException("Amount must be non-negative");
        }
        if (directionX < -1 || directionX > 1) {
            throw new IllegalArgumentException("directionX must be between -1 and 1");
        }
        if (directionY < -1 || directionY > 1) {
            throw new IllegalArgumentException("directionY must be between -1 and 1");
        }
        if (directionZ < -1 || directionZ > 1) {
            throw new IllegalArgumentException("directionZ must be between -1 and 1");
        }
    }
}
