@echo off
title ORFEAS AI Studio - Auto Startup
color 0A

echo.
echo 
echo                                                                               
echo                      ORFEAS AI STUDIO - AUTO STARTUP                       
echo                                                                               
echo                   2D to 3D Generation with Preview Fix                       
echo                                                                               
echo 
echo.

REM Check Python installation
echo [1/5] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo  ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python 3.8+ from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

python --version
echo  Python found
echo.

REM Check if backend directory exists
echo [2/5] Checking backend directory...
if not exist "backend\main.py" (
    echo  ERROR: Backend main.py not found
    echo Current directory: %CD%
    echo Expected: %CD%\backend\main.py
    pause
    exit /b 1
)
echo  Backend directory found
echo.

REM Check if frontend HTML exists
echo [3/5] Checking frontend...
if not exist "orfeas-studio.html" (
    echo   WARNING: orfeas-studio.html not found in root directory
    echo Frontend will not be opened automatically
) else (
    echo  Frontend HTML found
)
echo.

REM Start backend server in a new window
echo [4/5] Starting backend server...
echo.
echo  Opening backend server in new window...
start "ORFEAS Backend Server" cmd /k "cd /d "%~dp0backend" && python main.py"

REM Wait for server to start
echo ⏳ Waiting for backend to initialize (5 seconds)...
timeout /t 5 /nobreak >nul

REM Check if server is running
echo.
echo [5/5] Verifying server status...
curl -s http://127.0.0.1:5002/api/health >nul 2>&1
if errorlevel 1 (
    echo   WARNING: Backend server may still be starting...
    echo Check the backend window for any errors
) else (
    echo  Backend server is running on http://127.0.0.1:5002
)
echo.

echo 
echo                           STARTUP COMPLETE!                                
echo 
echo.
echo  Backend Server:  http://127.0.0.1:5002
echo  API Health:      http://127.0.0.1:5002/api/health
echo   Preview Endpoint: http://127.0.0.1:5002/api/preview/<filename>
echo.
echo  Frontend Options:
echo    • Open orfeas-studio.html in your browser
echo    • Or run: python -m http.server 8000
echo    • Then visit: http://localhost:8000/orfeas-studio.html
echo.

REM Ask user if they want to open the frontend
if exist "orfeas-studio.html" (
    echo.
    set /p OPEN_FRONTEND="Open frontend in browser? (Y/N): "
    if /i "%OPEN_FRONTEND%"=="Y" (
        echo.
        echo  Opening frontend in default browser...
        start "" "%~dp0orfeas-studio.html"
        echo  Frontend opened
    )
)

echo.
echo 
echo                              QUICK COMMANDS                                 
echo 
echo.
echo   • Test Backend:       curl http://127.0.0.1:5002/api/health
echo   • Run Tests:          cd backend ^&^& python test_preview_endpoints.py
echo   • View Docs:          Open PREVIEW_FIX_COMPLETE.md
echo   • Stop Backend:       Close the backend server window
echo.
echo 
echo                            SYSTEM READY FOR USE                             
echo 
echo.
echo Press any key to exit this window (backend will continue running)...
pause >nul
