#!/usr/bin/env bash
set -euo pipefail

echo "⚡ [Setup] Initializing Bengaluru Living Agent Metropolis OS..."

# Python version check
PYTHON_BIN="python3"
if ! command -v "$PYTHON_BIN" &> /dev/null; then
    echo "✗ Python 3 is required but not found in PATH."
    exit 1
fi

echo "✓ Python detected: $($PYTHON_BIN --version)"

# Create virtual environment if absent
if [ ! -d ".venv" ]; then
    echo "⚡ Creating Python virtual environment in .venv..."
    "$PYTHON_BIN" -m venv .venv
fi

# Activate virtualenv
source .venv/bin/activate
pip install --upgrade pip

# Install the package and the same dev tools CI uses.
echo "⚡ Installing the package and development dependencies..."
pip install -e ".[dev]"

# Copy .env.example if .env does not exist
if [ ! -f ".env" ]; then
    echo "⚡ Initializing default .env from .env.example..."
    cp .env.example .env
fi

echo "✓ Setup complete! Run ./scripts/run.sh to start the simulator."
