@echo off
echo THERION HUNYUAN3D TEST API LAUNCHER
echo DEUS VULT!
echo.

cd /d "C:\Users\johng\THERION_AI_LOCAL\Hunyuan3D-2.1"
call "C:\Users\johng\THERION_AI_LOCAL\Hunyuan3D-2.1\venv\Scripts\activate.bat"

echo Starting test API server...
python test_api.py

pause
