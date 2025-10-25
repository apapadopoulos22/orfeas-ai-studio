# ORFEAS AI - Production Deployment Script
# Automated blue-green deployment to production

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "ORFEAS AI - Production Deployment" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

$ErrorActionPreference = "Stop"

# Safety confirmation
Write-Host "⚠⚠⚠ PRODUCTION DEPLOYMENT ⚠⚠⚠" -ForegroundColor Red
Write-Host ""
Write-Host "This will deploy to production using blue-green strategy." -ForegroundColor Yellow
Write-Host "Are you sure you want to continue? (yes/no)" -ForegroundColor Yellow
$confirmation = Read-Host
if ($confirmation -ne "yes") {
    Write-Host "✗ Deployment cancelled" -ForegroundColor Red
    exit 0
}

# Step 1: Check git status
Write-Host "[1/9] Checking git status..." -ForegroundColor Yellow
$gitStatus = git status --porcelain
if ($gitStatus) {
    Write-Host "✗ Uncommitted changes detected - commit first!" -ForegroundColor Red
    git status --short
    exit 1
}
else {
    Write-Host "✓ Working directory clean" -ForegroundColor Green
}

# Step 2: Verify we're on main branch
Write-Host "[2/9] Verifying branch..." -ForegroundColor Yellow
$currentBranch = git branch --show-current
if ($currentBranch -ne "main") {
    Write-Host "⚠ Current branch: $currentBranch" -ForegroundColor Yellow
    Write-Host "Switch to main branch? (y/n)" -ForegroundColor Yellow
    $switch = Read-Host
    if ($switch -eq "y") {
        git checkout main
        Write-Host "✓ Switched to main branch" -ForegroundColor Green
    }
    else {
        Write-Host "✗ Must be on main branch for production deployment" -ForegroundColor Red
        exit 1
    }
}
else {
    Write-Host "✓ On main branch" -ForegroundColor Green
}

# Step 3: Pull latest changes
Write-Host "[3/9] Pulling latest changes..." -ForegroundColor Yellow
git pull origin main
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Latest changes pulled" -ForegroundColor Green
}
else {
    Write-Host "✗ Failed to pull changes" -ForegroundColor Red
    exit 1
}

# Step 4: Check if develop should be merged
Write-Host "[4/9] Checking develop branch..." -ForegroundColor Yellow
$developCommits = git log main..develop --oneline
if ($developCommits) {
    Write-Host "⚠ Develop branch has commits not in main:" -ForegroundColor Yellow
    Write-Host $developCommits
    Write-Host ""
    Write-Host "Merge develop into main? (y/n)" -ForegroundColor Yellow
    $merge = Read-Host
    if ($merge -eq "y") {
        git merge develop -m "Merge develop into main for production deployment"
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ Merged develop into main" -ForegroundColor Green
        }
        else {
            Write-Host "✗ Merge failed - resolve conflicts first" -ForegroundColor Red
            exit 1
        }
    }
}
else {
    Write-Host "✓ Main is up to date with develop" -ForegroundColor Green
}

# Step 5: Run all tests
Write-Host "[5/9] Running full test suite..." -ForegroundColor Yellow
pytest tests/ --tb=short -q
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ All tests passed" -ForegroundColor Green
}
else {
    Write-Host "✗ Tests failed" -ForegroundColor Red
    Write-Host "Deploy to production anyway? (yes/no)" -ForegroundColor Red
    $continue = Read-Host
    if ($continue -ne "yes") {
        exit 1
    }
}

# Step 6: Create git tag
Write-Host "[6/9] Creating git tag..." -ForegroundColor Yellow
$timestamp = Get-Date -Format "yyyy.MM.dd-HHmm"
$tagName = "v$timestamp"
Write-Host "Tag name: $tagName" -ForegroundColor Cyan
Write-Host "Enter release notes (optional):" -ForegroundColor Yellow
$releaseNotes = Read-Host
if ($releaseNotes) {
    git tag -a $tagName -m $releaseNotes
}
else {
    git tag -a $tagName -m "Production deployment $timestamp"
}
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Tag created: $tagName" -ForegroundColor Green
}
else {
    Write-Host "⚠ Failed to create tag (continuing)" -ForegroundColor Yellow
}

