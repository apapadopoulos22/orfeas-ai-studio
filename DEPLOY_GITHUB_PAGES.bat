@echo off
setlocal enabledelayedexpansion
cd /d c:\Users\johng\Documents\oscar

echo.
echo ════════════════════════════════════════════════════════════════
echo   ORFEAS AI - DEPLOY TO GITHUB PAGES (FREE)
echo ════════════════════════════════════════════════════════════════
echo.

echo [Step 1/3] Checking if gh-pages is installed...
npm list -g gh-pages >nul 2>&1
if errorlevel 1 (
    echo Installing gh-pages...
    call npm install -g gh-pages
)
echo ✓ gh-pages ready

echo.
echo [Step 2/3] Pushing to GitHub...
echo Make sure you have:
echo   1. Git configured: git config user.name and user.email
echo   2. Remote set: git remote add origin YOUR_GITHUB_REPO
echo   3. GitHub token ready (personal access token)
echo.

echo Current remote:
git remote -v

echo.
echo [Step 3/3] Deploying to GitHub Pages...
call npx gh-pages -d . -b gh-pages -m "ORFEAS AI - Auto deployment"

echo.
echo ════════════════════════════════════════════════════════════════
echo   ✓ DEPLOYED TO GITHUB PAGES
echo ════════════════════════════════════════════════════════════════
echo.
echo Your site will be available at:
echo   https://[YOUR_GITHUB_USERNAME].github.io/[REPO_NAME]
echo.
echo Check GitHub Pages settings:
echo   https://github.com/YOUR_USERNAME/YOUR_REPO/settings/pages
echo.
pause
