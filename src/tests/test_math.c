#include <stdio.h>
#include <math.h>


float std_sinf(float x) { return sinf(x); }
float std_expf(float x) { return expf(x); }
float std_powf(float x, float y) { return powf(x, y); }

#include "../maths.h"

#define TOLERANCE 1e-4f
#define ABS(x) ((x) < 0 ? -(x) : (x))

int test_failures = 0;

int check_result(const char* test_name, float got, float expected, const char* expr) {
    float diff = ABS(got - expected);
    printf("  DEBUG: %s: got=%.6f, expected=%.6f, diff=%.6f\n", expr, got, expected, diff);
    if (diff > TOLERANCE) {
        printf("  FAIL: %s = %.6f (expected: %.6f, diff: %.6f)\n", expr, got, expected, diff);
        test_failures++;
        return 0;
    } else {
        printf("  PASS: %s = %.6f\n", expr, got);
        return 1;
    }
}

void test_fmin() {
    printf("Testing fmin:\n");
    check_result("fmin", tiny_fmin(3.0f, 5.0f), 3.0f, "tiny_fmin(3.0, 5.0)");
    check_result("fmin", tiny_fmin(-2.0f, 1.0f), -2.0f, "tiny_fmin(-2.0, 1.0)");
    check_result("fmin", tiny_fmin(7.0f, 7.0f), 7.0f, "tiny_fmin(7.0, 7.0)");
}

void test_fmax() {
    printf("Testing fmax:\n");
    check_result("fmax", tiny_fmax(3.0f, 5.0f), 5.0f, "tiny_fmax(3.0, 5.0)");
    check_result("fmax", tiny_fmax(-2.0f, 1.0f), 1.0f, "tiny_fmax(-2.0, 1.0)");
    check_result("fmax", tiny_fmax(7.0f, 7.0f), 7.0f, "tiny_fmax(7.0, 7.0)");
}

void test_fabs() {
    printf("Testing fabs:\n");
    check_result("fabs", tiny_fabs(3.5f), 3.5f, "tiny_fabs(3.5)");
    check_result("fabs", tiny_fabs(-3.5f), 3.5f, "tiny_fabs(-3.5)");
    check_result("fabs", tiny_fabs(0.0f), 0.0f, "tiny_fabs(0.0)");
}

void test_sin() {
    printf("Testing sin:\n");
    check_result("sin", tiny_sin(0.0f), std_sinf(0.0f), "tiny_sin(0.0)");
    check_result("sin", tiny_sin(3.14159265f/2.0f), std_sinf(3.14159265f/2.0f), "tiny_sin(PI/2)");
    check_result("sin", tiny_sin(3.14159265f), std_sinf(3.14159265f), "tiny_sin(PI)");
    check_result("sin", tiny_sin(3.0f*3.14159265f/2.0f), std_sinf(3.0f*3.14159265f/2.0f), "tiny_sin(3*PI/2)");
}

void test_exp() {
    printf("Testing exp:\n");
    check_result("exp", tiny_exp(0.0f), std_expf(0.0f), "tiny_exp(0.0)");
    check_result("exp", tiny_exp(1.0f), std_expf(1.0f), "tiny_exp(1.0)");
    check_result("exp", tiny_exp(2.0f), std_expf(2.0f), "tiny_exp(2.0)");
    check_result("exp", tiny_exp(-1.0f), std_expf(-1.0f), "tiny_exp(-1.0)");
}

void test_pow() {
    printf("Testing pow:\n");
    check_result("pow", tiny_pow(2.0f, 3.0f), std_powf(2.0f, 3.0f), "tiny_pow(2.0, 3.0)");
    check_result("pow", tiny_pow(2.0f, 0.5f), std_powf(2.0f, 0.5f), "tiny_pow(2.0, 0.5)");
    check_result("pow", tiny_pow(440.0f, 1.0f/12.0f), std_powf(440.0f, 1.0f/12.0f), "tiny_pow(440.0, 1.0/12.0)");

    float pitch60_freq = 440.0f * tiny_pow(2.0f, (60.0f - 69.0f) / 12.0f);
    float pitch60_expected = 440.0f * std_powf(2.0f, (60.0f - 69.0f) / 12.0f);
    check_result("pow", pitch60_freq, pitch60_expected, "Pitch 60 frequency");

    float pitch72_freq = 440.0f * tiny_pow(2.0f, (72.0f - 69.0f) / 12.0f);
    float pitch72_expected = 440.0f * std_powf(2.0f, (72.0f - 69.0f) / 12.0f);
    check_result("pow", pitch72_freq, pitch72_expected, "Pitch 72 frequency");
}

int main() {
    printf("Testing custom math functions:\n\n");

    test_fmin();
    printf("\n");

    test_fmax();
    printf("\n");

    test_fabs();
    printf("\n");

    test_sin();
    printf("\n");

    test_exp();
    printf("\n");

    test_pow();
    printf("\n");

    if (test_failures == 0) {
        printf("All math tests PASSED!\n");
        return 0;
    } else {
        printf("%d math test(s) FAILED!\n", test_failures);
        return 1;
    }
}
