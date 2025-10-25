@echo off
REM Start ngrok tunnel for ORFEAS AI Backend
REM This batch file starts ngrok to expose the local Flask server to the internet

setlocal enabledelayedexpansion

echo.
echo ╔════════════════════════════════════════════════════════╗
echo ║           NGROK TUNNEL STARTUP - ORFEAS AI             ║
echo ╚════════════════════════════════════════════════════════╝
echo.

REM Check if ngrok is installed
ngrok version >nul 2>&1
if errorlevel 1 (
    echo ERROR: ngrok is not installed or not in PATH
    echo.
    echo To install ngrok:
    echo   1. Download from https://ngrok.com/download
    echo   2. Extract to C:\Program Files\ngrok or add to PATH
    echo   3. Run: ngrok config add-authtoken YOUR_AUTH_TOKEN
    echo.
    pause
    exit /b 1
)

echo ✓ ngrok found
echo.

REM Check if backend server is running
echo Checking if backend server is running on localhost:5000...
netstat -ano | find ":5000" >nul 2>&1
if errorlevel 1 (
    echo WARNING: Port 5000 does not appear to be in use
    echo.
    echo Make sure the Flask server is running:
    echo   - Run START_SERVER.bat first, or
    echo   - Run "python main.py" in backend directory
    echo.
    timeout /t 3
) else (
    echo ✓ Backend server detected on port 5000
    echo.
)

echo Starting ngrok tunnel...
echo.
echo Configuration:
echo   - Local endpoint:  http://127.0.0.1:5000
echo   - Tunnel protocol: HTTP
echo   - Region:          auto
echo.
echo Once started, the ngrok URL will be displayed above.
echo Share the ngrok URL to access the server from anywhere.
echo.
echo Press Ctrl+C to stop ngrok
echo.

REM Start ngrok with HTTP tunnel on port 5000
ngrok http 5000

REM If ngrok stops, show exit message
echo.
echo ngrok tunnel has stopped.
pause
