@echo off
REM Netlify Deployment Script for ORFEAS AI Frontend (Windows)
REM This script prepares and deploys the frontend to Netlify

setlocal enabledelayedexpansion

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║  ORFEAS AI - Netlify Frontend Deployment Script            ║
echo ║  Windows Edition                                           ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

REM Check if git is installed
git --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Git is not installed
    echo Please install Git from https://git-scm.com/
    pause
    exit /b 1
)

REM Check if netlify-cli is installed
netlify --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  netlify-cli not found. Installing...
    call npm install -g netlify-cli
)

REM Get user input
echo.
set /p NGROK_URL="Enter your ngrok URL (https://xxxx.ngrok.io): "
if "!NGROK_URL!"=="" (
    echo ❌ ngrok URL cannot be empty
    pause
    exit /b 1
)

set /p REPO_NAME="Enter GitHub repository name (e.g., orfeas-ai-frontend): "
if "!REPO_NAME!"=="" (
    echo ❌ Repository name cannot be empty
    pause
    exit /b 1
)

echo.
echo Configuration:
echo   ngrok URL: !NGROK_URL!
echo   Repository: !REPO_NAME!
echo.

REM Create project directory
set DEPLOY_DIR=%TEMP%\orfeas-netlify-deploy
if exist "!DEPLOY_DIR!" (
    rmdir /s /q "!DEPLOY_DIR!"
)
mkdir "!DEPLOY_DIR!"
cd /d "!DEPLOY_DIR!"

REM Copy files
echo [1/5] Copying project files...
copy "%~dp0synexa-style-studio.html" . >nul
copy "%~dp0netlify.toml" . >nul
copy "%~dp0QUICK_START_PRODUCTION.txt" . >nul

REM Update netlify.toml with ngrok URL
echo [2/5] Updating netlify.toml with ngrok URL...
powershell -Command "(Get-Content 'netlify.toml') -replace 'YOUR_NGROK_URL_HERE', '!NGROK_URL!' | Set-Content 'netlify.toml'"

REM Initialize git if needed
if not exist ".git" (
    echo [3/5] Initializing git repository...
    git init
    git remote add origin "https://github.com/%GITHUB_USER%/!REPO_NAME!.git"
)

REM Add and commit files
echo [4/5] Committing files...
git config user.email "deployer@orfeas.local"
git config user.name "ORFEAS Deployer"
git add .
git commit -m "ORFEAS AI Studio - Frontend deployment to Netlify with ngrok backend" 2>nul || true

REM Deploy to Netlify
echo [5/5] Deploying to Netlify...
call netlify deploy --prod

echo.
echo ✅ Deployment complete!
echo.
echo Next steps:
echo   1. Visit your Netlify site URL
echo   2. Check console: [CONFIG] API_BASE should show !NGROK_URL!
echo   3. Test image upload and generation
echo.
echo Remember: Keep ngrok tunnel running with START_NGROK_TUNNEL.bat
echo.
pause
