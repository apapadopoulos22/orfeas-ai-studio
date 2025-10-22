@echo off
echo ============================================================
echo   ORFEAS AI 2D-3D Studio - Frontend Server
echo   Starting simple HTTP server on port 8000
echo ============================================================
echo.
echo Access ORFEAS Studio at:
echo   http://localhost:8000/orfeas-studio.html
echo.
echo Press CTRL+C to stop the server
echo ============================================================
echo.

cd /d "%~dp0"
python -m http.server 8000
