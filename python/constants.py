from pathlib import Path

DATASET_PATH = Path("samples")
ARCHIVE_PATH = Path("data/harmonics.pkl")
MODEL_PATH = Path("models/tiny.pth")
CODE_PATH = Path("src/model.c")
WEIGHTS_PATH = Path("src/weights.c")
SONG_PATH = Path("src/data.c")

PITCH_LOWEST = 21  # A0
PITCH_HIGHEST = 114  # F#8
NOTES = PITCH_HIGHEST - PITCH_LOWEST + 1
MAX_HARMONICS = 32
SAMPLE_RATE = 48000

# Song/MIDI constants
TICKS_PER_QUARTER = 480  # Standard MIDI resolution
DEFAULT_BPM = 120
