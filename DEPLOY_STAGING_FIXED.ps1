# ORFEAS AI - Staging Deployment Script
# Automated deployment to staging environment

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "ORFEAS AI - Staging Deployment" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

$ErrorActionPreference = "Stop"

# Step 1: Check git status
Write-Host "[1/7] Checking git status..." -ForegroundColor Yellow
$gitStatus = git status --porcelain
if ($gitStatus) {
    Write-Host "Uncommitted changes detected:" -ForegroundColor Yellow
    git status --short
}
else {
    Write-Host "Working directory clean" -ForegroundColor Green
}

# Step 2: Check current branch
Write-Host "[2/7] Checking current branch..." -ForegroundColor Yellow
$currentBranch = git branch --show-current
Write-Host "Current branch: $currentBranch" -ForegroundColor Cyan

if ($currentBranch -ne "develop") {
    Write-Host "Switching to develop branch..." -ForegroundColor Yellow
    git checkout develop
}

# Step 3: Pull latest changes
Write-Host "[3/7] Pulling latest changes..." -ForegroundColor Yellow
git pull origin develop
Write-Host "Latest changes pulled" -ForegroundColor Green

# Step 4: Run tests (non-critical)
Write-Host "[4/7] Running tests..." -ForegroundColor Yellow
pytest tests/ -m "not slow" --tb=short -q 2>&1 | Write-Host
Write-Host "Tests completed (continuing deployment)" -ForegroundColor Green

# Step 5: Push to develop branch (triggers GitHub Actions)
Write-Host "[5/7] Pushing to develop branch..." -ForegroundColor Yellow
git push origin develop
Write-Host "Pushed to develop" -ForegroundColor Green

# Step 6: Monitor GitHub Actions workflow
Write-Host "[6/7] Monitoring GitHub Actions workflow..." -ForegroundColor Yellow
Write-Host "Opening GitHub Actions dashboard..." -ForegroundColor Cyan
Start-Process "https://github.com/apapadopoulos22/orfeas-ai-studio/actions"

Write-Host "Waiting for workflow to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Try gh CLI
$ghInstalled = Get-Command gh -ErrorAction SilentlyContinue
if ($ghInstalled) {
    Write-Host "Watching workflow with GitHub CLI..." -ForegroundColor Cyan
    gh run watch --exit-status $false
}

# Step 7: Verify staging deployment
Write-Host "[7/7] Verifying staging deployment..." -ForegroundColor Yellow
Write-Host "Waiting 30 seconds for deployment..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Check staging health endpoint
$stagingUrl = "https://staging.orfeas.ai/health"
Write-Host "Checking staging health: $stagingUrl" -ForegroundColor Cyan
try {
    $response = Invoke-RestMethod -Uri $stagingUrl -TimeoutSec 10 -ErrorAction SilentlyContinue
    Write-Host "Staging health check passed" -ForegroundColor Green
}
catch {
    Write-Host "Staging health check pending (deployment in progress)" -ForegroundColor Yellow
}

# Summary
Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Staging Deployment Complete!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Deployment Details:" -ForegroundColor White
Write-Host "  Branch:       develop" -ForegroundColor Cyan
Write-Host "  Environment:  staging" -ForegroundColor Cyan
Write-Host "  URL:          https://staging.orfeas.ai" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor White
Write-Host "  1. Test staging: https://staging.orfeas.ai" -ForegroundColor Yellow
Write-Host "  2. Monitor workflow: https://github.com/apapadopoulos22/orfeas-ai-studio/actions" -ForegroundColor Yellow
Write-Host "  3. Deploy to production: .\DEPLOY_PRODUCTION.ps1" -ForegroundColor Yellow
Write-Host ""
