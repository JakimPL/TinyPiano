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


def format_c_array(array, name, dtype="float"):
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

    # Generate weights header file with architecture constants
    header_code = f"""#pragma once

#define INPUT_SIZE {input_size}
#define HIDDEN1_SIZE {hidden1_size}
#define HIDDEN2_SIZE {hidden2_size}
#define HIDDEN3_SIZE {hidden3_size}
#define OUTPUT_SIZE {output_size}

extern float weights1[];
extern float biases1[];
extern float weights2[];
extern float biases2[];
extern float weights3[];
extern float biases3[];
extern float weights_out[];
extern float biases_out[];
"""

    header_file = WEIGHTS_PATH.parent / "weights.h"
    with open(header_file, "w") as f:
        f.write(header_code)

    print(f"Generated weights header written to {header_file}")

    c_code = """#include "weights.h"

"""

    layer_names = ["weights1", "weights2", "weights3", "weights_out"]
    bias_names = ["biases1", "biases2", "biases3", "biases_out"]

    for i, (w_name, b_name) in enumerate(zip(layer_names, bias_names)):
        if f"layer_{i}" in weights:
            c_code += format_c_array(weights[f"layer_{i}"], w_name)
            c_code += format_c_array(biases[f"layer_{i}"], b_name)

    output_file = WEIGHTS_PATH
    with open(output_file, "w") as f:
        f.write(c_code)

    print(f"Generated weights C file written to {output_file}")

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
