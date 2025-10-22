@echo off
REM ════════════════════════════════════════════════════════════════
REM  ORFEAS AI - Deployment Verification & Health Check
REM ════════════════════════════════════════════════════════════════

setlocal enabledelayedexpansion

cls
color 0A

echo.
echo ════════════════════════════════════════════════════════════════
echo           ORFEAS AI - Deployment Verification
echo ════════════════════════════════════════════════════════════════
echo.

REM Check 1: Backend Health
echo [1/6] Checking Backend Health...
powershell -Command "try { $r = Invoke-WebRequest -Uri http://127.0.0.1:5000/health -UseBasicParsing -TimeoutSec 5; if ($r.StatusCode -eq 200) { Write-Host '    ✅ Backend responding on http://127.0.0.1:5000' -ForegroundColor Green } else { Write-Host '    ⚠️  Backend returned status ' $r.StatusCode -ForegroundColor Yellow } } catch { Write-Host '    ❌ Backend not responding - Start with: python backend/main.py' -ForegroundColor Red }"
echo.

REM Check 2: GPU Status
echo [2/6] Checking GPU Status...
powershell -Command "try { $gpu = nvidia-smi --query-gpu=memory.used,memory.total --format=csv,noheader 2>$null; if ($gpu) { Write-Host '    ✅ GPU found:' $gpu -ForegroundColor Green } else { Write-Host '    ❌ GPU not detected' -ForegroundColor Red } } catch { Write-Host '    ❌ nvidia-smi not found' -ForegroundColor Red }"
echo.

REM Check 3: ngrok Status
echo [3/6] Checking ngrok Tunnel...
powershell -Command "try { $ng = Invoke-WebRequest -Uri http://localhost:4040/api/tunnels -UseBasicParsing -TimeoutSec 3 2>$null; if ($ng.StatusCode -eq 200) { $json = ConvertFrom-Json $ng.Content; $url = $json.tunnels[0].public_url; Write-Host '    ✅ ngrok tunnel active: ' $url -ForegroundColor Green } else { Write-Host '    ⚠️  ngrok not detected at http://localhost:4040' -ForegroundColor Yellow } } catch { Write-Host '    ⚠️  ngrok not running (optional) - Start with: START_NGROK_TUNNEL.bat' -ForegroundColor Yellow }"
echo.

REM Check 4: Frontend Files
echo [4/6] Checking Frontend Files...
if exist "synexa-style-studio.html" (
    echo     ✅ synexa-style-studio.html found
) else (
    echo     ❌ synexa-style-studio.html not found
)
if exist "netlify.toml" (
    echo     ✅ netlify.toml found
) else (
    echo     ❌ netlify.toml not found
)
echo.

REM Check 5: Netlify CLI
echo [5/6] Checking Netlify CLI...
netlify --version >nul 2>&1
if errorlevel 1 (
    echo     ⚠️  netlify-cli not installed. Install with: npm install -g netlify-cli
) else (
    for /f %%i in ('netlify --version') do set NETLIFY_VERSION=%%i
    echo     ✅ netlify-cli ready (version !NETLIFY_VERSION!)
)
echo.

REM Check 6: Git Status
echo [6/6] Checking Git Repository...
cd /d "c:\Users\johng\Documents\oscar" >nul 2>&1
if exist ".git" (
    echo     ✅ Git repository initialized
    for /f "delims=" %%i in ('git remote get-url origin 2^>nul') do set GIT_REMOTE=%%i
    if not "!GIT_REMOTE!"=="" (
        echo        Remote: !GIT_REMOTE!
    )
) else (
    echo     ℹ️  Git not initialized - Will initialize during deployment
)
echo.

REM Summary
echo ════════════════════════════════════════════════════════════════
echo                      SYSTEM STATUS
echo ════════════════════════════════════════════════════════════════
echo.
echo If all checks are green, you're ready to deploy!
echo.
echo Next steps:
echo   1. Run: .\DEPLOY_TO_NETLIFY_COMPLETE.bat
echo   2. Keep backend and ngrok terminals open
echo   3. Copy ngrok URL when prompted
echo   4. Watch for Netlify deployment URL
echo   5. Test image upload on deployed site
echo.

pause
