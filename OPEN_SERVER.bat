@echo off
setlocal ENABLEEXTENSIONS
chcp 65001 >nul

REM ============================================================
REM  ORFEAS AI Studio - One-click Server Starter (Windows .bat)
REM  - Starts backend in a new console window
REM  - Opens Studio in default browser
REM ============================================================

set "ROOT=%~dp0"
set "BACKEND=%ROOT%backend"
set "PYTHON_CMD="

REM Prefer project venv if present
if exist "%ROOT%venv\Scripts\python.exe" (
  set "PYTHON_CMD=%ROOT%venv\Scripts\python.exe"
) else (
  REM Fallback to system Python
  where python >nul 2>&1 && set "PYTHON_CMD=python"
  if not defined PYTHON_CMD (
    where py >nul 2>&1 && set "PYTHON_CMD=py -3"
  )
)

if not defined PYTHON_CMD (
  echo [ERROR] Python 3.x not found. Please install Python 3.10+ or create a venv at %%ROOT%%venv.
  echo        Download: https://www.python.org/downloads/windows/
  pause
  exit /b 1
)

REM Force Powerful 3D mode on launch
set ORFEAS_MODE=powerful_3d

REM Start backend in a new window, pinned to backend folder
set "CMD_LINE=cd /d \"%BACKEND%\" && %PYTHON_CMD% main.py"
start "ORFEAS Backend" cmd /k "%CMD_LINE%"

REM Give the server a moment to boot, then open Studio
ping -n 3 127.0.0.1 >nul
start "" "http://127.0.0.1:5000/studio"

echo [OK] Launched ORFEAS backend and opened Studio.
echo You can close this window; the server runs in its own console.
exit /b 0
