package com.manacore.core.gather;

import com.manacore.core.storage.ChunkManaMap;

public final class SphericalGathererContract {
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
        map.set(0, 0, 0, 1.0);
        map.set(1, 0, 0, 2.0);
        map.set(1, 1, 0, 3.0);
        map.set(2, 0, 0, 4.0);
        expectClose(3.0, SphericalGatherer.gather(map, 0, 0, 0, 1, 10.0), "radius-one gather");
        expectClose(0.0, map.get(0, 0, 0), "center drained");
        expectClose(0.0, map.get(1, 0, 0), "axis neighbor drained");
        expectClose(3.0, map.get(1, 1, 0), "diagonal outside radius one");
        expectClose(4.0, map.get(2, 0, 0), "distance-two outside radius one");

        double before = map.get(1, 1, 0) + map.get(2, 0, 0);
        double gathered = SphericalGatherer.gather(map, 0, 0, 0, 2, 4.0);
        double remaining = map.get(1, 1, 0) + map.get(2, 0, 0);
        expectClose(4.0, gathered, "cap respected");
        expectClose(before, gathered + remaining, "gather conservation");
        expect(map.get(1, 1, 0) >= 0.0 && map.get(2, 0, 0) >= 0.0, "no negative values");

        ChunkManaMap center = new ChunkManaMap();
        center.set(-20, 7, 31, 5.0);
        center.set(-19, 7, 31, 6.0);
        expectClose(3.0, SphericalGatherer.gather(center, -20, 7, 31, 0, 3.0), "radius zero center cap");
        expectClose(2.0, center.get(-20, 7, 31), "center remainder");
        expectClose(6.0, center.get(-19, 7, 31), "radius zero excludes neighbor");
        expectClose(0.0, SphericalGatherer.gather(center, -20, 7, 31, -1, 2.0), "negative radius rejected");
        expectClose(0.0, SphericalGatherer.gather(center, -20, 7, 31, 1, Double.NaN), "NaN cap rejected");
        expectClose(8.0, center.get(-20, 7, 31) + center.get(-19, 7, 31), "invalid inputs do not mutate");

        System.out.println("Spherical gather contract passed " + checks + " checks.");
    }
}
