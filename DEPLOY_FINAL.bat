@echo off
setlocal enabledelayedexpansion
cd /d c:\Users\johng\Documents\oscar

echo.
echo ════════════════════════════════════════════════════════════════
echo   ORFEAS AI - FINAL NETLIFY DEPLOYMENT
echo ════════════════════════════════════════════════════════════════
echo.

echo [Step 1/5] Initialize Git Repository...
git init
git config user.email "deploy@orfeas.local"
git config user.name "ORFEAS Deployer"
echo ✓ Git initialized

echo.
echo [Step 2/5] Stage all files...
git add .
echo ✓ Files staged

echo.
echo [Step 3/5] Create initial commit...
git commit -m "ORFEAS AI Studio - Production Deployment"
echo ✓ Commit created

echo.
echo [Step 4/5] Creating Netlify site...
echo Select: "Create & configure a new site"
echo Team: "apapadopoulos22's team"
echo Site name: "orfeas-ai-studio" (or press enter for auto-generated)
echo.
netlify link
echo ✓ Site linked

echo.
echo [Step 5/5] Deploying to production...
netlify deploy --prod

echo.
echo ════════════════════════════════════════════════════════════════
echo   ✓ DEPLOYMENT COMPLETE!
echo ════════════════════════════════════════════════════════════════
echo.
echo Your Netlify URL is shown above as "Site URL"
echo.
echo NEXT STEPS:
echo   1. Start Backend: cd backend && python -u main.py
echo   2. Start ngrok: .\START_NGROK_TUNNEL.bat
echo   3. Open your Netlify URL in browser
echo.
pause
