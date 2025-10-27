# PowerShell Script: THERION Phase 11 Test Launcher
# Auto-opens Phase 11 test suite in browser

Write-Host ""
Write-Host "â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—" -ForegroundColor Magenta
Write-Host "â•‘   âš”ï¸ THERION PHASE 11 TEST SUITE LAUNCHER âš”ï¸               â•‘" -ForegroundColor Magenta
Write-Host "â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•" -ForegroundColor Magenta
Write-Host ""

Write-Host "ðŸŽ¯ PHASE 11 OPTIMIZATIONS:" -ForegroundColor Cyan
Write-Host "   30. Production Mode Auto-Detection" -ForegroundColor White
Write-Host "   35. Lazy Load Socket.IO (~200KB saved)" -ForegroundColor White
Write-Host "   36. Prefetch & Preconnect Headers" -ForegroundColor White
Write-Host ""

Write-Host "ðŸ“Š TESTS TO RUN: 9" -ForegroundColor Yellow
Write-Host "   âœ… Production mode detection" -ForegroundColor White
Write-Host "   âœ… Debug mode configuration" -ForegroundColor White
Write-Host "   âœ… Error reporting system" -ForegroundColor White
Write-Host "   âœ… Socket.IO lazy loading" -ForegroundColor White
Write-Host "   âœ… Prefetch headers validation" -ForegroundColor White
Write-Host "   âœ… Performance metrics" -ForegroundColor White
Write-Host ""

# Check if HTTP server is running
$httpServer = Get-NetTCPConnection -LocalPort 8080 -ErrorAction SilentlyContinue

if ($httpServer) {
    Write-Host "âœ… HTTP SERVER: RUNNING (Port 8080)" -ForegroundColor Green
    Write-Host ""

    Write-Host "ðŸš€ LAUNCHING TEST SUITE..." -ForegroundColor Cyan
    Start-Sleep -Seconds 1

    # Open test page
    Start-Process "http://localhost:8080/test-orfeas-phase11-optimizations.html"

    Write-Host "âœ… Test suite opened in browser!" -ForegroundColor Green
    Write-Host ""

    Write-Host "ðŸ“‹ EXPECTED RESULTS:" -ForegroundColor Yellow
    Write-Host "   - 9/9 tests passing (100%)" -ForegroundColor Green
    Write-Host "   - Performance metrics displayed" -ForegroundColor Green
    Write-Host "   - PERFECT SCORE badge" -ForegroundColor Green
    Write-Host ""

    Write-Host "ðŸ“š DOCUMENTATION:" -ForegroundColor Magenta
    Write-Host "   md\PHASE_11_COMPLETE_REPORT.md" -ForegroundColor White
    Write-Host "   md\PHASE_11_OPTIMIZATION_PLAN.md" -ForegroundColor White
    Write-Host ""

} else {
    Write-Host "âŒ HTTP SERVER NOT RUNNING!" -ForegroundColor Red
    Write-Host ""
    Write-Host "âš¡ STARTING SERVER..." -ForegroundColor Yellow

    # Start server
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot'; python -m http.server 8080" -WindowStyle Minimized

    Write-Host "â³ Waiting for server to start..." -ForegroundColor Yellow
    Start-Sleep -Seconds 3

    Write-Host "âœ… Server started!" -ForegroundColor Green
    Write-Host "ðŸš€ Opening test suite..." -ForegroundColor Cyan

    Start-Process "http://localhost:8080/test-orfeas-phase11-optimizations.html"

    Write-Host "âœ… Test suite launched!" -ForegroundColor Green
    Write-Host ""
}

Write-Host "âš”ï¸ PHASE 11 TESTING INITIATED! âš”ï¸" -ForegroundColor Green
Write-Host ""
