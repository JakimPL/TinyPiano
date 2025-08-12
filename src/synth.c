#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

#include "synth.h"
#include "model.h"

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

float calculate_frequency(int pitch) {
    return 440.0f * powf(2.0f, (pitch - 69) / 12.0f);
}

void synthesize_note(
    float* buffer, size_t start,
    int pitch, int velocity, float duration
) {
    const float p = pitch / 127.0f;
    const float v = velocity / 127.0f;

    const float fundamental = calculate_frequency(pitch);
    const float e = 1.0f / ESTIMATION_FREQUENCY;
    const size_t estimation_samples = e * SAMPLE_RATE;
    const size_t size = (duration + FADE_OUT_DURATION) * SAMPLE_RATE;

    float* waveform = (float*)calloc(size, sizeof(float));

    // Test: Add some debugging for the first note
    static int note_count = 0;
    int debug_this_note = (note_count < 1);
    note_count++;

    for (uint8_t harmonic = 0; harmonic < MAX_HARMONICS; ++harmonic) {
        const float h = harmonic / (MAX_HARMONICS - 1.0f);
        const float f = 2.0f * M_PI * fundamental * (harmonic + 1);

        float amplitude = 0.0f;
        float next_amplitude = 0.0f;
        for (size_t sample = 0; sample < size; ++sample) {
            const float t = sample / SAMPLE_RATE;
            const size_t m = sample % estimation_samples;

            if (m == 0) {
                amplitude = next_amplitude;
                next_amplitude = predict_amplitude(p, v, h, t + e);
                // Don't apply envelope here - apply it per sample
            }

            const float a = ((float)m * next_amplitude + (float)(estimation_samples - m) * amplitude) / (float)estimation_samples;

            // Apply envelope per sample
            const float sample_time = (float)sample / SAMPLE_RATE;
            const float fade_in = sample_time / FADE_IN_DURATION;
            const float fade_out = (duration + FADE_OUT_DURATION - sample_time) / FADE_OUT_DURATION;
            float envelope = fade_in;
            if (fade_out < envelope) envelope = fade_out;
            if (envelope > 1.0f) envelope = 1.0f;

            const float y = a * envelope * sinf(f * t);
            waveform[sample] += y;
        }
    }

    float peak = 0.0f;
    for (size_t sample = 0; sample < size; ++sample) {
        peak = fmaxf(peak, fabsf(waveform[sample]));
    }

    if (peak > 0.0f) {
        float gain = 0.5f * v / peak;
        if (debug_this_note) {
            printf("  Peak: %.8f, Velocity: %.3f, Gain: %.3f\n", peak, v, gain);
        }
        for (size_t sample = 0; sample < size; ++sample) {
            waveform[sample] *= gain;
            // For now, assume buffer is large enough - this should be fixed by passing buffer_size
            buffer[start + sample] += waveform[sample];
        }
    } else if (debug_this_note) {
        printf("  Peak is zero - no sound generated!\n");
    }

    free(waveform);
}
