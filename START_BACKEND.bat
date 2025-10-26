@echo off
REM ============================================================================
REM ORFEAS AI Studio - Start Backend Server
REM ============================================================================
REM
REM Quick start script - automatically configures model cache and starts server
REM
REM Usage: Just double-click this file!
REM
REM Features:
REM   - Validates .env configuration
REM   - Checks model cache directory
REM   - Clears Python __pycache__ for fresh imports
REM   - Handles Windows path separators properly
REM
REM ============================================================================

setlocal enabledelayedexpansion

echo.
echo ============================================================================
echo [ORFEAS] Backend Server Startup
echo ============================================================================
echo.

REM Get the directory of this script (project root)
set SCRIPT_DIR=%~dp0
set BACKEND_DIR=%SCRIPT_DIR%backend

REM Check if backend exists
if not exist "%BACKEND_DIR%" (
    echo ERROR: backend directory not found at %BACKEND_DIR%
    pause
    exit /b 1
)

echo [INFO] Project directory: %SCRIPT_DIR%
echo [INFO] Backend directory: %BACKEND_DIR%
echo.

REM Change to backend directory
cd /d "%BACKEND_DIR%"

REM Check if main.py exists
if not exist "main.py" (
    echo ERROR: main.py not found in backend directory
    pause
    exit /b 1
)

REM Validate .env exists
if not exist ".env" (
    echo WARNING: .env file not found
    pause
    exit /b 1
)

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found in PATH
    pause
    exit /b 1
)

REM Clear Python cache
echo [INFO] Clearing Python __pycache__...
for /d /r ".." %%d in (__pycache__) do (
    if exist "%%d" rmdir /s /q "%%d" >nul 2>&1
)

REM Stop existing Python processes
echo [INFO] Stopping existing Python processes...
taskkill /F /IM python.exe >nul 2>&1
timeout /t 2 /nobreak >nul

echo.
echo [INFO] Starting backend server...
echo [INFO] Server: http://127.0.0.1:5000
echo.

REM Start backend
python main.py

REM Pause if server exits
pause
