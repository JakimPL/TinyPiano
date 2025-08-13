#pragma once

#include <stddef.h>
#include <stdint.h>

#define MAX_HARMONICS 32
#define SAMPLE_RATE 48000
#define FADE_IN_DURATION 0.1f
#define FADE_OUT_DURATION 1.0f
#define ESTIMATION_FREQUENCY 10.0f
#define MASTER_GAINER 0.1f

float calculate_frequency(int pitch);
void synthesize_note(float* buffer, size_t buffer_size, int pitch, int velocity, float duration);
