@echo off
REM Simple HTTP Server Launcher - No PowerShell complexity
cd /d "%~dp0"
echo.
echo 
echo        THERION ORFEAS - HTTP SERVER LAUNCHER       
echo 
echo.
echo Starting HTTP server on port 8080...
echo.
echo URLs:
echo   Main App:       http://localhost:8080/orfeas-studio.html
echo   Phase 9 Tests:  http://localhost:8080/test-orfeas-phase9-optimizations.html
echo   Phase 10 Tests: http://localhost:8080/test-orfeas-phase10-optimizations.html
echo.
echo Opening browser...
timeout /t 2 /nobreak >nul
start http://localhost:8080/orfeas-studio.html
echo.
echo Server running! Press Ctrl+C to stop.
echo 
echo.
python -m http.server 8080
