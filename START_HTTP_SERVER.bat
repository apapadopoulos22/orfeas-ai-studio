@echo off
REM 
REM   THERION PROTOCOL - ORFEAS LOCAL HTTP SERVER (BATCH)                    
REM  PWA Testing and Development Server - Windows Batch Launcher                 
REM 

echo.
echo 
echo            THERION ORFEAS - LOCAL HTTP SERVER LAUNCHER                
echo 
echo.

REM Server configuration
set PORT=8080
set HOST=localhost
set WORKSPACE=%~dp0

echo  Server Configuration:
echo   Port: %PORT%
echo   Host: %HOST%
echo   Workspace: %WORKSPACE%
echo.

REM Check if Python is available
echo  Checking for Python...
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo  ERROR: Python not found in PATH
    echo.
    echo Please install Python 3.7+ from https://www.python.org/
    echo.
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo  Python found: %PYTHON_VERSION%
echo.

echo 
echo                     STARTING HTTP SERVER                           
echo 
echo.

echo  Server URLs:
echo   Main Application:  http://%HOST%:%PORT%/orfeas-studio.html
echo   Test Suites:
echo     Phase 9 Tests:   http://%HOST%:%PORT%/test-orfeas-phase9-optimizations.html
echo     Phase 10 Tests:  http://%HOST%:%PORT%/test-orfeas-phase10-optimizations.html
echo.

echo  PWA Features Available:
echo    Service Worker Registration
echo    Install Prompt (beforeinstallprompt)
echo    Offline Caching
echo    Background Sync
echo    Push Notifications
echo.

echo  Quick Actions:
echo   Press Ctrl+C to stop the server
echo   Browser will auto-open in 3 seconds...
echo.

echo 
echo                      SERVER STARTING NOW...                            
echo 
echo.

REM Open browser after short delay
timeout /t 3 /nobreak >nul
start http://%HOST%:%PORT%/orfeas-studio.html

echo  Browser opened at: http://%HOST%:%PORT%/orfeas-studio.html
echo.
echo 
echo                        SERVER LOGS BELOW
echo 
echo.

REM Start Python HTTP server (this will block until Ctrl+C)
cd /d "%WORKSPACE%"
python -m http.server %PORT%

echo.
echo 
echo                      SERVER STOPPED                                    
echo 
echo.
pause
