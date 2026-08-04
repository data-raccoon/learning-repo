package com.manacore.core.config;

public final class ManaConfigContract {
    private static int checks;
    private static void expect(boolean value, String message) { checks++; if (!value) throw new AssertionError(message); }
    private static void rejects(Runnable action, String message) {
        checks++;
        try { action.run(); } catch (IllegalArgumentException expected) { return; }
        throw new AssertionError(message);
    }
    public static void main(String[] args) {
        var defaults = ManaConfig.defaults();
        expect(defaults.flowRate() == 0.25, "default flow rate");
        expect(defaults.gatherRadius() == 3, "default gather radius");
        expect(defaults.maxStorage() == 1000.0, "default max storage");
        var custom = new ManaConfig(0.0, 1, 1.0);
        expect(custom.flowRate() == 0.0 && custom.gatherRadius() == 1, "boundary values");
        rejects(() -> new ManaConfig(-0.1, 1, 1.0), "negative flow rejected");
        rejects(() -> new ManaConfig(Double.NaN, 1, 1.0), "NaN flow rejected");
        rejects(() -> new ManaConfig(0.1, 0, 1.0), "zero radius rejected");
        rejects(() -> new ManaConfig(0.1, 1, Double.POSITIVE_INFINITY), "infinite storage rejected");
        rejects(() -> new ManaConfig(0.1, 1, 0.0), "zero storage rejected");
        System.out.println("Mana config contract passed " + checks + " checks.");
    }
}
