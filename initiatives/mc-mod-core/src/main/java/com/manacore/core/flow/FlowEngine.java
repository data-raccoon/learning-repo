package com.manacore.core.flow;

import com.manacore.core.storage.ChunkManaMap;

/**
 * Pure Java flow engine for mana transfer between positions.
 * Uses GradientCalculator to determine flow direction and magnitude.
 * Transfers mana from higher to lower concentration, conserving total mana.
 */
public final class FlowEngine {

    private FlowEngine() {
        // Utility class - no instantiation
    }

    /**
     * Transfers mana between two positions along the gradient.
     * Uses GradientCalculator to determine direction and magnitude.
     * Moves min(maxTransfer, gradient magnitude / 2) from higher to lower.
     * Conserves total mana and returns zero for equal mana or invalid/non-positive maxTransfer.
     *
     * @param map the mana storage map
     * @param ax the X coordinate of position A
     * @param ay the Y coordinate of position A
     * @param az the Z coordinate of position A
     * @param bx the X coordinate of position B
     * @param by the Y coordinate of position B
     * @param bz the Z coordinate of position B
     * @param maxTransfer the maximum amount to transfer (must be positive and finite)
     * @return the amount of mana moved from higher to lower
     */
    public static double flowPair(ChunkManaMap map, int ax, int ay, int az, int bx, int by, int bz, double maxTransfer) {
        // Validate maxTransfer
        if (maxTransfer <= 0 || !Double.isFinite(maxTransfer)) {
            return 0.0;
        }

        // Calculate gradient
        GradientCalculator.Gradient gradient = GradientCalculator.calculate(map, ax, ay, az, bx, by, bz);

        // If no gradient (equal mana), return 0
        if (gradient.isZero()) {
            return 0.0;
        }

        // Calculate transfer amount: min(maxTransfer, magnitude / 2)
        // This ensures we never overshoot equalization (half the difference)
        double transferAmount = Math.min(maxTransfer, gradient.magnitude() / 2.0);

        // Determine source and target based on gradient direction
        // Gradient points from higher to lower mana
        double manaA = map.get(ax, ay, az);
        double manaB = map.get(bx, by, bz);

        int sourceX, sourceY, sourceZ;
        int targetX, targetY, targetZ;

        if (manaA > manaB) {
            // A has more mana, flow from A to B
            sourceX = ax;
            sourceY = ay;
            sourceZ = az;
            targetX = bx;
            targetY = by;
            targetZ = bz;
        } else {
            // B has more mana, flow from B to A
            sourceX = bx;
            sourceY = by;
            sourceZ = bz;
            targetX = ax;
            targetY = ay;
            targetZ = az;
        }

        // Get current values
        double sourceMana = map.get(sourceX, sourceY, sourceZ);
        double targetMana = map.get(targetX, targetY, targetZ);

        // Calculate actual transfer (don't transfer more than source has)
        double actualTransfer = Math.min(transferAmount, sourceMana);

        if (actualTransfer <= 0 || !Double.isFinite(actualTransfer)) {
            return 0.0;
        }

        // Perform the transfer
        map.add(sourceX, sourceY, sourceZ, -actualTransfer);
        map.add(targetX, targetY, targetZ, actualTransfer);

        return actualTransfer;
    }

    /**
     * Represents an edge between two mana positions for flow processing.
     * Immutable record connecting source and target coordinates.
     */
    public static record Edge(int ax, int ay, int az, int bx, int by, int bz) {
        /**
         * Creates a new Edge record.
         *
         * @param ax the X coordinate of position A
         * @param ay the Y coordinate of position A
         * @param az the Z coordinate of position A
         * @param bx the X coordinate of position B
         * @param by the Y coordinate of position B
         * @param bz the Z coordinate of position B
         */
        public Edge {
            // No validation needed - coordinates can be any integer
        }
    }

    /**
     * Processes multiple edges in iteration order, transferring mana along each.
     * Uses the specified maxTransferPerEdge for each individual edge.
     * Returns the total amount of mana moved across all edges.
     *
     * @param map the mana storage map
     * @param edges the iterable of edges to process
     * @param maxTransferPerEdge the maximum transfer amount per edge (must be positive and finite)
     * @return the total amount of mana moved
     */
    public static double flowAll(ChunkManaMap map, Iterable<Edge> edges, double maxTransferPerEdge) {
        // Validate maxTransferPerEdge
        if (maxTransferPerEdge <= 0 || !Double.isFinite(maxTransferPerEdge)) {
            return 0.0;
        }

        double totalMoved = 0.0;

        // Process edges in iteration order
        for (Edge edge : edges) {
            double moved = flowPair(map, edge.ax(), edge.ay(), edge.az(), edge.bx(), edge.by(), edge.bz(), maxTransferPerEdge);
            totalMoved += moved;
        }

        return totalMoved;
    }
}