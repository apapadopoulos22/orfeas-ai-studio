# ============================================================================
# ðŸ”¥ THERION BACKEND PUBLIC DEPLOYMENT - NGROK + CLOUDFLARE TUNNEL
# ============================================================================
# Deploys ORFEAS AI Backend to public internet with HTTPS
# Supports: Dynamic IP, GPU acceleration, Local AI APIs
# Options: Ngrok (fast), Cloudflare Tunnel (production), Port Forward (manual)
# ============================================================================

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("ngrok", "cloudflare", "portforward", "all")]
    [string]$Method = "ngrok"
)

Write-Host ""
Write-Host "â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—" -ForegroundColor Cyan
Write-Host "â•‘ âš”ï¸ THERION BACKEND PUBLIC DEPLOYMENT âš”ï¸                                     â•‘" -ForegroundColor Cyan
Write-Host "â•‘ Deploy ORFEAS AI Backend to Public Internet (HTTPS)                          â•‘" -ForegroundColor Cyan
Write-Host "â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•" -ForegroundColor Cyan
Write-Host ""

# =============================================================================
# STEP 1: Check Backend Status
# =============================================================================

Write-Host "ðŸ” STEP 1: Checking Backend Status..." -ForegroundColor Yellow
Write-Host ""

$backendRunning = $false
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5000/api/health" -Method GET -TimeoutSec 2 -ErrorAction Stop
    $backendRunning = $true
    Write-Host "âœ… Backend already running on port 5000" -ForegroundColor Green
} catch {
    Write-Host "âš ï¸ Backend not running - starting now..." -ForegroundColor Yellow
}

if (-not $backendRunning) {
    Write-Host ""
    Write-Host "ðŸš€ Starting ORFEAS Backend Server..." -ForegroundColor Cyan

    # Start backend in background
    $backendJob = Start-Job -ScriptBlock {
        Set-Location "C:\Users\johng\Documents\Erevus\orfeas\backend"
        python main.py
    }

    Write-Host "â³ Waiting for backend to initialize (15 seconds)..." -ForegroundColor Yellow
    Start-Sleep -Seconds 15

    # Verify backend started
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:5000/api/health" -Method GET -TimeoutSec 5 -ErrorAction Stop
        Write-Host "âœ… Backend started successfully!" -ForegroundColor Green
        $backendRunning = $true
    } catch {
        Write-Host "âŒ Backend failed to start" -ForegroundColor Red
        Write-Host "   Check backend/main.py for errors" -ForegroundColor Yellow
        Stop-Job -Job $backendJob -ErrorAction SilentlyContinue
        Remove-Job -Job $backendJob -ErrorAction SilentlyContinue
        exit 1
    }
}

Write-Host ""
Write-Host "â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•" -ForegroundColor Green
Write-Host ""

# =============================================================================
# STEP 2: Deploy via Selected Method
# =============================================================================

