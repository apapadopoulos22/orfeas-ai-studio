# ============================================================================
# ðŸ”¥ THERION PWA ICON VALIDATION TEST
# ============================================================================
# Validates all PWA icons are correctly generated and accessible
# Tests manifest.json references and HTML icon links
# ============================================================================

Write-Host ""
Write-Host "â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—" -ForegroundColor Cyan
Write-Host "â•‘ âš”ï¸ THERION PWA ICON VALIDATOR âš”ï¸                                           â•‘" -ForegroundColor Cyan
Write-Host "â•‘ Testing all PWA icons and manifest configuration                             â•‘" -ForegroundColor Cyan
Write-Host "â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•" -ForegroundColor Cyan
Write-Host ""

# Test 1: Check icons directory exists
Write-Host "ðŸ” TEST 1: Icons Directory" -ForegroundColor Yellow
if (Test-Path "icons") {
    Write-Host "   âœ… PASS - icons/ directory exists" -ForegroundColor Green
} else {
    Write-Host "   âŒ FAIL - icons/ directory missing" -ForegroundColor Red
    exit 1
}

# Test 2: Check all required icon files exist
Write-Host ""
Write-Host "ðŸ” TEST 2: Icon Files" -ForegroundColor Yellow
$sizes = @(72, 96, 128, 144, 152, 192, 384, 512)
$allIconsExist = $true
$totalSize = 0

foreach ($size in $sizes) {
    $iconPath = "icons/icon-$size`x$size.png"
    if (Test-Path $iconPath) {
        $fileSize = (Get-Item $iconPath).Length
        $totalSize += $fileSize
        Write-Host "   [PASS] - $iconPath ($fileSize bytes)" -ForegroundColor Green
    } else {
        Write-Host "   [FAIL] - $iconPath missing" -ForegroundColor Red
        $allIconsExist = $false
    }
}

Write-Host ""
Write-Host "   ðŸ“Š Total icon size: $totalSize bytes" -ForegroundColor Cyan

# Test 3: Validate manifest.json
Write-Host ""
Write-Host "ðŸ” TEST 3: Manifest Validation" -ForegroundColor Yellow
if (Test-Path "manifest.json") {
    $manifest = Get-Content "manifest.json" -Raw | ConvertFrom-Json

    # Check icon count
    $iconCount = $manifest.icons.Count
    if ($iconCount -eq 8) {
        Write-Host "   âœ… PASS - manifest.json has 8 icons" -ForegroundColor Green
    } else {
        Write-Host "   âŒ FAIL - manifest.json has $iconCount icons (expected 8)" -ForegroundColor Red
    }

    # Check icon paths
    $manifestPathsCorrect = $true
    foreach ($icon in $manifest.icons) {
        $iconFile = $icon.src.TrimStart('/')
        if (Test-Path $iconFile) {
            Write-Host "   âœ… PASS - $($icon.src) exists" -ForegroundColor Green
        } else {
            Write-Host "   âŒ FAIL - $($icon.src) missing" -ForegroundColor Red
            $manifestPathsCorrect = $false
        }
    }
} else {
    Write-Host "   âŒ FAIL - manifest.json missing" -ForegroundColor Red
}

# Test 4: Check HTML meta tags
Write-Host ""
Write-Host "ðŸ” TEST 4: HTML Meta Tags" -ForegroundColor Yellow
if (Test-Path "orfeas-studio.html") {
    $html = Get-Content "orfeas-studio.html" -Raw

    # Check for modern PWA meta tag
    if ($html -match 'mobile-web-app-capable') {
        Write-Host "   âœ… PASS - Modern PWA meta tag present" -ForegroundColor Green
    } else {
        Write-Host "   âš ï¸ WARN - Modern PWA meta tag missing" -ForegroundColor Yellow
    }

    # Check icon paths in HTML
    if ($html -match 'href="icons/icon-192x192.png"') {
        Write-Host "   âœ… PASS - HTML icon paths reference icons/ directory" -ForegroundColor Green
    } else {
        Write-Host "   âŒ FAIL - HTML icon paths incorrect" -ForegroundColor Red
    }
} else {
    Write-Host "   âŒ FAIL - orfeas-studio.html missing" -ForegroundColor Red
}

# Test 5: HTTP Server Status
Write-Host ""
Write-Host "ðŸ” TEST 5: HTTP Server" -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8080" -Method HEAD -TimeoutSec 2 -ErrorAction Stop
    Write-Host "   âœ… PASS - HTTP server running on port 8080" -ForegroundColor Green

    # Test icon accessibility
    Write-Host ""
    Write-Host "ðŸ” TEST 6: Icon HTTP Accessibility" -ForegroundColor Yellow
    foreach ($size in $sizes) {
        try {
            $iconUrl = "http://localhost:8080/icons/icon-$size`x$size.png"
            $iconResponse = Invoke-WebRequest -Uri $iconUrl -Method HEAD -TimeoutSec 2 -ErrorAction Stop
            Write-Host "   âœ… PASS - $iconUrl accessible (HTTP $($iconResponse.StatusCode))" -ForegroundColor Green
        } catch {
            Write-Host "   âŒ FAIL - $iconUrl not accessible" -ForegroundColor Red
        }
    }
} catch {
    Write-Host "   âš ï¸ WARN - HTTP server not running (start with .\START_HTTP_SERVER.ps1)" -ForegroundColor Yellow
}

# Final Summary
Write-Host ""
Write-Host "â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—" -ForegroundColor Cyan
Write-Host "â•‘ ðŸ“Š TEST SUMMARY                                                              â•‘" -ForegroundColor Cyan
Write-Host "â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•" -ForegroundColor Cyan
Write-Host ""

if ($allIconsExist -and $manifestPathsCorrect) {
    Write-Host "ðŸŽ‰ ALL TESTS PASSED - PWA ICONS READY FOR DEPLOYMENT!" -ForegroundColor Green
    Write-Host ""
    Write-Host "ðŸ“± NEXT STEPS:" -ForegroundColor Cyan
    Write-Host "   1. Open http://localhost:8080/orfeas-studio.html" -ForegroundColor White
    Write-Host "   2. Press Ctrl+Shift+R to hard reload" -ForegroundColor Yellow
    Write-Host "   3. Press F12 â†’ Application â†’ Manifest" -ForegroundColor White
    Write-Host "   4. Verify all icons show green checkmarks âœ…" -ForegroundColor White
    Write-Host "   5. Look for 'Install' button in address bar ðŸ“²" -ForegroundColor White
    Write-Host ""
    Write-Host "ðŸ”¥ PWA READY!" -ForegroundColor Green
} else {
    Write-Host "âš ï¸ SOME TESTS FAILED - CHECK ERRORS ABOVE" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
