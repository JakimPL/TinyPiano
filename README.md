# TinyPiano - Neural Network Piano Synthesizer

This project implements a complete piano synthesizer using a neural network for harmonic prediction, real-time synthesis, and MIDI conversion - all in pure C without external dependencies.

## Quick Overview

```bash
# Setup development environment (one-time)
./setup.sh

# Build project
./build.sh

# Build and run tests
./build.sh --test

# Debug build
./build.sh --debug

# Manual pre-commit checks
pre-commit run --all-files
```

**Core Components:**
- **Neural Network**: 4→8→8→4→1 harmonic predictor (~18KB binary)
- **Synthesizer**: Real-time additive synthesis (48kHz)
- **Song Player**: Polyphonic MIDI-like format with mixing
- **MIDI Converter**: Python script (MIDI → C data)

**Clean Structure:**
- `src/` - Core implementation (model, synth, song, data)
- `src/tests/` - Test programs (organized separately)
- `python/` - Training and conversion tools
- `models/` - Trained neural network weights

## Architecture

- **Neural Network**: 4 → 8 → 8 → 4 → 1 architecture with SiLU activation
- **Input**: Normalized pitch, velocity, harmonic, time [0, 1]
- **Output**: Log amplitude (use `expf()` for linear amplitude)
- **Synthesizer**: Real-time harmonic synthesis at 48kHz
- **Song Player**: Polyphonic MIDI-like format with automatic mixing
- **MIDI Converter**: Python script to convert MIDI files to C data

## File Structure

### Core Implementation (`src/`)
- **`model.h/c`** - Neural network inference functions
- **`weights.h/c`** - Generated weight data from trained PyTorch model
- **`synth.h/c`** - Real-time harmonic synthesizer using neural network
- **`song.h/c`** - Polyphonic song player and audio rendering
- **`data.h/c`** - Generated MIDI song data (from convert_midi.py)
- **`main.c`** - Simple neural network test program

### Test Programs (`src/tests/`)
- **`test_model_output.c`** - Neural network output verification
- **`test_synth.c`** - Synthesizer functionality test
- **`test_song.c`** - Polyphonic song player test

### Python Tools (`python/`)
- **`extract_weights.py`** - Extract weights from PyTorch model → `weights.c`
- **`convert_midi.py`** - Convert MIDI files → `data.c` song format
- **`model.py`** - PyTorch model definition and training
- **`constants.py`** - Shared configuration constants
- **Other files** - Training, dataset processing, and utilities

### Data & Models
- **`models/tiny.pth`** - Trained PyTorch model
- **`midi/test.mid`** - Example MIDI file for testing
- **`data/`** - Processed training data and archives

### Build & Development Tools
- **`CMakeLists.txt`** - Modern CMake build configuration
- **`build.sh`** - Convenient build script with options
- **`setup.sh`** - Development environment setup
- **`.pre-commit-config.yaml`** - Automated code quality checks
- **`build/`** - CMake build directory (auto-generated)
- **`bin/`** - Compiled executables

## Build System

The project uses CMake for organized builds and pre-commit for code quality.

### Build Commands
```bash
./build.sh              # Release build
./build.sh --debug      # Debug build
./build.sh --clean      # Clean build
./build.sh --test       # Build and run tests
```

### CMake Targets (from build/ directory)
```bash
cd build
make model              # Core neural network program
make test_model         # Neural network tests
make test_synth         # Synthesizer tests
make test_song          # Song player tests
make test_all           # Run all tests
make size               # Show binary sizes
```

### Pre-commit Hooks

Automated quality checks run on every commit:

```bash
git commit               # Automatically runs all checks
pre-commit run           # Manual check on staged files
pre-commit run --all-files  # Check all files
```

**Hooks included:**
- Extract neural network weights from PyTorch model
- Clean CMake build and compilation check
- Full test suite execution
- Python code formatting (black, isort)
- File checks (whitespace, large files, etc.)

### Development Workflow

1. **Setup**: `./setup.sh` (one-time setup)
2. **Develop**: Edit code in `src/`
3. **Build**: `./build.sh` or CMake targets
4. **Test**: `./build.sh --test`
5. **Commit**: `git commit` (triggers pre-commit checks)

## Quick Start

