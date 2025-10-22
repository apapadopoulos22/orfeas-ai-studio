@echo off
REM ════════════════════════════════════════════════════════════════
REM  ORFEAS AI - Complete Netlify Deployment Orchestrator
REM ════════════════════════════════════════════════════════════════
REM  This script guides you through the complete deployment process:
REM  1. Start backend (Flask)
REM  2. Start ngrok tunnel
REM  3. Deploy to Netlify
REM  4. Verify connection

setlocal enabledelayedexpansion

cls
color 0E

echo.
echo ════════════════════════════════════════════════════════════════
echo                ORFEAS AI - Netlify Deployment
echo                   Complete Setup Guide
echo ════════════════════════════════════════════════════════════════
echo.

REM Step 1: Check prerequisites
echo [STEP 1/4] Checking prerequisites...
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3.10+
    pause
    exit /b 1
)
echo   ✅ Python found
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo      Version: !PYTHON_VERSION!

REM Check Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js not found. Please install Node.js
    pause
    exit /b 1
)
echo   ✅ Node.js found
for /f %%i in ('node --version') do set NODE_VERSION=%%i
echo      Version: !NODE_VERSION!

REM Check netlify-cli
netlify --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  netlify-cli not found. Installing...
    call npm install -g netlify-cli
)
echo   ✅ netlify-cli ready

REM Check ngrok
ngrok --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  ngrok not found. You'll need to install it for tunneling.
    echo    Download from: https://ngrok.com/download
    echo.
    set NGROK_MISSING=1
) else (
    echo   ✅ ngrok ready
    for /f %%i in ('ngrok --version') do set NGROK_VERSION=%%i
    echo      Version: !NGROK_VERSION!
)

echo.

REM Step 2: Start backend
echo [STEP 2/4] Starting ORFEAS Backend...
echo.
echo This will start the Flask backend on http://127.0.0.1:5000
echo Press Enter to continue in a new terminal window...
pause

cd /d "c:\Users\johng\Documents\oscar\backend"

REM Create a new terminal for backend (non-blocking)
start "ORFEAS Backend" cmd /k "python -u main.py"
echo   ✅ Backend started (check terminal window)
echo.

echo Please wait for backend to initialize...
timeout /t 5 /nobreak

REM Test backend health
echo Testing backend connection...
for /f %%i in ('powershell -Command "try { $r = Invoke-WebRequest -Uri http://127.0.0.1:5000/health -UseBasicParsing -TimeoutSec 5; if ($r.StatusCode -eq 200) { Write-Host 'OK' } else { Write-Host 'FAIL' } } catch { Write-Host 'FAIL' }"') do set BACKEND_STATUS=%%i

if "!BACKEND_STATUS!"=="OK" (
    echo   ✅ Backend is responding
) else (
    echo   ⚠️  Backend not responding yet (might still be initializing)
)

echo.

REM Step 3: Start ngrok tunnel
if "!NGROK_MISSING!"=="" (
    echo [STEP 3/4] Starting ngrok Tunnel...
    echo.
    echo This will expose your backend to the internet via HTTPS
    echo Press Enter to start ngrok in a new terminal window...
    echo.
    echo ⚠️  IMPORTANT: Keep the ngrok window open during deployment!
    pause

    REM Start ngrok in new terminal
    start "ORFEAS ngrok Tunnel" cmd /k "c:\Users\johng\Documents\oscar\START_NGROK_TUNNEL.bat"

    echo   ✅ ngrok started (check terminal window)
    echo.
    echo Please wait 5 seconds for tunnel to establish...
    timeout /t 5 /nobreak

    echo.
    echo 📋 Copy your ngrok URL from the ngrok terminal window
    echo    Example: https://abc123def456.ngrok.io
    echo.
    set /p NGROK_URL="Enter your ngrok URL (https://xxxx.ngrok.io): "

    if "!NGROK_URL!"=="" (
        echo ❌ ngrok URL cannot be empty
        pause
        exit /b 1
    )

    echo.
) else (
    echo [STEP 3/4] ⚠️  ngrok not installed, skipping automatic tunnel
    echo.
    echo You can still deploy, but will need to:
    echo   1. Install ngrok from https://ngrok.com/download
    echo   2. Run: ngrok http 5000
    echo   3. Copy the public URL
    echo.
    set /p NGROK_URL="Enter your public backend URL (https://xxxx.ngrok.io): "
)

REM Step 4: Deploy to Netlify
echo [STEP 4/4] Deploying to Netlify...
echo.
echo This will:
echo   1. Create netlify.toml with your ngrok URL
echo   2. Push code to GitHub
echo   3. Deploy to Netlify
echo.
echo Press Enter to continue...
pause

cd /d "c:\Users\johng\Documents\oscar"

REM Update netlify.toml with ngrok URL
echo Updating netlify.toml with your ngrok URL...
powershell -Command "(Get-Content 'netlify.toml') -replace 'YOUR_NGROK_URL_HERE', '!NGROK_URL!' | Set-Content 'netlify.toml'"
echo   ✅ netlify.toml updated

REM Update synexa-style-studio.html
echo Updating frontend configuration...
powershell -Command "(Get-Content 'synexa-style-studio.html') -replace 'const API_BASE = .*', 'const API_BASE = \"!NGROK_URL!\";' | Set-Content 'synexa-style-studio.html'"
echo   ✅ Frontend configuration updated

REM Initialize git and commit
echo Preparing git repository...
if not exist ".git" (
    git init
    git remote add origin "https://github.com/YourUsername/orfeas-ai-frontend.git" 2>nul
)

git config user.email "deployer@orfeas.local" 2>nul
git config user.name "ORFEAS Deployer" 2>nul
git add . 2>nul
git commit -m "ORFEAS AI Studio - Deployment to Netlify with ngrok backend" 2>nul

echo   ✅ Git ready

REM Deploy to Netlify
echo.
echo 🚀 Deploying to Netlify...
echo    (You may be prompted to log in to Netlify)
echo.

netlify deploy --prod

echo.
echo ════════════════════════════════════════════════════════════════
echo                    ✅ DEPLOYMENT COMPLETE!
echo ════════════════════════════════════════════════════════════════
echo.

REM Get Netlify site info
for /f %%i in ('netlify api getUser 2^>^&1 ^| findstr /i "name"') do set USER_INFO=%%i

echo Your ORFEAS AI Studio is now live!
echo.
echo IMPORTANT - Keep these running:
echo   • Backend terminal (http://127.0.0.1:5000)
echo   • ngrok tunnel terminal (https://!NGROK_URL!)
echo.
echo TEST YOUR DEPLOYMENT:
echo   1. Open your Netlify site in browser
echo   2. Open browser console (F12 → Console)
echo   3. Check for [CONFIG] API_BASE = !NGROK_URL!
echo   4. Upload an image and generate a 3D model
echo   5. Watch GPU utilization on local machine
echo.
echo TROUBLESHOOTING:
echo   • If API calls fail, check ngrok tunnel is running
echo   • If CORS errors, verify netlify.toml has correct ngrok URL
echo   • Check backend logs for GPU/memory issues
echo.
echo Documentation:
echo   📖 NETLIFY_DEPLOYMENT_GUIDE.md
echo   📖 CONNECTION_FIX_COMPLETE.txt
echo   📖 TROUBLESHOOTING_CONNECTION_GUIDE.txt
echo.

pause
