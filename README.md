# Piano Harmonics Neural Network - C Implementation

This project implements a neural network model for predicting piano harmonics in pure C, without any external libraries. The model takes normalized inputs (pitch, velocity, harmonic, time) and outputs log amplitude.

## Architecture

- **Input**: 4 features (pitch, velocity, harmonic, time) - all normalized to [0, 1]
- **Hidden layers**: 4 → 8 → 8 → 4 → 1
- **Activation**: SiLU (Swish) activation function
- **Output**: Log amplitude (use `expf()` to get actual amplitude)

## Files

### C Implementations

- **`piano_model.c`** - Basic implementation with zero weights (for testing structure)
- **`piano_compact.c`** - Compact, demoscene-style implementation with embedded trained weights
- **`piano_model_with_weights.c`** - Generated file with full structure and real weights

### Python Tools

- **`extract_weights.py`** - Extracts weights from PyTorch model and generates C code
- **`test_consistency.py`** - Tests consistency between Python and C implementations

### Build System

- **`Makefile`** - Build system for all targets

## Quick Start

```bash
# Build all targets
make all

# Test the compact model (recommended)
make test_compact

# Clean build artifacts
make clean
```

## Usage Example

```c
#include "piano_compact.c"

int main() {
    float pitch = 0.5f;      // Middle of piano range
    float velocity = 0.8f;   // Strong key press
    float harmonic = 0.1f;   // First few harmonics
    float time = 0.3f;       // 30% into note duration
    
    float log_amp = piano_harmonics(pitch, velocity, harmonic, time);
    float amplitude = expf(log_amp);
    
    printf("Log amplitude: %.6f, Amplitude: %.6f\\n", log_amp, amplitude);
    return 0;
}
```

## Model Performance

The C implementation produces results identical to the original PyTorch model:

```
Input: (0.50, 0.80, 0.10, 0.30) -> -6.170 (amp: 0.002092)
Input: (0.00, 0.50, 0.00, 0.00) -> -5.218 (amp: 0.005417)
Input: (1.00, 1.00, 1.00, 1.00) -> -19.774 (amp: 0.000000)
```

## Compiling

The code requires only standard C libraries and math library:

```bash
gcc -O2 -o piano_compact piano_compact.c -lm
```

## Code Size

The compact implementation (`piano_compact.c`) is approximately:
- **Source**: ~100 lines of C code
- **Binary**: ~8KB (optimized with `-O2`)
- **Dependencies**: Only standard C library + libm

Perfect for demoscene productions or embedded systems!

## Technical Details

- **Precision**: Single precision floating point (32-bit)
- **Memory**: All weights embedded as static arrays
- **Standards**: C99 compatible
- **Tested**: GCC on Linux

## Extending

To retrain the model or modify architecture:
1. Update the PyTorch model in `model.py`
2. Train and save weights to `models/tiny.pth`
3. Run `python extract_weights.py` to regenerate C code
4. Update `piano_compact.c` if needed
