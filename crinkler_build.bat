@echo off
echo ============================================================
echo Crinkler compression for 4KB demo
echo ============================================================

echo Collecting object files from build directory...

REM Use the same Windows Kit library path as working build.bat
set WINKIT_LIB=C:\Program Files (x86)\Windows Kits\10\Lib\10.0.26100.0\um\x86

REM Convert CMake .obj files to .o files for Crinkler compatibility
echo Converting object files...
copy build\CMakeFiles\tinypiano_4k.dir\src\main.c.obj build\main.o
copy build\CMakeFiles\tinypiano_4k.dir\src\model.c.obj build\model.o
copy build\CMakeFiles\tinypiano_4k.dir\src\song.c.obj build\song.o
copy build\CMakeFiles\tinypiano_4k.dir\src\data.c.obj build\data.o
copy build\CMakeFiles\tinypiano_4k.dir\src\synth.c.obj build\synth.o
copy build\CMakeFiles\tinypiano_4k.dir\src\weights.c.obj build\weights.o

echo Stripping debug symbols...
strip --strip-debug build\main.o
strip --strip-debug build\model.o
strip --strip-debug build\song.o
strip --strip-debug build\data.o
strip --strip-debug build\synth.o
strip --strip-debug build\weights.o

echo Running Crinkler with working configuration...
crinkler /OUT:bin/tinypiano_4k.exe /TINYHEADER /TINYIMPORT /SUBSYSTEM:CONSOLE /COMPMODE:SLOW /HASHSIZE:500 /HASHTRIES:100 /ORDERTRIES:10000 build/main.o build/model.o build/song.o build/data.o build/synth.o build/weights.o "%WINKIT_LIB%\kernel32.lib"

echo ============================================================
echo Crinkler compression completed!
echo ============================================================
