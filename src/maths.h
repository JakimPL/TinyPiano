#pragma once

float tiny_fmin(float a, float b);
float tiny_fmax(float a, float b);
float tiny_sin(float x);
float tiny_exp(float x);
float tiny_ln(float x);
float tiny_pow(float base, float exp);
float tiny_fabs(float x);

#define fminf tiny_fmin
#define fmaxf tiny_fmax
#define sinf tiny_sin
#define expf tiny_exp
#define powf tiny_pow
#define fabsf tiny_fabs
