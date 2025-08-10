# TinyPiano - Simple build system
# CMake files go to build/, final executables go to bin/

BUILD_DIR = build
BIN_DIR = bin
CMAKE_BUILD_TYPE ?= Release

# Default target
all: setup build

# Setup CMake build directory 
setup:
	@echo "Setting up CMake build directory..."
	mkdir -p $(BUILD_DIR)
	mkdir -p $(BIN_DIR)
	cd $(BUILD_DIR) && cmake .. -G "MSYS Makefiles" -DCMAKE_BUILD_TYPE=$(CMAKE_BUILD_TYPE)

build: setup
	@echo "Building TinyPiano..."
	cd $(BUILD_DIR) && make -j

tinypiano: setup
	cd $(BUILD_DIR) && make tinypiano -j

tinypiano_4k: setup
	cd $(BUILD_DIR) && make tinypiano_4k -j

test_all: setup
	cd $(BUILD_DIR) && make test_all

extract_weights:
	@echo "Extracting neural network weights..."
	python python/extract_weights.py

convert_midi: setup
	cd $(BUILD_DIR) && make convert_midi

clean:
	@echo "Cleaning all build artifacts..."
	rm -rf $(BUILD_DIR)
	rm -rf $(BIN_DIR)
	rm -f song_output.txt

rebuild: clean all

info:
	@echo "TinyPiano Build System"
	@echo "====================="
	@echo "Available targets:"
	@echo "  all           - Setup and build everything"
	@echo "  build         - Build all targets"
	@echo "  tinypiano     - Build standard executable"
	@echo "  tinypiano_4k  - Build 4KB demo with Crinkler"
	@echo "  test_all      - Build and run all tests"
	@echo "  extract_weights - Extract neural network weights"
	@echo "  convert_midi  - Convert MIDI files"
	@echo "  clean         - Remove all build artifacts"
	@echo "  rebuild       - Clean and rebuild everything"

.PHONY: all setup build tinypiano tinypiano_4k test_all extract_weights convert_midi clean rebuild info
