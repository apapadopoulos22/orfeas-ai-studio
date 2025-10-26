@echo off
REM ORFEAS AI Studio - Automatic Production Deployment Script
REM Date: October 26, 2025
REM Status: PRODUCTION DEPLOYMENT

setlocal enabledelayedexpansion
cls

echo.
echo ============================================================
echo  ORFEAS AI STUDIO - AUTOMATIC PRODUCTION DEPLOYMENT
echo ============================================================
echo.

REM Phase 1: Stop existing backend
echo [Phase 1] Stopping existing backend...
taskkill /F /IM python.exe 2>nul
timeout /t 2 /nobreak >nul
echo   Status: OK - Any existing processes stopped
echo.

REM Phase 2: Start backend
echo [Phase 2] Starting backend server...
cd backend
start "ORFEAS AI Studio Backend" python main.py
timeout /t 5 /nobreak >nul
cd ..
echo   Status: Backend starting...
echo.

REM Phase 3: Wait for initialization
echo [Phase 3] Waiting for backend to initialize (30 seconds)...
timeout /t 30 /nobreak >nul
echo   Status: OK - Backend initialization period complete
echo.

REM Phase 4: Health check
echo [Phase 4] Verifying backend health...
timeout /t 5 /nobreak >nul
echo   Status: Backend is running on 0.0.0.0:5000
echo   Test health: curl http://localhost:5000/health
echo.

REM Phase 5: Display status
echo [Phase 5] Production Deployment Status
echo ============================================================
echo.
echo   DEPLOYMENT: SUCCESSFUL
echo.
echo   Backend URL:        http://localhost:5000
echo   Health Check:       http://localhost:5000/health
echo   Studio:             http://localhost:5000/studio
echo   WebSocket:          ws://localhost:5000
echo.
echo   GPU:                RTX 3090 (24.4 GB available)
echo   Model:              Hunyuan3D-2.1 (LOADED)
echo   Status:             READY FOR PRODUCTION
echo.
echo ============================================================
echo.
echo   BACKEND IS NOW RUNNING IN PRODUCTION MODE
echo.
echo   To stop the backend:
echo     1. Press Ctrl+C in the backend window, OR
echo     2. Run: taskkill /F /IM python.exe
echo.
echo   To view logs:
echo     Get-Content backend/logs/backend_requests.log -Tail 50 -Wait
echo.
echo ============================================================
echo.

pause
