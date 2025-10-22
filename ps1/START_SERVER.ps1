Write-Host ""
Write-Host "THERION ORFEAS - HTTP SERVER LAUNCHER" -ForegroundColor Cyan
Write-Host ""

$PORT = 8080
$WORKSPACE = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "Checking for Python..." -ForegroundColor Yellow
$pythonCheck = Get-Command python -ErrorAction SilentlyContinue

if (-not $pythonCheck) {
    Write-Host "ERROR: Python not found!" -ForegroundColor Red
    pause
    exit 1
}

Write-Host "Python found!" -ForegroundColor Green
Write-Host ""
Write-Host "Starting HTTP server on port $PORT..." -ForegroundColor Cyan
Write-Host ""
Write-Host "URLs:" -ForegroundColor Yellow
Write-Host "  Main App:       http://localhost:8080/orfeas-studio.html"
Write-Host "  Phase 9 Tests:  http://localhost:8080/test-orfeas-phase9-optimizations.html"
Write-Host "  Phase 10 Tests: http://localhost:8080/test-orfeas-phase10-optimizations.html"
Write-Host ""
Write-Host "Opening browser in 3 seconds..." -ForegroundColor Green
Write-Host "Press Ctrl+C to stop server" -ForegroundColor Yellow
Write-Host ""

Start-Sleep -Seconds 3
Start-Process "http://localhost:8080/orfeas-studio.html"

Write-Host "Browser opened! Server logs below:" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor White
Write-Host ""

Set-Location $WORKSPACE
python -m http.server $PORT
