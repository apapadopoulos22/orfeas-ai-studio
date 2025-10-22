# ==============================================================================
# RESTART BACKEND WITH NEW LOGGING
# ==============================================================================
# This script helps restart the backend to activate the new Python file logging
# ==============================================================================

Write-Host ""
Write-Host "=========================================================================" -ForegroundColor Cyan
Write-Host "BACKEND RESTART - ACTIVATING NEW LOGGING" -ForegroundColor Cyan
Write-Host "=========================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "INSTRUCTIONS:" -ForegroundColor Yellow
Write-Host ""
Write-Host "The backend is currently running in a separate PowerShell window." -ForegroundColor White
Write-Host "You need to manually restart it to activate the new logging configuration." -ForegroundColor White
Write-Host ""
Write-Host "=========================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "STEP 1: Stop the current backend" -ForegroundColor Yellow
Write-Host ""
Write-Host "  1. Find the PowerShell window running 'python main.py'" -ForegroundColor White
Write-Host "  2. Press Ctrl+C to stop the backend" -ForegroundColor White
Write-Host "  3. Wait for the process to fully terminate" -ForegroundColor White
Write-Host ""

Write-Host "STEP 2: Start the backend with new configuration" -ForegroundColor Yellow
Write-Host ""
Write-Host "  In the same PowerShell window, run:" -ForegroundColor White
Write-Host ""
Write-Host "  cd c:\Users\johng\Documents\Erevus\orfeas\backend" -ForegroundColor Cyan
Write-Host "  `$env:FLASK_ENV='production'; `$env:TESTING='0'; python main.py" -ForegroundColor Cyan
Write-Host ""

Write-Host "STEP 3: Verify new logging is active" -ForegroundColor Yellow
Write-Host ""
Write-Host "  Look for these lines in the startup output:" -ForegroundColor White
Write-Host ""
Write-Host "  [THERION] Dual logging initialized: console + logs/backend_requests.log" -ForegroundColor Green
Write-Host "  [THERION] File rotation: 10MB per file, 5 backups (50MB total)" -ForegroundColor Green
Write-Host ""

Write-Host "=========================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press any key when backend is restarted..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')

Write-Host ""
Write-Host "Checking if backend is running..." -ForegroundColor Yellow

$maxAttempts = 10
$attempt = 0
$backendRunning = $false

while ($attempt -lt $maxAttempts -and -not $backendRunning) {
    $attempt++
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:5000/health" -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
        $backendRunning = $true
        Write-Host " Backend is running!" -ForegroundColor Green
    }
    catch {
        Write-Host "  Attempt $attempt/$maxAttempts - Backend not responding yet..." -ForegroundColor Gray
        Start-Sleep -Seconds 2
    }
}

if (-not $backendRunning) {
    Write-Host " Backend is not responding" -ForegroundColor Red
    Write-Host "   Please check the backend terminal for errors" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "=========================================================================" -ForegroundColor Green
Write-Host "BACKEND RESTARTED - PROCEEDING TO TEST" -ForegroundColor Green
Write-Host "=========================================================================" -ForegroundColor Green
Write-Host ""

# Now run the file logging test
Write-Host "Running TEST_FILE_LOGGING.ps1..." -ForegroundColor Cyan
Write-Host ""

& ".\TEST_FILE_LOGGING.ps1"
