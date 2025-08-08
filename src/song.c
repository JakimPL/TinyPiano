#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include "song.h"
#include "synth.h"

#define FADE_OUT_DURATION 0.5f

Song* create_song(const Note* notes, size_t note_count, uint16_t bpm) {
    Song* song = malloc(sizeof(Song));
    if (!song) return NULL;

    song->notes = malloc(note_count * sizeof(Note));
    if (!song->notes) {
        free(song);
        return NULL;
    }

    for (size_t i = 0; i < note_count; i++) {
        song->notes[i] = notes[i];
    }
    song->note_count = note_count;
    song->bpm = bpm;

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

    for (size_t i = 0; i < total_samples; i++) {
        buffer[i] = 0.0f;
    }

    for (size_t note_idx = 0; note_idx < song->note_count; note_idx++) {
        const Note* note = &song->notes[note_idx];

        float start_time = note->start * tick_duration;
        float note_duration = note->duration * tick_duration;
        float extended_duration = note_duration + FADE_OUT_DURATION;

        size_t start_sample = (size_t)(start_time * sample_rate);
        size_t note_samples = (size_t)(note_duration * sample_rate);
        size_t extended_samples = (size_t)(extended_duration * sample_rate);
        size_t fade_samples = (size_t)(FADE_OUT_DURATION * sample_rate);

        if (start_sample >= total_samples) continue;

        if (start_sample + extended_samples > total_samples) {
            extended_samples = total_samples - start_sample;
        }

        float* note_buffer = malloc(extended_samples * sizeof(float));
        if (!note_buffer) continue;

        synthesize_note(note_buffer, extended_samples, note->pitch, note->velocity,
                       extended_duration, sample_rate);

        for (size_t i = 0; i < extended_samples; i++) {
            float sample = note_buffer[i];

            if (i >= note_samples) {
                size_t fade_pos = i - note_samples;
                if (fade_pos < fade_samples) {
                    float fade_factor = 1.0f - (float)fade_pos / fade_samples;
                    sample *= fade_factor;
                }
            }

            if (start_sample + i < total_samples) {
                buffer[start_sample + i] += sample;
            }
        }

        free(note_buffer);
    }

    float max_abs = 0.0f;
    for (size_t i = 0; i < total_samples; i++) {
        float abs_val = fabsf(buffer[i]);
        if (abs_val > max_abs) {
            max_abs = abs_val;
        }
    }

    if (max_abs > 0.0f) {
        float scale = 0.95f / max_abs;
        for (size_t i = 0; i < total_samples; i++) {
            buffer[i] *= scale;
        }
    }

    return total_samples;
}
