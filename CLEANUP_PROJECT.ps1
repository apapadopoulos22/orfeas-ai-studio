<#
================================================================================
ORFEAS AI 2D->3D STUDIO - PROJECT CLEANUP UTILITY
================================================================================
ORFEAS AI

Description:
    Removes unnecessary files, old versions, temporary test files, and
    obsolete removal scripts from the ORFEAS project.

Usage:
    powershell -ExecutionPolicy Bypass -File .\CLEANUP_PROJECT.ps1

Categories:
    1. Old version files (0.15.0, 1.0.0, 2.3.0, etc.)
    2. Removal scripts (REMOVE_THERION_*, REMOVE_EREVUS_DEUSVULT.ps1)
    3. Test files (test_*.py, test_*.js, test_*.html)
    4. Temporary PowerShell scripts (TEST_*.ps1)
    5. Backup scripts (backup.ps1)
    6. Utility scripts (REMOVE_ALL_EMOJIS.py, create_test_image.py)

================================================================================
#>

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "   ORFEAS AI 2D->3D STUDIO - PROJECT CLEANUP UTILITY" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# Statistics
$filesDeleted = 0
$totalSize = 0
$errors = 0

# Define cleanup categories
$cleanupTargets = @{
    "Old Version Files" = @(
        "0.15.0", "0.17.0", "0.2.7", "0.20.0", "0.21.0", "0.41.0", "0.57.0",
        "1.0.0", "1.3.0", "1.4.0", "10.0.0", "11.0.0", "12.0.0", "13.4.0",
        "2.0.0", "2.13.0", "2.3.0", "2.31.0", "21.0.0", "23.0.0",
        "3.21.0", "3.7.0", "3.8.0", "4.0.0", "4.30.0", "4.65.0", "4.8.0",
        "5.15.0", "5.3.0", "5.8.0", "5.9.0", "8.14.0", "8.6.0"
    )
    "Removal Scripts" = @(
        "REMOVE_THERION_REFERENCES.ps1",
        "REMOVE_THERION_SIMPLE.ps1",
        "REMOVE_THERION_CLEAN.ps1",
        "REMOVE_THERION_FINAL.ps1",
        "REMOVE_EREVUS_DEUSVULT.ps1",
        "REMOVE_ALL_EMOJIS.py"
    )
    "Test Files - Python" = @(
        "test_diagnostic_quick.py",
        "test_direct_generation.py",
        "test_generation_direct.py",
        "test_optimized_generation.py",
        "test_phase2_integration.py",
        "test_quality_proper.py",
        "test_quality_quick.py",
        "test_real_3d_generation.py",
        "test_websocket_progress.py",
        "test_websocket_quick.py",
        "create_test_image.py"
    )
    "Test Files - JavaScript" = @(
        "test_extracted.js",
        "test_extracted2.js",
        "test_final_js.js"
    )
    "Test Files - HTML" = @(
        "test_phase2_optimizations.html",
        "test_phase3_optimizations.html",
        "test-orfeas-phase4-optimizations.html",
        "test-orfeas-phase10-optimizations.html",
        "test-orfeas-phase11-optimizations.html"
    )
    "Test Scripts - PowerShell" = @(
        "TEST_FILE_LOGGING.ps1",
        "TEST_PRODUCTION_DEPLOYMENT.ps1",
        "TEST_QUALITY_INTEGRATION.ps1"
    )
    "Utility Scripts" = @(
        "backup.ps1"
    )
}

Write-Host "[CLEANUP] Starting project cleanup..." -ForegroundColor Yellow
Write-Host ""

# Process each category
foreach ($category in $cleanupTargets.Keys) {
    Write-Host "[$category]" -ForegroundColor Cyan
    $categoryFiles = $cleanupTargets[$category]

    foreach ($fileName in $categoryFiles) {
        $filePath = Join-Path -Path $PSScriptRoot -ChildPath $fileName

        if (Test-Path $filePath) {
            try {
                $fileSize = (Get-Item $filePath).Length
                Remove-Item -Path $filePath -Force -ErrorAction Stop
                $filesDeleted++
                $totalSize += $fileSize
                Write-Host "  [OK] Deleted: $fileName ($([math]::Round($fileSize/1KB, 2)) KB)" -ForegroundColor Green
            }
            catch {
                $errors++
                Write-Host "  [FAIL] Failed to delete: $fileName - $($_.Exception.Message)" -ForegroundColor Red
            }
        }
        else {
            Write-Host "  [SKIP] Not found: $fileName" -ForegroundColor DarkGray
        }
    }
    Write-Host ""
}

# Summary
Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "                   CLEANUP COMPLETE" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Files Deleted:    $filesDeleted" -ForegroundColor Green
Write-Host "Space Freed:      $([math]::Round($totalSize/1KB, 2)) KB ($([math]::Round($totalSize/1MB, 2)) MB)" -ForegroundColor Green
Write-Host "Errors:           $errors" -ForegroundColor $(if ($errors -eq 0) { "Green" } else { "Red" })
Write-Host ""

if ($filesDeleted -gt 0) {
    Write-Host "[SUCCESS] Project cleanup completed successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "NEXT STEPS:" -ForegroundColor Yellow
    Write-Host "  1. Review remaining files: Get-ChildItem -Path . -File | Select-Object Name" -ForegroundColor White
    Write-Host "  2. Check git status: git status" -ForegroundColor White
    Write-Host "  3. Run tests: cd backend && pytest" -ForegroundColor White
    Write-Host "  4. Commit cleanup: git add . && git commit -m `"Clean up project`"" -ForegroundColor White
}
else {
    Write-Host "[INFO] No files were deleted (already clean or files not found)" -ForegroundColor Yellow
}

Write-Host ""
