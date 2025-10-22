@echo off
setlocal enabledelayedexpansion
cd /d c:\Users\johng\Documents\oscar

echo.
echo ════════════════════════════════════════════════════════════════
echo   ORFEAS AI - GITHUB PAGES DEPLOYMENT SETUP
echo ════════════════════════════════════════════════════════════════
echo.

echo [Step 1/4] Configure git user...
git config --global user.email "apapadopoulos22@gmail.com"
git config --global user.name "ORFEAS Developer"
echo ✓ Git configured

echo.
echo [Step 2/4] Initialize git repository...
if exist .git (
    echo ✓ Git repository already exists
) else (
    git init
    echo ✓ Git initialized
)

echo.
echo [Step 3/4] Stage and commit files...
git add .
git commit -m "ORFEAS AI Studio - GitHub Pages Deployment" --allow-empty
echo ✓ Files committed

echo.
echo ════════════════════════════════════════════════════════════════
echo   READY FOR GITHUB PAGES
echo ════════════════════════════════════════════════════════════════
echo.

echo NEXT STEPS:
echo.
echo 1. Create GitHub Repository:
echo    Go to: https://github.com/new
echo    Repository name: orfeas-ai-studio
echo    Description: ORFEAS AI - 3D Model Generation Studio
echo    Public: YES
echo    Click "Create repository"
echo.
echo 2. Add Remote and Push:
echo    Open terminal and run these commands:
echo    (Replace YOUR-USERNAME with your actual GitHub username)
echo.
echo    git remote add origin https://github.com/YOUR-USERNAME/orfeas-ai-studio
echo    git branch -M main
echo    git push -u origin main
echo.
echo 3. Enable GitHub Pages:
echo    Go to: https://github.com/YOUR-USERNAME/orfeas-ai-studio
echo    Click: Settings (top right)
echo    Click: Pages (left sidebar)
echo    Source: Deploy from branch
echo    Branch: main
echo    Folder: / (root)
echo    Click: Save
echo.
echo 4. Your Live URL (wait 1-2 minutes):
echo    https://YOUR-USERNAME.github.io/orfeas-ai-studio
echo.
echo ════════════════════════════════════════════════════════════════
echo.
pause
