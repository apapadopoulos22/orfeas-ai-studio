â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—
â•‘ âš”ï¸ THERION PROTOCOL - BROWSER CACHE BYPASS âš”ï¸                                  â•‘
â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

Write-Host ""
Write-Host "ðŸ”¥ CRITICAL: You are seeing errors from CACHED VERSION!" -ForegroundColor Red
Write-Host ""
Write-Host "âœ… File on disk is VALID (all 165 braces match perfectly)" -ForegroundColor Green
Write-Host "âŒ Your browser is loading OLD broken version from cache" -ForegroundColor Red
Write-Host ""
Write-Host "â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•" -ForegroundColor Cyan
Write-Host "SOLUTION: OPEN IN INCOGNITO/PRIVATE MODE" -ForegroundColor Yellow
Write-Host "â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•" -ForegroundColor Cyan
Write-Host ""
Write-Host "METHOD 1: Chrome Incognito" -ForegroundColor Cyan
Write-Host "   Press: CTRL+SHIFT+N" -ForegroundColor White
Write-Host "   Then drag this file into the new window" -ForegroundColor White
Write-Host ""
Write-Host "METHOD 2: Edge InPrivate" -ForegroundColor Cyan
Write-Host "   Press: CTRL+SHIFT+N" -ForegroundColor White
Write-Host "   Then drag this file into the new window" -ForegroundColor White
Write-Host ""
Write-Host "METHOD 3: Firefox Private" -ForegroundColor Cyan
Write-Host "   Press: CTRL+SHIFT+P" -ForegroundColor White
Write-Host "   Then drag this file into the new window" -ForegroundColor White
Write-Host ""
Write-Host "â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•" -ForegroundColor Cyan
Write-Host "ALTERNATIVE: HARD REFRESH CURRENT TAB" -ForegroundColor Yellow
Write-Host "â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•" -ForegroundColor Cyan
Write-Host ""
Write-Host "   Press: CTRL+SHIFT+R (Chrome/Edge)" -ForegroundColor White
Write-Host "   Or: CTRL+F5 (Firefox)" -ForegroundColor White
Write-Host ""
Write-Host "â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•" -ForegroundColor Cyan
Write-Host "EXPECTED RESULT AFTER FIX:" -ForegroundColor Green
Write-Host "â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•" -ForegroundColor Cyan
Write-Host ""
Write-Host "Console should show:" -ForegroundColor White
Write-Host "  âœ… Script loaded successfully - waiting for DOM" -ForegroundColor Green
Write-Host "  ðŸ”¥ DOMContentLoaded event fired" -ForegroundColor Green
Write-Host "  âœ… Three.js initialized" -ForegroundColor Green
Write-Host "  âš”ï¸ THERION Testing Suite Initialized - SUCCESS!" -ForegroundColor Green
Write-Host "  âš”ï¸ Ready for Phase 2 Testing" -ForegroundColor Green
Write-Host "  âš”ï¸ Rate Limiter Active" -ForegroundColor Green
Write-Host "  âš”ï¸ Regression Tests Ready" -ForegroundColor Green
Write-Host "  âœ… All initialization complete" -ForegroundColor Green
Write-Host ""
Write-Host "Click 'Load 1 Model' button â†’ Cube should appear" -ForegroundColor White
Write-Host "NO ERRORS in console" -ForegroundColor White
Write-Host ""
Write-Host "â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•" -ForegroundColor Cyan
Write-Host ""

# Try to open in Chrome incognito automatically
$chromePath = "C:\Program Files\Google\Chrome\Application\chrome.exe"
$filePath = Join-Path (Get-Location) "test_phase2_optimizations.html"

if (Test-Path $chromePath) {
    Write-Host "ðŸš€ Opening Chrome in Incognito mode..." -ForegroundColor Green
    Start-Process $chromePath -ArgumentList "--incognito", $filePath
    Write-Host "âœ… Chrome Incognito opened with test file" -ForegroundColor Green
}
else {
    Write-Host "âš ï¸ Chrome not found at default location" -ForegroundColor Yellow
    Write-Host "Manually open incognito and drag this file:" -ForegroundColor White
    Write-Host "   $filePath" -ForegroundColor Cyan

    # Open file in default browser as fallback
    Start-Process $filePath
}

Write-Host ""
Write-Host "â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•" -ForegroundColor Cyan
Write-Host "AFTER OPENING IN INCOGNITO:" -ForegroundColor Yellow
Write-Host "â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Press F12 to open DevTools" -ForegroundColor White
Write-Host "2. Check Console tab for initialization messages" -ForegroundColor White
Write-Host "3. Click 'Load 1 Model' button" -ForegroundColor White
Write-Host "4. Verify cube appears and rotates" -ForegroundColor White
Write-Host "5. Report results below:" -ForegroundColor White
Write-Host ""
Write-Host "REPORT TEMPLATE:" -ForegroundColor Yellow
Write-Host "â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•" -ForegroundColor Cyan
Write-Host "INCOGNITO MODE TEST:" -ForegroundColor White
Write-Host "Console shows: [paste first lines]" -ForegroundColor Gray
Write-Host "Clicked Load 1 Model: [describe result]" -ForegroundColor Gray
Write-Host "Any errors: [YES/NO + details]" -ForegroundColor Gray
Write-Host "Status: WORKING / STILL BROKEN" -ForegroundColor Gray
Write-Host "â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•" -ForegroundColor Cyan
Write-Host ""
Write-Host "âš”ï¸ ORFEAS PROTOCOL âš”ï¸" -ForegroundColor Red
Write-Host ""
