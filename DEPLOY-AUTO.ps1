#!/usr/bin/env pwsh
# ORFEAS AI - Automatic Netlify Deployment
# PowerShell version for better compatibility

param(
    [switch]$NoPrompt = $false
)

Write-Host "`n╔════════════════════════════════════════════════════════════════╗"
Write-Host "║                                                                ║"
Write-Host "║      ORFEAS AI - AUTOMATIC NETLIFY DEPLOYMENT                 ║"
Write-Host "║                                                                ║"
Write-Host "╚════════════════════════════════════════════════════════════════╝`n" -ForegroundColor Green

# Step 1: Check prerequisites
Write-Host "[STEP 1 of 6] Checking prerequisites..." -ForegroundColor Yellow

try {
    $pythonVersion = python --version 2>&1
    Write-Host "  ✅ Python: $pythonVersion"
} catch {
    Write-Host "  ❌ Python not found" -ForegroundColor Red
    exit 1
}

try {
    $nodeVersion = node --version 2>&1
    Write-Host "  ✅ Node.js: $nodeVersion"
} catch {
    Write-Host "  ❌ Node.js not found" -ForegroundColor Red
    exit 1
}

try {
    $ngrokVersion = ngrok --version 2>&1
    Write-Host "  ✅ ngrok installed"
} catch {
    Write-Host "  ⚠️  ngrok not found - install from https://ngrok.com" -ForegroundColor Yellow
}

Write-Host ""

# Step 2: Start backend
Write-Host "[STEP 2 of 6] Starting backend service..." -ForegroundColor Yellow
Write-Host "  Opening new terminal for backend..."

Push-Location "c:\Users\johng\Documents\oscar\backend"
Start-Process -FilePath "cmd" -ArgumentList "/k python -u main.py" -WindowStyle Normal
Pop-Location

Write-Host "  ✅ Backend started (Terminal 1)"
Start-Sleep -Seconds 3
Write-Host ""

# Step 3: Start ngrok
Write-Host "[STEP 3 of 6] Starting ngrok tunnel..." -ForegroundColor Yellow
Write-Host "  Opening new terminal for ngrok..."

$ngrokPath = "c:\Users\johng\Documents\oscar\START_NGROK_TUNNEL.bat"
Start-Process -FilePath "cmd" -ArgumentList "/k $ngrokPath" -WindowStyle Normal

Write-Host "  ✅ ngrok started (Terminal 2)"
Start-Sleep -Seconds 3
Write-Host ""

# Step 4: Get ngrok URL
Write-Host "[STEP 4 of 6] Retrieving ngrok URL..." -ForegroundColor Yellow

$ngrokUrl = ""
$attempts = 0
while ([string]::IsNullOrEmpty($ngrokUrl) -and $attempts -lt 5) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:4040/api/tunnels" -UseBasicParsing
        $tunnels = $response.Content | ConvertFrom-Json
        $ngrokUrl = $tunnels.tunnels[0].public_url
        Write-Host "  ✅ ngrok URL retrieved: $ngrokUrl"
    } catch {
        $attempts++
        if ($attempts -lt 5) {
            Write-Host "  ⏳ Waiting for ngrok tunnel to establish... ($attempts/5)"
            Start-Sleep -Seconds 2
        }
    }
}

if ([string]::IsNullOrEmpty($ngrokUrl)) {
    Write-Host "  ⚠️  Could not auto-retrieve ngrok URL" -ForegroundColor Yellow
    $ngrokUrl = Read-Host "  Enter ngrok URL manually (https://xxxx-xxxx-xxxx.ngrok.io)"
}

if ([string]::IsNullOrEmpty($ngrokUrl)) {
    Write-Host "  ❌ ngrok URL is required" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Step 5: Update configuration
Write-Host "[STEP 5 of 6] Updating configuration..." -ForegroundColor Yellow

Push-Location "c:\Users\johng\Documents\oscar"

# Update netlify.toml
Write-Host "  Updating netlify.toml..."
$netlifyContent = Get-Content "netlify.toml" -Raw
$netlifyContent = $netlifyContent -replace "YOUR_NGROK_URL_HERE", $ngrokUrl
Set-Content "netlify.toml" $netlifyContent
Write-Host "    ✅ netlify.toml updated"

# Update frontend
Write-Host "  Updating frontend configuration..."
$htmlFile = "synexa-style-studio.html"
$frontendContent = Get-Content $htmlFile -Raw
$frontendContent = $frontendContent -replace 'const API_BASE = .*?;', "const API_BASE = `"$ngrokUrl`";"
Set-Content $htmlFile $frontendContent
Write-Host "    ✅ Frontend updated"

Write-Host "  ✅ Configuration complete"
Write-Host ""

# Step 6: Deploy to Netlify
Write-Host "[STEP 6 of 6] Deploying to Netlify..." -ForegroundColor Yellow

# Initialize git if needed
if (-not (Test-Path ".git")) {
    Write-Host "  Initializing git repository..."
    git init | Out-Null
}

# Configure git
git config user.email "deploy@orfeas.local" 2>$null
git config user.name "ORFEAS Deploy" 2>$null

# Add files
Write-Host "  Adding files to git..."
git add . 2>$null

# Commit
Write-Host "  Committing changes..."
git commit -m "ORFEAS AI - Automatic Netlify deployment $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" 2>$null

# Deploy
Write-Host "  Starting Netlify deployment..."
Write-Host "  (This may take 2-5 minutes)" -ForegroundColor Cyan

netlify deploy --prod

Pop-Location

Write-Host "`n"
Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║                                                                ║" -ForegroundColor Green
Write-Host "║           ✅ DEPLOYMENT COMPLETE!                            ║" -ForegroundColor Green
Write-Host "║                                                                ║" -ForegroundColor Green
Write-Host "║     Your ORFEAS AI Studio is now LIVE globally!              ║" -ForegroundColor Green
Write-Host "║                                                                ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Green

Write-Host "`n"
Write-Host "NEXT STEPS:" -ForegroundColor Cyan
Write-Host "  1. Keep backend and ngrok terminals open"
Write-Host "  2. Check output above for your Netlify URL"
Write-Host "  3. Open the URL in browser (https://your-app.netlify.app)"
Write-Host "  4. Test: Upload image → Generate 3D → Download"
Write-Host "  5. Press F12 to check console for [CONFIG] API_BASE message"
Write-Host ""
Write-Host "MONITORING:" -ForegroundColor Cyan
Write-Host "  GPU:       nvidia-smi"
Write-Host "  Logs:      backend/logs/backend_requests.log"
Write-Host "  Requests:  http://localhost:4040 (ngrok dashboard)"
Write-Host ""
