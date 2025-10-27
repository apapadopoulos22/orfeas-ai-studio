# ============================================================================
# ðŸ”¥ THERION FRONTEND AUTO-CONFIGURATOR FOR PUBLIC BACKEND
# ============================================================================
# Automatically updates orfeas-studio.html with public backend URL
# Reads from PUBLIC_BACKEND_URL.txt (created by deployment script)
# ============================================================================

Write-Host ""
Write-Host "â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—" -ForegroundColor Cyan
Write-Host "â•‘ âš”ï¸ THERION FRONTEND PUBLIC URL CONFIGURATOR âš”ï¸                              â•‘" -ForegroundColor Cyan
Write-Host "â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•" -ForegroundColor Cyan
Write-Host ""

# Check if public URL file exists
if (-not (Test-Path "PUBLIC_BACKEND_URL.txt")) {
    Write-Host "âŒ PUBLIC_BACKEND_URL.txt not found" -ForegroundColor Red
    Write-Host ""
    Write-Host "MANUAL CONFIGURATION REQUIRED:" -ForegroundColor Yellow
    Write-Host "   1. Run: .\DEPLOY_BACKEND_PUBLIC.ps1" -ForegroundColor White
    Write-Host "   2. Copy the public URL" -ForegroundColor White
    Write-Host "   3. Update orfeas-studio.html manually" -ForegroundColor White
    Write-Host ""
    Write-Host "OR enter public URL manually:" -ForegroundColor Cyan
    $manualUrl = Read-Host "Enter backend URL (or press Enter to cancel)"

    if ($manualUrl) {
        $publicUrl = $manualUrl.Trim()
    } else {
        exit 1
    }
} else {
    $publicUrl = Get-Content "PUBLIC_BACKEND_URL.txt" -Raw
    $publicUrl = $publicUrl.Trim()

    Write-Host "âœ… Public URL detected: $publicUrl" -ForegroundColor Green
}

Write-Host ""
Write-Host "ðŸ” Searching for BACKEND_URL in orfeas-studio.html..." -ForegroundColor Yellow

# Read orfeas-studio.html
$htmlContent = Get-Content "orfeas-studio.html" -Raw

# Find BACKEND_URL config line
if ($htmlContent -match "BACKEND_URL:\s*['\"]([^'\"]+)['\"]") {
    $currentUrl = $Matches[1]
    Write-Host "   Current URL: $currentUrl" -ForegroundColor White
    Write-Host "   New URL: $publicUrl" -ForegroundColor Cyan

    # Replace URL
    $newContent = $htmlContent -replace "(BACKEND_URL:\s*['\"])([^'\"]+)(['\"])", "`$1$publicUrl`$3"

    # Save updated file
    $newContent | Out-File -FilePath "orfeas-studio.html" -Encoding UTF8 -NoNewline

    Write-Host ""
    Write-Host "âœ… Frontend updated successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "ðŸ”„ CHANGES MADE:" -ForegroundColor Cyan
    Write-Host "   File: orfeas-studio.html" -ForegroundColor White
    Write-Host "   Config: ORFEAS_CONFIG.BACKEND_URL" -ForegroundColor White
    Write-Host "   Old: $currentUrl" -ForegroundColor Red
    Write-Host "   New: $publicUrl" -ForegroundColor Green
    Write-Host ""
    Write-Host "âš ï¸ REFRESH BROWSER:" -ForegroundColor Yellow
    Write-Host "   Press Ctrl+Shift+R to hard reload" -ForegroundColor White
    Write-Host "   Or close and reopen http://localhost:8080/orfeas-studio.html" -ForegroundColor White
    Write-Host ""
    Write-Host "ðŸŽ‰ Frontend now connected to public backend!" -ForegroundColor Green

} else {
    Write-Host "âŒ Could not find BACKEND_URL in orfeas-studio.html" -ForegroundColor Red
    Write-Host ""
    Write-Host "MANUAL UPDATE REQUIRED:" -ForegroundColor Yellow
    Write-Host "   1. Open orfeas-studio.html in editor" -ForegroundColor White
    Write-Host "   2. Find: ORFEAS_CONFIG section" -ForegroundColor White
    Write-Host "   3. Update: BACKEND_URL: '$publicUrl'" -ForegroundColor White
    Write-Host ""
}

Write-Host ""
Write-Host "ðŸ”¥ Configuration Complete!" -ForegroundColor Cyan
Write-Host ""
