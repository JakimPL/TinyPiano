BUILD_DIR = build
BIN_DIR = bin
VENV_DIR = venv
PYTHON_VENV = $(VENV_DIR)/bin/python
PIP_VENV = $(VENV_DIR)/bin/pip
CMAKE_BUILD_TYPE ?= Release

ifeq ($(OS),Windows_NT)
    PYTHON_VENV = $(VENV_DIR)/Scripts/python.exe
    PIP_VENV = $(VENV_DIR)/Scripts/pip.exe
endif

all: setup venv build

setup:
	@echo "Setting up CMake build directory..."
	mkdir -p $(BUILD_DIR)
	mkdir -p $(BIN_DIR)
	cd $(BUILD_DIR) && cmake .. -G "MSYS Makefiles" -DCMAKE_BUILD_TYPE=$(CMAKE_BUILD_TYPE)

venv:
	@echo "Setting up Python virtual environment..."
	@if [ ! -d "$(VENV_DIR)" ]; then \
		python -m venv $(VENV_DIR) --upgrade-deps; \
	fi
	@echo "Installing Python dependencies..."
	$(PYTHON_VENV) -m ensurepip --upgrade
	$(PYTHON_VENV) -m pip install --upgrade pip
	$(PYTHON_VENV) -m pip install numpy ipython scipy torch
	$(PYTHON_VENV) -m pip install -r python/requirements.txt

dataset:
	@echo "Building dataset from samples..."
	$(PYTHON_VENV) python/main.py build

train:
	@echo "Training the model..."
	$(PYTHON_VENV) python/main.py train

extract_weights:
	@echo "Extracting neural network weights..."
	$(PYTHON_VENV) python/extract_weights.py

convert_midi:
	@echo "Converting MIDI files..."
	$(PYTHON_VENV) python/convert_midi.py

test_consistency:
	@echo "Testing consistency between Python and C implementation..."
	$(PYTHON_VENV) python/test_consistency.py

build: setup
	@echo "Building TinyPiano..."
	cd $(BUILD_DIR) && make -j

tinypiano: setup
	cd $(BUILD_DIR) && make tinypiano -j

tinypiano_4k: setup
	cd $(BUILD_DIR) && make tinypiano_4k -j

test: setup
	cd $(BUILD_DIR) && make test_all

clean:
	@echo "Cleaning all build artifacts..."
	rm -rf $(BUILD_DIR)
	rm -rf $(BIN_DIR)
	rm -f song_output.txt

clean_all: clean
	@echo "Cleaning all artifacts including virtual environment..."
	rm -rf $(VENV_DIR)

rebuild: clean all

info:
	@echo "TinyPiano Build System"
	@echo "====================="
	@echo "Available targets:"
	@echo "  all               - Setup, install Python deps and build everything"
	@echo "  venv              - Create Python virtual environment and install dependencies"
	@echo "  build             - Build all targets"
	@echo "  tinypiano         - Build standard executable"
	@echo "  tinypiano_4k      - Build 4KB demo with Crinkler"
	@echo "  test              - Build and run all tests"
	@echo "  dataset           - Build dataset from samples (Python)"
	@echo "  train             - Train the model (Python)"
	@echo "  extract_weights   - Extract neural network weights (Python)"
	@echo "  convert_midi      - Convert MIDI files (Python)"
	@echo "  test_consistency  - Test Python/C consistency (Python)"
	@echo "  clean             - Remove build artifacts"
	@echo "  clean_all         - Remove all artifacts including venv"
	@echo "  rebuild           - Clean and rebuild everything"

.PHONY: all setup venv build tinypiano tinypiano_4k test_all dataset train extract_weights convert_midi test_consistency clean clean_all rebuild info
