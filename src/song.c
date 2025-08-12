#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "math.h"
#include "song.h"
#include "synth.h"

Song* create_song(const Note* notes, size_t note_count, uint16_t bpm) {
    Song* song = malloc(sizeof(Song));
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

void render_song(const Song *song, float *buffer) {
    const float unit = UNIT(song->bpm);
    for (size_t i = 0; i < song->note_count; i++) {
        const Note *note = &song->notes[i];
        const size_t start = note->start * unit * SAMPLE_RATE;
        const float duration = note->duration * unit;

        synthesize_note(buffer, start, note->pitch, note->velocity, duration);
    }
}
