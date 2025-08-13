#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#include "../song.h"
#include "../synth.h"
#include "../io.h"
#include "test_data.h"

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
    printf("  Duration: %.2f seconds\n", song->total_ticks * UNIT(song->bpm));
    printf("  Notes: %zu\n", song->note_count);

    printf("\nNote details:\n");
    for (size_t i = 0; i < song->note_count; i++) {
        const Note* note = &song->notes[i];
        float start_time = note->start * UNIT(song->bpm);
        float duration = note->duration * UNIT(song->bpm);
        printf("  Note %zu: Pitch=%d, Vel=%d, Start=%.3fs, Dur=%.3fs\n",
               i, note->pitch, note->velocity, start_time, duration);
    }

    float song_duration = song->total_ticks * UNIT(song->bpm);
    size_t buffer_size = (size_t)(song_duration * SAMPLE_RATE) + 1000;

    printf("\nRendering audio:\n");
    printf("  Sample rate: %d Hz\n", SAMPLE_RATE);
    printf("  Buffer size: %zu samples\n", buffer_size);

    float* buffer = malloc(buffer_size * sizeof(float));
    if (!buffer) {
        printf("Error: Could not allocate audio buffer\n");
        free_song(song);
        return 1;
    }

    render_song(song, buffer);
    size_t samples_written = buffer_size; // Use full buffer size for now

    printf("  Samples written: %zu\n", samples_written);
    printf("  Actual duration: %.3f seconds\n", (float)samples_written / SAMPLE_RATE);

    float rms = 0.0f;
    float peak = 0.0f;
    for (size_t i = 0; i < samples_written; i++) {
        rms += buffer[i] * buffer[i];
        float abs_val = fabsf(buffer[i]);
        if (abs_val > peak) peak = abs_val;
    }
    rms = powf(rms / samples_written, 0.5f);

    printf("  RMS level: %.6f\n", rms);
    printf("  Peak level: %.6f\n", peak);

    printf("\nSaving to file...\n");
    if (save_audio_to_file("song_output.txt", buffer, samples_written, SAMPLE_RATE) == 0) {
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
