#pragma once

#include <stddef.h>

#define MAX_HARMONICS 32
#define SAMPLE_RATE 48000

/**
 * Calculate frequency from MIDI pitch
 * @param pitch MIDI pitch (21-127, where 69 = A4 = 440Hz)
 * @return frequency in Hz
 */
float calculate_frequency(int pitch);

/**
 * Generate waveform for a piano note using harmonic synthesis
 * @param buffer Output buffer to fill with samples (must be pre-allocated)
 * @param buffer_size Size of the buffer in samples
 * @param pitch MIDI pitch (21-127)
 * @param velocity MIDI velocity (0-127)
 * @param duration Duration in seconds
 * @param sample_rate Sample rate in Hz
 * @return Number of samples actually written
 */
size_t synthesize_note(float* buffer, size_t buffer_size,
                      int pitch, int velocity, float duration,
                      int sample_rate);


