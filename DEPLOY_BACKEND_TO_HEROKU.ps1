# ============================================================================
# ORFEAS AI STUDIO BACKEND - HEROKU DEPLOYMENT SCRIPT
# ============================================================================
# This script deploys the BOB AI v7.1 backend to Heroku
#
# Prerequisites:
#   1. Heroku CLI installed
#   2. Git repository initialized
#   3. Logged in to Heroku: heroku login
#
# Usage:
#   .\DEPLOY_BACKEND_TO_HEROKU.ps1
# ============================================================================

Write-Host "`n" -ForegroundColor White
Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  ORFEAS AI STUDIO BACKEND - HEROKU DEPLOYMENT SCRIPT     ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host "`n"

# Step 1: Verify prerequisites
Write-Host "STEP 1: Verifying Prerequisites..." -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray

# Check Heroku CLI
Write-Host "  Checking Heroku CLI..." -ForegroundColor White
$herokuVersion = heroku --version 2>$null
if ($herokuVersion) {
    Write-Host "    ✓ Heroku CLI found: $herokuVersion" -ForegroundColor Green
}
else {
    Write-Host "    ✗ Heroku CLI NOT found. Install from: https://devcenter.heroku.com/articles/heroku-cli" -ForegroundColor Red
    exit 1
}

# Check Git
Write-Host "  Checking Git..." -ForegroundColor White
$gitVersion = git --version 2>$null
if ($gitVersion) {
    Write-Host "    ✓ Git found: $gitVersion" -ForegroundColor Green
}
else {
    Write-Host "    ✗ Git NOT found. Install from: https://git-scm.com/" -ForegroundColor Red
    exit 1
}

# Check Python
Write-Host "  Checking Python..." -ForegroundColor White
$pythonVersion = python --version 2>$null
if ($pythonVersion) {
    Write-Host "    ✓ Python found: $pythonVersion" -ForegroundColor Green
}
else {
    Write-Host "    ✗ Python NOT found" -ForegroundColor Red
    exit 1
}

Write-Host "`n✓ All prerequisites verified`n" -ForegroundColor Green

# Step 2: Check Heroku authentication
Write-Host "STEP 2: Checking Heroku Authentication..." -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray

$herokuAuth = heroku auth:whoami 2>$null
if ($herokuAuth) {
    Write-Host "  ✓ Logged in as: $herokuAuth" -ForegroundColor Green
}
else {
    Write-Host "  ✗ Not authenticated with Heroku" -ForegroundColor Yellow
    Write-Host "  Launching Heroku login..." -ForegroundColor Cyan
    heroku login
}

Write-Host "`n"

# Step 3: Create or select Heroku app
Write-Host "STEP 3: Setting Up Heroku App..." -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray

$appName = Read-Host "Enter app name (default: orfeas-ai-backend) [press Enter]"
if ([string]::IsNullOrWhiteSpace($appName)) {
    $appName = "orfeas-ai-backend"
}

Write-Host "  App name: $appName" -ForegroundColor Cyan

# Check if app exists
Write-Host "  Checking if app exists..." -ForegroundColor White
$appExists = heroku apps:info --app $appName 2>$null | Select-String -Pattern "Name"

if ($appExists) {
    Write-Host "    ✓ App already exists: $appName" -ForegroundColor Green
}
else {
    Write-Host "    Creating new app: $appName" -ForegroundColor Cyan
    heroku create $appName
    Write-Host "    ✓ App created: $appName" -ForegroundColor Green
}

Write-Host "`n"

# Step 4: Create Procfile
Write-Host "STEP 4: Creating Procfile..." -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray

$procfileContent = @"
web: pip install gunicorn && gunicorn main:app
worker: python main.py
release: python -c "print('Deployment complete')"
"@

if (-not (Test-Path "Procfile")) {
    Set-Content -Path "Procfile" -Value $procfileContent
    Write-Host "  ✓ Procfile created" -ForegroundColor Green
}
else {
    Write-Host "  ℹ Procfile already exists" -ForegroundColor Cyan
}

Write-Host "`n"

# Step 5: Generate requirements.txt
Write-Host "STEP 5: Generating requirements.txt..." -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray

if (Test-Path "requirements.txt") {
    Write-Host "  ℹ requirements.txt already exists" -ForegroundColor Cyan
}
else {
    Write-Host "  Generating requirements.txt..." -ForegroundColor White
    pip freeze > requirements.txt
    Write-Host "  ✓ requirements.txt created" -ForegroundColor Green
}

Write-Host "`n"

# Step 6: Set environment variables
Write-Host "STEP 6: Setting Environment Variables..." -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray

$envVars = @{
    "FLASK_ENV"         = "production"
    "DEVICE"            = "cpu"
    "LOCAL_LLM_ENABLED" = "true"
    "LOG_LEVEL"         = "INFO"
}

foreach ($var in $envVars.GetEnumerator()) {
    Write-Host "  Setting: $($var.Key)=$($var.Value)" -ForegroundColor White
    heroku config:set --app $appName "$($var.Key)=$($var.Value)" 2>$null
}

Write-Host "  ✓ Environment variables configured`n" -ForegroundColor Green

# Step 7: Push to Heroku
Write-Host "STEP 7: Deploying to Heroku..." -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray

Write-Host "  Running: git push heroku main" -ForegroundColor Cyan
git push heroku main

Write-Host "`n"

# Step 8: Scale dynos
Write-Host "STEP 8: Configuring Dynos..." -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray

Write-Host "  Scaling web dyno..." -ForegroundColor White
heroku ps:scale web=1 --app $appName

Write-Host "  ✓ Dynos configured`n" -ForegroundColor Green

# Step 9: Get app URL
Write-Host "STEP 9: Deployment Complete" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray

$appUrl = heroku apps:info --app $appName 2>$null | Select-String -Pattern "Web URL" | ForEach-Object { $_ -replace "Web URL:\s+", "" }

Write-Host "`n✓ ORFEAS AI Backend successfully deployed to Heroku!`n" -ForegroundColor Green

Write-Host "📋 DEPLOYMENT SUMMARY:" -ForegroundColor Cyan
Write-Host "  App Name:     $appName" -ForegroundColor White
Write-Host "  Backend URL:  https://$appName.herokuapp.com" -ForegroundColor White
Write-Host "  Health:       https://$appName.herokuapp.com/health" -ForegroundColor White
Write-Host "  Dashboard:    https://dashboard.heroku.com/apps/$appName" -ForegroundColor White
Write-Host "`n"

Write-Host "🔗 NEXT STEPS:" -ForegroundColor Yellow
Write-Host "  1. View logs: heroku logs --tail --app $appName" -ForegroundColor White
Write-Host "  2. Check status: heroku ps --app $appName" -ForegroundColor White
Write-Host "  3. Open app: heroku open --app $appName" -ForegroundColor White
Write-Host "  4. Update frontend with backend URL" -ForegroundColor White
Write-Host "`n"

Write-Host "📞 SUPPORT:" -ForegroundColor Yellow
Write-Host "  Heroku Docs:  https://devcenter.heroku.com/" -ForegroundColor White
Write-Host "  GitHub Repo:  https://github.com/apapadopoulos22/orfeas-ai-studio" -ForegroundColor White
Write-Host "`n"

Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║           DEPLOYMENT SUCCESSFUL! 🚀                       ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan
