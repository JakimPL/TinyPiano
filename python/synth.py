import numpy as np
import torch
from IPython.display import Audio

from constants import SAMPLE_RATE, MAX_HARMONICS
from dataset import NoteHarmonics
from notes import calculate_frequency

def resynthesize_note(note: NoteHarmonics, sample_rate: int = SAMPLE_RATE) -> np.ndarray:
    times = note.times  # shape (T_fft,), times of FFT windows in seconds
    duration = times[-1] - times[0]
    total_samples = int(np.ceil(duration * sample_rate))

    full_time = np.linspace(times[0], times[-1], total_samples, endpoint=False)

    pitch = note.pitch
    base_freq = calculate_frequency(pitch)

    waveform = np.zeros(total_samples, dtype=np.float32)

    for h, harmonic_data in note.harmonics.items():
        freq = base_freq * h
        amps = harmonic_data.amplitudes  # shape (T_fft,)

        amps_interp = np.interp(full_time, times, amps)
        sinusoid = np.sin(2 * np.pi * freq * full_time)
        waveform += amps_interp * sinusoid.astype(np.float32)

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
    model.eval()
    with torch.no_grad():
        N = int(duration * sample_rate)
        t = torch.linspace(0, duration, N, dtype=torch.float32, device=device)  # (N,)

        # Normalize pitch and velocity to [0, 1]
        pitch_tensor = torch.full((N,), pitch / 127.0, dtype=torch.float32, device=device)
        velocity_tensor = torch.full((N,), velocity / 127.0, dtype=torch.float32, device=device)
        time_tensor = t  # (N,)

        waveform = torch.zeros(N, dtype=torch.float32, device=device)

        for h in range(0, max_harmonics + 1):
            harmonic_tensor = torch.full((N,), float(h) / max_harmonics, dtype=torch.float32, device=device)

            amp = model(pitch_tensor, velocity_tensor, harmonic_tensor, time_tensor)  # (N,)
            amp = torch.exp(amp).clamp(min=1e-8, max=1e4)
            freq = calculate_frequency(pitch) * h  # pitch is still raw MIDI integer
            sine_wave = torch.sin(2 * np.pi * freq * t)  # (N,)
            waveform += amp * sine_wave

        return waveform.cpu().numpy().astype(np.float32)


def play_waveform(waveform: np.ndarray, sample_rate: int = SAMPLE_RATE, autoplay: bool = False) -> Audio:
    return Audio(waveform, rate=sample_rate, autoplay=autoplay)
