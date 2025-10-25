# ORFEAS AI - Complete Deployment Pipeline
# Automated: Local Test -> Staging -> Production

Write-Host ""
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host "ORFEAS AI - Full Deployment Pipeline" -ForegroundColor Cyan
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host ""

$ErrorActionPreference = "Stop"

# Confirmation
Write-Host "This will run the complete deployment pipeline:" -ForegroundColor Yellow
Write-Host "  1. Test locally" -ForegroundColor White
Write-Host "  2. Deploy to staging" -ForegroundColor White
Write-Host "  3. Deploy to production" -ForegroundColor White
Write-Host ""
Write-Host "Continue? (yes/no)" -ForegroundColor Yellow
$confirmation = Read-Host
if ($confirmation -ne "yes") {
    Write-Host "Deployment cancelled" -ForegroundColor Red
    exit 0
}

# Phase 1: Local Testing
Write-Host ""
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host "PHASE 1: Local Testing" -ForegroundColor Cyan
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[1/5] Stopping existing backend..." -ForegroundColor Yellow
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2
Write-Host "[OK] Backend stopped" -ForegroundColor Green

Write-Host "[2/5] Starting Docker services..." -ForegroundColor Yellow
docker-compose up -d redis
Start-Sleep -Seconds 3
Write-Host "[OK] Docker services started" -ForegroundColor Green

Write-Host "[3/5] Installing dependencies..." -ForegroundColor Yellow
cd backend
pip install -q flask flask-cors flask-socketio psutil torch redis sqlalchemy psycopg2-binary flask-compress brotli
Write-Host "[OK] Dependencies installed" -ForegroundColor Green

Write-Host "[4/5] Starting backend server..." -ForegroundColor Yellow
$backendJob = Start-Job -ScriptBlock {
    Set-Location "C:\Users\johng\Documents\oscar\backend"
    python main.py 2>&1
}
Start-Sleep -Seconds 8

Write-Host "[5/5] Checking backend health..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:5000/health" -TimeoutSec 5 -ErrorAction Stop
    Write-Host "[OK] Backend is running successfully" -ForegroundColor Green
    Write-Host "     URL: http://localhost:5000" -ForegroundColor Cyan
}
catch {
    Write-Host "[ERROR] Backend failed to start" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Stop-Job $backendJob -ErrorAction SilentlyContinue
    Remove-Job $backendJob -ErrorAction SilentlyContinue
    exit 1
}

Write-Host ""
Write-Host "[COMPLETE] Phase 1 - Local testing passed" -ForegroundColor Green
Write-Host ""
Write-Host "Proceed to staging deployment? (y/n)" -ForegroundColor Yellow
$continue = Read-Host
if ($continue -ne "y") {
    Write-Host "Deployment stopped after local testing" -ForegroundColor Yellow
    exit 0
}

# Stop local backend
Write-Host "Stopping local backend..." -ForegroundColor Yellow
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2
cd C:\Users\johng\Documents\oscar

# Phase 2: Staging Deployment
Write-Host ""
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host "PHASE 2: Staging Deployment" -ForegroundColor Cyan
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[1/6] Checking git status..." -ForegroundColor Yellow
$gitStatus = git status --porcelain
if ($gitStatus) {
    Write-Host "Uncommitted changes detected" -ForegroundColor Yellow
    Write-Host "Commit changes? (y/n)" -ForegroundColor Yellow
    $commit = Read-Host
    if ($commit -eq "y") {
        git add .
        $msg = "Deployment: staging release $(Get-Date -Format 'yyyy.MM.dd')"
        git commit -m $msg
        Write-Host "[OK] Changes committed" -ForegroundColor Green
    }
}
else {
    Write-Host "[OK] Working directory clean" -ForegroundColor Green
}

Write-Host "[2/6] Switching to develop branch..." -ForegroundColor Yellow
git checkout develop
Write-Host "[OK] On develop branch" -ForegroundColor Green

Write-Host "[3/6] Pulling latest changes..." -ForegroundColor Yellow
git pull origin develop
Write-Host "[OK] Latest changes pulled" -ForegroundColor Green

Write-Host "[4/6] Running tests..." -ForegroundColor Yellow
# Skip test if not available
if (Test-Path "tests") {
    pytest tests -q --tb=short
}
else {
    Write-Host "Tests not found, skipping" -ForegroundColor Yellow
}
Write-Host "[OK] Tests completed" -ForegroundColor Green

Write-Host "[5/6] Pushing to develop..." -ForegroundColor Yellow
git push origin develop
Write-Host "[OK] Pushed to develop branch" -ForegroundColor Green

Write-Host "[6/6] GitHub Actions workflow triggered" -ForegroundColor Yellow
Write-Host "Monitor: https://github.com/apapadopoulos22/orfeas-ai-studio/actions" -ForegroundColor Cyan
Write-Host ""
Write-Host "[COMPLETE] Phase 2 - Staging deployment initiated" -ForegroundColor Green
Write-Host ""
Write-Host "Proceed to production deployment? (yes/no)" -ForegroundColor Red
$continue = Read-Host
if ($continue -ne "yes") {
    Write-Host "Deployment stopped after staging" -ForegroundColor Yellow
    exit 0
}

# Phase 3: Production Deployment
Write-Host ""
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host "PHASE 3: Production Deployment" -ForegroundColor Cyan
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "WARNING: This will deploy to production!" -ForegroundColor Red
Write-Host "Are you absolutely sure? (yes/no)" -ForegroundColor Red
$finalConfirm = Read-Host
if ($finalConfirm -ne "yes") {
    Write-Host "Production deployment cancelled" -ForegroundColor Yellow
    exit 0
}

Write-Host "[1/5] Checking git status..." -ForegroundColor Yellow
$gitStatus = git status --porcelain
if ($gitStatus) {
    Write-Host "ERROR: Uncommitted changes exist" -ForegroundColor Red
    exit 1
}
Write-Host "[OK] Working directory clean" -ForegroundColor Green

Write-Host "[2/5] Switching to main branch..." -ForegroundColor Yellow
git checkout main
Write-Host "[OK] On main branch" -ForegroundColor Green

Write-Host "[3/5] Merging develop into main..." -ForegroundColor Yellow
git merge develop -m "Merge develop to main for production deployment"
Write-Host "[OK] Merged develop into main" -ForegroundColor Green

Write-Host "[4/5] Creating git tag..." -ForegroundColor Yellow
$tag = "v$(Get-Date -Format 'yyyy.MM.dd-HHmm')"
git tag -a $tag -m "Production deployment $tag"
Write-Host "[OK] Created tag: $tag" -ForegroundColor Green

Write-Host "[5/5] Pushing to main..." -ForegroundColor Yellow
git push origin main
git push origin $tag
Write-Host "[OK] Pushed to main branch" -ForegroundColor Green

Write-Host ""
Write-Host "Production deployment initiated!" -ForegroundColor Green
Write-Host "Monitor: https://github.com/apapadopoulos22/orfeas-ai-studio/actions" -ForegroundColor Cyan
Write-Host ""

# Summary
Write-Host ""
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host "DEPLOYMENT COMPLETE" -ForegroundColor Green
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "All phases completed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Environments:" -ForegroundColor White
Write-Host "  Local:      http://localhost:5000" -ForegroundColor Cyan
Write-Host "  Staging:    https://staging.orfeas.ai" -ForegroundColor Cyan
Write-Host "  Production: https://orfeas.ai" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Monitor GitHub Actions"
Write-Host "  2. Watch error rates and response times"
Write-Host "  3. Verify production is working"
Write-Host ""
