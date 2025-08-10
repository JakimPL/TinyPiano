#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#include "../synth.h"

int main() {
    int pitch = 69;
    int velocity = 100;
    float duration = 1.0f;
    int sample_rate = SAMPLE_RATE;

    size_t buffer_size = (size_t)(duration * sample_rate);

    float* buffer = malloc(buffer_size * sizeof(float));
    if (!buffer) {
        fprintf(stderr, "Error: Could not allocate buffer\n");
        return 1;
    }

    printf("Synthesizing note:\n");
    printf("  Pitch: %d (%.2f Hz)\n", pitch, calculate_frequency(pitch));
    printf("  Velocity: %d\n", velocity);
    printf("  Duration: %.2f seconds\n", duration);
    printf("  Sample rate: %d Hz\n", sample_rate);
    printf("  Buffer size: %zu samples\n", buffer_size);

    size_t samples_written = synthesize_note(buffer, buffer_size,
                                           pitch, velocity, duration,
                                           sample_rate);

    printf("Generated %zu samples\n", samples_written);

    printf("\nFirst 10 sample values:\n");
    for (int i = 0; i < 10 && i < (int)samples_written; i++) {
        printf("  Sample %d: %.6f\n", i, buffer[i]);
    }

    float rms = 0.0f;
    for (size_t i = 0; i < samples_written; i++) {
        rms += buffer[i] * buffer[i];
    }
    rms = powf(rms / samples_written, 0.5f);
    printf("\nRMS level: %.6f\n", rms);

    float peak = 0.0f;
    for (size_t i = 0; i < samples_written; i++) {
        float abs_val = fabsf(buffer[i]);
        if (abs_val > peak) peak = abs_val;
    }
    printf("Peak level: %.6f\n", peak);

    free(buffer);
    return 0;
}
