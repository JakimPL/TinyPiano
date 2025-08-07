#!/usr/bin/env python3
"""
Script to extract weights from the trained PyTorch model and generate
C code with embedded weights.
"""

import torch

from model import DirectTinyHarmonicModel
from constants import WEIGHTS_PATH, MODEL_PATH

def format_c_array(array, name, dtype="float"):
    """Format a numpy array as a C array initialization."""
    flat = array.flatten()

    if dtype == "float":
        values = [f"{x:.8f}f" for x in flat]
    else:
        values = [str(x) for x in flat]

    result = f"{dtype} {name}[] = {{\n    "

    for i, val in enumerate(values):
        if i > 0:
            result += ", "
        if i > 0 and i % 8 == 0:
            result += "\n    "
        result += val

    result += "\n};\n"
    return result

def extract_weights_and_generate_c():
    """Extract weights from trained model and generate weights C file."""

    model = DirectTinyHarmonicModel(hidden_sizes=(8, 8, 4))

    if MODEL_PATH.exists():
        print(f"Loading model weights from {MODEL_PATH}")
        state_dict = torch.load(MODEL_PATH, map_location='cpu')
        model.load_state_dict(state_dict)
    else:
        raise FileNotFoundError(f"Trained model not found at {MODEL_PATH}. Please train the model first or provide a valid model file.")

    model.eval()

    weights = {}
    biases = {}

    layers = list(model.mlp.children())
    linear_layers = [layer for layer in layers if isinstance(layer, torch.nn.Linear)]

    for i, layer in enumerate(linear_layers):
        weights[f'layer_{i}'] = layer.weight.data.numpy()
        biases[f'layer_{i}'] = layer.bias.data.numpy()

    print(f"Found {len(linear_layers)} linear layers:")
    for i, layer in enumerate(linear_layers):
        print(f"  Layer {i}: {layer.weight.shape[1]} -> {layer.weight.shape[0]}")

    # Generate only weights file
    c_code = '''#include "weights.h"

'''

    layer_names = ['weights1', 'weights2', 'weights3', 'weights_out']
    bias_names = ['biases1', 'biases2', 'biases3', 'biases_out']

    for i, (w_name, b_name) in enumerate(zip(layer_names, bias_names)):
        if f'layer_{i}' in weights:
            c_code += format_c_array(weights[f'layer_{i}'], w_name)
            c_code += format_c_array(biases[f'layer_{i}'], b_name)

    output_file = WEIGHTS_PATH
    with open(output_file, 'w') as f:
        f.write(c_code)

    print(f"Generated weights C file written to {output_file}")

    print("\nTesting Python model outputs with trained weights...")
    test_inputs = [
        (0.5, 0.5, 0.0, 0.0),  # Your test case
        (0.5, 0.8, 0.1, 0.3),
        (0.0, 0.5, 0.0, 0.0),
        (1.0, 1.0, 1.0, 1.0),
    ]

    for pitch, velocity, harmonic, time in test_inputs:
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
