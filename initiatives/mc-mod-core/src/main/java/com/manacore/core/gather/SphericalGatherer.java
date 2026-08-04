package com.manacore.core.gather;

import com.manacore.core.storage.ChunkManaMap;

/**
 * Pure Java spherical gatherer for mana collection.
 * Collects mana from positions within an inclusive Euclidean sphere around a center.
 * Iteration order is deterministic: X from center-radius to center+radius,
 * then Y, then Z. Drains each position up to the remaining cap without producing
 * negative mana. Conserves total mana (gathered + remaining = original).
 */
public final class SphericalGatherer {

    private SphericalGatherer() {
        // Utility class - no instantiation
    }

    /**
     * Gathers mana from positions within an inclusive Euclidean sphere around the center.
     * Only coordinates where squared Euclidean distance from center <= radius squared are drained.
     * Iteration order is deterministic: X from (centerX - radius) to (centerX + radius),
     * then Y from (centerY - radius) to (centerY + radius), then Z from (centerZ - radius) to (centerZ + radius).
     * Each visited position is drained up to the remaining cap without producing negative mana.
     *
     * @param map the mana storage map
     * @param centerX the X coordinate of the sphere center
     * @param centerY the Y coordinate of the sphere center
     * @param centerZ the Z coordinate of the sphere center
     * @param radius the sphere radius (must be non-negative)
     * @param maxTotal the maximum total mana to gather (must be positive and finite)
     * @return the total mana gathered (0 for invalid radius or maxTotal)
     */
    public static double gather(ChunkManaMap map, int centerX, int centerY, int centerZ, int radius, double maxTotal) {
        // Validate radius and maxTotal
        if (radius < 0) {
            return 0.0;
        }
        if (maxTotal <= 0 || !Double.isFinite(maxTotal)) {
            return 0.0;
        }

        double gathered = 0.0;
        double remainingCap = maxTotal;

        // Calculate squared radius for efficient distance check
        long radiusSquared = (long) radius * radius;

        // Iterate deterministically: X, then Y, then Z
        // From center-radius to center+radius inclusive
        int minX = centerX - radius;
        int maxX = centerX + radius;
        int minY = centerY - radius;
        int maxY = centerY + radius;
        int minZ = centerZ - radius;
        int maxZ = centerZ + radius;

        for (int x = minX; x <= maxX; x++) {
            for (int y = minY; y <= maxY; y++) {
                for (int z = minZ; z <= maxZ; z++) {
                    // Check if this position is within the inclusive Euclidean sphere
                    long dx = (long) x - centerX;
                    long dy = (long) y - centerY;
                    long dz = (long) z - centerZ;
                    long distanceSquared = dx * dx + dy * dy + dz * dz;

                    if (distanceSquared > radiusSquared) {
                        continue;
                    }

                    // Get current mana at this position
                    double currentMana = map.get(x, y, z);
                    if (currentMana <= 0) {
                        continue;
                    }

                    // Calculate how much we can take from this position
                    // Don't take more than remaining cap or current mana
                    double takeAmount = Math.min(remainingCap, currentMana);
                    if (takeAmount <= 0) {
                        continue;
                    }

                    // Drain the position
                    map.add(x, y, z, -takeAmount);
                    gathered += takeAmount;
                    remainingCap -= takeAmount;

                    // If we've reached the cap, stop gathering
                    if (remainingCap <= 0) {
                        return gathered;
                    }
                }
            }
        }

        return gathered;
    }
}
