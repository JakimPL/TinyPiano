#pragma once

#include "weights.h"

float silu(float x);

void linear_layer(const float *input, const float *weights, const float *biases,
                  float *output, int input_size, int output_size);

void apply_silu(float *array, int size);

float predict_amplitude(float pitch, float velocity, float harmonic,
                        float time);
