@echo off
REM ============================================================================
REM ORFEAS Model Cache Setup Script
REM ============================================================================
REM
REM This script fixes HuggingFace cache paths for Windows compatibility
REM Prevents: "Model path not exists, try to download from huggingface" errors
REM
REM Usage: setup_models.bat
REM ============================================================================

echo.
echo ============================================================================
echo [SETUP] ORFEAS Model Cache Configuration
echo ============================================================================
echo.

cd /d "%~dp0" || exit /b 1

REM Run Python setup script
python setup_model_cache.py

if errorlevel 1 (
    echo.
    echo [ERROR] Setup failed!
    exit /b 1
)

echo.
echo [SUCCESS] Model cache setup complete!
echo.
echo Next: Run "python main.py" to start the server
echo.

pause
