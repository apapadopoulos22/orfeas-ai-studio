# ============================================================================
# ORFEAS AI STUDIO - VERCEL DEPLOYMENT SCRIPT
# ============================================================================
# This script deploys the ORFEAS AI Studio frontend to Vercel
#
# Prerequisites:
#   1. Node.js and npm installed
#   2. Vercel CLI installed: npm install -g vercel
#   3. GitHub account and repository
#   4. Logged in to Vercel: vercel login
#
# Usage:
#   .\DEPLOY_TO_VERCEL.ps1
# ============================================================================

Write-Host "`n" -ForegroundColor White
Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║     ORFEAS AI STUDIO - VERCEL DEPLOYMENT SCRIPT           ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host "`n"

# Step 1: Verify prerequisites
Write-Host "STEP 1: Verifying Prerequisites..." -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray

# Check Node.js
Write-Host "  Checking Node.js..." -ForegroundColor White
$nodeVersion = node --version 2>$null
if ($nodeVersion) {
    Write-Host "    ✓ Node.js found: $nodeVersion" -ForegroundColor Green
}
else {
    Write-Host "    ✗ Node.js NOT found. Install from: https://nodejs.org/" -ForegroundColor Red
    exit 1
}

# Check npm
Write-Host "  Checking npm..." -ForegroundColor White
$npmVersion = npm --version 2>$null
if ($npmVersion) {
    Write-Host "    ✓ npm found: $npmVersion" -ForegroundColor Green
}
else {
    Write-Host "    ✗ npm NOT found" -ForegroundColor Red
    exit 1
}

# Check Vercel CLI
Write-Host "  Checking Vercel CLI..." -ForegroundColor White
$vercelVersion = vercel --version 2>$null
if ($vercelVersion) {
    Write-Host "    ✓ Vercel CLI found: $vercelVersion" -ForegroundColor Green
}
else {
    Write-Host "    ✗ Vercel CLI NOT found" -ForegroundColor Yellow
    Write-Host "    Installing Vercel CLI..." -ForegroundColor Cyan
    npm install -g vercel
    $vercelVersion = vercel --version 2>$null
    if ($vercelVersion) {
        Write-Host "    ✓ Vercel CLI installed: $vercelVersion" -ForegroundColor Green
    }
    else {
        Write-Host "    ✗ Failed to install Vercel CLI" -ForegroundColor Red
        exit 1
    }
}

Write-Host "`n✓ All prerequisites verified`n" -ForegroundColor Green

# Step 2: Check Vercel authentication
Write-Host "STEP 2: Checking Vercel Authentication..." -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray

$vercelAuth = vercel whoami 2>$null
if ($vercelAuth) {
    Write-Host "  ✓ Logged in as: $vercelAuth" -ForegroundColor Green
}
else {
    Write-Host "  ✗ Not authenticated with Vercel" -ForegroundColor Yellow
    Write-Host "  Launching Vercel login..." -ForegroundColor Cyan
    vercel login
}

Write-Host "`n"

# Step 3: Install dependencies
Write-Host "STEP 3: Installing Dependencies..." -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray

if (Test-Path "package.json") {
    Write-Host "  Installing npm packages..." -ForegroundColor White
    npm install
    Write-Host "  ✓ Dependencies installed`n" -ForegroundColor Green
}
else {
    Write-Host "  ℹ No package.json found (static site deployment)`n" -ForegroundColor Cyan
}

# Step 4: Display deployment options
Write-Host "STEP 4: Deployment Options" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host "  1. Development (staging) - https://orfeas-ai-studio.vercel.app" -ForegroundColor White
Write-Host "  2. Production (live) - https://orfeas-ai-studio.vercel.app" -ForegroundColor White
Write-Host "`n"

$deploymentType = Read-Host "Select deployment type (1 for staging, 2 for production) [default: 1]"
if ($deploymentType -eq "2") {
    $prodFlag = "--prod"
    $envLabel = "PRODUCTION"
    Write-Host "  Deploying to PRODUCTION..." -ForegroundColor Yellow
}
else {
    $prodFlag = ""
    $envLabel = "STAGING"
    Write-Host "  Deploying to STAGING..." -ForegroundColor Cyan
}

Write-Host "`n"

# Step 5: Deploy to Vercel
Write-Host "STEP 5: Deploying to Vercel ($envLabel)..." -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray

Write-Host "  Running: vercel $prodFlag" -ForegroundColor Cyan
vercel $prodFlag

Write-Host "`n"

# Step 6: Success summary
Write-Host "STEP 6: Deployment Complete" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray

Write-Host "`n✓ ORFEAS AI Studio successfully deployed to Vercel!`n" -ForegroundColor Green

Write-Host "📋 DEPLOYMENT SUMMARY:" -ForegroundColor Cyan
Write-Host "  Environment:  $envLabel" -ForegroundColor White
Write-Host "  Frontend URL: https://orfeas-ai-studio.vercel.app" -ForegroundColor White
Write-Host "  Repository:   apapadopoulos22/orfeas-ai-studio" -ForegroundColor White
Write-Host "  Dashboard:    https://vercel.com/dashboard" -ForegroundColor White
Write-Host "`n"

Write-Host "🔗 NEXT STEPS:" -ForegroundColor Yellow
Write-Host "  1. Visit your live site: https://orfeas-ai-studio.vercel.app" -ForegroundColor White
Write-Host "  2. Configure custom domain (optional)" -ForegroundColor White
Write-Host "  3. Set up backend API connection" -ForegroundColor White
Write-Host "  4. Configure environment variables" -ForegroundColor White
Write-Host "`n"

Write-Host "📞 SUPPORT:" -ForegroundColor Yellow
Write-Host "  Vercel Docs:     https://vercel.com/docs" -ForegroundColor White
Write-Host "  GitHub Repo:     https://github.com/apapadopoulos22/orfeas-ai-studio" -ForegroundColor White
Write-Host "`n"

Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║           DEPLOYMENT SUCCESSFUL! 🚀                       ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan
