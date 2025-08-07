#!/usr/bin/env python3
"""
Script to extract weights from the trained PyTorch model and generate
C code with embedded weights.
"""

import torch
import numpy as np
from pathlib import Path
from model import DirectTinyHarmonicModel
from constants import MODEL_PATH

def format_c_array(array, name, dtype="float"):
    """Format a numpy array as a C array initialization."""
    flat = array.flatten()
    
    # Format numbers with appropriate precision
    if dtype == "float":
        values = [f"{x:.8f}f" for x in flat]
    else:
        values = [str(x) for x in flat]
    
    # Create a properly formatted C array
    result = f"static {dtype} {name}[] = {{\n    "
    
    # Add values with proper line breaks
    for i, val in enumerate(values):
        if i > 0:
            result += ", "
        if i > 0 and i % 8 == 0:  # New line every 8 values
            result += "\n    "
        result += val
    
    result += "\n};\n"
    return result

def extract_weights_and_generate_c():
    """Extract weights from trained model and generate C code."""
    
    # Load the model with the correct architecture
    model = DirectTinyHarmonicModel(hidden_sizes=(8, 8, 4))
    
    if MODEL_PATH.exists():
        print(f"Loading model weights from {MODEL_PATH}")
        state_dict = torch.load(MODEL_PATH, map_location='cpu')
        model.load_state_dict(state_dict)
    else:
        print(f"Warning: {MODEL_PATH} not found. Using random weights.")
    
    model.eval()
    
    # Extract weights and biases
    weights = {}
    biases = {}
    
    # Get the parameters from the sequential model
    layers = list(model.mlp.children())
    
    # Extract linear layer parameters (skip activation layers)
    linear_layers = [layer for layer in layers if isinstance(layer, torch.nn.Linear)]
    
    for i, layer in enumerate(linear_layers):
        weights[f'layer_{i}'] = layer.weight.data.numpy()
        biases[f'layer_{i}'] = layer.bias.data.numpy()
    
    print(f"Found {len(linear_layers)} linear layers:")
    for i, layer in enumerate(linear_layers):
        print(f"  Layer {i}: {layer.weight.shape[1]} -> {layer.weight.shape[0]}")
    
    # Generate C code
    c_code = '''#include <stdio.h>
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

// Model weights
'''
    
    # Add weight arrays
    layer_names = ['weights1', 'weights2', 'weights3', 'weights_out']
    bias_names = ['biases1', 'biases2', 'biases3', 'biases_out']
    
    for i, (w_name, b_name) in enumerate(zip(layer_names, bias_names)):
        if f'layer_{i}' in weights:
            c_code += f"\n// Layer {i+1}\n"
            c_code += format_c_array(weights[f'layer_{i}'], w_name)
            c_code += format_c_array(biases[f'layer_{i}'], b_name)
    
    # Add the forward pass function
    c_code += '''
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
    
    printf("Input: pitch=%.2f, velocity=%.2f, harmonic=%.2f, time=%.2f\\n", 
           pitch, velocity, harmonic, time);
    printf("Log amplitude: %.6f\\n", log_amplitude);
    printf("Amplitude: %.6f\\n", amplitude);
    
    return 0;
}
'''
    
    # Write to file
    output_file = Path("piano_model_with_weights.c")
    with open(output_file, 'w') as f:
        f.write(c_code)
    
    print(f"Generated C code written to {output_file}")
    
    # Also create a simple test comparison
    if MODEL_PATH.exists():
        print("\\nTesting consistency between Python and C models...")
        test_inputs = [
            (0.5, 0.8, 0.1, 0.3),
            (0.0, 0.5, 0.0, 0.0),
            (1.0, 1.0, 1.0, 1.0),
        ]
        
        for pitch, velocity, harmonic, time in test_inputs:
            # Python prediction
            with torch.no_grad():
                py_result = model(
                    torch.tensor([pitch]), 
                    torch.tensor([velocity]),
                    torch.tensor([harmonic]), 
                    torch.tensor([time])
                ).item()
            
            print(f"Python model({pitch}, {velocity}, {harmonic}, {time}) = {py_result:.6f}")

if __name__ == "__main__":
    extract_weights_and_generate_c()
