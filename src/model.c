#include <stdio.h>

#include "maths.h"
#include "model.h"

float silu(float x) {
    return x / (1.0f + expf(-x));
}

void linear_layer(const float* input, const unsigned char* weights_q, const unsigned char* biases_q,
                  float weights_min, float weights_max, float biases_min, float biases_max,
                  float* output, int input_size, int output_size) {
    for (int i = 0; i < output_size; i++) {
        float bias = dequantize(biases_q[i], biases_min, biases_max);
        float sum = bias;
        for (int j = 0; j < input_size; j++) {
            float weight = dequantize(weights_q[i * input_size + j], weights_min, weights_max);
            sum += input[j] * weight;
        }
        output[i] = sum;
    }
}

void apply_silu(float* array, int size) {
    for (int i = 0; i < size; i++) {
        array[i] = silu(array[i]);
    }
}


float predict_amplitude(float pitch, float velocity, float harmonic, float time) {
    float input[INPUT_SIZE] = {pitch, velocity, harmonic, time};

    float hidden1[HIDDEN1_SIZE];
    float hidden2[HIDDEN2_SIZE];
    float hidden3[HIDDEN3_SIZE];
    float output[OUTPUT_SIZE];

    linear_layer(input, weights1_q, biases1_q, weights1_min, weights1_max, biases1_min, biases1_max,
                 hidden1, INPUT_SIZE, HIDDEN1_SIZE);
    apply_silu(hidden1, HIDDEN1_SIZE);

    linear_layer(hidden1, weights2_q, biases2_q, weights2_min, weights2_max, biases2_min, biases2_max,
                 hidden2, HIDDEN1_SIZE, HIDDEN2_SIZE);
    apply_silu(hidden2, HIDDEN2_SIZE);

    linear_layer(hidden2, weights3_q, biases3_q, weights3_min, weights3_max, biases3_min, biases3_max,
                 hidden3, HIDDEN2_SIZE, HIDDEN3_SIZE);
    apply_silu(hidden3, HIDDEN3_SIZE);

    linear_layer(hidden3, weights_out_q, biases_out_q, weights_out_min, weights_out_max,
                 biases_out_min, biases_out_max, output, HIDDEN3_SIZE, OUTPUT_SIZE);
    return expf(output[0]);
}
