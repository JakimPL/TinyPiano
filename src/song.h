#pragma once

#include <stddef.h>
#include <stdint.h>

// Time resolution: 480 ticks per quarter note (common MIDI standard)
// At 120 BPM: quarter note = 0.5s, so 1 tick = 0.5/480 ≈ 0.00104s
#define TICKS_PER_QUARTER 480
#define DEFAULT_BPM 120

// Calculate tick duration in seconds
#define TICK_DURATION(bpm) (60.0f / ((bpm) * TICKS_PER_QUARTER))

// Note structure - fits in 8 bytes total
typedef struct {
  uint8_t pitch;     // MIDI pitch (0-127)
  uint8_t velocity;  // MIDI velocity (0-127)
  uint16_t start;    // Start time in ticks (0-65535)
  uint16_t duration; // Duration in ticks (0-65535)
  uint16_t _padding; // Padding to align to 8 bytes
} Note;

// Song structure
typedef struct {
  Note *notes;          // Array of notes
  size_t note_count;    // Number of notes
  uint16_t bpm;         // Beats per minute
  uint16_t total_ticks; // Total song length in ticks
} Song;

/**
 * Create a new song
 * @param notes Array of notes (will be copied)
 * @param note_count Number of notes
 * @param bpm Beats per minute
 * @return Allocated song structure (must be freed with free_song)
 */
Song *create_song(const Note *notes, size_t note_count, uint16_t bpm);

/**
 * Free a song and its resources
 * @param song Song to free
 */
void free_song(Song *song);

/**
 * Render a song to audio buffer
 * @param song Song to render
 * @param buffer Output buffer
 * @param buffer_size Size of buffer in samples
 * @param sample_rate Sample rate
 * @return Number of samples written
 */
size_t render_song(const Song *song, float *buffer, size_t buffer_size,
                   int sample_rate);

/**
 * Save rendered audio to text file (one sample per line)
 * @param filename Output filename
 * @param buffer Audio buffer
 * @param sample_count Number of samples
 * @param sample_rate Sample rate
 * @return 0 on success, -1 on error
 */
int save_audio_to_file(const char *filename, const float *buffer,
                       size_t sample_count, int sample_rate);

/**
 * Create a sample test song
 * @return Allocated test song
 */
Song *create_test_song(void);
