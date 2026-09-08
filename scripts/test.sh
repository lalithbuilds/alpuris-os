#!/usr/bin/env bash
set -euo pipefail

echo "⚡ [Test Suite] Running 28-Suite Production Regression Tests..."

if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

python3 -m pytest tests/test_production_suite.py -v
echo "✓ All production test suites passed!"
