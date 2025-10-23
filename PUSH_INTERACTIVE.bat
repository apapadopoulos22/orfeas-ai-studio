@echo off
setlocal enabledelayedexpansion
cd /d c:\Users\johng\Documents\oscar

echo.
echo ════════════════════════════════════════════════════════════════
echo   PUSH TO GITHUB - INTERACTIVE SETUP
echo ════════════════════════════════════════════════════════════════
echo.

set /p USERNAME="Enter your GitHub username: "

if "%USERNAME%"=="" (
    echo Error: GitHub username is required
    pause
    exit /b 1
)

echo.
echo [Step 1] Adding remote origin...
git remote add origin https://github.com/%USERNAME%/orfeas-ai-studio 2>nul
if !errorlevel! equ 0 (
    echo ✓ Remote added
) else (
    echo Note: Remote may already exist, checking...
    for /f "tokens=*" %%i in ('git remote -v') do echo %%i
)

echo.
echo [Step 2] Switching to main branch...
git branch -M main
echo ✓ Branch renamed to main

echo.
echo [Step 3] Pushing to GitHub...
echo.
echo Important: You may be asked to authenticate
echo - If using HTTPS: Enter your GitHub personal access token as password
echo - You can create a token at: https://github.com/settings/tokens
echo.

git push -u origin main

echo.
echo ════════════════════════════════════════════════════════════════
if !errorlevel! equ 0 (
    echo ✅ PUSH SUCCESSFUL!
    echo.
    echo Your repository is now on GitHub:
    echo https://github.com/%USERNAME%/orfeas-ai-studio
    echo.
    echo NEXT STEP: Enable GitHub Pages
    echo ─────────────────────────────────
    echo 1. Go to: https://github.com/%USERNAME%/orfeas-ai-studio
    echo 2. Click Settings (top right)
    echo 3. Click Pages (left sidebar)
    echo 4. Source: Deploy from a branch
    echo 5. Branch: main, Folder: /
    echo 6. Click Save
    echo.
    echo Wait 1-2 minutes, then your site will be live at:
    echo https://%USERNAME%.github.io/orfeas-ai-studio
) else (
    echo ❌ PUSH FAILED
    echo.
    echo Common issues:
    echo - Repository not created on GitHub yet
    echo   Go to: https://github.com/new
    echo   Create: orfeas-ai-studio (PUBLIC)
    echo - Authentication failed
    echo   Use Personal Access Token, not password
    echo - Check your GitHub username is correct
)
echo.
pause
