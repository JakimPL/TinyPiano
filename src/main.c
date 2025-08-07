#include <stdio.h>
#include <math.h>
#include "model.h"

int main() {
    float pitch = 0.5f;
    float velocity = 0.5f;
    float harmonic = 0.0f;
    float time = 0.0f;

    float log_amp = predict_amplitude(pitch, velocity, harmonic, time);
    float amplitude = expf(log_amp);

    printf("Input: (%.2f, %.2f, %.2f, %.2f)\n", pitch, velocity, harmonic, time);
    printf("Log amplitude: %.6f\n", log_amp);
    printf("Amplitude: %.6f\n", amplitude);

    return 0;
}
