package com.manacore.core.flow;

import com.manacore.core.storage.ChunkManaMap;

public final class GradientCalculatorContract {
    private static int checks;

    private static void expect(boolean condition, String message) {
        checks++;
        if (!condition) {
            throw new AssertionError(message);
        }
    }

    private static void expectGradient(
            GradientCalculator.Gradient gradient,
            int dx,
            int dy,
            int dz,
            double magnitude) {
        expect(gradient.dx() == dx, "unexpected dx");
        expect(gradient.dy() == dy, "unexpected dy");
        expect(gradient.dz() == dz, "unexpected dz");
        expect(Double.compare(gradient.magnitude(), magnitude) == 0, "unexpected magnitude");
    }

    public static void main(String[] args) {
        ChunkManaMap map = new ChunkManaMap();
        map.set(0, 0, 0, 10.0);
        map.set(2, -3, 4, 4.0);

        expectGradient(GradientCalculator.calculate(map, 0, 0, 0, 2, -3, 4), 1, -1, 1, 6.0);
        expectGradient(GradientCalculator.calculate(map, 2, -3, 4, 0, 0, 0), 1, -1, 1, 6.0);
        expectGradient(GradientCalculator.calculate(map, 0, 0, 0, 9, 9, 9), 1, 1, 1, 10.0);

        map.set(-20, 8, 31, 7.5);
        map.set(-21, 8, 31, 7.5);
        expectGradient(GradientCalculator.calculate(map, -20, 8, 31, -21, 8, 31), 0, 0, 0, 0.0);

        System.out.println("Gradient contract passed " + checks + " checks.");
    }
}
