#pragma once

#include <stddef.h>
#include <stdint.h>

#define TICKS_PER_QUARTER 480
#define DEFAULT_BPM 120
#define TICK_DURATION(bpm) (60.0f / ((bpm) * TICKS_PER_QUARTER))

typedef struct {
  uint8_t pitch;
  uint8_t velocity;
  uint16_t start;
  uint16_t duration;
  uint16_t _padding;
} Note;

typedef struct {
  Note *notes;
  size_t note_count;
  uint16_t bpm;
  uint16_t total_ticks;
} Song;

Song *create_song(const Note *notes, size_t note_count, uint16_t bpm);
void free_song(Song *song);
size_t render_song(const Song *song, float *buffer, size_t buffer_size,
                   int sample_rate);
