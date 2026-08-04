package com.manacore.core.flow;

import com.manacore.core.storage.ChunkManaMap;

/**
 * Pure Java gradient calculator for mana flow direction and magnitude.
 * Computes the direction vector and magnitude between two mana positions.
 * Direction components are -1, 0, or 1 and point from higher mana to lower mana.
 * Magnitude is the absolute mana difference.
 */
public final class GradientCalculator {

    private GradientCalculator() {
        // Utility class - no instantiation
    }

    /**
     * Calculates the gradient between two positions in the mana map.
     *
     * @param map the mana storage map
     * @param ax the X coordinate of position A
     * @param ay the Y coordinate of position A
     * @param az the Z coordinate of position A
     * @param bx the X coordinate of position B
     * @param by the Y coordinate of position B
     * @param bz the Z coordinate of position B
     * @return a Gradient record with direction components and magnitude
     */
    public static Gradient calculate(ChunkManaMap map, int ax, int ay, int az, int bx, int by, int bz) {
        double manaA = map.get(ax, ay, az);
        double manaB = map.get(bx, by, bz);

        double difference = manaA - manaB;

        // Handle equal values - return zero gradient
        if (difference == 0.0) {
            return new Gradient(0, 0, 0, 0.0);
        }

        // Calculate direction components (-1, 0, or 1)
        // Direction points from higher mana to lower mana
        int dx = calculateDirectionComponent(ax, bx, difference);
        int dy = calculateDirectionComponent(ay, by, difference);
        int dz = calculateDirectionComponent(az, bz, difference);

        // Magnitude is absolute difference
        double magnitude = Math.abs(difference);

        return new Gradient(dx, dy, dz, magnitude);
    }

    /**
     * Calculates a single direction component based on coordinate difference and mana difference.
     * Returns -1, 0, or 1 pointing from higher mana to lower mana.
     */
    private static int calculateDirectionComponent(int coordA, int coordB, double manaDifference) {
        int coordDiff = coordB - coordA;
        
        if (coordDiff == 0) {
            return 0;
        }
        
        // If mana at A is higher than at B (positive difference), 
        // direction should point from A to B (which is the direction of coordDiff)
        // If mana at A is lower than at B (negative difference),
        // direction should point from B to A (which is opposite of coordDiff)
        if (manaDifference > 0) {
            // Higher at A, flow toward B
            return Integer.signum(coordDiff);
        } else {
            // Higher at B, flow toward A (opposite direction)
            return -Integer.signum(coordDiff);
        }
    }

    /**
     * Immutable record representing a mana gradient.
     * Direction components are -1, 0, or 1 and point from higher mana to lower mana.
     * Magnitude is the absolute mana difference (always non-negative).
     */
    public static record Gradient(int dx, int dy, int dz, double magnitude) {
        /**
         * Creates a new Gradient record.
         *
         * @param dx the X direction component (-1, 0, or 1)
         * @param dy the Y direction component (-1, 0, or 1)
         * @param dz the Z direction component (-1, 0, or 1)
         * @param magnitude the absolute mana difference (must be non-negative)
         */
        public Gradient {
            // Validate direction components
            if (dx != -1 && dx != 0 && dx != 1) {
                throw new IllegalArgumentException("dx must be -1, 0, or 1, got: " + dx);
            }
            if (dy != -1 && dy != 0 && dy != 1) {
                throw new IllegalArgumentException("dy must be -1, 0, or 1, got: " + dy);
            }
            if (dz != -1 && dz != 0 && dz != 1) {
                throw new IllegalArgumentException("dz must be -1, 0, or 1, got: " + dz);
            }
            if (magnitude < 0 || !Double.isFinite(magnitude)) {
                throw new IllegalArgumentException("magnitude must be non-negative and finite, got: " + magnitude);
            }
        }

        /**
         * Checks if this is a zero gradient (no direction, zero magnitude).
         *
         * @return true if all direction components are 0 and magnitude is 0
         */
        public boolean isZero() {
            return dx == 0 && dy == 0 && dz == 0 && magnitude == 0.0;
        }

        /**
         * Checks if the gradient has any direction component.
         *
         * @return true if any direction component is non-zero
         */
        public boolean hasDirection() {
            return dx != 0 || dy != 0 || dz != 0;
        }
    }
}