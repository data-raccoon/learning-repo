package com.manacore.core;

/**
 * Math utilities for mana calculations.
 * Ensures mana values are always valid (non-negative, finite).
 */
public final class ManaMath {

    private ManaMath() {
        // Utility class - no instantiation
    }

    /**
     * Clamps a mana value to be non-negative.
     * Negative values become zero.
     *
     * @param value the mana value to clamp
     * @return the clamped mana value (>= 0)
     */
    public static double clampNonNegative(double value) {
        return Math.max(0.0, value);
    }

    /**
     * Clamps a mana value to be non-negative.
     *
     * @param value the mana value to clamp
     * @return the clamped mana value (>= 0)
     */
    public static float clampNonNegative(float value) {
        return Math.max(0.0f, value);
    }

    /**
     * Clamps a mana value to be non-negative.
     *
     * @param value the mana value to clamp
     * @return the clamped mana value (>= 0)
     */
    public static int clampNonNegative(int value) {
        return Math.max(0, value);
    }

    /**
     * Clamps a mana value to be non-negative.
     *
     * @param value the mana value to clamp
     * @return the clamped mana value (>= 0)
     */
    public static long clampNonNegative(long value) {
        return Math.max(0L, value);
    }

    /**
     * Checks if a mana value is valid (non-negative and finite).
     *
     * @param value the mana value to check
     * @return true if the value is valid (>= 0 and finite)
     */
    public static boolean isValidMana(double value) {
        return value >= 0.0 && Double.isFinite(value);
    }

    /**
     * Checks if a mana value is valid (non-negative and finite).
     *
     * @param value the mana value to check
     * @return true if the value is valid (>= 0 and finite)
     */
    public static boolean isValidMana(float value) {
        return value >= 0.0f && Float.isFinite(value);
    }

    /**
     * Safely adds two mana values, clamping the result to non-negative.
     * If either value is invalid (negative or non-finite), returns 0.
     *
     * @param a the first mana value
     * @param b the second mana value
     * @return the sum clamped to non-negative, or 0 if either input is invalid
     */
    public static double safeAdd(double a, double b) {
        if (!isValidMana(a) || !isValidMana(b)) {
            return 0.0;
        }
        double result = a + b;
        // Check for overflow to positive infinity
        if (Double.isInfinite(result)) {
            return Double.MAX_VALUE;
        }
        return clampNonNegative(result);
    }

    /**
     * Safely subtracts two mana values, clamping the result to non-negative.
     * If either value is invalid (negative or non-finite), returns 0.
     *
     * @param a the first mana value
     * @param b the second mana value
     * @return the difference clamped to non-negative, or 0 if either input is invalid
     */
    public static double safeSubtract(double a, double b) {
        if (!isValidMana(a) || !isValidMana(b)) {
            return 0.0;
        }
        return clampNonNegative(a - b);
    }

    /**
     * Safely multiplies two mana values, clamping the result to non-negative.
     * If either value is invalid (negative or non-finite), returns 0.
     *
     * @param a the first mana value
     * @param b the second mana value
     * @return the product clamped to non-negative, or 0 if either input is invalid
     */
    public static double safeMultiply(double a, double b) {
        if (!isValidMana(a) || !isValidMana(b)) {
            return 0.0;
        }
        double result = a * b;
        // Check for overflow to positive infinity
        if (Double.isInfinite(result)) {
            return Double.MAX_VALUE;
        }
        return clampNonNegative(result);
    }

    /**
     * Safely divides two mana values, clamping the result to non-negative.
     * If either value is invalid (negative or non-finite), or divisor is zero, returns 0.
     *
     * @param a the dividend
     * @param b the divisor
     * @return the quotient clamped to non-negative, or 0 if invalid or division by zero
     */
    public static double safeDivide(double a, double b) {
        if (!isValidMana(a) || !isValidMana(b) || b == 0.0) {
            return 0.0;
        }
        return clampNonNegative(a / b);
    }

    /**
     * Linearly interpolates between two mana values.
     * If either value is invalid, returns the valid one or 0.
     *
     * @param a the first mana value
     * @param b the second mana value
     * @param t the interpolation factor (0.0 to 1.0)
     * @return the interpolated value clamped to non-negative
     */
    public static double lerp(double a, double b, double t) {
        if (!isValidMana(a) || !isValidMana(b)) {
            if (isValidMana(a)) return a;
            if (isValidMana(b)) return b;
            return 0.0;
        }
        // Clamp t to [0, 1] range
        t = Math.max(0.0, Math.min(1.0, t));
        return clampNonNegative(a + (b - a) * t);
    }

    /**
     * Gets the minimum of two mana values, ensuring non-negative result.
     *
     * @param a the first mana value
     * @param b the second mana value
     * @return the minimum of the two values, or 0 if either is invalid
     */
    public static double min(double a, double b) {
        if (!isValidMana(a) || !isValidMana(b)) {
            return 0.0;
        }
        return Math.min(a, b);
    }

    /**
     * Gets the maximum of two mana values, ensuring non-negative result.
     *
     * @param a the first mana value
     * @param b the second mana value
     * @return the maximum of the two values, or 0 if either is invalid
     */
    public static double max(double a, double b) {
        if (!isValidMana(a) || !isValidMana(b)) {
            return 0.0;
        }
        return Math.max(a, b);
    }

    /**
     * Checks if a value is approximately zero (within epsilon).
     *
     * @param value the value to check
     * @param epsilon the tolerance
     * @return true if the value is approximately zero
     */
    public static boolean isApproximatelyZero(double value, double epsilon) {
        return Math.abs(value) < epsilon;
    }

    /**
     * Checks if a value is approximately zero (within default epsilon).
     *
     * @param value the value to check
     * @return true if the value is approximately zero
     */
    public static boolean isApproximatelyZero(double value) {
        return isApproximatelyZero(value, 1e-10);
    }
}
