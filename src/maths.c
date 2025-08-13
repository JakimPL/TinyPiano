#include "maths.h"

float tiny_fmin(float a, float b) {
    return (a < b) ? a : b;
}

float tiny_fmax(float a, float b) {
    return (a > b) ? a : b;
}

float tiny_fabs(float x) {
    return (x < 0.0f) ? -x : x;
}

float tiny_sin(float x) {
    float result;
    __asm__ volatile ("fsin" : "=t" (result) : "0" (x));
    return result;
}

// log2(x) using native fyl2x
static float tiny_log2(float x) {
    float result;
    __asm__ volatile (
        "fld1\n\t"
        "fxch\n\t"
        "fyl2x"
        : "=t" (result) : "0" (x)
    );
    return result;
}

float tiny_exp(float x) {
    float r;
    __asm__ __volatile__(
        "flds    %1             \n\t"
        "fldl2e                 \n\t"
        "fmulp   %%st(1)        \n\t"
        "fld1                   \n\t"
        "fscale                 \n\t"
        "fxch                   \n\t"
        "fld1                   \n\t"
        "fxch                   \n\t"
        "fprem                  \n\t"
        "f2xm1                  \n\t"
        "faddp   %%st(1)        \n\t"
        "fmulp   %%st(1)        \n\t"
        : "=t"(r)
        : "m"(x)
        : "st(1)", "st(2)"
    );
    return r;
}

float tiny_ln(float x) {
    if (x <= 0.0f) return -1000.0f;
    return tiny_log2(x) * 0.693147f; // log2(x) * ln(2)
}

float tiny_pow(float base, float exp) {
    if (base <= 0.0f) return 0.0f;
    if (exp == 0.0f) return 1.0f;
    return tiny_exp(exp * tiny_ln(base));
}
