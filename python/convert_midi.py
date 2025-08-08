#!/usr/bin/env python3
"""
Script to convert MIDI files to our custom song format and generate C code.
"""

import mido
import argparse
from pathlib import Path
from typing import List, Tuple, Optional
from constants import TICKS_PER_QUARTER, DEFAULT_BPM, SONG_PATH

def quantize_time(time_ticks: int, quantize_level: int) -> int:
    """
    Quantize time to the nearest quantization level.

    Args:
        time_ticks: Time in ticks
        quantize_level: Quantization level (e.g., 120 = 32nd note, 240 = 16th note)

    Returns:
        Quantized time in ticks
    """
    if quantize_level <= 0:
        return time_ticks
    return round(time_ticks / quantize_level) * quantize_level

def midi_to_notes(midi_file: str, quantize_level: int = 0, max_duration: Optional[float] = None) -> Tuple[List[tuple], int]:
    """
    Convert MIDI file to list of notes.

    Args:
        midi_file: Path to MIDI file
        quantize_level: Quantization level in ticks (0 = no quantization)
        max_duration: Maximum song duration in seconds (None = no limit)

    Returns:
        Tuple of (notes_list, bpm) where notes_list contains (pitch, velocity, start, duration) tuples
    """
    try:
        mid = mido.MidiFile(midi_file)
    except Exception as e:
        raise ValueError(f"Could not load MIDI file: {e}")

    # Find tempo (BPM) - use first tempo change or default
    bpm = DEFAULT_BPM
    for track in mid.tracks:
        for msg in track:
            if msg.type == 'set_tempo':
                # MIDI tempo is in microseconds per beat
                bpm = int(60_000_000 / msg.tempo)
                break
        if bpm != DEFAULT_BPM:
            break

    print(f"MIDI file info:")
    print(f"  Tracks: {len(mid.tracks)}")
    print(f"  Ticks per beat: {mid.ticks_per_beat}")
    print(f"  BPM: {bpm}")

    # Convert MIDI ticks to our tick format
    # MIDI files can have different ticks_per_beat, we normalize to our TICKS_PER_QUARTER
    tick_scale = TICKS_PER_QUARTER / mid.ticks_per_beat

    # Track note on/off events
    active_notes = {}  # note_pitch -> (start_time, velocity)
    notes = []

    current_time = 0
    max_time_ticks = None
    if max_duration:
        max_time_ticks = int(max_duration * bpm * TICKS_PER_QUARTER / 60)

    # Process all tracks
    for track_idx, track in enumerate(mid.tracks):
        current_time = 0
        print(f"\nProcessing track {track_idx}: {track.name}")

        for msg in track:
            current_time += int(msg.time * tick_scale)

            # Stop if we've exceeded max duration
            if max_time_ticks and current_time > max_time_ticks:
                break

            if msg.type == 'note_on' and msg.velocity > 0:
                # Note on
                key = (msg.channel, msg.note)
                start_time = quantize_time(current_time, quantize_level)
                active_notes[key] = (start_time, msg.velocity)

            elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                # Note off
                key = (msg.channel, msg.note)
                if key in active_notes:
                    start_time, velocity = active_notes[key]
                    end_time = quantize_time(current_time, quantize_level)
                    duration = max(1, end_time - start_time)  # Ensure minimum duration

                    # Clamp values to our format limits
                    pitch = max(0, min(127, msg.note))
                    velocity = max(1, min(127, velocity))
                    start_time = max(0, min(65535, start_time))
                    duration = max(1, min(65535, duration))

                    notes.append((pitch, velocity, start_time, duration))
                    del active_notes[key]

    # Handle any remaining active notes (force them to end)
    if active_notes:
        print(f"Warning: {len(active_notes)} notes were still active at end of file")
        for key, (start_time, velocity) in active_notes.items():
            channel, note = key
            duration = max(1, min(65535, TICKS_PER_QUARTER))  # Default to quarter note
            pitch = max(0, min(127, note))
            velocity = max(1, min(127, velocity))
            start_time = max(0, min(65535, start_time))
            notes.append((pitch, velocity, start_time, duration))

    # Sort notes by start time
    notes.sort(key=lambda x: x[2])

    print(f"\nExtracted {len(notes)} notes")
    if notes:
        total_ticks = max(note[2] + note[3] for note in notes)
        duration_seconds = total_ticks * 60 / (bpm * TICKS_PER_QUARTER)
        print(f"Total duration: {total_ticks} ticks ({duration_seconds:.2f} seconds)")

    return notes, bpm

def generate_c_code(notes: List[tuple], bpm: int, output_file: str) -> None:
    """
    Generate C code with the notes array.

    Args:
        notes: List of (pitch, velocity, start, duration) tuples
        bpm: Beats per minute
        output_file: Output C file path
    """
    c_code = f'''#include "data.h"

Song* create_midi_song(void) {{
    Note notes[] = {{
'''

    # Add each note
    for pitch, velocity, start, duration in notes:
        c_code += f'        {{{pitch}, {velocity}, {start}, {duration}, 0}},\n'

    c_code += f'''    }};

    return create_song(notes, {len(notes)}, {bpm});
}}
'''
    # Write to file
    with open(output_file, 'w') as f:
        f.write(c_code)

    print(f"Generated C code written to {output_file}")

def main():
    parser = argparse.ArgumentParser(description='Convert MIDI file to our custom song format')
    parser.add_argument('input', help='Input MIDI file path')
    parser.add_argument('-o', '--output', help='Output C file path', default=SONG_PATH)
    parser.add_argument('-q', '--quantize', type=int, default=0,
                       help='Quantization level in ticks (0=none, 120=32nd note, 240=16th note)')
    parser.add_argument('-d', '--duration', type=float,
                       help='Maximum duration in seconds (truncate long songs)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Parse MIDI and show info without generating C code')

    args = parser.parse_args()

    if not Path(args.input).exists():
        print(f"Error: Input file '{args.input}' not found")
        return 1

    try:
        print(f"Converting MIDI file: {args.input}")
        if args.quantize > 0:
            print(f"Quantization: {args.quantize} ticks")
        if args.duration:
            print(f"Max duration: {args.duration} seconds")
        print()

        notes, bpm = midi_to_notes(args.input, args.quantize, args.duration)

        if not notes:
            print("Warning: No notes found in MIDI file")
            return 1

        # Show some example notes
        print(f"\nFirst few notes:")
        for i, (pitch, velocity, start, duration) in enumerate(notes[:5]):
            start_sec = start * 60 / (bpm * TICKS_PER_QUARTER)
            dur_sec = duration * 60 / (bpm * TICKS_PER_QUARTER)
            print(f"  Note {i}: Pitch={pitch}, Vel={velocity}, Start={start_sec:.3f}s, Dur={dur_sec:.3f}s")

        if len(notes) > 5:
            print(f"  ... and {len(notes) - 5} more notes")

        if not args.dry_run:
            generate_c_code(notes, bpm, args.output)
            print(f"\nTo use in your C code:")
            print(f"  #include \"{args.output}\"")
            print(f"  Song* song = create_midi_song();")

        return 0

    except Exception as e:
        print(f"Error: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
