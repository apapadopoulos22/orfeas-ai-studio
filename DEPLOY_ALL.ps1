# ORFEAS AI - Complete Deployment Pipeline
# Runs all deployment phases: Local Test → Staging → Production

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "ORFEAS AI - Full Deployment Pipeline" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
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
    Write-Host "✗ Deployment cancelled" -ForegroundColor Red
    exit 0
}

# Phase 1: Local Testing
Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Phase 1: Local Testing" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

& .\DEPLOY_TEST_LOCAL.ps1
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Local testing failed" -ForegroundColor Red
    Write-Host "Fix issues before deploying to staging" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "✓ Phase 1 Complete: Local tests passed" -ForegroundColor Green
Write-Host ""
Write-Host "Proceed to staging deployment? (y/n)" -ForegroundColor Yellow
$continue = Read-Host
if ($continue -ne "y") {
    Write-Host "Deployment stopped after local testing" -ForegroundColor Yellow
    exit 0
}

# Stop local backend before deploying
Write-Host "Stopping local backend..." -ForegroundColor Yellow
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

# Phase 2: Staging Deployment
Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Phase 2: Staging Deployment" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

& .\DEPLOY_STAGING.ps1
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Staging deployment failed" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "✓ Phase 2 Complete: Staging deployed" -ForegroundColor Green
Write-Host ""
Write-Host "Test staging thoroughly before production deployment!" -ForegroundColor Yellow
Write-Host "Staging URL: https://staging.orfeas.ai" -ForegroundColor Cyan
Write-Host ""
Write-Host "Proceed to production deployment? (yes/no)" -ForegroundColor Red
$continue = Read-Host
if ($continue -ne "yes") {
    Write-Host "Deployment stopped after staging" -ForegroundColor Yellow
    exit 0
}

# Phase 3: Production Deployment
Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Phase 3: Production Deployment" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

& .\DEPLOY_PRODUCTION.ps1
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Production deployment failed" -ForegroundColor Red
    exit 1
}

# Final Summary
Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "🎉 Complete Deployment Success! 🎉" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "All phases completed:" -ForegroundColor White
Write-Host "  ✓ Local testing" -ForegroundColor Green
Write-Host "  ✓ Staging deployment" -ForegroundColor Green
Write-Host "  ✓ Production deployment" -ForegroundColor Green
Write-Host ""
Write-Host "Environments:" -ForegroundColor White
Write-Host "  • Staging:    https://staging.orfeas.ai" -ForegroundColor Cyan
Write-Host "  • Production: https://orfeas.ai" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor White
Write-Host "  1. Monitor production metrics" -ForegroundColor Yellow
Write-Host "  2. Watch error rates and response times" -ForegroundColor Yellow
Write-Host "  3. Gather user feedback" -ForegroundColor Yellow
Write-Host ""
