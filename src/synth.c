#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "maths.h"
#include "model.h"
#include "synth.h"

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
    for (uint8_t harmonic = 0; harmonic < MAX_HARMONICS; ++harmonic) {
        const float h = harmonic / (MAX_HARMONICS - 1.0f);
        const float f = 2.0f * M_PI * fundamental * (harmonic + 1);

        float amplitude = 0.0f;
        float next_amplitude = 0.0f;
        for (size_t sample = 0; sample < size; ++sample) {
            const float t = (float)sample / SAMPLE_RATE;
            const size_t m = sample % estimation_samples;

            if (m == 0) {
                amplitude = next_amplitude;
                next_amplitude = predict_amplitude(p, v, h, t + e);
                const float fade_in = t / FADE_IN_DURATION;
                const float fade_out = (duration + FADE_OUT_DURATION - t) / FADE_OUT_DURATION;
                const float envelope = fminf(fade_in, fade_out);
                next_amplitude *= fminf(1.0f, envelope);
            }

            const float m_f = (float)m / estimation_samples;
            const float a = (m_f * next_amplitude + (1.0f - m_f) * amplitude);
            const float y = a * sinf(f * t);
            waveform[sample] += y;
        }
    }

    float peak = 0.0f;
    for (size_t sample = 0; sample < size; ++sample) {
        peak = fmaxf(peak, fabsf(waveform[sample]));
    }

    float gain = 0.2f / peak;
    for (size_t sample = 0; sample < size; ++sample) {
        waveform[sample] *= gain;
        buffer[start + sample] += waveform[sample];
    }

    free(waveform);
}
