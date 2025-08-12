#pragma once

static inline float tiny_fmin(float a, float b) {
    return (a < b) ? a : b;
}

static inline float tiny_fmax(float a, float b) {
    return (a > b) ? a : b;
}

static inline float tiny_sin(float x) {
    float result;
    __asm__ volatile ("fsin" : "=t" (result) : "0" (x));
    return result;
}

static inline float tiny_exp(float x) {
    if (x < -10.0f) return 0.0f;

    float result;
    __asm__ volatile (
        "fldl2e\n\t"
        "fmul %%st(1)\n\t"
        "fst %%st(1)\n\t"
        "frndint\n\t"
        "fsubr %%st(1)\n\t"
        "f2xm1\n\t"
        "fld1\n\t"
        "faddp\n\t"
        "fscale\n\t"
        "fstp %%st(1)"
        : "=t" (result) : "0" (x)
    );
    return result;
}

static inline float tiny_pow(float base, float exp) {
    if (base == 2.0f) {
        float result;
        __asm__ volatile (
            "fst %%st(1)\n\t"
            "frndint\n\t"
            "fsubr %%st(1)\n\t"
            "f2xm1\n\t"
            "fld1\n\t"
            "faddp\n\t"
            "fscale\n\t"
            "fstp %%st(1)"
            : "=t" (result) : "0" (exp)
        );
        return result;
    }

    return tiny_exp(exp * 0.693147f * (base - 1.0f));
}

static inline float tiny_fabs(float x) {
    return (x < 0.0f) ? -x : x;
}

#define fminf tiny_fmin
#define fmaxf tiny_fmax
#define sinf tiny_sin
#define expf tiny_exp
#define powf tiny_pow
#define fabsf tiny_fabs
