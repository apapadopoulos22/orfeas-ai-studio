@echo off
echo THERION AI 2D STUDIO - Hunyuan3D 2.1 Launcher
echo DEUS VULT - MAXIMUM EFFORT!
echo.

cd /d "C:\Users\johng\THERION_AI_LOCAL\Hunyuan3D-2.1"

echo Activating virtual environment...
call "C:\Users\johng\THERION_AI_LOCAL\Hunyuan3D-2.1\venv\Scripts\activate.bat"

echo Starting API server...
python enhanced_api_server.py

pause
