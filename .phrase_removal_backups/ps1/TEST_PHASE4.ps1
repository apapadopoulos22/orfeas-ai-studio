# 
# â•'                                                                              â•'
#              THERION PROTOCOL - PHASE 4 TEST LAUNCHER                         
# â•'                                                                              â•'
# â•'                      RELOAD PHASE 4 OPTIMIZATION TESTS                       â•'
# â•'                                                                              â•'
# â•'                         >>> TEST! <<<                                â•'
# â•'                                                                              â•'
# 

Write-Host ""
Write-Host "" -ForegroundColor Cyan
Write-Host "      THERION PROTOCOL - PHASE 4 OPTIMIZATION TEST LAUNCHER          " -ForegroundColor Cyan
Write-Host "" -ForegroundColor Cyan
Write-Host ""

# Get the absolute path to the test file
$testFile = Join-Path $PSScriptRoot "test-orfeas-phase4-optimizations.html"

# Check if file exists
if (Test-Path $testFile) {
    Write-Host " Test file found: $testFile" -ForegroundColor Green
    Write-Host ""
    Write-Host " Opening Phase 4 Optimization Tests in Chrome..." -ForegroundColor Yellow
    Write-Host ""

    # Open in Chrome Incognito mode
    Start-Process chrome.exe -ArgumentList "--incognito", $testFile

    Write-Host " Test page opened in Chrome Incognito mode" -ForegroundColor Green
    Write-Host ""
    Write-Host " EXPECTED TEST RESULTS:" -ForegroundColor Cyan
    Write-Host "   • Category 1: Blob URL Management (4 tests)" -ForegroundColor White
    Write-Host "   • Category 2: Three.js GPU Memory (4 tests)" -ForegroundColor White
    Write-Host "   • Category 3: Input Debouncing (4 tests)" -ForegroundColor White
    Write-Host "   • Category 4: Lazy Loading Three.js (4 tests)" -ForegroundColor White
    Write-Host "   • Category 5: Integration & Performance (5 tests)" -ForegroundColor White
    Write-Host ""
    Write-Host "   TOTAL: 21 tests" -ForegroundColor Yellow
    Write-Host "   TARGET: 100% pass rate (20/20 with some INFO)" -ForegroundColor Green
    Write-Host ""
    Write-Host "ℹ  NOTE: INFO results count as PASS (external dependencies)" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "" -ForegroundColor Cyan
    Write-Host ""
    Write-Host " PHASE 4 OPTIMIZATION TESTS LAUNCHED! " -ForegroundColor Green
    Write-Host ""
} else {
    Write-Host " ERROR: Test file not found!" -ForegroundColor Red
    Write-Host "   Expected: $testFile" -ForegroundColor Yellow
    Write-Host ""
}
