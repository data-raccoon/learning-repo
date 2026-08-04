package com.manacore.core.flow;

import com.manacore.core.storage.ChunkManaMap;
import java.util.List;

public final class FlowEngineContract {
    private static int checks;

    private static void expect(boolean condition, String message) {
        checks++;
        if (!condition) {
            throw new AssertionError(message);
        }
    }

    private static void expectClose(double expected, double actual, String message) {
        expect(Math.abs(expected - actual) < 1.0e-9, message + ": " + actual);
    }

    public static void main(String[] args) {
        ChunkManaMap map = new ChunkManaMap();
        map.set(0, 0, 0, 10.0);
        map.set(1, 0, 0, 2.0);
        double before = map.get(0, 0, 0) + map.get(1, 0, 0);
        expectClose(3.0, FlowEngine.flowPair(map, 0, 0, 0, 1, 0, 0, 3.0), "cap must limit transfer");
        expectClose(7.0, map.get(0, 0, 0), "source after capped transfer");
        expectClose(5.0, map.get(1, 0, 0), "target after capped transfer");
        expectClose(before, map.get(0, 0, 0) + map.get(1, 0, 0), "pair conservation");

        expectClose(1.0, FlowEngine.flowPair(map, 1, 0, 0, 0, 0, 0, 99.0), "reversed arguments equalize");
        expectClose(6.0, map.get(0, 0, 0), "first value equalized");
        expectClose(6.0, map.get(1, 0, 0), "second value equalized");
        expectClose(0.0, FlowEngine.flowPair(map, 0, 0, 0, 1, 0, 0, 1.0), "equal values do not flow");
        expectClose(0.0, FlowEngine.flowPair(map, 0, 0, 0, 1, 0, 0, Double.NaN), "NaN cap rejected");
        expectClose(0.0, FlowEngine.flowPair(map, 0, 0, 0, 1, 0, 0, -1.0), "negative cap rejected");

        ChunkManaMap chain = new ChunkManaMap();
        chain.set(0, 0, 0, 12.0);
        FlowEngine.Edge first = new FlowEngine.Edge(0, 0, 0, 1, 0, 0);
        FlowEngine.Edge second = new FlowEngine.Edge(1, 0, 0, 2, 0, 0);
        expectClose(6.0, FlowEngine.flowAll(chain, List.of(first, second), 4.0), "flowAll total");
        expectClose(8.0, chain.get(0, 0, 0), "chain first");
        expectClose(2.0, chain.get(1, 0, 0), "chain middle");
        expectClose(2.0, chain.get(2, 0, 0), "chain last");
        expectClose(12.0, chain.get(0, 0, 0) + chain.get(1, 0, 0) + chain.get(2, 0, 0), "flowAll conservation");

        System.out.println("Flow contract passed " + checks + " checks.");
    }
}