if ($Method -eq "ngrok" -or $Method -eq "all") {
    Write-Host "ðŸ”¥ STEP 2A: NGROK TUNNEL DEPLOYMENT (Fastest)" -ForegroundColor Yellow
    Write-Host ""

    # Check if ngrok is installed
    $ngrokInstalled = Get-Command ngrok -ErrorAction SilentlyContinue

    if (-not $ngrokInstalled) {
        Write-Host "âš ï¸ Ngrok not installed - installing now..." -ForegroundColor Yellow
        Write-Host ""
        Write-Host "INSTALLATION OPTIONS:" -ForegroundColor Cyan
        Write-Host "   1. Download: https://ngrok.com/download" -ForegroundColor White
        Write-Host "   2. OR use: winget install ngrok" -ForegroundColor White
        Write-Host "   3. OR use: choco install ngrok" -ForegroundColor White
        Write-Host ""

        # Try winget first
        try {
            Write-Host "ðŸ”„ Attempting automatic install via winget..." -ForegroundColor Cyan
            winget install ngrok --silent --accept-source-agreements --accept-package-agreements
            Write-Host "âœ… Ngrok installed successfully!" -ForegroundColor Green
            $ngrokInstalled = $true
        } catch {
            Write-Host "âš ï¸ Automatic install failed - please install manually" -ForegroundColor Yellow
            Write-Host "   Download from: https://ngrok.com/download" -ForegroundColor White
            Write-Host "   Then extract to PATH and run this script again" -ForegroundColor White
            Write-Host ""
        }
    }

    if ($ngrokInstalled -or (Get-Command ngrok -ErrorAction SilentlyContinue)) {
        Write-Host "âœ… Ngrok detected - starting tunnel..." -ForegroundColor Green
        Write-Host ""

        # Start ngrok tunnel
        Write-Host "ðŸŒ Creating HTTPS tunnel to localhost:5000..." -ForegroundColor Cyan
        Write-Host ""

        # Kill any existing ngrok processes
        Get-Process ngrok -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue

        # Start ngrok in background
        $ngrokJob = Start-Job -ScriptBlock {
            ngrok http 5000 --log stdout
        }

        Write-Host "â³ Waiting for ngrok to establish tunnel (5 seconds)..." -ForegroundColor Yellow
        Start-Sleep -Seconds 5

        # Get ngrok public URL
        try {
            $ngrokApi = Invoke-RestMethod -Uri "http://localhost:4040/api/tunnels" -Method GET -ErrorAction Stop
            $publicUrl = $ngrokApi.tunnels[0].public_url

            Write-Host ""
            Write-Host "â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•" -ForegroundColor Green
            Write-Host "ðŸŽ‰ NGROK TUNNEL ACTIVE!" -ForegroundColor Green
            Write-Host "â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•" -ForegroundColor Green
            Write-Host ""
            Write-Host "ðŸ“¡ PUBLIC URL: $publicUrl" -ForegroundColor Cyan
            Write-Host "ðŸ” Protocol: HTTPS (SSL included)" -ForegroundColor Green
            Write-Host "âš¡ Local Backend: http://localhost:5000" -ForegroundColor White
            Write-Host ""
            Write-Host "ðŸŒ ACCESSIBLE FROM ANYWHERE:" -ForegroundColor Yellow
            Write-Host "   - Your phone/tablet" -ForegroundColor White
            Write-Host "   - Other computers on internet" -ForegroundColor White
            Write-Host "   - Cloud services and webhooks" -ForegroundColor White
            Write-Host ""
            Write-Host "ðŸ“Š NGROK WEB INTERFACE:" -ForegroundColor Magenta
            Write-Host "   http://localhost:4040 (request inspector, replay, etc.)" -ForegroundColor White
            Write-Host ""
            Write-Host "âš ï¸ IMPORTANT:" -ForegroundColor Yellow
            Write-Host "   - Keep this terminal window open" -ForegroundColor White
            Write-Host "   - Free tier: 2-hour session limit (auto-reconnect available)" -ForegroundColor White
            Write-Host "   - For permanent URL: ngrok.com/pricing (Static domain)" -ForegroundColor White
            Write-Host ""
            Write-Host "ðŸ”— UPDATE FRONTEND:" -ForegroundColor Cyan
            Write-Host "   In orfeas-studio.html, change:" -ForegroundColor White
            Write-Host "   BACKEND_URL: '$publicUrl'" -ForegroundColor Yellow
            Write-Host ""
            Write-Host "â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•" -ForegroundColor Green
            Write-Host ""

            # Save URL to file for frontend auto-config
            $publicUrl | Out-File -FilePath "PUBLIC_BACKEND_URL.txt" -Encoding UTF8
            Write-Host "âœ… Public URL saved to: PUBLIC_BACKEND_URL.txt" -ForegroundColor Green
            Write-Host ""

        } catch {
            Write-Host "âŒ Failed to get ngrok tunnel URL" -ForegroundColor Red
            Write-Host "   Error: $_" -ForegroundColor Yellow
            Write-Host "   Check ngrok is running: http://localhost:4040" -ForegroundColor White
            Write-Host ""
        }
    }
}

