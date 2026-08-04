package com.manacore.core.api;

import com.manacore.core.config.ManaConfig;
import java.lang.reflect.Constructor;
import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.lang.reflect.Modifier;
import java.util.List;

/** Controller-authored structural and black-box contract for ManaAPI. */
public final class ManaApiFacadeContract {
    private static int checks;

    private ManaApiFacadeContract() {}

    public static void main(String[] args) throws Exception {
        structure();
        behavior();
        System.out.println("Mana API facade contract passed " + checks + " checks.");
    }

    private static void structure() throws Exception {
        require(Modifier.isFinal(ManaAPI.class.getModifiers()), "class is final");
        Constructor<?> constructor = ManaAPI.class.getDeclaredConstructor();
        require(Modifier.isPublic(constructor.getModifiers()), "constructor is public");
        for (Field field : ManaAPI.class.getDeclaredFields()) {
            require(!Modifier.isStatic(field.getModifiers()), "state must not be static");
            require(Modifier.isPrivate(field.getModifiers()), "state must be private");
        }
        List<Method> methods = List.of(
                method("getMana", int.class, int.class, int.class),
                method("setMana", int.class, int.class, int.class, double.class),
                method("addMana", int.class, int.class, int.class, double.class),
                method("gatherMana", int.class, int.class, int.class, int.class, double.class),
                method("flowMana", int.class, int.class, int.class,
                        int.class, int.class, int.class, double.class),
                method("getConfig"),
                method("setConfig", ManaConfig.class));
        require(ManaAPI.class.getDeclaredMethods().length == methods.size(),
                "no additional methods");
        for (Method method : methods) {
            int modifiers = method.getModifiers();
            require(Modifier.isPublic(modifiers), method.getName() + " is public");
            require(!Modifier.isStatic(modifiers), method.getName() + " is instance-scoped");
            require(Modifier.isSynchronized(modifiers), method.getName() + " is synchronized");
        }
    }

    private static void behavior() {
        ManaAPI first = new ManaAPI();
        ManaAPI second = new ManaAPI();
        first.setMana(100, -2, 7, 10.0);
        require(second.getMana(100, -2, 7) == 0.0, "instances isolate storage");
        require(first.addMana(100, -2, 7, 5.0) == 15.0, "add returns result");
        require(first.addMana(100, -2, 7, Double.NaN) == 15.0, "invalid add ignored");
        require(first.addMana(100, -2, 7, -30.0) == 0.0, "negative result removed");

        first.setMana(200, 0, 0, 20.0);
        first.setMana(201, 0, 0, 0.0);
        require(first.flowMana(200, 0, 0, 201, 0, 0, 100.0) == 10.0,
                "flow equalizes");
        require(first.getMana(200, 0, 0) + first.getMana(201, 0, 0) == 20.0,
                "flow conserves");

        ManaConfig custom = new ManaConfig(0.75, 2, 500.0);
        first.setConfig(custom);
        require(first.getConfig() == custom, "config retained");
        require(second.getConfig().equals(ManaConfig.defaults()), "config isolated");
    }

    private static Method method(String name, Class<?>... parameters) throws Exception {
        return ManaAPI.class.getDeclaredMethod(name, parameters);
    }

    private static void require(boolean condition, String message) {
        checks++;
        if (!condition) {
            throw new AssertionError(message);
        }
    }
}
