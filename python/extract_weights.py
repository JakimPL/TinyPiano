import numpy as np
import torch
from constants import MODEL_PATH, WEIGHTS_PATH
from model import DirectTinyHarmonicModel


def infer_architecture_from_state_dict(state_dict):
    weight_keys = [k for k in state_dict.keys() if k.endswith(".weight")]
    weight_keys.sort(key=lambda x: int(x.split(".")[1]))

    hidden_sizes = []
    for key in weight_keys[:-1]:
        output_size = state_dict[key].shape[0]
        hidden_sizes.append(output_size)

    return tuple(hidden_sizes)


def dequantization(y: int, minimum: float, maximum: float) -> float:
    return y * (maximum - minimum) / 255.0 + minimum


def quantization(x: float, minimum: float, maximum: float) -> int:
    value = (x - minimum) * 255.0 / (maximum - minimum)
    value = round(value)
    return max(min(255, value), 0)


def quantize_array(array):
    flat = array.flatten()
    minimum, maximum = np.min(flat), np.max(flat)

    if minimum == maximum:
        quantized = np.zeros(flat.shape, dtype=np.uint8)
        return quantized, minimum, maximum

    quantized = np.array(
        [quantization(x, minimum, maximum) for x in flat], dtype=np.uint8
    )
    return quantized, minimum, maximum


def format_c_array(array, name, dtype="float"):
    flat = array.flatten()

    if dtype == "float":
        values = [f"{x:.8f}f" for x in flat]
    elif dtype == "unsigned char":
        values = [str(x) for x in flat]
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


