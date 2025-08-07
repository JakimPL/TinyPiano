from pathlib import Path

DATASET_PATH = Path("samples")
ARCHIVE_PATH = Path("data/harmonics.pkl")
MODEL_PATH = Path("models/tiny.pth")

PITCH_LOWEST = 21  # A0
PITCH_HIGHEST = 114  # F#8
NOTES = PITCH_HIGHEST - PITCH_LOWEST + 1
MAX_HARMONICS = 32
SAMPLE_RATE = 48000

