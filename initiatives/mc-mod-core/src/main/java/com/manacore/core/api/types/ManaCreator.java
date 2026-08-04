package com.manacore.core.api.types;

/**
 * Interface for entities or blocks that create mana.
 * Server is authoritative for all mana operations.
 */
public interface ManaCreator {
    
    /**
     * Returns the radius within which this creator can inject mana.
     * @return the injection radius in blocks
     */
    int injectionRadius();
    
    /**
     * Returns the amount of mana produced per tick.
     * @return mana generated per tick
     */
    double manaPerTick();
}
