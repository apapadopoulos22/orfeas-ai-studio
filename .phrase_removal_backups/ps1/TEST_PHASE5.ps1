# =====================================================================
# ORFEAS STUDIO - Phase 5 Test Suite Launcher
# =====================================================================
# Purpose: Launch Phase 5 optimization tests (8-13) in Chrome Incognito
# Tests: InputSanitizer, RateLimiter, ImageCompressor, ErrorLogger,
#        ThreeJSErrorBoundary, IntervalManager
# =====================================================================

Write-Host "=======================================================================" -ForegroundColor Cyan
Write-Host "ORFEAS STUDIO - PHASE 5 TEST SUITE (22 Tests)" -ForegroundColor Yellow
Write-Host "=======================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Testing Optimizations 8-13:" -ForegroundColor Green
Write-Host "  - OPTIMIZATION 8: InputSanitizer (3 tests)" -ForegroundColor White
Write-Host "  - OPTIMIZATION 9: RateLimiter (3 tests)" -ForegroundColor White
Write-Host "  - OPTIMIZATION 10: ImageCompressor (4 tests)" -ForegroundColor White
Write-Host "  - OPTIMIZATION 11: ErrorLogger (4 tests)" -ForegroundColor White
Write-Host "  - OPTIMIZATION 12: ThreeJSErrorBoundary (4 tests)" -ForegroundColor White
Write-Host "  - OPTIMIZATION 13: IntervalManager (4 tests)" -ForegroundColor White
Write-Host ""
Write-Host "Launching in Chrome Incognito Mode..." -ForegroundColor Cyan
Write-Host ""

# Get the full path to the test file
$testFile = Join-Path $PSScriptRoot "test-orfeas-phase5-optimizations.html"

# Check if file exists
if (Test-Path $testFile) {
    Write-Host "Test file found: $testFile" -ForegroundColor Green

    # Find Chrome executable
    $chromePaths = @(
        "${env:ProgramFiles}\Google\Chrome\Application\chrome.exe",
        "${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe",
        "${env:LocalAppData}\Google\Chrome\Application\chrome.exe"
    )

    $chromePath = $chromePaths | Where-Object { Test-Path $_ } | Select-Object -First 1

    if ($chromePath) {
        Write-Host "Chrome found: $chromePath" -ForegroundColor Green
        Write-Host ""
        Write-Host "Opening test suite..." -ForegroundColor Yellow

        # Launch Chrome in incognito mode
        & $chromePath --incognito --new-window "file:///$($testFile -replace '\\', '/')"

        Write-Host ""
        Write-Host "Test suite launched successfully!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Expected Results:" -ForegroundColor Cyan
        Write-Host "  - Total Tests: 22" -ForegroundColor White
        Write-Host "  - Expected Pass Rate: 95-100%" -ForegroundColor White
        Write-Host "  - Categories: 6 (Input, Rate, Compress, Log, Boundary, Interval)" -ForegroundColor White
        Write-Host ""
        Write-Host "THERION PHASE 5 TESTING" -ForegroundColor Yellow
    } else {
        Write-Host "Chrome not found in standard locations" -ForegroundColor Red
        Write-Host "Opening test file in default browser..." -ForegroundColor Yellow
        Start-Process $testFile
    }
} else {
    Write-Host "Test file not found: $testFile" -ForegroundColor Red
    Write-Host "Please ensure test-orfeas-phase5-optimizations.html exists" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
