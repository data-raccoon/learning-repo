package com.manacore.core.api.types;

public final class ManaApiTypesContract {
    private static int checks;
    private static void expect(boolean value, String message) {
        checks++;
        if (!value) throw new AssertionError(message);
    }
    public static void main(String[] args) throws Exception {
        expect(ManaConsumer.class.isInterface(), "consumer interface");
        expect(ManaCreator.class.isInterface(), "creator interface");
        expect(ManaStorage.class.isInterface(), "storage interface");
        expect(ManaConsumer.class.getMethod("gatherRadius").getReturnType() == int.class, "gatherRadius signature");
        expect(ManaConsumer.class.getMethod("acceptMana", double.class).getReturnType() == double.class, "acceptMana signature");
        expect(ManaCreator.class.getMethod("injectionRadius").getReturnType() == int.class, "injectionRadius signature");
        expect(ManaCreator.class.getMethod("manaPerTick").getReturnType() == double.class, "manaPerTick signature");
        expect(ManaStorage.class.getMethod("storedMana").getReturnType() == double.class, "storedMana signature");
        expect(ManaStorage.class.getMethod("capacity").getReturnType() == double.class, "capacity signature");
        expect(ManaStorage.class.getMethod("insert", double.class).getReturnType() == double.class, "insert signature");
        expect(ManaStorage.class.getMethod("extract", double.class).getReturnType() == double.class, "extract signature");
        System.out.println("Mana API types contract passed " + checks + " checks.");
    }
}