```bash
# 1. Setup development environment (includes weights extraction)
./setup.sh

# 2. Convert MIDI to C song data (optional)
python python/convert_midi.py midi/test.mid

# 3. Build and test
./build.sh --test

# 4. Or build individual components
./build.sh               # Release build
./build.sh --debug       # Debug build
```

## Usage Examples

### Neural Network Model
```c
#include "src/model.h"

int main() {
    float pitch = 0.5f;      // Middle of piano range
    float velocity = 0.8f;   // Strong key press
    float harmonic = 0.1f;   // First few harmonics
    float time = 0.3f;       // 30% into note duration

    float log_amp = predict_amplitude(pitch, velocity, harmonic, time);
    float amplitude = expf(log_amp);
    return 0;
}
```

### Real-time Synthesis
```c
#include "src/synth.h"

int main() {
    float buffer[48000];  // 1 second at 48kHz
    size_t samples = synthesize_note(69, 100, 1.0f, buffer, 48000, 48000);
    // buffer now contains 1 second of A4 (440Hz) audio
    return 0;
}
```

### Polyphonic Song Player
```c
#include "src/song.h"
#include "src/data.h"  // Generated from MIDI

int main() {
    Song* song = create_midi_song();  // Load converted MIDI

    size_t buffer_size = song->total_ticks * TICK_DURATION(song->bpm) * SAMPLE_RATE;
    float* buffer = malloc(buffer_size * sizeof(float));

    size_t samples = render_song(song, buffer, buffer_size, SAMPLE_RATE);
    save_audio_to_file("output.txt", buffer, samples, SAMPLE_RATE);

    free(buffer);
    free_song(song);
    return 0;
}
```

### MIDI Conversion
```bash
# Convert MIDI file to C data with 16th note quantization
python python/convert_midi.py midi/song.mid -o src/data.c -q 240

# Limit to first 30 seconds
python python/convert_midi.py midi/song.mid -d 30

# Show analysis without generating code
python python/convert_midi.py midi/song.mid --dry-run
```

## Compilation

### Individual Components
```bash
# Neural network only (minimal)
gcc -O2 -o neural src/main.c src/model.c src/weights.c -lm

# With synthesizer
gcc -O2 -o synth your_program.c src/synth.c src/model.c src/weights.c -lm

# Full song player with MIDI data
gcc -O2 -o player your_program.c src/song.c src/synth.c src/model.c src/weights.c src/data.c -lm
```

### Tests
```bash
# Build and run all tests
./build.sh --test

# Or using CMake directly (from build/ directory)
cd build && make test_all
```

## Performance & Code Size

- **Binary Size**: ~12KB optimized (`-O2`) for full synthesizer
- **Memory**: All weights embedded as static arrays (~2KB)
- **Dependencies**: Only standard C library + libm
- **Standards**: C99 compatible
- **Audio Quality**: 48kHz sample rate, 32 harmonics maximum

## Technical Details

### Neural Network
- **Precision**: 32-bit floating point
- **Activation**: SiLU (Swish): `x * sigmoid(x)`
- **Normalization**: All inputs scaled to [0,1] range
- **Output**: Log amplitude (requires `expf()` for linear)

### Audio Pipeline
1. **Neural Network** predicts harmonic amplitudes
2. **Synthesizer** generates waveforms using additive synthesis
3. **Song Player** mixes polyphonic notes in real-time
4. **Output** raw audio samples or text format

### MIDI Format Support
- **Resolution**: 480 ticks per quarter note
- **Range**: 16-bit time values (0-65535 ticks)
- **Velocity**: 8-bit MIDI velocity (1-127)
- **Pitch**: 8-bit MIDI pitch (0-127)

## Extending the System

### Retrain Neural Network
1. Update PyTorch model in `python/model.py`
2. Train and save to `models/tiny.pth`
3. Run `./setup.sh` or `python python/extract_weights.py`
4. Rebuild with `./build.sh`

### Add New MIDI Songs
1. Place MIDI file in `midi/` directory
2. Convert: `python python/convert_midi.py midi/your_song.mid`
3. Include generated `data.c` in your program
4. Call `create_midi_song()` to load

### Optimize for Size
- Remove printf statements (already done for core modules)
- Use `-Os` instead of `-O2` for size optimization
- Strip debug symbols: `strip your_program`
