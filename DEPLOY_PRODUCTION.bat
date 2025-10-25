@echo off
REM Production Deployment Script for ORFEAS AI Studio
REM Version: 1.0
REM Date: October 25, 2025

setlocal enabledelayedexpansion

cls
echo.
echo ============================================================================
echo  ORFEAS AI 2D3D Studio - Production Deployment Script
echo ============================================================================
echo.

REM Check if running as admin
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: This script must be run as Administrator
    echo Please right-click and select "Run as Administrator"
    pause
    exit /b 1
)

REM Set paths
set SCRIPT_DIR=%~dp0
set BACKEND_DIR=%SCRIPT_DIR%backend
set LOG_DIR=%SCRIPT_DIR%logs
set DEPLOY_LOG=%LOG_DIR%\deployment_%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%.log

REM Create log directory
if not exist %LOG_DIR% mkdir %LOG_DIR%

echo [%date% %time%] Starting ORFEAS Production Deployment >> %DEPLOY_LOG%

REM Step 1: Stop existing instances
echo.
echo [Step 1/5] Stopping existing Python instances...
echo [%date% %time%] Stopping existing Python instances >> %DEPLOY_LOG%

taskkill /F /IM python.exe >nul 2>&1
timeout /t 3 /nobreak >nul

echo Done.

REM Step 2: Verify backend exists
echo.
echo [Step 2/5] Verifying backend files...
echo [%date% %time%] Verifying backend files >> %DEPLOY_LOG%

if not exist %BACKEND_DIR%\main.py (
    echo ERROR: backend\main.py not found!
    echo [%date% %time%] ERROR: backend\main.py not found >> %DEPLOY_LOG%
    pause
    exit /b 1
)

echo Backend found.

REM Step 3: Check port availability
echo.
echo [Step 3/5] Checking port 5000 availability...
echo [%date% %time%] Checking port 5000 availability >> %DEPLOY_LOG%

netstat -ano | findstr :5000 >nul
if !errorLevel! equ 0 (
    echo WARNING: Port 5000 is in use. Killing process...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5000') do (
        taskkill /F /PID %%a >nul 2>&1
    )
    timeout /t 2 /nobreak >nul
)

echo Port 5000 is free.

REM Step 4: Start backend
echo.
echo [Step 4/5] Starting backend server...
echo [%date% %time%] Starting backend server >> %DEPLOY_LOG%

cd /d %BACKEND_DIR%
start "ORFEAS Production Backend" python main.py >> %DEPLOY_LOG% 2>&1

timeout /t 5 /nobreak >nul

REM Step 5: Verify deployment
echo.
echo [Step 5/5] Verifying deployment...
echo [%date% %time%] Verifying deployment >> %DEPLOY_LOG%

setlocal enabledelayedexpansion
set RETRY_COUNT=0
set MAX_RETRIES=10

:HEALTH_CHECK_RETRY
if !RETRY_COUNT! geq !MAX_RETRIES! (
    echo ERROR: Backend failed to start within timeout period
    echo [%date% %time%] ERROR: Backend health check timeout >> %DEPLOY_LOG%
    pause
    exit /b 1
)

powershell -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; try { $r = Invoke-WebRequest -Uri 'http://127.0.0.1:5000/api/health' -UseBasicParsing -TimeoutSec 3; if ($r.StatusCode -eq 200) { exit 0 } } catch { exit 1 }" >nul 2>&1

if !errorLevel! neq 0 (
    set /a RETRY_COUNT=!RETRY_COUNT!+1
    echo Waiting for backend... (!RETRY_COUNT!/!MAX_RETRIES!)
    timeout /t 2 /nobreak >nul
    goto HEALTH_CHECK_RETRY
)

echo Backend is healthy!
echo [%date% %time%] Backend health check passed >> %DEPLOY_LOG%

REM Display deployment info
echo.
echo ============================================================================
echo  Deployment Successful!
echo ============================================================================
echo.
echo Backend Status: RUNNING
echo Port: 5000
echo Access: http://127.0.0.1:5000
echo Logs: %BACKEND_DIR%\logs\backend_requests.log
echo Deployment Log: %DEPLOY_LOG%
echo.
echo Key Endpoints:
echo   - Health: http://127.0.0.1:5000/api/health
echo   - Portal: http://127.0.0.1:5000/
echo   - Metrics: http://127.0.0.1:5000/metrics
echo.
echo ============================================================================
echo.
echo [%date% %time%] Deployment successful >> %DEPLOY_LOG%

endlocal
pause
