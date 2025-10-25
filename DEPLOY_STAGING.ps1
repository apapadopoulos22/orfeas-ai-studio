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
    Write-Host "⚠ Uncommitted changes detected:" -ForegroundColor Yellow
    git status --short
    Write-Host ""
    Write-Host "Commit changes before deploying? (y/n)" -ForegroundColor Yellow
    $commit = Read-Host
    if ($commit -eq "y") {
        Write-Host "Enter commit message:" -ForegroundColor Yellow
        $commitMsg = Read-Host
        git add .
        git commit -m $commitMsg
        Write-Host "✓ Changes committed" -ForegroundColor Green
    }
    else {
        Write-Host "✗ Deployment aborted" -ForegroundColor Red
        exit 1
    }
}
else {
    Write-Host "✓ Working directory clean" -ForegroundColor Green
}

# Step 2: Check current branch
Write-Host "[2/7] Checking current branch..." -ForegroundColor Yellow
$currentBranch = git branch --show-current
if ($currentBranch -ne "develop") {
    Write-Host "⚠ Current branch: $currentBranch" -ForegroundColor Yellow
    Write-Host "Switch to develop branch? (y/n)" -ForegroundColor Yellow
    $switch = Read-Host
    if ($switch -eq "y") {
        git checkout develop
        Write-Host "✓ Switched to develop branch" -ForegroundColor Green
    }
    else {
        Write-Host "✗ Deployment aborted" -ForegroundColor Red
        exit 1
    }
}
else {
    Write-Host "✓ On develop branch" -ForegroundColor Green
}

# Step 3: Pull latest changes
Write-Host "[3/7] Pulling latest changes..." -ForegroundColor Yellow
git pull origin develop
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Latest changes pulled" -ForegroundColor Green
}
else {
    Write-Host "✗ Failed to pull changes" -ForegroundColor Red
    exit 1
}

# Step 4: Run tests
Write-Host "[4/7] Running tests..." -ForegroundColor Yellow
pytest tests/ -m "not slow" --tb=short -q
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Tests passed" -ForegroundColor Green
}
else {
    Write-Host "✗ Tests failed" -ForegroundColor Red
    Write-Host "Deploy anyway? (y/n)" -ForegroundColor Yellow
    $continue = Read-Host
    if ($continue -ne "y") {
        exit 1
    }
}

# Step 5: Push to develop branch (triggers GitHub Actions)
Write-Host "[5/7] Pushing to develop branch..." -ForegroundColor Yellow
git push origin develop
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Pushed to develop" -ForegroundColor Green
}
else {
    Write-Host "✗ Failed to push" -ForegroundColor Red
    exit 1
}

# Step 6: Monitor GitHub Actions workflow
Write-Host "[6/7] Monitoring GitHub Actions workflow..." -ForegroundColor Yellow
Write-Host "Opening GitHub Actions in browser..." -ForegroundColor Cyan
Start-Process "https://github.com/apapadopoulos22/orfeas-ai-studio/actions"

Write-Host ""
Write-Host "Waiting for workflow to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Try to use gh CLI to watch the workflow
$ghInstalled = Get-Command gh -ErrorAction SilentlyContinue
if ($ghInstalled) {
    Write-Host "Watching workflow with gh CLI..." -ForegroundColor Cyan
    gh run watch
}
else {
    Write-Host "⚠ GitHub CLI (gh) not installed" -ForegroundColor Yellow
    Write-Host "Install: winget install GitHub.cli" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Manually check: https://github.com/apapadopoulos22/orfeas-ai-studio/actions" -ForegroundColor Cyan
}

# Step 7: Verify staging deployment
Write-Host "[7/7] Verifying staging deployment..." -ForegroundColor Yellow
Write-Host "Waiting 30 seconds for deployment to complete..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Check staging health endpoint
$stagingUrl = "https://staging.orfeas.ai/health"
Write-Host "Checking staging health: $stagingUrl" -ForegroundColor Cyan
try {
    $healthCheck = Invoke-RestMethod -Uri $stagingUrl -TimeoutSec 10
    if ($healthCheck.status -eq "healthy") {
        Write-Host "✓ Staging deployment successful!" -ForegroundColor Green
    }
    else {
        Write-Host "⚠ Staging health check returned: $($healthCheck.status)" -ForegroundColor Yellow
    }
}
catch {
    Write-Host "⚠ Staging health check failed (might still be deploying)" -ForegroundColor Yellow
    Write-Host "Check manually: $stagingUrl" -ForegroundColor Cyan
}

# Summary
Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Staging Deployment Complete!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Deployment Details:" -ForegroundColor White
Write-Host "  • Branch:    develop" -ForegroundColor Cyan
Write-Host "  • Environment: staging" -ForegroundColor Cyan
Write-Host "  • URL:       https://staging.orfeas.ai" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor White
Write-Host "  1. Test staging: https://staging.orfeas.ai" -ForegroundColor Yellow
Write-Host "  2. Check logs: kubectl logs -n orfeas-staging -l app=orfeas-backend" -ForegroundColor Yellow
Write-Host "  3. Monitor metrics: https://grafana.orfeas.ai" -ForegroundColor Yellow
Write-Host "  4. Deploy to prod: .\DEPLOY_PRODUCTION.ps1" -ForegroundColor Yellow
Write-Host ""
