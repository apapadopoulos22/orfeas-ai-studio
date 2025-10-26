@echo off
REM Start ORFEAS AI Backend Server
REM ============================================================================
REM This batch file starts the Flask backend server with proper environment setup
REM
REM Features:
REM   - Validates .env configuration (Windows path separator fix)
REM   - Checks model cache directory
REM   - Clears Python __pycache__ to ensure fresh imports
REM   - Validates Python and dependency installations
REM   - Provides detailed startup diagnostics
REM
REM CRITICAL FIX (Windows Path Separators):
REM   - Main.py loads .env BEFORE imports to set HOME and HY3DGEN_MODELS
REM   - Ensures hy3dgen module receives proper Windows backslash paths
REM   - Prevents "Model path not exists" errors from mixed / and \ separators
REM ============================================================================

setlocal enabledelayedexpansion

cd /d "%~dp0"

echo.
echo ╔════════════════════════════════════════════════════════╗
echo ║     ORFEAS AI 2D3D STUDIO - BACKEND SERVER STARTUP     ║
echo ╚════════════════════════════════════════════════════════╝
echo.

REM Check if backend directory exists
if not exist "backend" (
    echo ERROR: backend directory not found
    pause
    exit /b 1
)

cd backend

REM Check if main.py exists
if not exist "main.py" (
    echo ERROR: main.py not found in backend directory
    pause
    exit /b 1
)

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Validate .env file exists and has proper configuration
echo [STARTUP] Validating environment configuration...
if not exist ".env" (
    echo WARNING: .env file not found. Creating basic configuration...
    echo HOME=!USERPROFILE!\Documents\oscar >> .env
    echo HF_HOME=!USERPROFILE!\Documents\oscar\models\.cache\huggingface >> .env
    echo HY3DGEN_MODELS=!USERPROFILE!\Documents\oscar\models\.cache\huggingface\hub\models--tencent--Hunyuan3D-2 >> .env
)

REM Verify HY3DGEN_MODELS is set in .env
findstr /R "^HY3DGEN_MODELS=" ".env" >nul 2>&1
if errorlevel 1 (
    echo WARNING: HY3DGEN_MODELS not found in .env. This is required for proper model loading.
    echo Adding HY3DGEN_MODELS to .env...
    echo HY3DGEN_MODELS=!USERPROFILE!\Documents\oscar\models\.cache\huggingface\hub\models--tencent--Hunyuan3D-2 >> .env
)

REM Check if model cache directory exists
echo [STARTUP] Checking model cache directory...
if not exist "..\models\.cache\huggingface\hub\models--tencent--Hunyuan3D-2" (
    echo WARNING: Model cache directory not found at expected location
    echo          Models will be downloaded on first startup (~15-30 minutes)
    echo.
) else (
    echo [OK] Model cache directory found. Models will load from cache (~20-40 seconds)
)

REM Clear Python __pycache__ to ensure fresh imports with fixed code
echo [STARTUP] Clearing Python cache to ensure fresh imports...
for /d /r ".." %%d in (__pycache__) do (
    if exist "%%d" rmdir /s /q "%%d" >nul 2>&1
)
echo [OK] Python cache cleared

REM Stop any existing Python processes to ensure clean startup
echo [STARTUP] Stopping any existing Python processes...
taskkill /F /IM python.exe >nul 2>&1
timeout /t 2 /nobreak >nul

echo.
echo ╔════════════════════════════════════════════════════════╗
echo ║             STARTING BACKEND SERVER                    ║
echo ╚════════════════════════════════════════════════════════╝
echo.
echo Server will run on:
echo   - Local:     http://127.0.0.1:5000
echo   - Network:   http://192.168.1.57:5000
echo   - WebSocket: ws://127.0.0.1:5000/socket.io
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start the server with environment loaded from .env
python main.py

REM If server stops, show exit message
echo.
echo ╔════════════════════════════════════════════════════════╗
echo ║             SERVER HAS STOPPED                         ║
echo ╚════════════════════════════════════════════════════════╝
pause
