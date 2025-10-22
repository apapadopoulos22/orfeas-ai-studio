@echo off
setlocal enabledelayedexpansion
cd /d c:\Users\johng\Documents\oscar

echo.
echo ════════════════════════════════════════════════════════════════
echo   ORFEAS AI - DEPLOY TO SURGE.SH (FREE, INSTANT)
echo ════════════════════════════════════════════════════════════════
echo.
echo Surge.sh = Instant free hosting, no account needed!
echo.

echo [Step 1/2] Installing surge...
call npm install -g surge
echo ✓ Surge ready

echo.
echo [Step 2/2] Deploying to Surge...
echo When prompted:
echo   - Email: Use any email (or press enter to use existing)
echo   - Domain: Leave blank for auto-generated or enter custom
echo.
call surge . --domain orfeas-ai-studio.surge.sh

echo.
echo ════════════════════════════════════════════════════════════════
echo   ✓ DEPLOYED TO SURGE.SH
echo ════════════════════════════════════════════════════════════════
echo.
echo Your site URL:
echo   https://orfeas-ai-studio.surge.sh
echo.
echo This deployment has NO credit limits, NO billing!
echo.
pause
