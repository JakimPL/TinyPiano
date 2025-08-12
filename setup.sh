#!/bin/bash
# Setup script for TinyPiano development environment

set -e

echo "TinyPiano Development Setup"
echo "=========================="

# Check Python dependencies first
echo "Checking Python dependencies..."
python3 -c "import torch; print('✓ PyTorch available')" 2>/dev/null || echo "⚠ PyTorch not found. Install with: pip install torch"
python3 -c "import mido; print('✓ mido available')" 2>/dev/null || echo "⚠ mido not found. Install with: pip install mido"

# Install pre-commit
echo "Setting up pre-commit..."
if command -v pre-commit &> /dev/null; then
    echo "✓ pre-commit found"
else
    echo "Installing pre-commit..."
    pip install pre-commit
fi

# Install pre-commit hooks
echo "Installing pre-commit hooks..."
pre-commit install
echo "✓ Pre-commit hooks installed"

# Optional: Install additional Python tools for better development
echo "Installing additional Python development tools..."
pip install black isort flake8 2>/dev/null || echo "⚠ Some Python tools failed to install (optional)"

# Create initial build
echo "Performing initial build..."
./build.sh --clean --test

echo ""
echo "Setup complete! 🎹"
echo ""
echo "Development workflow:"
echo "  ./build.sh          - Build project"
echo "  ./build.sh --test   - Build and run tests"
echo "  ./build.sh --debug  - Debug build"
echo "  git commit          - Triggers pre-commit checks automatically"
echo "  pre-commit run      - Run hooks manually"
echo "  pre-commit run --all-files  - Run hooks on all files"
echo ""
echo "CMake commands (in build/ directory):"
echo "  make model          - Build core model"
echo "  make test           - Run all tests"
echo "  make size           - Show binary sizes"
