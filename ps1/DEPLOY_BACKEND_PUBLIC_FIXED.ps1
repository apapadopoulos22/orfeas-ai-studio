# THERION BACKEND DEPLOYMENT - NGROK QUICK START
# ASCII-safe version for PowerShell compatibility

param(
    [Parameter(Mandatory=$false)]
    [string]$Method = "ngrok"
)

Write-Host ""
Write-Host "THERION BACKEND PUBLIC DEPLOYMENT" -ForegroundColor Cyan
Write-Host "Deploy ORFEAS AI Backend to Public Internet (HTTPS)" -ForegroundColor Cyan
Write-Host ""

# Check Backend Status
Write-Host "[STEP 1] Checking Backend Status..." -ForegroundColor Yellow
Write-Host ""

$backendRunning = $false
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5000/api/health" -Method GET -TimeoutSec 2 -ErrorAction Stop
    $backendRunning = $true
    Write-Host "[OK] Backend already running on port 5000" -ForegroundColor Green
} catch {
    Write-Host "[WARN] Backend not running - starting now..." -ForegroundColor Yellow
}

if (-not $backendRunning) {
    Write-Host ""
    Write-Host "[STARTING] ORFEAS Backend Server..." -ForegroundColor Cyan

    # Start backend in new window
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'C:\Users\johng\Documents\Erevus\orfeas\backend'; python main.py"

    Write-Host "[WAIT] Waiting for backend to initialize (20 seconds)..." -ForegroundColor Yellow
    Start-Sleep -Seconds 20

    # Verify backend started
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:5000/api/health" -Method GET -TimeoutSec 5 -ErrorAction Stop
        Write-Host "[OK] Backend started successfully!" -ForegroundColor Green
        $backendRunning = $true
    } catch {
        Write-Host "[ERROR] Backend failed to start" -ForegroundColor Red
        Write-Host "   Check backend console window for errors" -ForegroundColor Yellow
        exit 1
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# NGROK DEPLOYMENT
Write-Host "[STEP 2] NGROK TUNNEL DEPLOYMENT (Fastest)" -ForegroundColor Yellow
Write-Host ""

# Check if ngrok is installed
$ngrokInstalled = Get-Command ngrok -ErrorAction SilentlyContinue

if (-not $ngrokInstalled) {
    Write-Host "[WARN] Ngrok not installed - installing now..." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "INSTALLATION OPTIONS:" -ForegroundColor Cyan
    Write-Host "   1. Download: https://ngrok.com/download" -ForegroundColor White
    Write-Host "   2. OR run: winget install ngrok" -ForegroundColor White
    Write-Host ""

    # Try winget first
    try {
        Write-Host "[INSTALLING] Attempting automatic install via winget..." -ForegroundColor Cyan
        winget install ngrok --silent --accept-source-agreements --accept-package-agreements 2>&1 | Out-Null

        # Check if installed
        Start-Sleep -Seconds 3
        $ngrokInstalled = Get-Command ngrok -ErrorAction SilentlyContinue

        if ($ngrokInstalled) {
            Write-Host "[OK] Ngrok installed successfully!" -ForegroundColor Green
        } else {
            Write-Host "[WARN] Auto-install may have failed" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "[WARN] Automatic install failed" -ForegroundColor Yellow
        Write-Host "   Please install manually from: https://ngrok.com/download" -ForegroundColor White
        Write-Host "   Then run this script again" -ForegroundColor White
        Write-Host ""
        exit 1
    }
}

# Refresh PATH if ngrok just installed
$ngrokInstalled = Get-Command ngrok -ErrorAction SilentlyContinue

if ($ngrokInstalled) {
    Write-Host "[OK] Ngrok detected - starting tunnel..." -ForegroundColor Green
    Write-Host ""

    # Kill any existing ngrok processes
    Get-Process ngrok -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue

    # Start ngrok in new window
    Write-Host "[TUNNEL] Creating HTTPS tunnel to localhost:5000..." -ForegroundColor Cyan
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "ngrok http 5000"

    Write-Host "[WAIT] Waiting for ngrok to establish tunnel (10 seconds)..." -ForegroundColor Yellow
    Start-Sleep -Seconds 10

    # Get ngrok public URL
    try {
        $ngrokApi = Invoke-RestMethod -Uri "http://localhost:4040/api/tunnels" -Method GET -ErrorAction Stop
        $publicUrl = $ngrokApi.tunnels[0].public_url

        Write-Host ""
        Write-Host "========================================" -ForegroundColor Green
        Write-Host "NGROK TUNNEL ACTIVE!" -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "PUBLIC URL: $publicUrl" -ForegroundColor Cyan
        Write-Host "Protocol: HTTPS (SSL included)" -ForegroundColor Green
        Write-Host "Local Backend: http://localhost:5000" -ForegroundColor White
        Write-Host ""
        Write-Host "ACCESSIBLE FROM ANYWHERE:" -ForegroundColor Yellow
        Write-Host "   - Your phone/tablet" -ForegroundColor White
        Write-Host "   - Other computers on internet" -ForegroundColor White
        Write-Host "   - Cloud services and webhooks" -ForegroundColor White
        Write-Host ""
        Write-Host "NGROK WEB INTERFACE:" -ForegroundColor Magenta
        Write-Host "   http://localhost:4040 (request inspector)" -ForegroundColor White
        Write-Host ""
        Write-Host "IMPORTANT:" -ForegroundColor Yellow
        Write-Host "   - Keep ngrok window open" -ForegroundColor White
        Write-Host "   - Free tier: 2-hour session limit" -ForegroundColor White
        Write-Host "   - For permanent URL: ngrok.com/pricing" -ForegroundColor White
        Write-Host ""
        Write-Host "UPDATE FRONTEND:" -ForegroundColor Cyan
        Write-Host "   In orfeas-studio.html, change:" -ForegroundColor White
        Write-Host "   BACKEND_URL: '$publicUrl'" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Green
        Write-Host ""

        # Save URL to file
        $publicUrl | Out-File -FilePath "PUBLIC_BACKEND_URL.txt" -Encoding UTF8
        Write-Host "[SAVED] Public URL saved to: PUBLIC_BACKEND_URL.txt" -ForegroundColor Green
        Write-Host ""

        # Auto-update frontend
        Write-Host "[STEP 3] Auto-updating frontend configuration..." -ForegroundColor Yellow
        Write-Host ""

        $htmlPath = "orfeas-studio.html"
        if (Test-Path $htmlPath) {
            $htmlContent = Get-Content $htmlPath -Raw

            if ($htmlContent -match "BACKEND_URL:\s*['\"]([^'\"]+)['\"]") {
                $currentUrl = $Matches[1]
                Write-Host "   Current URL: $currentUrl" -ForegroundColor White
                Write-Host "   New URL: $publicUrl" -ForegroundColor Cyan

                # Replace URL
                $newContent = $htmlContent -replace "(BACKEND_URL:\s*['\"])([^'\"]+)(['\"])", "`$1$publicUrl`$3"
                $newContent | Out-File -FilePath $htmlPath -Encoding UTF8 -NoNewline

                Write-Host ""
                Write-Host "[OK] Frontend updated successfully!" -ForegroundColor Green
                Write-Host ""
                Write-Host "REFRESH BROWSER:" -ForegroundColor Yellow
                Write-Host "   Press Ctrl+Shift+R to hard reload" -ForegroundColor White
                Write-Host ""
            }
        }

    } catch {
        Write-Host "[ERROR] Failed to get ngrok tunnel URL" -ForegroundColor Red
        Write-Host "   Error: $_" -ForegroundColor Yellow
        Write-Host "   Check ngrok window or http://localhost:4040" -ForegroundColor White
        Write-Host ""
    }

    # GPU Status
    Write-Host "[STEP 4] GPU Acceleration Status" -ForegroundColor Yellow
    Write-Host ""

    try {
        $gpuStatus = Invoke-RestMethod -Uri "http://localhost:5000/api/health" -Method GET -ErrorAction Stop

        if ($gpuStatus.gpu_info) {
            Write-Host "[OK] GPU ACCELERATION: ENABLED" -ForegroundColor Green
            Write-Host "   Device: $($gpuStatus.gpu_info.device_name)" -ForegroundColor White
            Write-Host "   Memory: $([math]::Round($gpuStatus.gpu_info.total_memory_gb, 2)) GB total" -ForegroundColor White
            Write-Host "   Available: $([math]::Round($gpuStatus.gpu_info.available_memory_gb, 2)) GB" -ForegroundColor White
            Write-Host "   CUDA: $($gpuStatus.gpu_info.cuda_version)" -ForegroundColor White
        } else {
            Write-Host "[WARN] GPU ACCELERATION: DISABLED (CPU mode)" -ForegroundColor Yellow
        }

        Write-Host ""
        Write-Host "AI CAPABILITIES:" -ForegroundColor Cyan
        foreach ($capability in $gpuStatus.capabilities) {
            Write-Host "   [OK] $capability" -ForegroundColor Green
        }
    } catch {
        Write-Host "[WARN] Could not fetch GPU status" -ForegroundColor Yellow
    }

    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "THERION BACKEND DEPLOYMENT COMPLETE!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "BACKEND NOW ACCESSIBLE WORLDWIDE!" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "NEXT STEPS:" -ForegroundColor Yellow
    Write-Host "   1. Test API: $publicUrl/api/health" -ForegroundColor White
    Write-Host "   2. Open frontend: http://localhost:8080/orfeas-studio.html" -ForegroundColor White
    Write-Host "   3. Monitor traffic: http://localhost:4040" -ForegroundColor White
    Write-Host ""
    Write-Host "Keep this window and ngrok window open!" -ForegroundColor Yellow
    Write-Host ""

} else {
    Write-Host "[ERROR] Ngrok not found - installation failed" -ForegroundColor Red
    Write-Host ""
    Write-Host "MANUAL INSTALLATION:" -ForegroundColor Yellow
    Write-Host "   1. Download: https://ngrok.com/download" -ForegroundColor White
    Write-Host "   2. Extract to PATH (e.g., C:\Windows\System32)" -ForegroundColor White
    Write-Host "   3. Run this script again" -ForegroundColor White
    Write-Host ""
    exit 1
}
