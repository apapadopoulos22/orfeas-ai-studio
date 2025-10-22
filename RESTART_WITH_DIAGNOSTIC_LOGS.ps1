#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Restart backend with diagnostic logging and capture output
.DESCRIPTION
    Stops existing backend, starts new one with diagnostic logging to file
#>

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host " RESTARTING BACKEND WITH DIAGNOSTIC LOGGING" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Stop existing backend
Write-Host "[1/5] Stopping existing backend..." -ForegroundColor Yellow
$pythonProcesses = Get-Process python -ErrorAction SilentlyContinue | Where-Object {
    $_.CommandLine -like "*main.py*" -or $_.Path -like "*orfeas*backend*"
}
if ($pythonProcesses) {
    $pythonProcesses | Stop-Process -Force
    Start-Sleep -Seconds 2
    Write-Host "   Backend stopped" -ForegroundColor Green
}
else {
    Write-Host "  ℹ No backend process found to stop" -ForegroundColor Gray
}

# Step 2: Clear cache
Write-Host "[2/5] Clearing output cache..." -ForegroundColor Yellow
$cacheCleared = 0
if (Test-Path "outputs") {
    Get-ChildItem "outputs" -Directory | ForEach-Object {
        Remove-Item $_.FullName -Recurse -Force
        $cacheCleared++
    }
}
Write-Host "   Cleared $cacheCleared cached outputs" -ForegroundColor Green

# Step 3: Create log directory
Write-Host "[3/5] Creating log directory..." -ForegroundColor Yellow
if (-not (Test-Path "logs")) {
    New-Item -ItemType Directory -Path "logs" | Out-Null
}
$logFile = "logs\backend_diagnostic_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"
Write-Host "   Log file: $logFile" -ForegroundColor Green

# Step 4: Start backend with diagnostic logging
Write-Host "[4/5] Starting backend with diagnostic logging..." -ForegroundColor Yellow
Write-Host "  ℹ This will take 30-45 seconds for model loading..." -ForegroundColor Gray

Push-Location backend

$env:FLASK_ENV = 'production'
$env:TESTING = '0'
$env:GPU_MEMORY_LIMIT = '0.8'
$env:DISABLE_RESULT_CACHE = '1'
$env:PYTHONUNBUFFERED = '1'

# Start backend and tee output to both console and file
Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "Set-Location '$PWD'; " +
    "`$env:FLASK_ENV='production'; " +
    "`$env:TESTING='0'; " +
    "`$env:GPU_MEMORY_LIMIT='0.8'; " +
    "`$env:DISABLE_RESULT_CACHE='1'; " +
    "`$env:PYTHONUNBUFFERED='1'; " +
    "python main.py 2>&1 | Tee-Object -FilePath '../$logFile'"
)

Pop-Location

Write-Host "   Backend starting in new window" -ForegroundColor Green
Write-Host "   Logs will be saved to: $logFile" -ForegroundColor Green

# Step 5: Wait for backend to be ready
Write-Host "[5/5] Waiting for backend to be ready..." -ForegroundColor Yellow
$maxAttempts = 60
$attempt = 0
$ready = $false

while ($attempt -lt $maxAttempts -and -not $ready) {
    $attempt++
    Start-Sleep -Seconds 1

    try {
        $response = Invoke-WebRequest -Uri "http://localhost:5000/health" -TimeoutSec 2 -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            $ready = $true
            Write-Host "   Backend is ready! ($attempt seconds)" -ForegroundColor Green
        }
    }
    catch {
        # Still waiting...
        if ($attempt % 10 -eq 0) {
            Write-Host "    Still waiting... ($attempt seconds)" -ForegroundColor Gray
        }
    }
}

if (-not $ready) {
    Write-Host "   Backend did not respond after $maxAttempts seconds" -ForegroundColor Red
    Write-Host "    Check the backend window for errors" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host " BACKEND READY - YOU CAN NOW RUN THE TEST" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Run the diagnostic test with:" -ForegroundColor Yellow
Write-Host "  python test_diagnostic_quick.py" -ForegroundColor White
Write-Host ""
Write-Host "After the test completes:" -ForegroundColor Yellow
Write-Host "  1. Check the backend window for [DIAGNOSTIC] logs" -ForegroundColor White
Write-Host "  2. Or view the log file: $logFile" -ForegroundColor White
Write-Host ""
