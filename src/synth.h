#pragma once

#include <stddef.h>

#define MAX_HARMONICS 32
#define SAMPLE_RATE 48000

float calculate_frequency(int pitch);
size_t synthesize_note(float* buffer, size_t buffer_size,
                      int pitch, int velocity, float duration,
                      int sample_rate);
