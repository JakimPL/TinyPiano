cmake_minimum_required(VERSION 3.10)
project(TinyPiano VERSION 1.0.0 LANGUAGES C)

# Set C standard
set(CMAKE_C_STANDARD 99)
set(CMAKE_C_STANDARD_REQUIRED ON)

# Compiler flags
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -Wall -Wextra")
set(CMAKE_C_FLAGS_RELEASE "-O2 -DNDEBUG")
set(CMAKE_C_FLAGS_DEBUG "-g -O0")

# Default to Release build
if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Release)
endif()

# Output directories
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}/bin)
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}/build/lib)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}/build/lib)

# Include directories
include_directories(${CMAKE_SOURCE_DIR})

# Find math library
find_library(MATH_LIBRARY m)

# Core library sources
set(CORE_SOURCES
    src/model.c
    src/weights.c
)

set(SYNTH_SOURCES
    ${CORE_SOURCES}
    src/synth.c
)

set(SONG_SOURCES
    ${SYNTH_SOURCES}
    src/song.c
)

set(MIDI_SOURCES
    ${SONG_SOURCES}
    src/data.c
)

# Create static libraries for modular builds
add_library(tinypiano_core STATIC ${CORE_SOURCES})
target_link_libraries(tinypiano_core ${MATH_LIBRARY})

add_library(tinypiano_synth STATIC ${SYNTH_SOURCES})
target_link_libraries(tinypiano_synth ${MATH_LIBRARY})

add_library(tinypiano_song STATIC ${SONG_SOURCES})
target_link_libraries(tinypiano_song ${MATH_LIBRARY})

add_library(tinypiano_midi STATIC ${MIDI_SOURCES})
target_link_libraries(tinypiano_midi ${MATH_LIBRARY})

# Main executables
add_executable(model src/main.c)
target_link_libraries(model tinypiano_core)

# Test executables
add_executable(test_model src/tests/test_model_output.c)
target_link_libraries(test_model tinypiano_core)

add_executable(test_synth src/tests/test_synth.c)
target_link_libraries(test_synth tinypiano_synth)

add_executable(test_song src/tests/test_song.c)
target_link_libraries(test_song tinypiano_song)

# Custom targets for Python tools
add_custom_target(extract_weights
    COMMAND python3 ${CMAKE_SOURCE_DIR}/python/extract_weights.py
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
    COMMENT "Extracting weights from PyTorch model"
)

add_custom_target(convert_midi
    COMMAND echo "MIDI converter ready. Usage: python3 python/convert_midi.py midi/file.mid"
    COMMENT "MIDI converter setup"
)

# Test runner target
add_custom_target(test_all
    COMMAND echo "Running neural network test..." && ${CMAKE_SOURCE_DIR}/bin/test_model
    COMMAND echo "Running synthesizer test..." && ${CMAKE_SOURCE_DIR}/bin/test_synth
    COMMAND echo "Running song player test..." && ${CMAKE_SOURCE_DIR}/bin/test_song
    COMMAND echo "All tests completed."
    DEPENDS test_model test_synth test_song
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
    COMMENT "Running all tests"
)

# Development helpers
add_custom_target(size
    COMMAND echo "Binary sizes:" && ls -lh ${CMAKE_SOURCE_DIR}/bin/* 2>/dev/null | awk '{print $$9 ": " $$5}' || true
    COMMAND echo "Library sizes:" && ls -lh ${CMAKE_SOURCE_DIR}/build/lib/* 2>/dev/null | awk '{print $$9 ": " $$5}' || true
    COMMENT "Showing binary and library sizes"
)

# Install Python dependencies
add_custom_target(install_deps
    COMMAND pip install torch mido
    COMMENT "Installing Python dependencies"
)

# Clean target (handled automatically by CMake, but we can add custom cleaning)
add_custom_target(clean_all
    COMMAND ${CMAKE_COMMAND} --build ${CMAKE_BINARY_DIR} --target clean
    COMMAND rm -rf ${CMAKE_SOURCE_DIR}/bin/*
    COMMAND rm -f ${CMAKE_SOURCE_DIR}/song_output.txt
    COMMENT "Cleaning all build artifacts and outputs"
)
