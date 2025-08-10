@echo off
echo ==================================
echo TinyPiano - 4KB Demo Build Script
echo ==================================

REM Create build directories
if not exist "build\demo" mkdir "build\demo"
if not exist "bin" mkdir "bin"

echo [STEP 1/3] Compiling object files with aggressive optimization...
gcc -m32 -std=c99 -O3 -Os -ffast-math -fomit-frame-pointer ^
    -fno-stack-protector -fno-exceptions -fno-unwind-tables ^
    -fno-asynchronous-unwind-tables -fmerge-all-constants ^
    -fdata-sections -ffunction-sections -nostartfiles ^
    -DTINYHEADER -DTINYIMPORT -Isrc ^
    -c src/main.c -o build/demo/main.o

gcc -m32 -std=c99 -O3 -Os -ffast-math -fomit-frame-pointer ^
    -fno-stack-protector -fno-exceptions -fno-unwind-tables ^
    -fno-asynchronous-unwind-tables -fmerge-all-constants ^
    -fdata-sections -ffunction-sections -DTINYHEADER -DTINYIMPORT -Isrc ^
    -c src/model.c -o build/demo/model.o

gcc -m32 -std=c99 -O3 -Os -ffast-math -fomit-frame-pointer ^
    -fno-stack-protector -fno-exceptions -fno-unwind-tables ^
    -fno-asynchronous-unwind-tables -fmerge-all-constants ^
    -fdata-sections -ffunction-sections -DTINYHEADER -DTINYIMPORT -Isrc ^
    -c src/song.c -o build/demo/song.o

gcc -m32 -std=c99 -O3 -Os -ffast-math -fomit-frame-pointer ^
    -fno-stack-protector -fno-exceptions -fno-unwind-tables ^
    -fno-asynchronous-unwind-tables -fmerge-all-constants ^
    -fdata-sections -ffunction-sections -DTINYHEADER -DTINYIMPORT -Isrc ^
    -c src/data.c -o build/demo/data.o

gcc -m32 -std=c99 -O3 -Os -ffast-math -fomit-frame-pointer ^
    -fno-stack-protector -fno-exceptions -fno-unwind-tables ^
    -fno-asynchronous-unwind-tables -fmerge-all-constants ^
    -fdata-sections -ffunction-sections -DTINYHEADER -DTINYIMPORT -Isrc ^
    -c src/synth.c -o build/demo/synth.o

gcc -m32 -std=c99 -O3 -Os -ffast-math -fomit-frame-pointer ^
    -fno-stack-protector -fno-exceptions -fno-unwind-tables ^
    -fno-asynchronous-unwind-tables -fmerge-all-constants ^
    -fdata-sections -ffunction-sections -DTINYHEADER -DTINYIMPORT -Isrc ^
    -c src/weights.c -o build/demo/weights.o

echo [STEP 2/3] Stripping debug symbols (preserving entry points)...
for %%f in (build\demo\main.o build\demo\model.o build\demo\song.o build\demo\data.o build\demo\synth.o build\demo\weights.o) do strip --strip-debug "%%f"

echo [STEP 3/3] Linking with Crinkler (original working method)...
REM First try with Windows Kit libraries
set WINKIT_LIB=C:\Program Files (x86)\Windows Kits\10\Lib\10.0.26100.0\um\x86

crinkler /OUT:bin/tinypiano_4k.exe /TINYHEADER /TINYIMPORT /SUBSYSTEM:CONSOLE ^
    /COMPMODE:SLOW /HASHSIZE:500 /HASHTRIES:100 /ORDERTRIES:10000 ^
    build/demo/main.o build/demo/model.o build/demo/song.o ^
    build/demo/data.o build/demo/synth.o build/demo/weights.o ^
    "%WINKIT_LIB%\kernel32.lib"

REM Check final result
if exist "bin/tinypiano_4k.exe" (
    for %%F in (bin/tinypiano_4k.exe) do (
        if %%~zF gtr 0 (
            echo ============================================================
            echo SUCCESS: 4KB demo build completed!
            echo Final size: %%~zF bytes
            if %%~zF gtr 4096 (
                echo WARNING: Size exceeds 4KB limit!
            ) else (
                echo EXCELLENT: Within 4KB demoscene limit!
            )
            echo ============================================================
        ) else (
            echo ERROR: Executable created but has 0 bytes (Crinkler failed)
        )
    )
) else (
    echo ERROR: Build failed - executable not created
)

pause
