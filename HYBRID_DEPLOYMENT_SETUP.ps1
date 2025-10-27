# ============================================================================
# HYBRID DEPLOYMENT QUICK START
# ============================================================================
# Frontend on Vercel + Backend on Local Machine
#
# This script helps you set up a hybrid deployment in 3 simple steps:
# 1. Deploy frontend to Vercel
# 2. Start backend locally
# 3. Test the connection
#
# Usage:
#   .\HYBRID_DEPLOYMENT_SETUP.ps1
# ============================================================================

Write-Host "`n" -ForegroundColor White
Write-Host "HYBRID DEPLOYMENT SETUP" -ForegroundColor Cyan
Write-Host "Frontend: Vercel | Backend: Local Machine" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host "`n"

# Step 1: Frontend Deployment
Write-Host "STEP 1: Deploy Frontend to Vercel" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray

$deployFrontend = Read-Host "Deploy frontend to Vercel now? (y/n)"

if ($deployFrontend -eq "y" -or $deployFrontend -eq "Y") {
    Write-Host "Running Vercel deployment..." -ForegroundColor Cyan
    if (Test-Path ".\DEPLOY_TO_VERCEL.ps1") {
        .\DEPLOY_TO_VERCEL.ps1
    }
    else {
        Write-Host "Note: DEPLOY_TO_VERCEL.ps1 not found. Please deploy manually." -ForegroundColor Yellow
    }
    $frontendUrl = Read-Host "Enter your Vercel frontend URL (e.g., https://orfeas-ai-studio.vercel.app)"
    Write-Host "Frontend deployed to: $frontendUrl" -ForegroundColor Green
}
else {
    Write-Host "Skipping frontend deployment" -ForegroundColor Yellow
    $frontendUrl = Read-Host "Enter your Vercel frontend URL"
}

Write-Host "`n"

# Step 2: Backend Configuration
Write-Host "STEP 2: Configure Backend" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host ""
Write-Host "Backend access options:" -ForegroundColor White
Write-Host "  1. Local only (localhost:5000)" -ForegroundColor Gray
Write-Host "  2. Remote via ngrok" -ForegroundColor Gray
Write-Host ""
$backendOption = Read-Host "Enter your choice (1 or 2)"

if ($backendOption -eq "2") {
    Write-Host "You will need ngrok to expose your local backend" -ForegroundColor Yellow
    $hasNgrok = Read-Host "Do you have ngrok installed? (y/n)"

    if ($hasNgrok -ne "y" -and $hasNgrok -ne "Y") {
        Write-Host "Install ngrok from: https://ngrok.com/download" -ForegroundColor Cyan
        Write-Host "Then run: ngrok http 5000" -ForegroundColor Green
    }

    $backendUrl = Read-Host "Enter your ngrok URL (e.g., https://abc123.ngrok.io)"
}
else {
    $backendUrl = "http://localhost:5000"
    Write-Host "Backend URL set to: http://localhost:5000" -ForegroundColor Green
}

Write-Host "`n"

# Step 3: Create Configuration File
Write-Host "STEP 3: Create Configuration File" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray

Write-Host "Creating configuration file..." -ForegroundColor Cyan

$wsUrl = $backendUrl.Replace("https://", "wss://").Replace("http://", "ws://")

$configContent = @"
{
  "frontendUrl": "$frontendUrl",
  "backendUrl": "$backendUrl",
  "apiBase": "$backendUrl/api",
  "healthEndpoint": "$backendUrl/health",
  "wsUrl": "$wsUrl",
  "deploymentType": "hybrid",
  "timestamp": "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
}
"@

$configContent | Out-File -FilePath "hybrid_config.json" -Encoding UTF8 -Force
Write-Host "Configuration saved to: hybrid_config.json" -ForegroundColor Green
Write-Host "`n"

# Step 4: Display Instructions
Write-Host "STEP 4: Next Steps" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray

Write-Host "`nUPDATE YOUR HTML FILES:" -ForegroundColor Cyan
Write-Host "Edit these files and add the backend URL:" -ForegroundColor White
Write-Host "  - orfeas-ai-studio.html" -ForegroundColor Gray
Write-Host "  - babylon-viewer.html" -ForegroundColor Gray
Write-Host "  - camera-studio.html" -ForegroundColor Gray
Write-Host "  - batch-studio.html" -ForegroundColor Gray

Write-Host "`nAdd this script block in the <head> section:" -ForegroundColor White
Write-Host ""
Write-Host "  <script>" -ForegroundColor Green
Write-Host "    const BACKEND_URL = '$backendUrl';" -ForegroundColor Green
Write-Host "    const API_BASE = BACKEND_URL + '/api';" -ForegroundColor Green
Write-Host "    const WS_URL = '$wsUrl';" -ForegroundColor Green
Write-Host "    console.log('Backend configured:', BACKEND_URL);" -ForegroundColor Green
Write-Host "  </script>" -ForegroundColor Green
Write-Host ""

Write-Host "START BACKEND LOCALLY:" -ForegroundColor Cyan
Write-Host "Open a new PowerShell terminal and run:" -ForegroundColor White
Write-Host ""
Write-Host "  cd backend" -ForegroundColor Green
Write-Host "  python main.py" -ForegroundColor Green
Write-Host ""
Write-Host "Keep this terminal window open while working!" -ForegroundColor Yellow

Write-Host "`nDEPLOY UPDATED FRONTEND:" -ForegroundColor Cyan
Write-Host "After updating HTML files:" -ForegroundColor White
Write-Host ""
Write-Host "  git add ." -ForegroundColor Green
Write-Host "  git commit -m 'Configure for hybrid deployment'" -ForegroundColor Green
Write-Host "  git push origin main" -ForegroundColor Green
Write-Host ""
Write-Host "Vercel will auto-deploy in 1-2 minutes" -ForegroundColor Gray

Write-Host "`nVERIFY SETUP:" -ForegroundColor Cyan
Write-Host "1. Check frontend loads:" -ForegroundColor White
Write-Host "   Visit: $frontendUrl" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Check backend responds:" -ForegroundColor White
Write-Host "   Run: curl $backendUrl/health" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Check browser console for errors:" -ForegroundColor White
Write-Host "   Press F12 in browser, check Console tab" -ForegroundColor Gray
Write-Host ""
Write-Host "4. Check Network tab for API calls:" -ForegroundColor White
Write-Host "   API calls should go to: $backendUrl/api" -ForegroundColor Gray
Write-Host ""

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "CONFIGURATION COMPLETE!" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "`n"

Write-Host "Configuration Summary:" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Get-Content hybrid_config.json
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host "`n"

Write-Host "For more details, see: HYBRID_DEPLOYMENT_GUIDE.md" -ForegroundColor Cyan
Write-Host "`n"
