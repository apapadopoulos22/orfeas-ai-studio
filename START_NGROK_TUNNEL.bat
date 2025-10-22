@echo off
REM ============================================
REM ORFEAS AI - Start ngrok Tunnel for Backend
REM ============================================
REM This batch file starts an ngrok tunnel to expose
REM your local backend to the internet via HTTPS

cls
echo.
echo ============================================
echo   ORFEAS AI - ngrok Tunnel Starter
echo ============================================
echo.

REM Check if ngrok is installed
where ngrok >nul 2>&1
if errorlevel 1 (
    echo ERROR: ngrok not found in PATH
    echo.
    echo Please install ngrok first:
    echo   1. Download from: https://ngrok.com/download
    echo   2. Extract to: C:\ngrok\
    echo   3. Add C:\ngrok\ to your Windows PATH
    echo   4. Restart this terminal
    echo.
    pause
    exit /b 1
)

echo [INFO] ngrok found
ngrok --version
echo.

echo [INFO] Starting ngrok tunnel to localhost:5000
echo [INFO] Your backend will be available at: https://xxxx-xxxx-xxxx.ngrok.io
echo.
echo [IMPORTANT] Copy the forwarding URL and update netlify.toml!
echo [IMPORTANT] Keep this window open while using Netlify deployment
echo.
echo Press Ctrl+C to stop the tunnel
echo.

ngrok http 5000

echo.
echo Tunnel stopped.
pause