if ($Method -eq "cloudflare" -or $Method -eq "all") {
    Write-Host ""
    Write-Host "ðŸ”¥ STEP 2B: CLOUDFLARE TUNNEL DEPLOYMENT (Production Grade)" -ForegroundColor Yellow
    Write-Host ""

    # Check if cloudflared is installed
    $cloudflaredInstalled = Get-Command cloudflared -ErrorAction SilentlyContinue

    if (-not $cloudflaredInstalled) {
        Write-Host "âš ï¸ Cloudflared not installed - installing now..." -ForegroundColor Yellow
        Write-Host ""

        try {
            Write-Host "ðŸ”„ Downloading cloudflared..." -ForegroundColor Cyan
            $cloudflaredUrl = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"
            Invoke-WebRequest -Uri $cloudflaredUrl -OutFile "cloudflared.exe" -ErrorAction Stop
            Write-Host "âœ… Cloudflared downloaded successfully!" -ForegroundColor Green
            $cloudflaredInstalled = $true
        } catch {
            Write-Host "âš ï¸ Download failed - please install manually" -ForegroundColor Yellow
            Write-Host "   Download from: https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/" -ForegroundColor White
            Write-Host ""
        }
    }

    if ($cloudflaredInstalled -or (Test-Path "cloudflared.exe")) {
        Write-Host "âœ… Cloudflared detected - starting tunnel..." -ForegroundColor Green
        Write-Host ""

        # Start cloudflare tunnel
        Write-Host "ðŸŒ Creating Cloudflare Tunnel to localhost:5000..." -ForegroundColor Cyan
        Write-Host ""
        Write-Host "âš ï¸ FIRST TIME SETUP:" -ForegroundColor Yellow
        Write-Host "   1. Cloudflare will open browser for login" -ForegroundColor White
        Write-Host "   2. Login to your Cloudflare account (free)" -ForegroundColor White
        Write-Host "   3. Authorize the tunnel" -ForegroundColor White
        Write-Host "   4. You'll get a permanent *.trycloudflare.com URL" -ForegroundColor White
        Write-Host ""

        # Start cloudflared tunnel
        if (Test-Path "cloudflared.exe") {
            Start-Process -FilePath ".\cloudflared.exe" -ArgumentList "tunnel --url http://localhost:5000" -NoNewWindow
        } else {
            Start-Process -FilePath "cloudflared" -ArgumentList "tunnel --url http://localhost:5000" -NoNewWindow
        }

        Write-Host "âœ… Cloudflare Tunnel started!" -ForegroundColor Green
        Write-Host "   Check terminal output above for your public URL" -ForegroundColor White
        Write-Host ""
        Write-Host "ðŸŽ‰ BENEFITS:" -ForegroundColor Cyan
        Write-Host "   âœ… Free forever (no time limits)" -ForegroundColor Green
        Write-Host "   âœ… DDoS protection included" -ForegroundColor Green
        Write-Host "   âœ… Custom domain support (optional)" -ForegroundColor Green
        Write-Host "   âœ… Persistent URL (doesn't change)" -ForegroundColor Green
        Write-Host ""
    }
}

