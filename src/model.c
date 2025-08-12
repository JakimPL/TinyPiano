#include <stdio.h>

#include "math.h"
#include "model.h"

float silu(float x) {
    return x / (1.0f + expf(-x));
}

void linear_layer(const float* input, const float* weights, const float* biases,
                  float* output, int input_size, int output_size) {
    for (int i = 0; i < output_size; i++) {
        float sum = biases[i];
        for (int j = 0; j < input_size; j++) {
            sum += input[j] * weights[i * input_size + j];
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

    linear_layer(input, weights1, biases1, hidden1, INPUT_SIZE, HIDDEN1_SIZE);
    apply_silu(hidden1, HIDDEN1_SIZE);

    linear_layer(hidden1, weights2, biases2, hidden2, HIDDEN1_SIZE, HIDDEN2_SIZE);
    apply_silu(hidden2, HIDDEN2_SIZE);

    linear_layer(hidden2, weights3, biases3, hidden3, HIDDEN2_SIZE, HIDDEN3_SIZE);
    apply_silu(hidden3, HIDDEN3_SIZE);

    linear_layer(hidden3, weights_out, biases_out, output, HIDDEN3_SIZE, OUTPUT_SIZE);
    return expf(output[0]);
}
