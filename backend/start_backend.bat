@echo off
REM ============================================================================
REM ORFEAS Backend Startup Script with Model Cache Configuration
REM ============================================================================
REM
REM This batch script:
REM  1. Configures HuggingFace cache paths (fixes mixed path separators)
REM  2. Creates cache directories if they don't exist
REM  3. Starts the ORFEAS backend server
REM
REM Usage: start_backend.bat
REM        (Just double-click or run from command prompt)
REM
REM ============================================================================

setlocal enabledelayedexpansion

REM Get the directory of this script
set SCRIPT_DIR=%~dp0
set PROJECT_ROOT=%SCRIPT_DIR%..

echo.
echo ============================================================================
echo [START] ORFEAS Backend with Model Cache Configuration
echo ============================================================================
echo.

REM Step 1: Configure model cache paths
echo [SETUP] Configuring model cache paths...

REM Create cache directories
set CACHE_DIR=%PROJECT_ROOT%\models\.cache\huggingface
set TRANSFORMERS_CACHE=%CACHE_DIR%\transformers
set DATASETS_CACHE=%CACHE_DIR%\datasets
set HY3DGEN_CACHE=%CACHE_DIR%\hy3dgen

if not exist "%CACHE_DIR%" (
    mkdir "%CACHE_DIR%"
    echo   OK Created: %CACHE_DIR%
) else (
    echo   OK Found: %CACHE_DIR%
)

if not exist "%TRANSFORMERS_CACHE%" (
    mkdir "%TRANSFORMERS_CACHE%"
    echo   OK Created: transformers/
)

if not exist "%DATASETS_CACHE%" (
    mkdir "%DATASETS_CACHE%"
    echo   OK Created: datasets/
)

if not exist "%HY3DGEN_CACHE%" (
    mkdir "%HY3DGEN_CACHE%"
    echo   OK Created: hy3dgen/
)

echo.

REM Step 2: Set environment variables (proper Windows paths with backslashes)
echo [CONFIG] Setting environment variables...
set HF_HOME=%CACHE_DIR%
set TRANSFORMERS_CACHE=%TRANSFORMERS_CACHE%
set HF_DATASETS_CACHE=%DATASETS_CACHE%
set HY3DGEN_CACHE=%HY3DGEN_CACHE%
set HOME=%PROJECT_ROOT%

echo   OK HF_HOME = %HF_HOME%
echo   OK TRANSFORMERS_CACHE = %TRANSFORMERS_CACHE%
echo   OK HY3DGEN_CACHE = %HY3DGEN_CACHE%

echo.

REM Step 3: Verify cache directories
echo [VERIFY] Checking cache directory structure...

if exist "%CACHE_DIR%" (
    echo   OK Cache root exists
) else (
    echo   ERROR Cache directory not found!
    pause
    exit /b 1
)

if exist "%TRANSFORMERS_CACHE%" (
    echo   OK transformers/ exists
)

if exist "%DATASETS_CACHE%" (
    echo   OK datasets/ exists
)

if exist "%HY3DGEN_CACHE%" (
    echo   OK hy3dgen/ exists
)

echo.

REM Step 4: Start backend
echo [START] Starting ORFEAS Backend Server...
echo   Backend directory: %SCRIPT_DIR%
echo   Model cache: %HF_HOME%
echo.

echo ============================================================================
echo Backend is starting. Press Ctrl+C to stop.
echo ============================================================================
echo.

REM Change to backend directory and start
cd /d "%SCRIPT_DIR%"

REM Run Python main.py
python main.py

REM If Python exits, show result
if errorlevel 1 (
    echo.
    echo ERROR Backend exited with error code: %ERRORLEVEL%
) else (
    echo.
    echo OK Backend stopped gracefully
)

echo.
pause
