@echo off
setlocal enabledelayedexpansion
cd /d c:\Users\johng\Documents\oscar

echo.
echo ════════════════════════════════════════════════════════════════
echo   ORFEAS AI - PUSH TO GITHUB
echo ════════════════════════════════════════════════════════════════
echo.

echo [Step 1] Verify git status...
git status
echo.

echo [Step 2] Check if remote is configured...
for /f "tokens=*" %%i in ('git remote -v') do (
    echo %%i
)
echo.

echo ════════════════════════════════════════════════════════════════
echo   PUSH INSTRUCTIONS
echo ════════════════════════════════════════════════════════════════
echo.
echo To push your code to GitHub, you have 2 options:
echo.
echo OPTION 1: If you already created the repository on GitHub
echo ───────────────────────────────────────────────────────────
echo Run this command (replace YOUR-USERNAME with your GitHub username):
echo.
echo   git remote add origin https://github.com/YOUR-USERNAME/orfeas-ai-studio
echo   git branch -M main
echo   git push -u origin main
echo.
echo Example (if your username is john-smith):
echo   git remote add origin https://github.com/john-smith/orfeas-ai-studio
echo   git branch -M main
echo   git push -u origin main
echo.
echo.
echo OPTION 2: If you haven't created the repository yet
echo ──────────────────────────────────────────────────
echo 1. Go to: https://github.com/new
echo 2. Repository name: orfeas-ai-studio
echo 3. Make it PUBLIC
echo 4. Click "Create repository"
echo 5. Then run the commands from OPTION 1 above
echo.
echo.
echo ════════════════════════════════════════════════════════════════
echo.
pause
