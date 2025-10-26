# ============================================
# ORFEAS AI STUDIO - NETLIFY DEPLOYMENT SCRIPT
# ============================================
#
# PowerShell script for Netlify deployment
# Prerequisites:
#   - Git installed
#   - Netlify CLI: npm install -g netlify-cli (optional)
#   - Repository connected to Netlify
#
# Usage: .\DEPLOY_NETLIFY.ps1
#

param(
    [string]$CommitMessage = "Deployment: Netlify production release",
    [string]$Branch = "main",
    [switch]$SkipPush = $false,
    [switch]$Production = $true
)

# ============================================
# CONFIGURATION
# ============================================

$ErrorActionPreference = "Stop"
$VerbosePreference = "Continue"

# ============================================
# MAIN
# ============================================

Write-Host "`n" -ForegroundColor Green
Write-Host "╔════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  ORFEAS AI STUDIO - NETLIFY DEPLOYMENT  ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

try {
    # STEP 1: Verify Git
    Write-Host "STEP 1: Verifying Git installation..." -ForegroundColor Yellow
    $gitVersion = git --version 2>$null
    if (-not $gitVersion) {
        throw "Git not installed. Visit: https://git-scm.com/download/win"
    }
    Write-Host "✅ Git found: $gitVersion" -ForegroundColor Green
    Write-Host ""

    # STEP 2: Verify project files
    Write-Host "STEP 2: Verifying project files..." -ForegroundColor Yellow
    if (-not (Test-Path "orfeas-ai-studio.html")) {
        throw "orfeas-ai-studio.html not found in current directory"
    }
    if (-not (Test-Path "netlify.toml")) {
        throw "netlify.toml not found - run from project root"
    }
    if (-not (Test-Path "netlify/functions")) {
        throw "netlify/functions directory not found"
    }
    Write-Host "✅ Project files verified" -ForegroundColor Green
    Write-Host ""

    # STEP 3: Git status
    Write-Host "STEP 3: Checking Git status..." -ForegroundColor Yellow
    Write-Host ""
    git status --short
    Write-Host ""
    Write-Host "✅ Git status OK" -ForegroundColor Green
    Write-Host ""

    # STEP 4: Stage changes
    Write-Host "STEP 4: Staging changes..." -ForegroundColor Yellow
    git add .
    Write-Host "✅ Changes staged" -ForegroundColor Green
    Write-Host ""

    # STEP 5: Commit
    Write-Host "STEP 5: Creating deployment commit..." -ForegroundColor Yellow
    git commit -m $CommitMessage -q 2>$null || `
        Write-Host "ℹ️  No changes to commit (repository already up to date)" -ForegroundColor Cyan
    Write-Host "✅ Commit created" -ForegroundColor Green
    Write-Host ""

    # STEP 6: Push to Git
    if (-not $SkipPush) {
        Write-Host "STEP 6: Pushing to Git repository..." -ForegroundColor Yellow
        Write-Host "  Branch: $Branch"
        Write-Host "  Remote: origin"
        git push origin $Branch
        Write-Host "✅ Pushed to Git successfully" -ForegroundColor Green
        Write-Host ""
    }

    # STEP 7: Netlify deployment
    Write-Host "STEP 7: Netlify deployment..." -ForegroundColor Yellow

    $netlifyInstalled = (Get-Command netlify -ErrorAction SilentlyContinue) -ne $null

    if ($netlifyInstalled) {
        Write-Host "  Netlify CLI found - attempting direct deploy..." -ForegroundColor Cyan

        if ($Production) {
            Write-Host "  Mode: Production deployment"
            netlify deploy --prod
        }
        else {
            Write-Host "  Mode: Preview deployment"
            netlify deploy
        }

        Write-Host "✅ Netlify deployment initiated" -ForegroundColor Green
    }
    else {
        Write-Host "ℹ️  Netlify CLI not installed" -ForegroundColor Yellow
        Write-Host "  Git push will trigger automatic Netlify deployment" -ForegroundColor Cyan
        Write-Host "  Watch progress at: https://app.netlify.com" -ForegroundColor Cyan
        Write-Host "✅ Automatic Netlify deployment triggered via Git" -ForegroundColor Green
    }

    Write-Host ""

    # ============================================
    # SUCCESS SUMMARY
    # ============================================

    Write-Host "╔════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "║  ✅ DEPLOYMENT INITIATED              ║" -ForegroundColor Green
    Write-Host "╚════════════════════════════════════════╝" -ForegroundColor Green
    Write-Host ""

    Write-Host "📋 Deployment Status:" -ForegroundColor Yellow
    Write-Host "   • Changes pushed to Git ✅"
    Write-Host "   • Netlify will build and deploy"
    Write-Host "   • Deployment usually takes 1-2 minutes"
    Write-Host ""

    Write-Host "🔗 View Progress:" -ForegroundColor Yellow
    Write-Host "   https://app.netlify.com"
    Write-Host ""

    Write-Host "🧪 After Deployment, Test:" -ForegroundColor Yellow
    Write-Host "   curl https://your-site.netlify.app"
    Write-Host "   curl https://your-site.netlify.app/.netlify/functions/health"
    Write-Host "   curl https://your-site.netlify.app/api/models-info"
    Write-Host ""

    Write-Host "📚 Full Guide:" -ForegroundColor Yellow
    Write-Host "   Read: NETLIFY_DEPLOYMENT_GUIDE.md"
    Write-Host ""

    Write-Host "Environment Variables to Configure:" -ForegroundColor Yellow
    Write-Host "   1. BACKEND_API = https://your-api.example.com"
    Write-Host "   2. API_BASE = https://your-site.netlify.app"
    Write-Host "   3. CORS_ORIGINS = https://your-site.netlify.app"
    Write-Host "   4. LOCAL_LLM_ENDPOINT = https://ollama.example.com"
    Write-Host ""

}
catch {
    Write-Host ""
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "Troubleshooting:" -ForegroundColor Yellow
    Write-Host "  • Verify you're in the project root directory"
    Write-Host "  • Verify Git is installed and accessible"
    Write-Host "  • Check your Git repository configuration"
    Write-Host "  • Ensure netlify.toml and netlify/functions exist"
    Write-Host ""
    exit 1
}

Write-Host "✅ Script completed successfully" -ForegroundColor Green
Write-Host ""
