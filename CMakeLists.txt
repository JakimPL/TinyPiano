cmake_minimum_required(VERSION 3.10)

if(WIN32 AND NOT DEFINED CMAKE_C_COMPILER)
    find_program(GCC_COMPILER gcc)
    if(GCC_COMPILER)
        set(CMAKE_C_COMPILER ${GCC_COMPILER})
        set(CMAKE_CXX_COMPILER g++)
        message(STATUS "Using GCC compiler: ${GCC_COMPILER}")
    endif()
endif()

project(TinyPiano VERSION 1.0.0 LANGUAGES C)

set(CMAKE_C_STANDARD 99)
set(CMAKE_C_STANDARD_REQUIRED ON)

if(CMAKE_C_COMPILER_ID STREQUAL "GNU")
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -Wall -Wextra")
    set(CMAKE_C_FLAGS_RELEASE "-O2 -DNDEBUG")
    set(CMAKE_C_FLAGS_DEBUG "-g -O0")
    message(STATUS "Using GCC compiler with GNU-specific flags")
elseif(CMAKE_C_COMPILER_ID STREQUAL "MSVC")
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} /W4")
    set(CMAKE_C_FLAGS_RELEASE "/O2 /DNDEBUG")
    set(CMAKE_C_FLAGS_DEBUG "/Zi /Od")
    message(STATUS "Using MSVC compiler")
endif()

if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Release)
endif()

set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}/bin)
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}/build/lib)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}/build/lib)

set(CMAKE_OBJECT_PATH_MAX 260)
set(CMAKE_C_OBJECT_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}/build/obj)

include_directories(${CMAKE_SOURCE_DIR}/src)

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

set(IO_SOURCES
    src/io.c
)

add_library(tinypiano_core STATIC ${CORE_SOURCES})
add_library(tinypiano_synth STATIC ${SYNTH_SOURCES})
add_library(tinypiano_song STATIC ${SONG_SOURCES})
add_library(tinypiano_midi STATIC ${MIDI_SOURCES})
add_library(tinypiano_io STATIC ${IO_SOURCES})

add_executable(tinypiano src/main.c)
target_link_libraries(tinypiano tinypiano_midi m winmm)

add_executable(test_model src/tests/test_model_output.c)
target_link_libraries(test_model tinypiano_core m)

add_executable(test_synth src/tests/test_synth.c)
target_link_libraries(test_synth tinypiano_synth m)

add_executable(test_song src/tests/test_song.c src/tests/test_data.c)
target_link_libraries(test_song tinypiano_song tinypiano_io m)

add_executable(tinypiano_4k
    src/main.c
    src/model.c
    src/song.c
    src/data.c
    src/synth.c
    src/weights.c
)

if(CMAKE_C_COMPILER_ID STREQUAL "GNU")
    target_compile_options(tinypiano_4k PRIVATE
        -m32
        -std=c99
        -O3 -Os
        -ffast-math
        -fomit-frame-pointer
        -fno-stack-protector
        -fno-exceptions
        -fno-unwind-tables
        -fno-asynchronous-unwind-tables
        -fmerge-all-constants
        -fdata-sections
        -ffunction-sections
        -nostartfiles
    )

    target_compile_definitions(tinypiano_4k PRIVATE
        TINYHEADER
        TINYIMPORT
    )

    target_include_directories(tinypiano_4k PRIVATE src)

    set_target_properties(tinypiano_4k PROPERTIES
        RUNTIME_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}/bin
        OUTPUT_NAME tinypiano_4k
    )

    target_link_libraries(tinypiano_4k m winmm)

    add_custom_command(TARGET tinypiano_4k POST_BUILD
        COMMAND ${CMAKE_SOURCE_DIR}/crinkler_build.bat
        WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}

        COMMENT "Compressing executable with Crinkler for 4KB demo"
    )
else()
    message(WARNING "4KB demo target requires GCC compiler for Crinkler compatibility")
endif()
