@echo off
REM ============================================
REM ORFEAS AI 2D3D Studio - Server Launcher
REM ============================================
REM This batch file starts the Flask backend server
REM with proper environment configuration

setlocal enabledelayedexpansion

REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0
set BACKEND_DIR=%SCRIPT_DIR%backend

REM Color codes for output
for /F %%a in ('copy /Z "%~f0" nul') do set "BS=%%a"

REM Clear screen
cls

REM Display header
echo.
echo ============================================
echo   ORFEAS AI Studio - Server Launcher
echo ============================================
echo.

REM Check if backend directory exists
if not exist "%BACKEND_DIR%" (
    echo %BS%[ERROR] Backend directory not found:
    echo %BS%        %BACKEND_DIR%
    echo.
    pause
    exit /b 1
)

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo %BS%[ERROR] Python is not installed or not in PATH
    echo.
    echo Please install Python 3.10+ from:
    echo   https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

REM Display Python version
echo [INFO] Python version:
python --version
echo.

REM Check if main.py exists
if not exist "%BACKEND_DIR%\main.py" (
    echo %BS%[ERROR] main.py not found in backend directory
    echo %BS%        %BACKEND_DIR%\main.py
    echo.
    pause
    exit /b 1
)

REM Check if .env exists, warn if missing
if not exist "%SCRIPT_DIR%.env" (
    echo %BS%[WARN] .env file not found in project root
    echo %BS%       Some features may not work properly
    echo.
)

REM Display server info
echo [INFO] Starting ORFEAS Backend Server
echo        Location: %BACKEND_DIR%
echo.

REM Change to backend directory
cd /d "%BACKEND_DIR%"

if errorlevel 1 (
    echo %BS%[ERROR] Failed to change directory to %BACKEND_DIR%
    echo.
    pause
    exit /b 1
)

REM Set production environment variables
set FLASK_ENV=production
set DEBUG=false
set DEVICE=cuda
set XFORMERS_DISABLED=1
set GPU_MEMORY_LIMIT=0.8
set MAX_CONCURRENT_JOBS=3
set LOCAL_LLM_ENABLED=false
set ENABLE_MONITORING=true
set LOG_LEVEL=INFO

echo [INFO] Environment Configuration:
echo        FLASK_ENV: !FLASK_ENV!
echo        DEBUG: !DEBUG!
echo        GPU Memory Limit: !GPU_MEMORY_LIMIT!
echo        Max Concurrent Jobs: !MAX_CONCURRENT_JOBS!
echo.

REM Display startup information
echo ============================================
echo   ORFEAS AI Studio - PRODUCTION MODE
echo ============================================
echo.
echo   Backend Server: http://127.0.0.1:5000
echo   Frontend Studio: http://127.0.0.1:5000/studio
echo   Health Check: http://127.0.0.1:5000/health
echo   API Base: https://api.orfeas.ai (production)
echo.
echo   GPU: NVIDIA RTX 3090 (24GB VRAM)
echo   Mode: Full AI 3D Generation
echo.
echo   Press Ctrl+C to stop the server
echo ============================================
echo.

REM Start the server
python main.py

REM If we get here, the server stopped
echo.
echo ============================================
echo   Server has stopped
echo ============================================
echo.
pause

endlocal
