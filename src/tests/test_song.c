#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include "src/song.h"
#include "src/synth.h"
#include "test_data.h"
#include "src/io.h"

int main() {
    printf("Piano Song Player Test\n");
    printf("======================\n\n");

    Song* song = create_test_song();
    if (!song) {
        printf("Error: Could not create test song\n");
        return 1;
    }

    printf("Test song created:\n");
    printf("  BPM: %d\n", song->bpm);
    printf("  Total ticks: %d\n", song->total_ticks);
    printf("  Duration: %.2f seconds\n", song->total_ticks * TICK_DURATION(song->bpm));
    printf("  Notes: %zu\n", song->note_count);

    printf("\nNote details:\n");
    for (size_t i = 0; i < song->note_count; i++) {
        const Note* note = &song->notes[i];
        float start_time = note->start * TICK_DURATION(song->bpm);
        float duration = note->duration * TICK_DURATION(song->bpm);
        printf("  Note %zu: Pitch=%d, Vel=%d, Start=%.3fs, Dur=%.3fs\n",
               i, note->pitch, note->velocity, start_time, duration);
    }

    float song_duration = song->total_ticks * TICK_DURATION(song->bpm);
    int sample_rate = SAMPLE_RATE;
    size_t buffer_size = (size_t)(song_duration * sample_rate) + 1000;

    printf("\nRendering audio:\n");
    printf("  Sample rate: %d Hz\n", sample_rate);
    printf("  Buffer size: %zu samples\n", buffer_size);

    float* buffer = malloc(buffer_size * sizeof(float));
    if (!buffer) {
        printf("Error: Could not allocate audio buffer\n");
        free_song(song);
        return 1;
    }

    size_t samples_written = render_song(song, buffer, buffer_size, sample_rate);

    printf("  Samples written: %zu\n", samples_written);
    printf("  Actual duration: %.3f seconds\n", (float)samples_written / sample_rate);

    float rms = 0.0f;
    float peak = 0.0f;
    for (size_t i = 0; i < samples_written; i++) {
        rms += buffer[i] * buffer[i];
        float abs_val = fabsf(buffer[i]);
        if (abs_val > peak) peak = abs_val;
    }
    rms = sqrtf(rms / samples_written);

    printf("  RMS level: %.6f\n", rms);
    printf("  Peak level: %.6f\n", peak);

    printf("\nSaving to file...\n");
    if (save_audio_to_file("song_output.txt", buffer, samples_written, sample_rate) == 0) {
        printf("  Saved to: song_output.txt\n");
    } else {
        printf("  Error saving file\n");
    }

    printf("\nFirst 10 samples:\n");
    for (int i = 0; i < 10 && i < (int)samples_written; i++) {
        printf("  Sample %d: %.6f\n", i, buffer[i]);
    }

    free(buffer);
    free_song(song);

    printf("\nDone!\n");
    return 0;
}
