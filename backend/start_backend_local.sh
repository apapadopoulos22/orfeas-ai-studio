#!/bin/bash
# Local Backend Startup Script for ORFEAS AI Studio
# Run from backend directory: bash start_backend_local.sh

set -e  # Exit on error

echo "================================================"
echo "ORFEAS AI - Local Backend Startup"
echo "================================================"
echo ""

# Check Python version
echo "[1/4] Checking Python version..."
python_version=$(python --version 2>&1 | awk '{print $2}')
echo "✓ Python $python_version"

# Install dependencies
echo "[2/4] Installing dependencies..."
python -m pip install --upgrade pip wheel setuptools > /dev/null 2>&1
pip install -r requirements.txt > /dev/null 2>&1
echo "✓ Dependencies installed"

# Set environment variables
echo "[3/4] Configuring environment..."
export DEVICE=${DEVICE:-cpu}
export FLASK_ENV=${FLASK_ENV:-development}
export FLASK_DEBUG=${FLASK_DEBUG:-1}
export LOCAL_LLM_ENABLED=${LOCAL_LLM_ENABLED:-false}
export REDIS_CACHE_ENABLED=${REDIS_CACHE_ENABLED:-false}
export ENABLE_MONITORING=${ENABLE_MONITORING:-false}
export PORT=${PORT:-5000}

echo "  - DEVICE: $DEVICE"
echo "  - FLASK_ENV: $FLASK_ENV"
echo "  - PORT: $PORT"
echo "✓ Environment configured"

# Start backend
echo "[4/4] Starting backend server..."
echo ""
echo "Backend starting on http://127.0.0.1:$PORT"
echo "Press Ctrl+C to stop"
echo "================================================"
echo ""

python main.py