if ($Method -eq "portforward") {
    Write-Host ""
    Write-Host "ðŸ”¥ STEP 2C: PORT FORWARDING + DDNS (Manual Setup)" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "âš ï¸ MANUAL CONFIGURATION REQUIRED:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "ROUTER PORT FORWARDING:" -ForegroundColor Cyan
    Write-Host "   1. Login to router admin panel (usually 192.168.1.1)" -ForegroundColor White
    Write-Host "   2. Find 'Port Forwarding' or 'NAT' settings" -ForegroundColor White
    Write-Host "   3. Forward external port 5000 â†’ internal IP:5000" -ForegroundColor White
    Write-Host "   4. Save and apply settings" -ForegroundColor White
    Write-Host ""
    Write-Host "GET YOUR PUBLIC IP:" -ForegroundColor Cyan
    try {
        $publicIP = (Invoke-WebRequest -Uri "https://api.ipify.org" -UseBasicParsing).Content
        Write-Host "   Your current public IP: $publicIP" -ForegroundColor Yellow
        Write-Host "   Your backend will be at: http://$publicIP:5000" -ForegroundColor White
    } catch {
        Write-Host "   Visit: https://whatismyipaddress.com" -ForegroundColor White
    }
    Write-Host ""
    Write-Host "DYNAMIC DNS (Optional):" -ForegroundColor Cyan
    Write-Host "   Free DDNS providers:" -ForegroundColor White
    Write-Host "   - No-IP: https://www.noip.com" -ForegroundColor White
    Write-Host "   - DuckDNS: https://www.duckdns.org" -ForegroundColor White
    Write-Host "   - Dynu: https://www.dynu.com" -ForegroundColor White
    Write-Host ""
    Write-Host "âš ï¸ SECURITY WARNING:" -ForegroundColor Red
    Write-Host "   - Enable HTTPS (use reverse proxy like Caddy)" -ForegroundColor Yellow
    Write-Host "   - Set up firewall rules" -ForegroundColor Yellow
    Write-Host "   - Use authentication tokens" -ForegroundColor Yellow
    Write-Host ""
}

# =============================================================================
# STEP 3: GPU Status Check
# =============================================================================

Write-Host ""
Write-Host "ðŸŽ® STEP 3: GPU Acceleration Status" -ForegroundColor Yellow
Write-Host ""

try {
    $gpuStatus = Invoke-RestMethod -Uri "http://localhost:5000/api/health" -Method GET -ErrorAction Stop

    if ($gpuStatus.gpu_info) {
        Write-Host "âœ… GPU ACCELERATION: ENABLED" -ForegroundColor Green
        Write-Host "   Device: $($gpuStatus.gpu_info.device_name)" -ForegroundColor White
        Write-Host "   Memory: $([math]::Round($gpuStatus.gpu_info.total_memory_gb, 2)) GB total" -ForegroundColor White
        Write-Host "   Available: $([math]::Round($gpuStatus.gpu_info.available_memory_gb, 2)) GB" -ForegroundColor White
        Write-Host "   CUDA: $($gpuStatus.gpu_info.cuda_version)" -ForegroundColor White
    } else {
        Write-Host "âš ï¸ GPU ACCELERATION: DISABLED (CPU mode)" -ForegroundColor Yellow
    }

    Write-Host ""
    Write-Host "ðŸ¤– AI CAPABILITIES:" -ForegroundColor Cyan
    foreach ($capability in $gpuStatus.capabilities) {
        Write-Host "   âœ… $capability" -ForegroundColor Green
    }
} catch {
    Write-Host "âš ï¸ Could not fetch GPU status" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•" -ForegroundColor Green
Write-Host "ðŸ”¥ THERION BACKEND DEPLOYMENT COMPLETE!" -ForegroundColor Green
Write-Host "â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•" -ForegroundColor Green
Write-Host ""
Write-Host "âš”ï¸ BACKEND NOW ACCESSIBLE WORLDWIDE! âš”ï¸" -ForegroundColor Cyan
Write-Host ""
Write-Host "NEXT STEPS:" -ForegroundColor Yellow
Write-Host "   1. Copy your public URL from above" -ForegroundColor White
Write-Host "   2. Update orfeas-studio.html BACKEND_URL config" -ForegroundColor White
Write-Host "   3. Test API endpoint: [PUBLIC_URL]/api/health" -ForegroundColor White
Write-Host "   4. Deploy frontend to Netlify/Vercel for complete solution" -ForegroundColor White
Write-Host ""
Write-Host "ðŸ“Š MONITOR TRAFFIC:" -ForegroundColor Cyan
Write-Host "   Ngrok: http://localhost:4040" -ForegroundColor White
Write-Host "   Backend Logs: Check this terminal output" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop deployment" -ForegroundColor Yellow
Write-Host ""

# Keep script running
Wait-Event -Timeout 3600  # Wait 1 hour or until Ctrl+C