def extract_weights():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Trained model not found at {MODEL_PATH}. Please train the model first or provide a valid model file."
        )

    print(f"Loading model weights from {MODEL_PATH}")
    state_dict = torch.load(MODEL_PATH, map_location="cpu")

    hidden_sizes = infer_architecture_from_state_dict(state_dict)
    print(f"Inferred model architecture: hidden_sizes={hidden_sizes}")

    model = DirectTinyHarmonicModel(hidden_sizes=hidden_sizes)
    model.load_state_dict(state_dict)

    model.eval()

    weights = {}
    biases = {}
    quantization_params = {}

    layers = list(model.mlp.children())
    linear_layers = [layer for layer in layers if isinstance(layer, torch.nn.Linear)]

    for i, layer in enumerate(linear_layers):
        weights[f"layer_{i}"] = layer.weight.data.numpy()
        biases[f"layer_{i}"] = layer.bias.data.numpy()

    print(f"Found {len(linear_layers)} linear layers:")
    for i, layer in enumerate(linear_layers):
        print(f"  Layer {i}: {layer.weight.shape[1]} -> {layer.weight.shape[0]}")

    input_size = linear_layers[0].weight.shape[1]
    hidden1_size = linear_layers[0].weight.shape[0]
    hidden2_size = linear_layers[1].weight.shape[0]
    hidden3_size = linear_layers[2].weight.shape[0]
    output_size = linear_layers[3].weight.shape[0]

    layer_names = ["weights1", "weights2", "weights3", "weights_out"]
    bias_names = ["biases1", "biases2", "biases3", "biases_out"]

    quantized_weights = {}
    quantized_biases = {}

    for i, (w_name, b_name) in enumerate(zip(layer_names, bias_names)):
        if f"layer_{i}" in weights:
            q_weights, w_min, w_max = quantize_array(weights[f"layer_{i}"])
            quantized_weights[w_name] = q_weights
            quantization_params[f"{w_name}_min"] = w_min
            quantization_params[f"{w_name}_max"] = w_max

            q_biases, b_min, b_max = quantize_array(biases[f"layer_{i}"])
            quantized_biases[b_name] = q_biases
            quantization_params[f"{b_name}_min"] = b_min
            quantization_params[f"{b_name}_max"] = b_max

            print(
                f"Layer {i}: weights [{w_min:.6f}, {w_max:.6f}], biases [{b_min:.6f}, {b_max:.6f}]"
            )

    header_code = f"""#pragma once

#define INPUT_SIZE {input_size}
#define HIDDEN1_SIZE {hidden1_size}
#define HIDDEN2_SIZE {hidden2_size}
#define HIDDEN3_SIZE {hidden3_size}
#define OUTPUT_SIZE {output_size}

extern unsigned char weights1_q[];
extern unsigned char biases1_q[];
extern unsigned char weights2_q[];
extern unsigned char biases2_q[];
extern unsigned char weights3_q[];
extern unsigned char biases3_q[];
extern unsigned char weights_out_q[];
extern unsigned char biases_out_q[];

extern float weights1_min, weights1_max;
extern float biases1_min, biases1_max;
extern float weights2_min, weights2_max;
extern float biases2_min, biases2_max;
extern float weights3_min, weights3_max;
extern float biases3_min, biases3_max;
extern float weights_out_min, weights_out_max;
extern float biases_out_min, biases_out_max;

float dequantize(unsigned char value, float min_val, float max_val);
"""

    header_file = WEIGHTS_PATH.parent / "weights.h"
    with open(header_file, "w") as f:
        f.write(header_code)

    print(f"Generated weights header written to {header_file}")

    c_code = """#include "weights.h"

float dequantize(unsigned char value, float min_val, float max_val) {
    return (float)value * (max_val - min_val) / 255.0f + min_val;
}

"""

    for param_name, param_value in quantization_params.items():
        c_code += f"float {param_name} = {param_value:.8f}f;\n"

    c_code += "\n"

    layer_names = ["weights1", "weights2", "weights3", "weights_out"]
    bias_names = ["biases1", "biases2", "biases3", "biases_out"]

    for i, (w_name, b_name) in enumerate(zip(layer_names, bias_names)):
        if w_name in quantized_weights:
            c_code += format_c_array(
                quantized_weights[w_name], f"{w_name}_q", "unsigned char"
            )
            c_code += format_c_array(
                quantized_biases[b_name], f"{b_name}_q", "unsigned char"
            )

    output_file = WEIGHTS_PATH
    with open(output_file, "w") as f:
        f.write(c_code)

    print(f"Generated weights C file written to {output_file}")

    print("\nQuantization quality analysis:")
    total_mse = 0
    total_elements = 0

    for i, (w_name, b_name) in enumerate(zip(layer_names, bias_names)):
        if w_name in quantized_weights:
            original_weights = weights[f"layer_{i}"].flatten()
            quantized_vals = quantized_weights[w_name]
            w_min, w_max = (
                quantization_params[f"{w_name}_min"],
                quantization_params[f"{w_name}_max"],
            )

            reconstructed = np.array(
                [dequantization(q, w_min, w_max) for q in quantized_vals]
            )
            mse = np.mean((original_weights - reconstructed) ** 2)

            print(
                f"  {w_name}: MSE = {mse:.8f}, Max error = {np.max(np.abs(original_weights - reconstructed)):.6f}"
            )
            total_mse += mse * len(original_weights)
            total_elements += len(original_weights)

            original_biases = biases[f"layer_{i}"].flatten()
            quantized_bias_vals = quantized_biases[b_name]
            b_min, b_max = (
                quantization_params[f"{b_name}_min"],
                quantization_params[f"{b_name}_max"],
            )

            reconstructed_biases = np.array(
                [dequantization(q, b_min, b_max) for q in quantized_bias_vals]
            )
            bias_mse = np.mean((original_biases - reconstructed_biases) ** 2)

            print(
                f"  {b_name}: MSE = {bias_mse:.8f}, Max error = {np.max(np.abs(original_biases - reconstructed_biases)):.6f}"
            )
            total_mse += bias_mse * len(original_biases)
            total_elements += len(original_biases)

    avg_mse = total_mse / total_elements
    print(f"\nOverall quantization MSE: {avg_mse:.8f}")

    print("\nTesting Python model outputs with trained weights...")
    test_inputs = [
        (0.5, 0.5, 0.0, 0.0),
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
                torch.tensor([time]),
            ).item()

        print(
            f"Python model({pitch}, {velocity}, {harmonic}, {time}) = {py_result:.6f}"
        )


if __name__ == "__main__":
    extract_weights()
