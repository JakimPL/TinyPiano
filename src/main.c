#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/wait.h>
#include "data.h"
#include "song.h"
#include "synth.h"

#define FRAME_SIZE 1024

static int setup_audio_pipe(void) {
    int pipe_fds[2];
    if (pipe(pipe_fds) == -1) return -1;

    pid_t pid = fork();
    if (pid == -1) return -1;

    if (pid == 0) {
        close(pipe_fds[1]);
        dup2(pipe_fds[0], STDIN_FILENO);
        close(pipe_fds[0]);

        execlp("aplay", "aplay", "-f", "FLOAT_LE", "-c", "1", "-r", "48000", NULL);
        exit(127);
    }

    close(pipe_fds[0]);
    return pipe_fds[1];
}

int main() {
    Song* song = create_midi_song();
    if (!song) return 1;

    printf("Loaded song: %d notes, %.2f seconds\n",
           (int)song->note_count,
           song->total_ticks * TICK_DURATION(song->bpm));

    int audio_fd = setup_audio_pipe();
    if (audio_fd == -1) {
        free_song(song);
        return 1;
    }

    float song_duration = song->total_ticks * TICK_DURATION(song->bpm);
    size_t total_samples = (size_t)(song_duration * SAMPLE_RATE);

    float* buffer = malloc(total_samples * sizeof(float));
    if (!buffer) {
        close(audio_fd);
        free_song(song);
        return 1;
    }

    printf("Rendering and streaming audio...\n");

    size_t samples_written = render_song(song, buffer, total_samples, SAMPLE_RATE);

    float frame[FRAME_SIZE];
    for (size_t i = 0; i < samples_written; i += FRAME_SIZE) {
        size_t frame_size = (i + FRAME_SIZE > samples_written) ?
                           samples_written - i : FRAME_SIZE;

        for (size_t j = 0; j < frame_size; j++) {
            frame[j] = buffer[i + j];
        }

        if (write(audio_fd, frame, frame_size * sizeof(float)) == -1) break;
    }

    free(buffer);
    close(audio_fd);
    wait(NULL);
    free_song(song);

    return 0;
}
