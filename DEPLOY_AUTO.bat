@echo off
REM ════════════════════════════════════════════════════════════════
REM  ORFEAS AI - Automatic Netlify Deployment (No Prompts)
REM ════════════════════════════════════════════════════════════════

setlocal enabledelayedexpansion

cls
color 0A

echo.
echo ════════════════════════════════════════════════════════════════
echo           ORFEAS AI - AUTOMATIC NETLIFY DEPLOYMENT
echo              (Running in automatic mode - no prompts)
echo ════════════════════════════════════════════════════════════════
echo.

REM Step 1: Check prerequisites
echo [STEP 1/6] Checking prerequisites...
python --version >nul 2>&1 || goto ERROR_PYTHON
netlify --version >nul 2>&1 || goto ERROR_NETLIFY
ngrok --version >nul 2>&1 || goto ERROR_NGROK
echo    ✅ All prerequisites found
echo.

REM Step 2: Start backend
echo [STEP 2/6] Starting backend service...
cd /d c:\Users\johng\Documents\oscar\backend
start "ORFEAS Backend" cmd /k "python -u main.py"
echo    ✅ Backend started (check terminal window)
timeout /t 3 /nobreak
echo.

REM Step 3: Start ngrok
echo [STEP 3/6] Starting ngrok tunnel...
start "ORFEAS ngrok" cmd /k "c:\Users\johng\Documents\oscar\START_NGROK_TUNNEL.bat"
echo    ✅ ngrok tunnel started (check terminal window)
timeout /t 3 /nobreak
echo.

REM Step 4: Get ngrok URL
echo [STEP 4/6] Retrieving ngrok URL...
timeout /t 3 /nobreak
for /f %%i in ('powershell -Command "try { $r = Invoke-WebRequest -Uri http://localhost:4040/api/tunnels -UseBasicParsing; $j = ConvertFrom-Json $r.Content; Write-Host $j.tunnels[0].public_url } catch { Write-Host \\\"ERROR\\\" }"') do set NGROK_URL=%%i

if "!NGROK_URL!"=="ERROR" (
    echo ❌ Could not retrieve ngrok URL
    echo Please copy ngrok URL manually from ngrok terminal window
    set /p NGROK_URL="Enter ngrok URL (https://xxxx-xxxx-xxxx.ngrok.io): "
)

if "!NGROK_URL!"=="" (
    echo ❌ ngrok URL is empty
    goto ERROR_NGROK_URL
)

echo    ✅ ngrok URL: !NGROK_URL!
echo.

REM Step 5: Update configuration
echo [STEP 5/6] Updating Netlify configuration...
cd /d c:\Users\johng\Documents\oscar

REM Update netlify.toml
powershell -Command "(Get-Content 'netlify.toml') -replace 'YOUR_NGROK_URL_HERE', '!NGROK_URL!' | Set-Content 'netlify.toml'"

REM Update frontend
powershell -Command "(Get-Content 'synexa-style-studio.html') -replace 'const API_BASE = .*', 'const API_BASE = \"!NGROK_URL!\";' | Set-Content 'synexa-style-studio.html'"

echo    ✅ Configuration updated
echo.

REM Step 6: Deploy to Netlify
echo [STEP 6/6] Deploying to Netlify...

if not exist ".git" (
    git init
    git remote add origin "https://github.com/orfeas-ai/orfeas-ai-frontend.git" 2>nul || echo (Git remote optional)
)

git config user.email "deploy@orfeas.local" 2>nul
git config user.name "ORFEAS Deploy" 2>nul
git add . 2>nul
git commit -m "ORFEAS AI - Auto deployment to Netlify" 2>nul

netlify deploy --prod

echo.
echo ════════════════════════════════════════════════════════════════
echo                  ✅ DEPLOYMENT COMPLETE!
echo ════════════════════════════════════════════════════════════════
echo.
echo Your ORFEAS AI Studio is now live!
echo.
echo Next steps:
echo   1. Copy your Netlify URL from the output above
echo   2. Open it in browser
echo   3. Check console (F12) for [CONFIG] API_BASE message
echo   4. Upload an image to test 3D generation
echo   5. Keep backend and ngrok terminals open
echo.
pause
goto END

:ERROR_PYTHON
echo ❌ ERROR: Python not found. Install Python 3.10+
pause
exit /b 1

:ERROR_NETLIFY
echo ❌ ERROR: netlify-cli not found
echo Run: npm install -g netlify-cli
pause
exit /b 1

:ERROR_NGROK
echo ❌ ERROR: ngrok not found
echo Download from: https://ngrok.com/download
pause
exit /b 1

:ERROR_NGROK_URL
echo ❌ ERROR: Could not get ngrok URL
pause
exit /b 1

:END
echo Done!
