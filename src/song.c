#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include "song.h"
#include "synth.h"

Song* create_song(const Note* notes, size_t note_count, uint16_t bpm) {
    Song* song = malloc(sizeof(Song));
    if (!song) return NULL;

    song->notes = malloc(note_count * sizeof(Note));
    if (!song->notes) {
        free(song);
        return NULL;
    }

    // Copy notes
    for (size_t i = 0; i < note_count; i++) {
        song->notes[i] = notes[i];
    }
    song->note_count = note_count;
    song->bpm = bpm;

    // Calculate total song length
    song->total_ticks = 0;
    for (size_t i = 0; i < note_count; i++) {
        uint16_t note_end = notes[i].start + notes[i].duration;
        if (note_end > song->total_ticks) {
            song->total_ticks = note_end;
        }
    }

    return song;
}

void free_song(Song* song) {
    if (song) {
        free(song->notes);
        free(song);
    }
}

size_t render_song(const Song* song, float* buffer, size_t buffer_size, int sample_rate) {
    if (!song || !buffer || buffer_size == 0) return 0;

    float tick_duration = TICK_DURATION(song->bpm);
    float song_duration = song->total_ticks * tick_duration;
    size_t total_samples = (size_t)(song_duration * sample_rate);

    if (total_samples > buffer_size) {
        total_samples = buffer_size;
    }

    // Clear buffer
    for (size_t i = 0; i < total_samples; i++) {
        buffer[i] = 0.0f;
    }

    // Render each note
    for (size_t note_idx = 0; note_idx < song->note_count; note_idx++) {
        const Note* note = &song->notes[note_idx];

        float start_time = note->start * tick_duration;
        float note_duration = note->duration * tick_duration;

        size_t start_sample = (size_t)(start_time * sample_rate);
        size_t note_samples = (size_t)(note_duration * sample_rate);

        // Skip notes that start beyond our buffer
        if (start_sample >= total_samples) continue;

        // Clamp note samples to buffer bounds
        if (start_sample + note_samples > total_samples) {
            note_samples = total_samples - start_sample;
        }

        // Create temporary buffer for this note
        float* note_buffer = malloc(note_samples * sizeof(float));
        if (!note_buffer) continue;

        // Synthesize the note
        synthesize_note(note_buffer, note_samples, note->pitch, note->velocity,
                       note_duration, sample_rate);

        // Mix into main buffer
        for (size_t i = 0; i < note_samples; i++) {
            buffer[start_sample + i] += note_buffer[i];
        }

        free(note_buffer);
    }

    return total_samples;
}

int save_audio_to_file(const char* filename, const float* buffer, size_t sample_count, int sample_rate) {
    FILE* file = fopen(filename, "w");
    if (!file) return -1;

    // Write header with metadata
    fprintf(file, "# Audio samples\n");
    fprintf(file, "# Sample rate: %d Hz\n", sample_rate);
    fprintf(file, "# Sample count: %zu\n", sample_count);
    fprintf(file, "# Duration: %.3f seconds\n", (float)sample_count / sample_rate);
    fprintf(file, "\n");

    // Write samples (one per line)
    for (size_t i = 0; i < sample_count; i++) {
        fprintf(file, "%.8f\n", buffer[i]);
    }

    fclose(file);
    return 0;
}

Song* create_test_song(void) {
    // Create a simple test song: C major arpeggio with polyphony
    Note notes[] = {
        // C major arpeggio - first voice
        {60, 80, 0,    TICKS_PER_QUARTER, 0},     // C4, quarter note
        {64, 80, TICKS_PER_QUARTER, TICKS_PER_QUARTER, 0},     // E4
        {67, 80, TICKS_PER_QUARTER*2, TICKS_PER_QUARTER, 0},   // G4
        {72, 80, TICKS_PER_QUARTER*3, TICKS_PER_QUARTER, 0},   // C5

        // Bass line - second voice (overlapping)
        {36, 100, 0, TICKS_PER_QUARTER*2, 0},                  // C3, half note
        {55, 100, TICKS_PER_QUARTER*2, TICKS_PER_QUARTER*2, 0}, // G3, half note

        // Harmony - third voice
        {64, 60, TICKS_PER_QUARTER/2, TICKS_PER_QUARTER*3, 0}, // E4, dotted half
        {67, 60, TICKS_PER_QUARTER*2 + TICKS_PER_QUARTER/2, TICKS_PER_QUARTER + TICKS_PER_QUARTER/2, 0}, // G4
    };

    return create_song(notes, sizeof(notes)/sizeof(notes[0]), DEFAULT_BPM);
}
