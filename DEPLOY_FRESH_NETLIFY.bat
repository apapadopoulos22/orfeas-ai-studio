@echo off
setlocal enabledelayedexpansion
cd /d c:\Users\johng\Documents\oscar

echo.
echo ════════════════════════════════════════════════════════════════
echo   ORFEAS AI - FRESH NETLIFY DEPLOYMENT (New Account/Site)
echo ════════════════════════════════════════════════════════════════
echo.

echo [Step 1/4] Verify previous site is unlinked...
if exist ".netlify" (
  echo ✗ .netlify folder still exists, removing...
  rmdir /s /q .netlify
) else (
  echo ✓ Site unlinked (clean state)
)

echo.
echo [Step 2/4] Creating new Netlify site...
echo Netlify will ask you:
echo   1. Create & configure a new site
echo   2. Choose your team: "apapadopoulos22's team"
echo   3. Site name: "orfeas-ai-studio-free" or press enter
echo.
netlify link

echo.
echo [Step 3/4] Deploying to production...
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
