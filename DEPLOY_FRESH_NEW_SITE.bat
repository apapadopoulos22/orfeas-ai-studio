@echo off
setlocal enabledelayedexpansion
cd /d c:\Users\johng\Documents\oscar

echo.
echo ════════════════════════════════════════════════════════════════
echo   ORFEAS AI - FRESH NETLIFY DEPLOYMENT (Brand New Site)
echo ════════════════════════════════════════════════════════════════
echo.

echo [Step 1/5] Initialize Git Repository...
if exist .git rmdir /s /q .git >nul 2>&1
git init >nul 2>&1
git config user.email "deploy@orfeas.local" >nul 2>&1
git config user.name "ORFEAS Deployer" >nul 2>&1
echo ✓ Git initialized fresh

echo.
echo [Step 2/5] Stage all files...
git add . >nul 2>&1
echo ✓ Files staged

echo.
echo [Step 3/5] Create initial commit...
git commit -m "ORFEAS AI Studio - Fresh Production Deployment" >nul 2>&1
echo ✓ Commit created

echo.
echo [Step 4/5] Deploy to Netlify (Creating new site)...
echo This will:
echo   - Create NEW Netlify site with fresh free tier
echo   - Deploy all files
echo   - Give you a unique URL
echo.
netlify deploy --prod --create-site

echo.
echo ════════════════════════════════════════════════════════════════
echo   ✓ DEPLOYMENT COMPLETE!
echo ════════════════════════════════════════════════════════════════
echo.
echo Your NEW Netlify URL is shown above as "Production" or "Live URL"
echo.
echo NEXT STEPS:
echo   1. Copy your new Netlify URL
echo   2. Start Backend: cd backend && python -u main.py
echo   3. Start ngrok: .\START_NGROK_TUNNEL.bat
echo   4. Open your URL in browser and test
echo.
pause
