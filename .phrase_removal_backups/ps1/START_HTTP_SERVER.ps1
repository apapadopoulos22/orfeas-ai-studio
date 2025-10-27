#!/usr/bin/env pwsh
# 
#   THERION PROTOCOL - ORFEAS LOCAL HTTP SERVER                            
#  PWA Testing and Development Server                                          
# 

Write-Host ""
Write-Host "" -ForegroundColor Cyan
Write-Host "           THERION ORFEAS - LOCAL HTTP SERVER LAUNCHER                " -ForegroundColor Cyan
Write-Host "" -ForegroundColor Cyan
Write-Host ""

# Server configuration
$PORT = 8080
$HOST = "localhost"
$WORKSPACE = $PSScriptRoot

Write-Host " Server Configuration:" -ForegroundColor Yellow
Write-Host "  Port: $PORT" -ForegroundColor White
Write-Host "  Host: $HOST" -ForegroundColor White
Write-Host "  Workspace: $WORKSPACE" -ForegroundColor White
Write-Host ""

# Check if Python is available
Write-Host " Checking for Python..." -ForegroundColor Cyan
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue

if (-not $pythonCmd) {
    Write-Host " ERROR: Python not found in PATH" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install Python 3.7+ from https://www.python.org/" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

$pythonVersion = & python --version 2>&1
Write-Host " Python found: $pythonVersion" -ForegroundColor Green
Write-Host ""

# Check if port is already in use
Write-Host " Checking if port $PORT is available..." -ForegroundColor Cyan
$portInUse = Get-NetTCPConnection -LocalPort $PORT -ErrorAction SilentlyContinue

if ($portInUse) {
    Write-Host " WARNING: Port $PORT is already in use!" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Attempting to kill existing process..." -ForegroundColor Yellow

    $processId = $portInUse | Select-Object -First 1 -ExpandProperty OwningProcess
    Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2

    Write-Host " Port cleared" -ForegroundColor Green
}

Write-Host ""
Write-Host "" -ForegroundColor Green
Write-Host "                    STARTING HTTP SERVER                           " -ForegroundColor Green
Write-Host "" -ForegroundColor Green
Write-Host ""

Write-Host " Server URLs:" -ForegroundColor Cyan
Write-Host "  Main Application:  http://$HOST`:$PORT/orfeas-studio.html" -ForegroundColor White
Write-Host "  Test Suites:" -ForegroundColor Yellow
Write-Host "    Phase 9 Tests:   http://$HOST`:$PORT/test-orfeas-phase9-optimizations.html" -ForegroundColor White
Write-Host "    Phase 10 Tests:  http://$HOST`:$PORT/test-orfeas-phase10-optimizations.html" -ForegroundColor White
Write-Host ""

Write-Host " PWA Features Available:" -ForegroundColor Magenta
Write-Host "   Service Worker Registration" -ForegroundColor Green
Write-Host "   Install Prompt (beforeinstallprompt)" -ForegroundColor Green
Write-Host "   Offline Caching" -ForegroundColor Green
Write-Host "   Background Sync" -ForegroundColor Green
Write-Host "   Push Notifications" -ForegroundColor Green
Write-Host ""

Write-Host " Quick Actions:" -ForegroundColor Yellow
Write-Host "  Press Ctrl+C to stop the server" -ForegroundColor White
Write-Host "  Browser will auto-open in 3 seconds..." -ForegroundColor White
Write-Host ""

Write-Host "" -ForegroundColor Cyan
Write-Host "                     SERVER STARTING NOW...                            " -ForegroundColor Cyan
Write-Host "" -ForegroundColor Cyan
Write-Host ""

# Start server in background and open browser
$url = "http://$HOST`:$PORT/orfeas-studio.html"

# Open browser after short delay
Start-Sleep -Seconds 3
Start-Process $url

Write-Host " Browser opened at: $url" -ForegroundColor Green
Write-Host ""
Write-Host "" -ForegroundColor White
Write-Host "                        SERVER LOGS BELOW                                  " -ForegroundColor White
Write-Host "" -ForegroundColor White
Write-Host ""

# Start Python HTTP server (this will block until Ctrl+C)
try {
    Push-Location $WORKSPACE
    python -m http.server $PORT
}
catch {
    Write-Host ""
    Write-Host " Server error: $_" -ForegroundColor Red
}
finally {
    Pop-Location
    Write-Host ""
    Write-Host "" -ForegroundColor Yellow
    Write-Host "                     SERVER STOPPED                                    " -ForegroundColor Yellow
    Write-Host "" -ForegroundColor Yellow
    Write-Host ""
}
