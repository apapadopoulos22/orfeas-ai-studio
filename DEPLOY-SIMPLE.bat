@echo off
REM Simplified ORFEAS AI Automatic Netlify Deployment
REM No complex features, just straightforward steps

setlocal enabledelayedexpansion

cls
color 0A

echo.
echo ========================================
echo   ORFEAS AI - Automatic Deployment
echo ========================================
echo.

REM Check prerequisites
echo Checking prerequisites...
python --version >nul 2>&1 || (echo ERROR: Python not found && exit /b 1)
node --version >nul 2>&1 || (echo ERROR: Node.js not found && exit /b 1)
echo All prerequisites OK
echo.

REM Start backend
echo Starting backend...
cd /d c:\Users\johng\Documents\oscar\backend
start "Backend" cmd /k "python -u main.py"
timeout /t 3 /nobreak
echo.

REM Start ngrok
echo Starting ngrok tunnel...
cd /d c:\Users\johng\Documents\oscar
start "ngrok" cmd /k "START_NGROK_TUNNEL.bat"
timeout /t 5 /nobreak
echo.

REM Get ngrok URL
echo Retrieving ngrok URL...
for /f %%i in ('powershell -Command "try { $r = Invoke-WebRequest -Uri http://localhost:4040/api/tunnels -UseBasicParsing; $j = ConvertFrom-Json $r.Content; Write-Host $j.tunnels[0].public_url } catch { Write-Host \\\"ERROR\\\" }"') do set NGROK_URL=%%i

if "!NGROK_URL!"=="" set NGROK_URL=ERROR
if "!NGROK_URL!"=="ERROR" (
    echo Could not get ngrok URL automatically
    set /p NGROK_URL="Enter ngrok URL: "
)

echo ngrok URL: !NGROK_URL!
echo.

REM Update configuration
echo Updating configuration...
powershell -Command "(Get-Content 'netlify.toml') -replace 'YOUR_NGROK_URL_HERE', '!NGROK_URL!' | Set-Content 'netlify.toml'"
powershell -Command "(Get-Content 'synexa-style-studio.html') -replace 'const API_BASE = .*', 'const API_BASE = \\\"!NGROK_URL!\\\";' | Set-Content 'synexa-style-studio.html'"
echo Configuration updated
echo.

REM Deploy
echo Deploying to Netlify...
git init >nul 2>&1
git config user.email "deploy@orfeas.local" >nul 2>&1
git config user.name "ORFEAS Deploy" >nul 2>&1
git add . >nul 2>&1
git commit -m "ORFEAS Auto Deployment" >nul 2>&1
netlify deploy --prod

echo.
echo ========================================
echo Deployment complete!
echo ========================================
echo.
echo Your app is live at: https://your-app.netlify.app
echo Keep backend and ngrok terminals open!
echo.
pause
