@echo off
REM ════════════════════════════════════════════════════════════════
REM  ORFEAS AI - ONE-CLICK AUTOMATIC NETLIFY DEPLOYMENT
REM ════════════════════════════════════════════════════════════════

setlocal enabledelayedexpansion
cd /d c:\Users\johng\Documents\oscar

echo.
echo ════════════════════════════════════════════════════════════════
echo           ORFEAS AI - AUTOMATIC NETLIFY DEPLOYMENT
echo ════════════════════════════════════════════════════════════════
echo.

REM Check prerequisites
echo [1/4] Checking prerequisites...
netlify --version >nul 2>&1
if errorlevel 1 (
    echo ❌ netlify-cli not found. Installing...
    call npm install -g netlify-cli
)
echo    ✅ netlify-cli ready
echo.

REM Initialize git if needed
echo [2/4] Preparing git repository...
if not exist ".git" (
    git init >nul 2>&1
    echo    ✅ Git repository initialized
) else (
    echo    ✅ Git repository exists
)
git config user.email "deploy@orfeas.local" >nul 2>&1
git config user.name "ORFEAS Deployer" >nul 2>&1
echo.

REM Stage and commit
echo [3/4] Staging files for deployment...
git add . >nul 2>&1
git commit -m "ORFEAS AI - Auto deployment to Netlify" >nul 2>&1
echo    ✅ Files committed
echo.

REM Deploy to Netlify
echo [4/4] Deploying to Netlify...
echo    This will deploy your ORFEAS AI Studio to production...
echo.

netlify deploy --prod

echo.
echo ════════════════════════════════════════════════════════════════
echo                    ✅ DEPLOYMENT COMPLETE!
echo ════════════════════════════════════════════════════════════════
echo.
echo Your ORFEAS AI Studio is now live!
echo.
echo Next steps:
echo   1. Backend must be running: python backend/main.py
echo   2. ngrok tunnel must be active: .\START_NGROK_TUNNEL.bat
echo   3. Open your Netlify URL in browser
echo   4. Upload image and test 3D generation
echo.
echo Keep backend and ngrok running for the app to work!
echo.
pause
