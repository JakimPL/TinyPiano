#include <stdio.h>
#include <math.h>

// Model architecture constants
#define INPUT_SIZE 4
#define HIDDEN1_SIZE 8
#define HIDDEN2_SIZE 8
#define HIDDEN3_SIZE 4
#define OUTPUT_SIZE 1

// SiLU activation function: x * sigmoid(x)
float silu(float x) {
    return x / (1.0f + expf(-x));
}

// Linear layer computation: output = input * weight + bias
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

// Apply activation function to array
void apply_silu(float* array, int size) {
    for (int i = 0; i < size; i++) {
        array[i] = silu(array[i]);
    }
}

// Model weights (initialized to zero for now)
// Layer 1: 4 -> 8
static float weights1[HIDDEN1_SIZE * INPUT_SIZE] = {0};
static float biases1[HIDDEN1_SIZE] = {0};

// Layer 2: 8 -> 8  
static float weights2[HIDDEN2_SIZE * HIDDEN1_SIZE] = {0};
static float biases2[HIDDEN2_SIZE] = {0};

// Layer 3: 8 -> 4
static float weights3[HIDDEN3_SIZE * HIDDEN2_SIZE] = {0};
static float biases3[HIDDEN3_SIZE] = {0};

// Output layer: 4 -> 1
static float weights_out[OUTPUT_SIZE * HIDDEN3_SIZE] = {0};
static float biases_out[OUTPUT_SIZE] = {0};

// Forward pass for a single point
float predict_amplitude(float pitch, float velocity, float harmonic, float time) {
    // Input vector
    float input[INPUT_SIZE] = {pitch, velocity, harmonic, time};
    
    // Hidden layer activations
    float hidden1[HIDDEN1_SIZE];
    float hidden2[HIDDEN2_SIZE];
    float hidden3[HIDDEN3_SIZE];
    float output[OUTPUT_SIZE];
    
    // Forward pass
    // Layer 1: 4 -> 8
    linear_layer(input, weights1, biases1, hidden1, INPUT_SIZE, HIDDEN1_SIZE);
    apply_silu(hidden1, HIDDEN1_SIZE);
    
    // Layer 2: 8 -> 8
    linear_layer(hidden1, weights2, biases2, hidden2, HIDDEN1_SIZE, HIDDEN2_SIZE);
    apply_silu(hidden2, HIDDEN2_SIZE);
    
    // Layer 3: 8 -> 4
    linear_layer(hidden2, weights3, biases3, hidden3, HIDDEN2_SIZE, HIDDEN3_SIZE);
    apply_silu(hidden3, HIDDEN3_SIZE);
    
    // Output layer: 4 -> 1 (no activation)
    linear_layer(hidden3, weights_out, biases_out, output, HIDDEN3_SIZE, OUTPUT_SIZE);
    
    return output[0]; // Return log amplitude
}

// Test function
int main() {
    // Test with normalized values [0, 1]
    float pitch = 0.5f;    // Middle pitch
    float velocity = 0.8f; // Strong velocity
    float harmonic = 0.1f; // First few harmonics
    float time = 0.3f;     // Some time into the note
    
    float log_amplitude = predict_amplitude(pitch, velocity, harmonic, time);
    float amplitude = expf(log_amplitude); // Convert from log space
    
    printf("Input: pitch=%.2f, velocity=%.2f, harmonic=%.2f, time=%.2f\n", 
           pitch, velocity, harmonic, time);
    printf("Log amplitude: %.6f\n", log_amplitude);
    printf("Amplitude: %.6f\n", amplitude);
    
    return 0;
}
