package com.manacore.core.api.types;

/**
 * Interface for entities or blocks that store mana.
 * Server is authoritative for all mana operations.
 */
public interface ManaStorage {
    
    /**
     * Returns the current amount of mana stored.
     * @return the amount of mana currently stored
     */
    double storedMana();
    
    /**
     * Returns the maximum mana capacity.
     * @return the maximum mana capacity
     */
    double capacity();
    
    /**
     * Inserts mana into storage.
     * @param amount the amount of mana to insert
     * @return the amount of mana actually inserted
     */
    double insert(double amount);
    
    /**
     * Extracts mana from storage.
     * @param amount the amount of mana to extract
     * @return the amount of mana actually extracted
     */
    double extract(double amount);
}
