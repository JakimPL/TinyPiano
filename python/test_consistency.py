#!/usr/bin/env python3
"""
Test script to verify consistency between Python and C implementations
"""

import torch
import subprocess
import tempfile
import os
from model import DirectTinyHarmonicModel
from constants import MODEL_PATH

def test_consistency():
    # Load Python model
    model = DirectTinyHarmonicModel(hidden_sizes=(8, 8, 4))
    if MODEL_PATH.exists():
        state_dict = torch.load(MODEL_PATH, map_location='cpu')
        model.load_state_dict(state_dict)
    model.eval()

    # Test cases
    test_cases = [
        (0.5, 0.8, 0.1, 0.3),
        (0.0, 0.5, 0.0, 0.0),
        (1.0, 1.0, 1.0, 1.0),
        (0.25, 0.6, 0.5, 0.8),
        (0.75, 0.9, 0.3, 0.1),
    ]

    print("Testing Python vs C model consistency:")
    print("=" * 60)

    for i, (pitch, velocity, harmonic, time) in enumerate(test_cases):
        # Python prediction
        with torch.no_grad():
            py_result = model(
                torch.tensor([pitch]),
                torch.tensor([velocity]),
                torch.tensor([harmonic]),
                torch.tensor([time])
            ).item()

        # Create a temporary C program to test this specific input
        c_test_code = f'''
#include <stdio.h>
#include <math.h>
#include "src/model.h"

int main() {{
    float result = predict_amplitude({pitch}f, {velocity}f, {harmonic}f, {time}f);
    printf("%.6f\\n", result);
    return 0;
}}
'''

        # Write temporary C file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as f:
            f.write(c_test_code)
            temp_c_file = f.name

        try:
            # Compile and run C test
            temp_exe = temp_c_file.replace('.c', '')
            compile_result = subprocess.run([
                'gcc', '-o', temp_exe, temp_c_file, 'src/model.c', 'src/weights.c', '-lm'
            ], capture_output=True, text=True)

            if compile_result.returncode == 0:
                run_result = subprocess.run([temp_exe], capture_output=True, text=True)
                c_result = float(run_result.stdout.strip())

                # Compare results
                diff = abs(py_result - c_result)
                status = "✓ PASS" if diff < 1e-5 else "✗ FAIL"

                print(f"Test {i+1}: ({pitch}, {velocity}, {harmonic}, {time})")
                print(f"  Python: {py_result:.6f}")
                print(f"  C:      {c_result:.6f}")
                print(f"  Diff:   {diff:.2e}")
                print(f"  Status: {status}")
                print()
            else:
                print(f"Test {i+1}: Compilation failed")
                print(compile_result.stderr)

        finally:
            # Clean up temporary files
            for temp_file in [temp_c_file, temp_exe]:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)

if __name__ == "__main__":
    test_consistency()
