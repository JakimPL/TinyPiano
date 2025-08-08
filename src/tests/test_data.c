#include "test_data.h"

Song* create_test_song(void) {
    Note notes[] = {
        {60, 80, 0,    TICKS_PER_QUARTER, 0},
        {64, 80, TICKS_PER_QUARTER, TICKS_PER_QUARTER, 0},
        {67, 80, TICKS_PER_QUARTER*2, TICKS_PER_QUARTER, 0},
        {72, 80, TICKS_PER_QUARTER*3, TICKS_PER_QUARTER, 0},
        {36, 100, 0, TICKS_PER_QUARTER*2, 0},
        {55, 100, TICKS_PER_QUARTER*2, TICKS_PER_QUARTER*2, 0},
        {64, 60, TICKS_PER_QUARTER/2, TICKS_PER_QUARTER*3, 0},
        {67, 60, TICKS_PER_QUARTER*2 + TICKS_PER_QUARTER/2, TICKS_PER_QUARTER + TICKS_PER_QUARTER/2, 0},
    };

    return create_song(notes, sizeof(notes)/sizeof(notes[0]), DEFAULT_BPM);
}
