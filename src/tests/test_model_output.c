#include <stdio.h>
#include <math.h>
#include "src/model.h"

int main() {
    float pitch = 0.5f;
    float velocity = 0.5f;
    float harmonic = 0.0f;
    float time = 0.0f;

    float log_amp = predict_amplitude(pitch, velocity, harmonic, time);

    printf("C Model Output:\n");
    printf("Input: (%.1f, %.1f, %.1f, %.1f)\n", pitch, velocity, harmonic, time);
    printf("Log amplitude: %.6f\n", log_amp);

    return 0;
}
