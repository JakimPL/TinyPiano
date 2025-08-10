#include <stdlib.h>
#include <stdio.h>

#include "data.h"
#include "song.h"
#include "synth.h"

#define FRAME_SIZE 1024


void __main(void) {
}


int main() {
    Song* song = create_midi_song();
    float song_duration = song->total_ticks * TICK_DURATION(song->bpm);
    size_t total_samples = (size_t)(song_duration * SAMPLE_RATE);
    float* buffer = malloc(total_samples * sizeof(float));

    render_song(song, buffer, total_samples, SAMPLE_RATE);
    
    return 0;
}
