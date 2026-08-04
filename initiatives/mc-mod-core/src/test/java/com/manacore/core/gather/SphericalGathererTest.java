package com.manacore.core.gather;

import com.manacore.core.storage.ChunkManaMap;

public final class SphericalGathererTest {
    public static void main(String[] args) {
        testRadiusZero();
        testEuclideanSphere();
        testCapAndConservation();
        testInvalidInputs();
        testNegativeCoordinates();
        System.out.println("All SphericalGatherer tests passed.");
    }

    private static void testRadiusZero() {
        ChunkManaMap map = new ChunkManaMap();
        map.set(0, 0, 0, 5.0);
        map.set(1, 0, 0, 7.0);
        assert SphericalGatherer.gather(map, 0, 0, 0, 0, 3.0) == 3.0;
        assert map.get(0, 0, 0) == 2.0;
        assert map.get(1, 0, 0) == 7.0;
    }

    private static void testEuclideanSphere() {
        ChunkManaMap radiusOne = new ChunkManaMap();
        radiusOne.set(1, 0, 0, 2.0);
        radiusOne.set(1, 1, 0, 3.0);
        assert SphericalGatherer.gather(radiusOne, 0, 0, 0, 1, 10.0) == 2.0;
        assert radiusOne.get(1, 1, 0) == 3.0;

        ChunkManaMap radiusTwo = new ChunkManaMap();
        radiusTwo.set(2, 0, 0, 4.0);
        radiusTwo.set(2, 1, 0, 6.0);
        assert SphericalGatherer.gather(radiusTwo, 0, 0, 0, 2, 20.0) == 4.0;
        assert radiusTwo.get(2, 1, 0) == 6.0;
    }

    private static void testCapAndConservation() {
        ChunkManaMap map = new ChunkManaMap();
        map.set(-1, 0, 0, 4.0);
        map.set(0, 0, 0, 5.0);
        map.set(1, 0, 0, 6.0);
        double before = 15.0;
        double gathered = SphericalGatherer.gather(map, 0, 0, 0, 1, 7.0);
        double remaining = map.get(-1, 0, 0) + map.get(0, 0, 0) + map.get(1, 0, 0);
        assert gathered == 7.0;
        assert gathered + remaining == before;
        assert map.get(-1, 0, 0) >= 0.0;
        assert map.get(0, 0, 0) >= 0.0;
        assert map.get(1, 0, 0) >= 0.0;
    }

    private static void testInvalidInputs() {
        ChunkManaMap map = new ChunkManaMap();
        map.set(0, 0, 0, 9.0);
        assert SphericalGatherer.gather(map, 0, 0, 0, -1, 2.0) == 0.0;
        assert SphericalGatherer.gather(map, 0, 0, 0, 1, 0.0) == 0.0;
        assert SphericalGatherer.gather(map, 0, 0, 0, 1, -1.0) == 0.0;
        assert SphericalGatherer.gather(map, 0, 0, 0, 1, Double.NaN) == 0.0;
        assert SphericalGatherer.gather(map, 0, 0, 0, 1, Double.POSITIVE_INFINITY) == 0.0;
        assert map.get(0, 0, 0) == 9.0;
    }

    private static void testNegativeCoordinates() {
        ChunkManaMap map = new ChunkManaMap();
        map.set(-20, -5, -31, 8.0);
        assert SphericalGatherer.gather(map, -20, -5, -31, 0, 8.0) == 8.0;
        assert map.get(-20, -5, -31) == 0.0;
    }
}
