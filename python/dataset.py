import pickle
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional, Iterable, Tuple, Union

import numpy as np
import torch
from torch.utils.data import Dataset
from tqdm import tqdm

from constants import MAX_HARMONICS
from fft import find_window, get_harmonic
from file import read_audio
from notes import calculate_frequency


@dataclass
class HarmonicData:
    amplitudes: np.ndarray  # shape (T,)

    def to_dict(self) -> Dict[str, Any]:
        return {"amplitudes": self.amplitudes.tolist()}

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "HarmonicData":
        return HarmonicData(amplitudes=np.asarray(d["amplitudes"], dtype=np.float32))


@dataclass
class NoteHarmonics:
    pitch: int
    volume: int
    times: np.ndarray
    window_size: int
    harmonics: Dict[int, HarmonicData] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pitch": int(self.pitch),
            "volume": int(self.volume),
            "times": self.times.tolist(),
            "window_size": int(self.window_size),
            "harmonics": {int(h): hd.to_dict() for h, hd in self.harmonics.items()}
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "NoteHarmonics":
        harmonics = {int(h): HarmonicData.from_dict(hd) for h, hd in d["harmonics"].items()}
        return NoteHarmonics(
            pitch=int(d["pitch"]),
            volume=int(d["volume"]),
            times=np.asarray(d["times"], dtype=np.float32),
            window_size=int(d["window_size"]),
            harmonics=harmonics
        )


@dataclass
class HarmonicsArchive:
    notes: Dict[Tuple[int, int], NoteHarmonics] = field(default_factory=dict)

    def save(self, path: Union[str, Path]):
        with open(path, "wb") as f:
            pickle.dump({k: v.to_dict() for k, v in self.notes.items()}, f, protocol=pickle.HIGHEST_PROTOCOL)

    @staticmethod
    def load(path: Union[str, Path]) -> "HarmonicsArchive":
        with open(path, "rb") as f:
            raw = pickle.load(f)
        notes = {tuple(k): NoteHarmonics.from_dict(v) if not isinstance(v, NoteHarmonics) else v
                 for k, v in raw.items()}
        return HarmonicsArchive(notes=notes)

    @classmethod
    def from_raw_dict(cls, raw_dict: Dict[Tuple[int, int], Dict[str, Any]]) -> "HarmonicsArchive":
        notes = {}
        for (pitch, volume), info in raw_dict.items():
            times = np.asarray(info["times"], dtype=np.float32)
            window_size = int(info["window_size"])
            harmonics = {}
            for h, amps in info.get("harmonics", {}).items():
                harmonics[int(h)] = HarmonicData(amplitudes=np.asarray(amps["amplitudes"], dtype=np.float32))
            notes[(int(pitch), int(volume))] = NoteHarmonics(
                pitch=int(pitch), volume=int(volume), times=times, window_size=window_size, harmonics=harmonics
            )
        return cls(notes=notes)


class HarmonicTorchDataset(Dataset):
    def __init__(
            self,
            archive: HarmonicsArchive,
            keys: Optional[Iterable[Tuple[int, int]]] = None,
            harmonics: Optional[Iterable[int]] = None,
            use_log: bool = True,
            eps: float = 1e-9,
            return_torch: bool = False,
            time_grid: Optional[np.ndarray] = None
    ):
        self.archive = archive
        self.eps = float(eps)
        self.use_log = bool(use_log)
        self.return_torch = bool(return_torch)
        self.time_grid = None if time_grid is None else np.asarray(time_grid, dtype=np.float32)

        # Build flat index of available (pitch,volume,harmonic) triples
        all_keys = list(archive.notes.keys()) if keys is None else list(keys)
        idx = []
        for k in all_keys:
            if k not in archive.notes:
                continue
            note = archive.notes[k]
            available_h = sorted(note.harmonics.keys())
            sel_h = list(harmonics) if harmonics is not None else available_h
            for h in sel_h:
                if h in note.harmonics:
                    idx.append((k[0], k[1], h))  # (pitch, volume, harmonic)
        self.index = idx

        self._global_log_mean = None
        self._global_log_std = None
        if self.use_log:
            self._compute_global_log_stats()

    def _compute_global_log_stats(self):
        logs = []
        for (p, v, h) in self.index:
            note = self.archive.notes[(p, v)]
            amps = note.harmonics[h].amplitudes.astype(np.float32)
            amps = np.maximum(amps, self.eps)
            logs.append(np.log(amps).ravel())
        if len(logs) == 0:
            self._global_log_mean = 0.0
            self._global_log_std = 1.0
            return
        all_logs = np.concatenate(logs, axis=0)
        self._global_log_mean = float(np.mean(all_logs))
        self._global_log_std = float(np.std(all_logs) + 1e-12)

    @property
    def global_log_stats(self):
        return self._global_log_mean, self._global_log_std

    def __len__(self):
        return len(self.index)

    def _resample_to_grid(self, src_times: np.ndarray, src_amps: np.ndarray) -> np.ndarray:
        if self.time_grid is None:
            return src_amps.astype(np.float32)

        src_times = np.asarray(src_times, dtype=np.float32)
        src_amps = np.asarray(src_amps, dtype=np.float32)
        res = np.interp(self.time_grid, src_times, src_amps, left=src_amps[0], right=src_amps[-1])
        return res.astype(np.float32)

    def __getitem__(self, idx):
        p, v, h = self.index[idx]
        note = self.archive.notes[(p, v)]
        hd = note.harmonics[h]
        amps = hd.amplitudes  # shape (T_src,)
        times = note.times

        amps = self._resample_to_grid(times, amps)  # shape (T_target,)
        amps = np.maximum(amps, self.eps)

        if self.use_log:
            target = np.log(amps).astype(np.float32)
        else:
            target = amps.astype(np.float32)

        norm_pitch = p / 127.0
        norm_velocity = float(v) / 127.0
        norm_harmonic = float(h - 1) / (MAX_HARMONICS - 1) if MAX_HARMONICS > 1 else 0.0

        if self.return_torch:
            return (
                torch.tensor(norm_pitch, dtype=torch.float32),
                torch.tensor(norm_velocity, dtype=torch.float32),
                torch.tensor(norm_harmonic, dtype=torch.float32),
                torch.from_numpy(target)
            )
        else:
            return norm_pitch, norm_velocity, norm_harmonic, target


def get_pitch_and_volume_from_path(path: Path) -> Tuple[int, int]:
    pitch, volume = map(int, "".join(s for s in path.stem if not s.isalpha()).split("_"))
    return pitch, volume


def build_archive_from_files(path: Path) -> HarmonicsArchive:
    paths = sorted(path.glob("*.wav"))
    archive = HarmonicsArchive()
    for path in tqdm(paths, desc="Building Harmonics Archive"):
        pitch, volume = get_pitch_and_volume_from_path(path)
        frequency = calculate_frequency(pitch)
        sample_rate, sample = read_audio(path)

        window_size = find_window(sample_rate, frequency)
        harmonics_map = {}
        times = None
        for harmonic in range(1, MAX_HARMONICS + 1):
            times_h, amplitudes = get_harmonic(sample, sample_rate, window_size, frequency, harmonic)
            if times is None:
                times = np.asarray(times_h, dtype=np.float32)

            harmonics_map[harmonic] = HarmonicData(amplitudes=np.asarray(amplitudes, dtype=np.float32))

        note = NoteHarmonics(
            pitch=pitch,
            volume=volume,
            times=times,
            window_size=window_size,
            harmonics=harmonics_map
        )

        archive.notes[(pitch, volume)] = note

    return archive
