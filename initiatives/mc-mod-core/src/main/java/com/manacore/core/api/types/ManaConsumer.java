package com.manacore.core.api.types;

/**
 * Interface for entities or blocks that consume mana.
 * Server is authoritative for all mana operations.
 */
public interface ManaConsumer {
    
    /**
     * Returns the radius within which this consumer can gather mana.
     * @return the gather radius in blocks
     */
    int gatherRadius();
    
    /**
     * Accepts an offered amount of mana.
     * @param offered the amount of mana offered
     * @return the amount of mana actually accepted
     */
    double acceptMana(double offered);
}
