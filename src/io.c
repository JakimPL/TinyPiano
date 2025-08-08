#include <stdio.h>
#include "io.h"

int save_audio_to_file(const char* filename, const float* buffer,
                       size_t sample_count, int sample_rate) {
    FILE* file = fopen(filename, "w");
    if (!file) return -1;

    fprintf(file, "# Audio samples\n");
    fprintf(file, "# Sample rate: %d Hz\n", sample_rate);
    fprintf(file, "# Sample count: %zu\n", sample_count);
    fprintf(file, "# Duration: %.3f seconds\n", (float)sample_count / sample_rate);
    fprintf(file, "\n");

    for (size_t i = 0; i < sample_count; i++) {
        fprintf(file, "%.8f\n", buffer[i]);
    }

    fclose(file);
    return 0;
}
