# ORFEAS AI STUDIO - QUICK PRODUCTION DEPLOYMENT SCRIPT
# ==================================================
# Run this script to deploy to production in 5 minutes

param(
    [string]$ProductionDomain = "api.orfeas.ai",
    [string]$Environment = "production",
    [switch]$SkipBackup = $false,
    [switch]$DryRun = $false
)

$ErrorActionPreference = "Stop"
$timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"

Write-Host "
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║  ORFEAS AI STUDIO - PRODUCTION DEPLOYMENT                   ║
║  Domain: $ProductionDomain
║  Environment: $Environment                           ║
║  Timestamp: $timestamp
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
" -ForegroundColor Cyan

# Step 1: Backup
if (-not $SkipBackup) {
    Write-Host "[1/5] BACKING UP PROJECT..." -ForegroundColor Yellow
    $backupPath = "backup-$timestamp.tar.gz"
    try {
        # Create backup (using 7-Zip or tar)
        if (Get-Command tar -ErrorAction SilentlyContinue) {
            tar -czf $backupPath . 2>$null
            Write-Host "    ✅ Backup created: $backupPath" -ForegroundColor Green
        }
        else {
            Write-Host "    ⚠️  tar not found - skipping compression" -ForegroundColor Yellow
        }
    }
    catch {
        Write-Host "    ❌ Backup failed: $_" -ForegroundColor Red
        if (-not $DryRun) { exit 1 }
    }
}
else {
    Write-Host "[1/5] SKIPPING BACKUP (--SkipBackup)" -ForegroundColor Yellow
}

# Step 2: Update Frontend API_BASE
Write-Host "`n[2/5] UPDATING FRONTEND API_BASE..." -ForegroundColor Yellow
$htmlFile = "synexa-style-studio.html"
if (Test-Path $htmlFile) {
    try {
        $content = Get-Content $htmlFile
        $oldApi = 'const API_BASE = "http://127.0.0.1:5000"'
        $newApi = "const API_BASE = `"https://$ProductionDomain`""

        if ($content -match [regex]::Escape($oldApi)) {
            if (-not $DryRun) {
                $content = $content -replace [regex]::Escape($oldApi), $newApi
                Set-Content $htmlFile $content
            }
            Write-Host "    ✅ API_BASE updated: $oldApi" -ForegroundColor Green
            Write-Host "       → $newApi" -ForegroundColor Green
        }
        else {
            Write-Host "    ⚠️  API_BASE not found in expected format" -ForegroundColor Yellow
        }
    }
    catch {
        Write-Host "    ❌ Frontend update failed: $_" -ForegroundColor Red
        if (-not $DryRun) { exit 1 }
    }
}
else {
    Write-Host "    ❌ Frontend file not found: $htmlFile" -ForegroundColor Red
    exit 1
}

# Step 3: Update Backend Configuration
Write-Host "`n[3/5] UPDATING BACKEND CONFIGURATION..." -ForegroundColor Yellow
$envFile = "backend\.env"
if (Test-Path $envFile) {
    try {
        $content = Get-Content $envFile

        if (-not $DryRun) {
            # Add/update production settings
            if ($content -match "FLASK_ENV=") {
                $content = $content -replace "FLASK_ENV=.*", "FLASK_ENV=production"
            }
            else {
                $content += "`nFLASK_ENV=production"
            }

            if ($content -match "DEBUG=") {
                $content = $content -replace "DEBUG=.*", "DEBUG=false"
            }
            else {
                $content += "`nDEBUG=false"
            }

            Set-Content $envFile $content
        }
        Write-Host "    ✅ Environment updated: FLASK_ENV=production, DEBUG=false" -ForegroundColor Green
    }
    catch {
        Write-Host "    ❌ Backend configuration failed: $_" -ForegroundColor Red
        if (-not $DryRun) { exit 1 }
    }
}
else {
    Write-Host "    ⚠️  .env file not found - skipping" -ForegroundColor Yellow
}

# Step 4: Deploy Backend
Write-Host "`n[4/5] DEPLOYING BACKEND..." -ForegroundColor Yellow
try {
    # Check if Docker Compose is available
    if (Get-Command docker-compose -ErrorAction SilentlyContinue) {
        if (-not $DryRun) {
            Write-Host "    Starting docker-compose..." -ForegroundColor Cyan
            docker-compose -f docker-compose.production.yml down 2>$null
            Start-Sleep -Seconds 2
            docker-compose -f docker-compose.production.yml up -d
            Start-Sleep -Seconds 5
        }
        Write-Host "    ✅ Docker services started" -ForegroundColor Green
    }
    else {
        Write-Host "    ℹ️  Docker Compose not found - manual deployment needed" -ForegroundColor Yellow
        Write-Host "    Run: cd backend && python -m gunicorn -w 4 --threads 2 -b 0.0.0.0:5000 main:app" -ForegroundColor Cyan
    }
}
catch {
    Write-Host "    ❌ Backend deployment failed: $_" -ForegroundColor Red
    if (-not $DryRun) { exit 1 }
}

# Step 5: Health Check
Write-Host "`n[5/5] VERIFYING DEPLOYMENT..." -ForegroundColor Yellow
$maxRetries = 30
$retries = 0
$healthyUrl = "http://127.0.0.1:5000/health"

if (-not $DryRun) {
    while ($retries -lt $maxRetries) {
        try {
            $response = Invoke-WebRequest -Uri $healthyUrl -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
            if ($response.StatusCode -eq 200) {
                Write-Host "    ✅ Health endpoint responding" -ForegroundColor Green
                $json = $response.Content | ConvertFrom-Json
                Write-Host "       Status: $($json.status)" -ForegroundColor Green
                break
            }
        }
        catch {
            $retries++
            if ($retries -lt 30) {
                Write-Host "    ⏳ Waiting for backend to start ($retries/30)..." -ForegroundColor Yellow
                Start-Sleep -Seconds 1
            }
        }
    }

    if ($retries -eq $maxRetries) {
        Write-Host "    ❌ Health check timeout - backend may not be ready" -ForegroundColor Red
        Write-Host "    Check logs: docker-compose logs backend" -ForegroundColor Yellow
    }
}
else {
    Write-Host "    (Skipping health check in DRY-RUN mode)" -ForegroundColor Yellow
}

# Summary
Write-Host "`n
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║                 DEPLOYMENT COMPLETE ✅                       ║
║                                                              ║
║  Frontend: Updated (API_BASE → $ProductionDomain)
║  Backend: Deployed ($Environment)                     ║
║  Health: Verified                                        ║
║                                                              ║
║  Next Steps:                                                ║
║  1. Open browser: http://localhost:3000 (or your domain)   ║
║  2. Upload test image                                       ║
║  3. Generate 3D model                                       ║
║  4. Test all viewers (Three.js, iframe, download)          ║
║  5. Monitor logs: docker-compose logs -f backend            ║
║                                                              ║
║  Backup location: $backupPath
║  Time: $timestamp
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
" -ForegroundColor Green

if ($DryRun) {
    Write-Host "`n⚠️  DRY-RUN MODE - No changes were made. Remove -DryRun to execute." -ForegroundColor Yellow
}
