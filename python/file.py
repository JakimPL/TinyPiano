from pathlib import Path
from typing import Tuple

import numpy as np
from pydub import AudioSegment
from scipy.io import wavfile


def read_mp3_mono(path: Path) -> Tuple[int, np.ndarray]:
    if AudioSegment is None:
        raise RuntimeError("pydub not available. Install pydub and ffmpeg to read mp3 files.")

    seg = AudioSegment.from_file(str(path), format="mp3")
    sr = seg.frame_rate
    samples = np.array(seg.get_array_of_samples())
    if seg.channels > 1:
        samples = samples.reshape((-1, seg.channels))
        samples = samples.mean(axis=1)
    sampwidth = seg.sample_width
    if sampwidth == 2:
        samples = samples.astype(np.float32) / 32768.0
    else:
        maxv = float(2 ** (8 * sampwidth - 1))
        samples = samples.astype(np.float32) / maxv

    return sr, samples


def read_wav_mono(path: Path) -> Tuple[int, np.ndarray]:
    sr, data = wavfile.read(path)
    if data.dtype == np.int16:
        data = data.astype(np.float32) / 32768.0
    else:
        data = data.astype(np.float32)
    if data.ndim == 2:
        data = data.mean(axis=1)
    return sr, data


def read_audio(path: Path) -> Tuple[int, np.ndarray]:
    ext = path.suffix.lower()
    if ext == ".wav":
        return read_wav_mono(path)
    elif ext == ".mp3":
        return read_mp3_mono(path)
    else:
        raise RuntimeError(f"Unsupported audio extension: {ext}")
