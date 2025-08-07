#include <stdio.h>
#include <math.h>
#include <string.h>
#include "synth.h"
#include "model.h"

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

float calculate_frequency(int pitch) {
    // MIDI pitch 69 = A4 = 440 Hz
    // Formula: freq = 440 * 2^((pitch - 69) / 12)
    return 440.0f * powf(2.0f, (pitch - 69) / 12.0f);
}

size_t synthesize_note(float* buffer, size_t buffer_size,
                      int pitch, int velocity, float duration,
                      int sample_rate) {
    if (!buffer || buffer_size == 0 || duration <= 0.0f) {
        return 0;
    }

    // Calculate number of samples needed
    size_t num_samples = (size_t)(duration * sample_rate);
    if (num_samples > buffer_size) {
        num_samples = buffer_size;
    }

    // Clear buffer
    for (size_t i = 0; i < num_samples; i++) {
        buffer[i] = 0.0f;
    }

    // Normalize inputs to [0, 1] range as expected by the model
    float pitch_norm = pitch / 127.0f;
    float velocity_norm = velocity / 127.0f;

    float base_freq = calculate_frequency(pitch);

    // Generate each harmonic
    for (int h = 0; h < MAX_HARMONICS; h++) {
        float harmonic_norm = (float)h / MAX_HARMONICS;
        float harmonic_freq = base_freq * h;

        // Skip harmonics that are too high frequency
        if (harmonic_freq > sample_rate / 2.0f) {
            break;
        }

        // Generate samples for this harmonic
        for (size_t i = 0; i < num_samples; i++) {
            float time = (float)i / sample_rate;

            // Get amplitude from neural network model
            float log_amp = predict_amplitude(pitch_norm, velocity_norm,
                                           harmonic_norm, time);
            float amplitude = expf(log_amp);

            // Clamp amplitude to reasonable range for audio
            if (amplitude > 1.0f) amplitude = 1.0f;
            if (amplitude < 1e-8f) amplitude = 1e-8f;            // Generate sine wave for this harmonic
            float phase = 2.0f * M_PI * harmonic_freq * time;
            float sine_wave = sinf(phase);

            // Add weighted harmonic to buffer
            buffer[i] += amplitude * sine_wave;
        }
    }

    return num_samples;
}
