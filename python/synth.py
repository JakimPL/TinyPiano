from IPython.display import Audio
import torch

from constants import SAMPLE_RATE, MAX_HARMONICS
from dataset import NoteHarmonics
from notes import calculate_frequency

import numpy as np


def resynthesize_note(note: NoteHarmonics, sample_rate: int = SAMPLE_RATE) -> np.ndarray:
    """
    Resynthesize a waveform from NoteHarmonics by interpolating amplitudes
    to full audio sample rate and summing harmonics.

    Args:
        note: NoteHarmonics instance with sparse harmonic envelopes.
        sample_rate: target output sample rate.

    Returns:
        waveform: np.ndarray float32, time-domain waveform at sample_rate.
    """
    times = note.times  # shape (T_fft,), times of FFT windows in seconds
    duration = times[-1] - times[0]
    total_samples = int(np.ceil(duration * sample_rate))

    # Full time axis for output waveform
    full_time = np.linspace(times[0], times[-1], total_samples, endpoint=False)

    pitch = note.pitch
    base_freq = calculate_frequency(pitch)

    waveform = np.zeros(total_samples, dtype=np.float32)

    for h, harmonic_data in note.harmonics.items():
        freq = base_freq * h
        amps = harmonic_data.amplitudes  # shape (T_fft,)

        # Interpolate amplitude envelope to full time axis
        amps_interp = np.interp(full_time, times, amps)

        # Generate sinusoid at harmonic frequency
        sinusoid = np.sin(2 * np.pi * freq * full_time)

        # Add weighted harmonic to waveform
        waveform += amps_interp * sinusoid.astype(np.float32)

    # Normalize to -1..1
    max_val = np.max(np.abs(waveform))
    if max_val > 0:
        waveform /= max_val

    return waveform.astype(np.float32)


def synthesize_note(
        model,
        pitch: int,
        velocity: int,
        duration: float,
        sample_rate: int = SAMPLE_RATE,
        max_harmonics: int = MAX_HARMONICS,
        device: torch.device = torch.device("cpu")
) -> np.ndarray:
    """
    Generate a waveform for a given note using a trained DirectTinyHarmonicModel (float input version).

    Args:
        model: DirectTinyHarmonicModel
        pitch: MIDI pitch (int)
        velocity: MIDI velocity (int)
        duration: Duration in seconds (float)
        sample_rate: Sample rate (Hz)
        max_harmonics: Number of harmonics to synthesize
        device: torch.device

    Returns:
        waveform: np.ndarray of shape (samples,) in float32
    """
    model.eval()
    with torch.no_grad():
        N = int(duration * sample_rate)
        t = torch.linspace(0, duration, N, dtype=torch.float32, device=device)  # (N,)

        # Normalize pitch and velocity to [0, 1]
        pitch_tensor = torch.full((N,), pitch / 127.0, dtype=torch.float32, device=device)
        velocity_tensor = torch.full((N,), velocity / 127.0, dtype=torch.float32, device=device)
        time_tensor = t  # (N,)

        waveform = torch.zeros(N, dtype=torch.float32, device=device)

        for h in range(1, max_harmonics + 1):
            harmonic_tensor = torch.full((N,), float(h) / max_harmonics, dtype=torch.float32, device=device)

            amp = model(pitch_tensor, velocity_tensor, harmonic_tensor, time_tensor)  # (N,)
            amp = torch.exp(amp).clamp(min=1e-8, max=1e4)
            freq = calculate_frequency(pitch) * h  # pitch is still raw MIDI integer
            sine_wave = torch.sin(2 * np.pi * freq * t)  # (N,)
            waveform += amp * sine_wave

        # Normalize to [-1, 1]
        waveform /= waveform.abs().max().clamp(min=1e-6)
        return waveform.cpu().numpy().astype(np.float32)


def play_waveform(waveform: np.ndarray, sample_rate: int = SAMPLE_RATE) -> Audio:
    """
    Play a waveform directly in a Jupyter notebook.

    Args:
        waveform: NumPy array (float32), shape (N,), values in [-1, 1]
        sample_rate: Sample rate in Hz

    Returns:
        IPython.display.Audio widget
    """
    return Audio(waveform, rate=sample_rate, autoplay=True)
