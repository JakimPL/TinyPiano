#pragma once

#include "weights.h"

float silu(float x);

void linear_layer(const float *input, const unsigned char *weights_q, const unsigned char *biases_q,
                  float weights_min, float weights_max, float biases_min, float biases_max,
                  float *output, int input_size, int output_size);

void apply_silu(float *array, int size);

float predict_amplitude(float pitch, float velocity, float harmonic,
                        float time);
