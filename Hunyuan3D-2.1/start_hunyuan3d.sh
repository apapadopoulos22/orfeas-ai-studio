#!/bin/bash
echo " AI 2D STUDIO - Hunyuan3D 2.1 Launcher"
echo " - MAXIMUM EFFORT!"
echo ""

cd "C:\Users\johng\_AI_LOCAL\Hunyuan3D-2.1"

echo "Activating virtual environment..."
source "C:\Users\johng\_AI_LOCAL\Hunyuan3D-2.1\venv/bin/activate"

echo "Starting API server..."
python enhanced_api_server.py
