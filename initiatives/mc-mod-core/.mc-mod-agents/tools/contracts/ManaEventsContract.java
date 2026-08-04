package com.manacore.core.api.events;

public final class ManaEventsContract {
    private static int checks;
    private static void expect(boolean value, String message) { checks++; if (!value) throw new AssertionError(message); }
    private static void rejects(Runnable action, String message) {
        checks++;
        try { action.run(); } catch (IllegalArgumentException expected) { return; }
        throw new AssertionError(message);
    }
    public static void main(String[] args) {
        var flow = new ManaFlowEvent(1, 2, 3, 4, 5, 6, 2.5, -1, 0, 1);
        expect(flow.sourceX() == 1 && flow.targetZ() == 6 && flow.amount() == 2.5, "flow accessors");
        rejects(() -> new ManaFlowEvent(0,0,0,1,0,0, Double.NaN, 1,0,0), "NaN flow rejected");
        rejects(() -> new ManaFlowEvent(0,0,0,1,0,0, 1.0, 2,0,0), "invalid direction rejected");
        var gather = new ManaGatherEvent(7, 8, 9, 3, 4.5);
        expect(gather.radius() == 3 && gather.amount() == 4.5, "gather accessors");
        rejects(() -> new ManaGatherEvent(0,0,0,-1,1.0), "negative radius rejected");
        var store = new ManaStoreEvent("collector-1", 6.0, ManaStoreEvent.Operation.INSERT);
        expect(store.storageId().equals("collector-1") && store.operation() == ManaStoreEvent.Operation.INSERT, "store accessors");
        rejects(() -> new ManaStoreEvent("", 1.0, ManaStoreEvent.Operation.EXTRACT), "blank id rejected");
        rejects(() -> new ManaStoreEvent("x", -1.0, ManaStoreEvent.Operation.INSERT), "negative amount rejected");
        System.out.println("Mana events contract passed " + checks + " checks.");
    }
}