# Step 7: Push to main branch (triggers GitHub Actions)
Write-Host "[7/9] Pushing to main branch..." -ForegroundColor Yellow
Write-Host "This will trigger blue-green production deployment!" -ForegroundColor Red
Write-Host "Continue? (yes/no)" -ForegroundColor Yellow
$finalConfirm = Read-Host
if ($finalConfirm -ne "yes") {
    Write-Host "✗ Deployment cancelled" -ForegroundColor Red
    exit 0
}

git push origin main
git push origin $tagName
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Pushed to main" -ForegroundColor Green
}
else {
    Write-Host "✗ Failed to push" -ForegroundColor Red
    exit 1
}

# Step 8: Monitor GitHub Actions workflow
Write-Host "[8/9] Monitoring GitHub Actions workflow..." -ForegroundColor Yellow
Write-Host "Opening GitHub Actions in browser..." -ForegroundColor Cyan
Start-Process "https://github.com/apapadopoulos22/orfeas-ai-studio/actions"

Write-Host ""
Write-Host "Waiting for workflow to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Try to use gh CLI to watch the workflow
$ghInstalled = Get-Command gh -ErrorAction SilentlyContinue
if ($ghInstalled) {
    Write-Host "Watching workflow with gh CLI..." -ForegroundColor Cyan
    Write-Host "(This will show progress of blue-green deployment)" -ForegroundColor Yellow
    gh run watch
}
else {
    Write-Host "⚠ GitHub CLI (gh) not installed" -ForegroundColor Yellow
    Write-Host "Install: winget install GitHub.cli" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Manually check: https://github.com/apapadopoulos22/orfeas-ai-studio/actions" -ForegroundColor Cyan
}

# Step 9: Verify production deployment
Write-Host "[9/9] Verifying production deployment..." -ForegroundColor Yellow
Write-Host "Waiting 60 seconds for blue-green deployment..." -ForegroundColor Yellow
Start-Sleep -Seconds 60

# Check production health endpoint
$productionUrl = "https://orfeas.ai/health"
Write-Host "Checking production health: $productionUrl" -ForegroundColor Cyan
try {
    $healthCheck = Invoke-RestMethod -Uri $productionUrl -TimeoutSec 10
    if ($healthCheck.status -eq "healthy") {
        Write-Host "✓ Production deployment successful!" -ForegroundColor Green
    }
    else {
        Write-Host "⚠ Production health check returned: $($healthCheck.status)" -ForegroundColor Yellow
    }
}
catch {
    Write-Host "⚠ Production health check failed" -ForegroundColor Yellow
    Write-Host "Check manually: $productionUrl" -ForegroundColor Cyan
}

# Summary
Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Production Deployment Complete!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Deployment Details:" -ForegroundColor White
Write-Host "  • Branch:      main" -ForegroundColor Cyan
Write-Host "  • Tag:         $tagName" -ForegroundColor Cyan
Write-Host "  • Environment: production" -ForegroundColor Cyan
Write-Host "  • Strategy:    blue-green" -ForegroundColor Cyan
Write-Host "  • URL:         https://orfeas.ai" -ForegroundColor Cyan
Write-Host ""
Write-Host "Post-Deployment Checklist:" -ForegroundColor White
Write-Host "  ☐ Verify production: https://orfeas.ai" -ForegroundColor Yellow
Write-Host "  ☐ Check metrics: https://grafana.orfeas.ai" -ForegroundColor Yellow
Write-Host "  ☐ Monitor logs: kubectl logs -n orfeas-production -l app=orfeas-backend" -ForegroundColor Yellow
Write-Host "  ☐ Watch error rate: <1% expected" -ForegroundColor Yellow
Write-Host "  ☐ Verify response times: <15s expected" -ForegroundColor Yellow
Write-Host ""
Write-Host "Rollback (if needed):" -ForegroundColor White
Write-Host "  kubectl rollout undo deployment/orfeas-backend-green -n orfeas-production" -ForegroundColor Red
Write-Host ""
Write-Host "🎉 Congratulations on the production deployment! 🎉" -ForegroundColor Green
Write-Host ""
