from pathlib import Path

DATASET_PATH = Path("wav")
ARCHIVE_PATH = Path("data/harmonics.pkl")
MODEL_PATH = Path("models/tiny.pth")
CODE_PATH = Path("src/model.c")
WEIGHTS_PATH = Path("src/weights.c")
SONG_PATH = Path("src/data.c")

MAX_HARMONICS = 32
SAMPLE_RATE = 48000

TICKS_PER_QUARTER = 480
DEFAULT_BPM = 120
