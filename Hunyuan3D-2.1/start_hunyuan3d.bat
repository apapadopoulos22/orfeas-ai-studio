@echo off
echo  AI 2D STUDIO - Hunyuan3D 2.1 Launcher
echo  - MAXIMUM EFFORT!
echo.

cd /d "C:\Users\johng\_AI_LOCAL\Hunyuan3D-2.1"

echo Activating virtual environment...
call "C:\Users\johng\_AI_LOCAL\Hunyuan3D-2.1\venv\Scripts\activate.bat"

echo Starting API server...
python enhanced_api_server.py

pause
