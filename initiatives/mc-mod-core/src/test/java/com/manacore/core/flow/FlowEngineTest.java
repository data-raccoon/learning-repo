package com.manacore.core.flow;

import com.manacore.core.storage.ChunkManaMap;
import java.util.List;

/**
 * Executable test for FlowEngine.
 * Tests flowPair, flowAll, and Edge APIs with native Java assert statements.
 */
public class FlowEngineTest {

    public static void main(String[] args) {
        testFlowPairBasic();
        testFlowPairEqualMana();
        testFlowPairInvalidMaxTransfer();
        testFlowPairConservation();
        testFlowPairDirection();
        testFlowAllBasic();
        testFlowAllEmpty();
        testFlowAllInvalidMaxTransfer();
        testEdgeRecord();
        testFlowPairCappedBySource();
        System.out.println("All FlowEngine tests passed.");
    }

    private static void testFlowPairBasic() {
        ChunkManaMap map = new ChunkManaMap();
        map.set(0, 0, 0, 10.0);
        map.set(1, 0, 0, 0.0);
        
        double moved = FlowEngine.flowPair(map, 0, 0, 0, 1, 0, 0, 5.0);
        assert moved == 5.0 : "Expected 5.0 moved, got " + moved;
        assert map.get(0, 0, 0) == 5.0 : "Expected source to have 5.0, got " + map.get(0, 0, 0);
        assert map.get(1, 0, 0) == 5.0 : "Expected target to have 5.0, got " + map.get(1, 0, 0);
    }

    private static void testFlowPairEqualMana() {
        ChunkManaMap map = new ChunkManaMap();
        map.set(0, 0, 0, 5.0);
        map.set(1, 0, 0, 5.0);
        
        double moved = FlowEngine.flowPair(map, 0, 0, 0, 1, 0, 0, 5.0);
        assert moved == 0.0 : "Expected 0.0 moved for equal mana, got " + moved;
        assert map.get(0, 0, 0) == 5.0 : "Expected source unchanged, got " + map.get(0, 0, 0);
        assert map.get(1, 0, 0) == 5.0 : "Expected target unchanged, got " + map.get(1, 0, 0);
    }

    private static void testFlowPairInvalidMaxTransfer() {
        ChunkManaMap map = new ChunkManaMap();
        map.set(0, 0, 0, 10.0);
        map.set(1, 0, 0, 0.0);
        
        double moved1 = FlowEngine.flowPair(map, 0, 0, 0, 1, 0, 0, 0.0);
        assert moved1 == 0.0 : "Expected 0.0 for zero maxTransfer, got " + moved1;
        
        double moved2 = FlowEngine.flowPair(map, 0, 0, 0, 1, 0, 0, -1.0);
        assert moved2 == 0.0 : "Expected 0.0 for negative maxTransfer, got " + moved2;
        
        double moved3 = FlowEngine.flowPair(map, 0, 0, 0, 1, 0, 0, Double.POSITIVE_INFINITY);
        assert moved3 == 0.0 : "Expected 0.0 for infinite maxTransfer, got " + moved3;
    }

    private static void testFlowPairConservation() {
        ChunkManaMap map = new ChunkManaMap();
        map.set(0, 0, 0, 10.0);
        map.set(1, 0, 0, 0.0);
        
        double totalBefore = map.get(0, 0, 0) + map.get(1, 0, 0);
        double moved = FlowEngine.flowPair(map, 0, 0, 0, 1, 0, 0, 3.0);
        double totalAfter = map.get(0, 0, 0) + map.get(1, 0, 0);
        
        assert Math.abs(totalBefore - totalAfter) < 1e-10 : "Mana not conserved: before=" + totalBefore + ", after=" + totalAfter;
    }

    private static void testFlowPairDirection() {
        ChunkManaMap map = new ChunkManaMap();
        map.set(0, 0, 0, 0.0);
        map.set(1, 0, 0, 10.0);
        
        // Flow should go from B (higher) to A (lower)
        double moved = FlowEngine.flowPair(map, 0, 0, 0, 1, 0, 0, 5.0);
        assert moved == 5.0 : "Expected 5.0 moved, got " + moved;
        assert map.get(0, 0, 0) == 5.0 : "Expected A to have 5.0, got " + map.get(0, 0, 0);
        assert map.get(1, 0, 0) == 5.0 : "Expected B to have 5.0, got " + map.get(1, 0, 0);
    }

    private static void testFlowAllBasic() {
        ChunkManaMap map = new ChunkManaMap();
        map.set(0, 0, 0, 10.0);
        map.set(1, 0, 0, 0.0);
        map.set(2, 0, 0, 0.0);
        
        List<FlowEngine.Edge> edges = List.of(
            new FlowEngine.Edge(0, 0, 0, 1, 0, 0),
            new FlowEngine.Edge(0, 0, 0, 2, 0, 0)
        );
        
        double totalMoved = FlowEngine.flowAll(map, edges, 2.5);
        assert totalMoved == 5.0 : "Expected 5.0 total moved, got " + totalMoved;
    }

    private static void testFlowAllEmpty() {
        ChunkManaMap map = new ChunkManaMap();
        map.set(0, 0, 0, 10.0);
        
        List<FlowEngine.Edge> edges = List.of();
        double totalMoved = FlowEngine.flowAll(map, edges, 5.0);
        assert totalMoved == 0.0 : "Expected 0.0 for empty edges, got " + totalMoved;
    }

    private static void testFlowAllInvalidMaxTransfer() {
        ChunkManaMap map = new ChunkManaMap();
        map.set(0, 0, 0, 10.0);
        map.set(1, 0, 0, 0.0);
        
        List<FlowEngine.Edge> edges = List.of(new FlowEngine.Edge(0, 0, 0, 1, 0, 0));
        double totalMoved = FlowEngine.flowAll(map, edges, 0.0);
        assert totalMoved == 0.0 : "Expected 0.0 for invalid maxTransfer, got " + totalMoved;
    }

    private static void testEdgeRecord() {
        FlowEngine.Edge edge = new FlowEngine.Edge(0, 1, 2, 3, 4, 5);
        assert edge.ax() == 0 && edge.ay() == 1 && edge.az() == 2 : "Edge A coordinates incorrect";
        assert edge.bx() == 3 && edge.by() == 4 && edge.bz() == 5 : "Edge B coordinates incorrect";
    }

    private static void testFlowPairCappedBySource() {
        ChunkManaMap map = new ChunkManaMap();
        map.set(0, 0, 0, 3.0);
        map.set(1, 0, 0, 0.0);
        
        // maxTransfer is 10, but source only has 3, and gradient magnitude / 2 = 1.5
        double moved = FlowEngine.flowPair(map, 0, 0, 0, 1, 0, 0, 10.0);
        assert moved == 1.5 : "Expected 1.5 moved (capped by gradient/2), got " + moved;
        assert map.get(0, 0, 0) == 1.5 : "Expected source to have 1.5, got " + map.get(0, 0, 0);
        assert map.get(1, 0, 0) == 1.5 : "Expected target to have 1.5, got " + map.get(1, 0, 0);
    }
}