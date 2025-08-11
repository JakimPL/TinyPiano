from typing import Tuple, Optional

import numpy as np
from scipy.signal import stft


def find_window(
        fs: float,
        f0: float,
        max_window_time: float = 0.1,
        m_max: Optional[int] = None,
) -> int:

    samples_per_period = fs / f0
    max_samples = int(round(max_window_time * fs))
    if max_samples < 1:
        raise ValueError("max_window_time too small for given sample rate")

    if m_max is None:
        m_max = max(1, int(np.ceil(max_samples / max(1.0, samples_per_period))))

    best_N = None
    best_err = np.inf

    for m in range(1, m_max + 1):
        target = m * samples_per_period  # target samples ideally
        N = int(round(target))
        if N < 3:
            continue
        if N > max_samples:
            break
        err = abs(N - target)  # absolute sample rounding error
        if err < best_err:
            best_err = err
            best_N = N

    if best_N is None:
        raise RuntimeError("Could not find a suitable window length with given constraints")

    return best_N


def get_harmonic(
        signal: np.ndarray,
        fs: float,
        window_size: int,
        f0: float,
        harmonic: int = 1,
        hop_size: Optional[int] = None,
        window_type: str = "hann",
) -> Tuple[np.ndarray, np.ndarray]:
    if signal.ndim != 1:
        raise ValueError("signal must be a 1D numpy array")
    if hop_size is None:
        hop_size = max(1, window_size // 4)

    freqs, times, Zxx = stft(
        signal,
        fs=fs,
        window=window_type,
        nperseg=window_size,
        noverlap=window_size - hop_size,
        boundary=None,
        padded=False,
    )

    target_freq = f0 * harmonic
    bin_index = int(np.argmin(np.abs(freqs - target_freq)))
    amplitudes = np.abs(Zxx[bin_index, :])

    return times, amplitudes
