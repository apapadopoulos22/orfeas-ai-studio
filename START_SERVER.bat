@echo off
REM Start ORFEAS AI Backend Server
REM This batch file starts the Flask backend server with proper environment setup

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

echo Starting backend server...
echo.
echo Server will run on:
echo   - Local:     http://127.0.0.1:5000
echo   - Network:   http://192.168.1.57:5000
echo   - WebSocket: ws://127.0.0.1:5000/socket.io
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start the server
python main.py

REM If server stops, show exit message
echo.
echo Server has stopped.
pause
