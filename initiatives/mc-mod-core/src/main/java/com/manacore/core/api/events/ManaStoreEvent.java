package com.manacore.core.api.events;

/**
 * Immutable record representing a mana storage event.
 * Captures storage ID, amount, and operation type.
 */
public record ManaStoreEvent(
    String storageId,
    double amount,
    Operation operation
) {
    
    /**
     * Operation types for mana storage events.
     */
    public enum Operation {
        INSERT,
        EXTRACT
    }
    
    /**
     * Creates a new ManaStoreEvent with validation.
     * 
     * @param storageId the ID of the storage entity/block (must be non-blank)
     * @param amount the amount of mana (must be finite and non-negative)
     * @param operation the operation type (must be non-null)
     * @throws IllegalArgumentException if any validation fails
     * @throws NullPointerException if storageId or operation is null
     */
    public ManaStoreEvent {
        if (storageId == null) {
            throw new NullPointerException("StorageId must not be null");
        }
        if (storageId.isBlank()) {
            throw new IllegalArgumentException("StorageId must not be blank");
        }
        if (!Double.isFinite(amount)) {
            throw new IllegalArgumentException("Amount must be finite");
        }
        if (amount < 0) {
            throw new IllegalArgumentException("Amount must be non-negative");
        }
        if (operation == null) {
            throw new NullPointerException("Operation must not be null");
        }
    }
}
