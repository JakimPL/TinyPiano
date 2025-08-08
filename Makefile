CC = gcc
CFLAGS = -Wall -Wextra -O2 -std=c99 -I.
LDFLAGS = -lm

# Source directories
SRC_DIR = src
TEST_DIR = src/tests

# Core object files
CORE_OBJS = $(SRC_DIR)/model.o $(SRC_DIR)/weights.o
SYNTH_OBJS = $(CORE_OBJS) $(SRC_DIR)/synth.o
SONG_OBJS = $(SYNTH_OBJS) $(SRC_DIR)/song.o
MIDI_OBJS = $(SONG_OBJS) $(SRC_DIR)/data.o

# Main targets
all: extract_weights convert_midi model

# Core programs
model: $(SRC_DIR)/main.c $(CORE_OBJS)
	$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS)

# Test programs (built on demand)
test_model: $(TEST_DIR)/test_model_output.c $(CORE_OBJS)
	$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS)

test_synth: $(TEST_DIR)/test_synth.c $(SYNTH_OBJS)
	$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS)

test_song: $(TEST_DIR)/test_song.c $(SONG_OBJS)
	$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS)

# Build and run all tests
test: test_model test_synth test_song
	@echo "Running neural network test..."
	./test_model
	@echo "\nRunning synthesizer test..."
	./test_synth
	@echo "\nRunning song player test..."
	./test_song
	@echo "\nAll tests completed."

# Python tools
extract_weights: python/extract_weights.py
	python3 python/extract_weights.py

convert_midi: python/convert_midi.py
	@echo "MIDI converter ready. Usage: python3 python/convert_midi.py midi/file.mid"

# Object file compilation
%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

# Clean up
clean:
	rm -f model test_model test_synth test_song
	rm -f $(SRC_DIR)/*.o
	rm -f song_output.txt

# Development helpers
size: model
	@echo "Binary sizes:"
	@ls -lh model test_* 2>/dev/null | awk '{print $$9 ": " $$5}' || true
	@echo "Core library sizes:"
	@wc -c $(SRC_DIR)/*.o 2>/dev/null | tail -1 || true

install_deps:
	@echo "Installing Python dependencies..."
	pip install torch mido

.PHONY: all test clean extract_weights convert_midi size install_deps
