@echo off
echo  HUNYUAN3D TEST API LAUNCHER
echo !
echo.

cd /d "C:\Users\johng\_AI_LOCAL\Hunyuan3D-2.1"
call "C:\Users\johng\_AI_LOCAL\Hunyuan3D-2.1\venv\Scripts\activate.bat"

echo Starting test API server...
python test_api.py

pause
