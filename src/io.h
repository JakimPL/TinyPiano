#pragma once

#include <stddef.h>

int save_audio_to_file(const char *filename, const float *buffer,
                       size_t sample_count, int sample_rate);
