#include <stdlib.h>
#include <stdio.h>
#include <math.h>
#include <windows.h>
#include <mmsystem.h>

#include "data.h"
#include "song.h"
#include "synth.h"

#define FRAME_SIZE 1024


void __main(void) {
}

void play_audio(float* buffer, size_t samples) {
    WAVEFORMATEX wfx = {
        1,
        2,
        SAMPLE_RATE,
        SAMPLE_RATE * 2 * 2,
        4,
        16,
        0
    };

    HWAVEOUT hwo;
    MMRESULT result = waveOutOpen(&hwo, WAVE_MAPPER, &wfx, 0, 0, CALLBACK_NULL);
    if(result != MMSYSERR_NOERROR)
        return;

    short* pcm = malloc(samples * 2 * sizeof(short));
    for(size_t i = 0; i < samples; i++) {
        short sample = (short)(buffer[i] * 32767.0f);
        pcm[i * 2] = sample;
        pcm[i * 2 + 1] = sample;
    }

    WAVEHDR whdr = {0};
    whdr.lpData = (char*)pcm;
    whdr.dwBufferLength = samples * 2 * sizeof(short);

    result = waveOutPrepareHeader(hwo, &whdr, sizeof(whdr));
    if(result != MMSYSERR_NOERROR) {
        free(pcm);
        return;
    }

    result = waveOutWrite(hwo, &whdr, sizeof(whdr));
    if(result != MMSYSERR_NOERROR) {
        waveOutUnprepareHeader(hwo, &whdr, sizeof(whdr));
        free(pcm);
        return;
    }

    while(!(whdr.dwFlags & WHDR_DONE)) {
        Sleep(1);
    }

    waveOutUnprepareHeader(hwo, &whdr, sizeof(whdr));
    waveOutClose(hwo);
    free(pcm);
}


int main() {
    Song* song = create_midi_song();
    const float song_duration = song->total_ticks * UNIT(song->bpm) + FADE_OUT_DURATION;
    const size_t total_samples = (size_t)(song_duration * SAMPLE_RATE);
    float* buffer = malloc(total_samples * sizeof(float));

#ifdef PRINT
    printf("Creating song with %zu notes and duration: %.2f seconds\n", song->note_count, song_duration);
#endif
    render_song(song, buffer);

#ifdef PRINT
    printf("Playing song with duration: %.2f seconds\n", song_duration);
#endif
    play_audio(buffer, total_samples);

    free(buffer);
    free_song(song);
    return 0;
}
