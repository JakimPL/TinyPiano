#!/bin/bash
# CMake build script for TinyPiano

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}TinyPiano CMake Build Script${NC}"
echo "================================"

# Parse command line arguments
BUILD_TYPE="Release"
CLEAN=false
TESTS=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -d|--debug)
            BUILD_TYPE="Debug"
            shift
            ;;
        -c|--clean)
            CLEAN=true
            shift
            ;;
        -t|--test)
            TESTS=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  -d, --debug    Build in Debug mode"
            echo "  -c, --clean    Clean build directory first"
            echo "  -t, --test     Run tests after building"
            echo "  -h, --help     Show this help"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

# Clean if requested
if [ "$CLEAN" = true ]; then
    echo -e "${YELLOW}Cleaning build directory...${NC}"
    rm -rf build/*
    rm -rf bin/*
fi

# Create build directory
mkdir -p build
cd build

# Configure CMake
echo -e "${YELLOW}Configuring CMake (${BUILD_TYPE} mode)...${NC}"
cmake -DCMAKE_BUILD_TYPE=$BUILD_TYPE ..

# Build
echo -e "${YELLOW}Building project...${NC}"
make -j$(nproc)

# Run tests if requested
if [ "$TESTS" = true ]; then
    echo -e "${YELLOW}Running tests...${NC}"
    make test
fi

echo -e "${GREEN}Build completed successfully!${NC}"
echo "Binaries are in: bin/"
echo "Libraries are in: build/lib/"

# Show binary sizes
echo -e "\n${YELLOW}Binary sizes:${NC}"
ls -lh ../bin/* 2>/dev/null | awk '{print $9 ": " $5}' || echo "No binaries found"
