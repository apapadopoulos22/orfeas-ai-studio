@echo off
REM ============================================
REM ORFEAS AI STUDIO - NETLIFY DEPLOYMENT
REM ============================================
REM
REM Quick deployment script for Windows PowerShell
REM Prerequisites:
REM   - Git installed
REM   - Netlify CLI installed (npm install -g netlify-cli)
REM   - Repository connected to Netlify
REM
REM Usage: .\DEPLOY_NETLIFY.bat
REM

setlocal enabledelayedexpansion

cls
echo.
echo ╔════════════════════════════════════════╗
echo ║  ORFEAS AI STUDIO - NETLIFY DEPLOYMENT  ║
echo ╚════════════════════════════════════════╝
echo.

REM Check if Git is available
git --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Git is not installed or not in PATH
    echo    Visit: https://git-scm.com/download/win
    pause
    exit /b 1
)

REM Check if in correct directory
if not exist "orfeas-ai-studio.html" (
    echo ❌ Error: orfeas-ai-studio.html not found in current directory
    echo    Please run from project root
    cd /d "%~dp0"
    if not exist "orfeas-ai-studio.html" (
        pause
        exit /b 1
    )
)

echo ✅ Project files detected
echo.

REM STEP 1: Git status
echo STEP 1: Checking Git status...
git status --short
if errorlevel 1 (
    echo ❌ Git error
    pause
    exit /b 1
)
echo ✅ Git status OK
echo.

REM STEP 2: Stage changes
echo STEP 2: Staging changes for deployment...
git add .
echo ✅ Changes staged
echo.

REM STEP 3: Commit (with option to skip if nothing changed)
echo STEP 3: Creating deployment commit...
git commit -m "Deployment: Netlify production release" || (
    echo ℹ️  No changes to commit (already up to date)
)
echo.

REM STEP 4: Push to Git
echo STEP 4: Pushing to Git repository...
echo    Branch: main
git push origin main
if errorlevel 1 (
    echo ❌ Git push failed
    echo    Check your remote and branch name
    pause
    exit /b 1
)
echo ✅ Pushed to Git
echo.

REM STEP 5: Netlify deployment
echo STEP 5: Deploying to Netlify...
echo    Note: Netlify will auto-deploy from Git
echo    Watch deployment progress at: https://app.netlify.com
echo.

REM Check for Netlify CLI
where netlify >nul 2>&1
if errorlevel 1 (
    echo ℹ️  Netlify CLI not installed
    echo    For manual deployment, use: netlify deploy --prod
    echo    Or visit: https://app.netlify.com
) else (
    echo Running: netlify deploy --prod
    call netlify deploy --prod
)

echo.
echo ╔════════════════════════════════════════╗
echo ║  ✅ DEPLOYMENT INITIATED              ║
echo ╚════════════════════════════════════════╝
echo.
echo 📋 Deployment Status:
echo    • Changes pushed to Git ✅
echo    • Netlify will build and deploy automatically
echo    • Deployment usually takes 1-2 minutes
echo.
echo 🔗 View Progress:
echo    https://app.netlify.com
echo.
echo 🧪 After Deployment, Test:
echo    curl https://your-site.netlify.app
echo    curl https://your-site.netlify.app/.netlify/functions/health
echo.
echo 📚 Full guide:
echo    Read: NETLIFY_DEPLOYMENT_GUIDE.md
echo.
pause
