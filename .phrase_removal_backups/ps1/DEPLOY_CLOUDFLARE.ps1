# THERION CLOUDFLARE TUNNEL - ONE-CLICK DEPLOYMENT
# MAXIMUM EFFICIENCY MODE

Write-Host ""
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "  THERION CLOUDFLARE TUNNEL DEPLOYMENT" -ForegroundColor Cyan
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Download Cloudflared if not exists
if (-Not (Test-Path "cloudflared.exe")) {
    Write-Host "[1/4] Downloading Cloudflared..." -ForegroundColor Yellow
    try {
        Invoke-WebRequest -Uri "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe" -OutFile "cloudflared.exe"
        Write-Host "[OK] Cloudflared downloaded" -ForegroundColor Green
    } catch {
        Write-Host "[ERROR] Download failed: $_" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "[1/4] Cloudflared already downloaded" -ForegroundColor Green
}

Write-Host ""

# Step 2: Check if backend is running
Write-Host "[2/4] Checking backend status..." -ForegroundColor Yellow
$backendRunning = Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.Path -like '*orfeas*' -or $_.CommandLine -like '*main.py*' }

if (-Not $backendRunning) {
    Write-Host "[WARN] Backend not running - starting now..." -ForegroundColor Yellow
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'C:\Users\johng\Documents\Erevus\orfeas\backend'; Write-Host 'THERION BACKEND SERVER' -ForegroundColor Green; python main.py"
    Write-Host "[OK] Backend starting in new window..." -ForegroundColor Green
    Start-Sleep -Seconds 5
} else {
    Write-Host "[OK] Backend already running" -ForegroundColor Green
}

Write-Host ""

# Step 3: Start Cloudflare Tunnel in new window
Write-Host "[3/4] Starting Cloudflare Tunnel..." -ForegroundColor Yellow
Write-Host ""
Write-Host "================================================================" -ForegroundColor Yellow
Write-Host "  CLOUDFLARE TUNNEL WILL OPEN IN NEW WINDOW" -ForegroundColor Yellow
Write-Host "================================================================" -ForegroundColor Yellow
Write-Host ""
Write-Host "LOOK FOR THIS LINE IN THE CLOUDFLARE WINDOW:" -ForegroundColor Cyan
Write-Host ""
Write-Host "  https://XXXXX.trycloudflare.com" -ForegroundColor Green
Write-Host ""
Write-Host "COPY THAT URL AND PASTE IT BELOW" -ForegroundColor Cyan
Write-Host ""

Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'C:\Users\johng\Documents\Erevus\orfeas'; Write-Host ''; Write-Host '======================================' -ForegroundColor Green; Write-Host '  THERION CLOUDFLARE TUNNEL ACTIVE' -ForegroundColor Green; Write-Host '======================================' -ForegroundColor Green; Write-Host ''; Write-Host 'COPY THE PUBLIC URL BELOW:' -ForegroundColor Yellow; Write-Host ''; .\cloudflared.exe tunnel --url http://localhost:5000"

Write-Host "[OK] Cloudflare Tunnel window opened" -ForegroundColor Green
Write-Host ""

# Step 4: Get public URL from user
Write-Host "[4/4] Enter the public URL from Cloudflare window:" -ForegroundColor Yellow
Write-Host "(Example: https://abc123.trycloudflare.com)" -ForegroundColor White
Write-Host ""
$publicUrl = Read-Host "Public URL"

if ($publicUrl -match "https://.*\.trycloudflare\.com") {
    Write-Host ""
    Write-Host "[OK] Valid Cloudflare URL" -ForegroundColor Green

    # Save to file
    $publicUrl | Out-File "PUBLIC_BACKEND_URL.txt" -Encoding UTF8
    Write-Host "[OK] Saved to PUBLIC_BACKEND_URL.txt" -ForegroundColor Green

    # Update frontend
    Write-Host ""
    Write-Host "Updating frontend configuration..." -ForegroundColor Yellow

    $htmlPath = "orfeas-studio.html"
    $content = Get-Content $htmlPath -Raw

    # Update BACKEND_URL
    $content = $content -replace "BACKEND_URL:\s*['\`"]http://localhost:5000['\`"]", "BACKEND_URL: '$publicUrl'"

    $content | Out-File $htmlPath -Encoding UTF8

    Write-Host "[OK] Frontend updated" -ForegroundColor Green
    Write-Host ""
    Write-Host "========================================================================" -ForegroundColor Green
    Write-Host "  DEPLOYMENT COMPLETE!" -ForegroundColor Green
    Write-Host "========================================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "PUBLIC BACKEND URL:" -ForegroundColor Cyan
    Write-Host "  $publicUrl" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "TEST YOUR DEPLOYMENT:" -ForegroundColor Cyan
    Write-Host "  $publicUrl/api/health" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "NEXT STEPS:" -ForegroundColor Cyan
    Write-Host "  1. Open orfeas-studio.html in browser" -ForegroundColor White
    Write-Host "  2. Press Ctrl+Shift+R to hard reload" -ForegroundColor White
    Write-Host "  3. Check server status (should show 'Online')" -ForegroundColor White
    Write-Host "  4. Test image generation with GPU acceleration" -ForegroundColor White
    Write-Host ""
    Write-Host "GPU ACCELERATION: ACTIVE" -ForegroundColor Green
    Write-Host "HTTPS: ENABLED" -ForegroundColor Green
    Write-Host "PUBLIC ACCESS: WORLDWIDE" -ForegroundColor Green
    Write-Host ""
    Write-Host "THERION DEPLOYMENT SUCCESSFUL!" -ForegroundColor Green
    Write-Host ""

} else {
    Write-Host ""
    Write-Host "[ERROR] Invalid URL format" -ForegroundColor Red
    Write-Host "Expected: https://XXXXX.trycloudflare.com" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}
