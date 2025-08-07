A4_PITCH = 69
A4_FREQUENCY = 440.0


def calculate_frequency(
        pitch: int,
        a4_frequency: float = A4_FREQUENCY,
        a4_pitch: int = A4_PITCH
) -> float:
    """MIDI pitch -> frequency in Hz (A4 = 440 Hz)."""
    return a4_frequency * (2.0 ** ((pitch - a4_pitch) / 12.0))
