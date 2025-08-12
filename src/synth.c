#include <stdio.h>
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
    float* buffer, size_t buffer_size,
    int pitch, int velocity, float duration
) {
}
