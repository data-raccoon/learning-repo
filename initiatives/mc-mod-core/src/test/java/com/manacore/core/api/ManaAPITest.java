package com.manacore.core.api;

import com.manacore.core.config.ManaConfig;

/** Executable dependency-free behavior checks for the world-scoped facade. */
public final class ManaAPITest {
    private static int checks;

    private ManaAPITest() {}

    public static void main(String[] args) {
        storageAndInvalidInputs();
        gatheringAndFlow();
        configurationAndWorldIsolation();
        System.out.println("ManaAPITest passed " + checks + " checks.");
    }

    private static void storageAndInvalidInputs() {
        ManaAPI api = new ManaAPI();
        require(api.getMana(-4, 2, 9) == 0.0, "unset positions are zero");
        api.setMana(-4, 2, 9, 12.5);
        require(api.getMana(-4, 2, 9) == 12.5, "set/get round trip");
        require(api.addMana(-4, 2, 9, 2.5) == 15.0, "add returns stored result");
        require(api.addMana(-4, 2, 9, Double.NaN) == 15.0, "NaN delta is ignored");
        require(api.addMana(-4, 2, 9, -20.0) == 0.0, "negative result removes");
        api.setMana(-4, 2, 9, Double.POSITIVE_INFINITY);
        require(api.getMana(-4, 2, 9) == 0.0, "non-finite set removes");
        api.setMana(-4, 2, 9, Double.MAX_VALUE);
        require(api.addMana(-4, 2, 9, Double.MAX_VALUE) == Double.MAX_VALUE,
                "overflow clamps in storage");
    }

    private static void gatheringAndFlow() {
        ManaAPI api = new ManaAPI();
        api.setMana(-1, 0, 0, 10.0);
        api.setMana(1, 0, 0, 10.0);
        require(api.gatherMana(0, 0, 0, 1, 15.0) == 15.0, "gather obeys cap");
        require(api.getMana(-1, 0, 0) == 0.0, "gather visits lower X first");
        require(api.getMana(1, 0, 0) == 5.0, "gather ordering is deterministic");
        require(api.gatherMana(0, 0, 0, -1, 10.0) == 0.0,
                "negative radius is rejected");

        api.setMana(10, 0, 0, 20.0);
        api.setMana(11, 0, 0, 0.0);
        require(api.flowMana(10, 0, 0, 11, 0, 0, 100.0) == 10.0,
                "flow stops at equalization");
        require(api.getMana(10, 0, 0) + api.getMana(11, 0, 0) == 20.0,
                "flow conserves mana");
    }

    private static void configurationAndWorldIsolation() {
        ManaAPI overworld = new ManaAPI();
        ManaAPI nether = new ManaAPI();
        overworld.setMana(1, 2, 3, 40.0);
        require(nether.getMana(1, 2, 3) == 0.0, "world state is isolated");
        require(overworld.getConfig().equals(ManaConfig.defaults()), "default config");
        ManaConfig custom = new ManaConfig(0.5, 5, 2000.0);
        overworld.setConfig(custom);
        require(overworld.getConfig() == custom, "config replacement is retained");
        require(nether.getConfig().equals(ManaConfig.defaults()), "world config is isolated");
        boolean rejected = false;
        try {
            overworld.setConfig(null);
        } catch (NullPointerException expected) {
            rejected = true;
        }
        require(rejected, "null config is rejected");
    }

    private static void require(boolean condition, String message) {
        checks++;
        if (!condition) {
            throw new AssertionError(message);
        }
    }
}
