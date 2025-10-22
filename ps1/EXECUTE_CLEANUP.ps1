# 
#                     ORFEAS DIRECTORY CLEANUP SCRIPT                           
#                   Automated removal of redundant files                        
# 

Write-Host "" -ForegroundColor Cyan
Write-Host "                ORFEAS DIRECTORY CLEANUP AUTOMATION                       " -ForegroundColor Cyan
Write-Host "" -ForegroundColor Cyan
Write-Host ""

$totalDeleted = 0
$totalErrors = 0

# Phase 1: Create Archive Directory
Write-Host "[Phase 1] Creating ARCHIVE directory..." -ForegroundColor Yellow
try {
    New-Item -ItemType Directory -Path "ARCHIVE" -Force | Out-Null
    Write-Host " ARCHIVE directory created" -ForegroundColor Green
}
catch {
    Write-Host "  ARCHIVE directory already exists or error: $_" -ForegroundColor Yellow
}
Write-Host ""

# Phase 2: Archive Historical Scripts
Write-Host "[Phase 2] Archiving historical scripts..." -ForegroundColor Yellow
$archiveFiles = @(
    "cleanup_unnecessary_files.py",
    "setup_ultra_performance.py"
)

foreach ($file in $archiveFiles) {
    if (Test-Path $file) {
        try {
            Move-Item $file "ARCHIVE/" -Force
            Write-Host " Archived: $file" -ForegroundColor Green
        }
        catch {
            Write-Host " Failed to archive: $file" -ForegroundColor Red
            $totalErrors++
        }
    }
    else {
        Write-Host "  Not found: $file" -ForegroundColor Yellow
    }
}
Write-Host ""

# Phase 3: Delete Redundant Startup Scripts
Write-Host "[Phase 3] Removing redundant startup scripts..." -ForegroundColor Yellow
$startupScripts = @(
    " START ORFEAS.bat",
    " START ORFEAS COMPLETE.bat",
    " START ORFEAS SERVICE.bat",
    "START_ORFEAS_SERVICE.bat",
    "START_ORFEAS_SERVICE.ps1",
    "START_ORFEAS_COMPLETE.bat",
    "START_ORFEAS_COMPLETE.ps1",
    "start_orfeas_ai.bat",
    "start_orfeas_ai.ps1",
    "start_orfeas.bat",
    "start_orfeas.ps1",
    "start_ultra.bat",
    "START_BACKEND_SAFE.bat",
    "START_BACKEND_FROM_BROWSER.bat",
    "start.bat",
    "start.ps1"
)

foreach ($script in $startupScripts) {
    if (Test-Path $script) {
        try {
            Remove-Item $script -Force
            Write-Host " Deleted: $script" -ForegroundColor Green
            $totalDeleted++
        }
        catch {
            Write-Host " Failed to delete: $script" -ForegroundColor Red
            $totalErrors++
        }
    }
}
Write-Host ""

# Phase 4: Delete Old Documentation
Write-Host "[Phase 4] Removing old documentation files..." -ForegroundColor Yellow
$oldDocs = @(
    "COMPLETE_NGROK_SETUP.md",
    "CONNECTION_FIX_GUIDE.md",
    "CONSOLIDATION_COMPLETE.md",
    "COMPREHENSIVE_TESTING_REPORT.md",
    "COMPLETE_WORKFLOW_SUCCESS.md",
    "COMPLETE_AUTO_START_SYSTEM.md",
    "MISSION_COMPLETE_PREVIEW_FIX.md",
    "MISSION_COMPLETE_FULLY_AUTOMATIC.md",
    "MISSION_COMPLETE_FORMAT_TESTING.md",
    "MISSION_COMPLETE_BROWSER_AUTO_START.md",
    "MISSION_ACCOMPLISHED_UNIVERSAL.md",
    "IMMEDIATE_CONNECTION_FIX.md",
    "IMAGE_PREVIEW_FLOW_DIAGRAM.md",
    "WORKFLOW_TEST_FINDINGS.md",
    "UNIVERSAL_AUTO_START_COMPLETE.md",
    "UI_UPGRADE_SMALL_STATUS_INDICATOR.md",
    "TQM_COMPLETE_SUMMARY.md",
    "TOTAL_QUALITY_MANAGEMENT_REPORT.md",
    "TIMEOUT_AND_DUPLICATE_ANALYSIS.md",
    "SYSTEM_OPTIMIZATION_COMPLETE.md",
    "SESSION_COMPLETION_REPORT.md",
    "SESSION_6_COMPLETE_SUMMARY.md",
    "SECURITY_HARDENING_COMPLETE.md",
    "PREVIEW_FIX_COMPLETE.md",
    "POWERFUL_3D_ENGINE_COMPLETE.md",
    "POWERFUL_3D_ENGINE.md",
    "ORFEAS_QUICK_START.md",
    "QUICK_START.md",
    "NGROK_SETUP_GUIDE.md",
    "NETLIFY_UPLOAD_FIX.md",
    "NETLIFY_DEPLOYMENT_COMPLETE.md",
    "MISSION_COMPLETE_SECURITY_BYPASS.md",
    "FULLY_AUTOMATIC_STARTUP.md",
    "FRONTEND_STL_WORKFLOW_SUCCESS.md",
    "FILE_NAMING_CONVENTIONS.md",
    "FILES_CHANGED_SUMMARY.md",
    "BROWSER_AUTO_START_BACKEND.md",
    "AUTO_STARTUP_SUCCESS.md",
    "AUTO_STARTUP_GUIDE.md",
    "ENDPOINT_DIAGNOSTICS_REPORT.md"
)

foreach ($doc in $oldDocs) {
    if (Test-Path $doc) {
        try {
            Remove-Item $doc -Force
            Write-Host " Deleted: $doc" -ForegroundColor Green
            $totalDeleted++
        }
        catch {
            Write-Host " Failed to delete: $doc" -ForegroundColor Red
            $totalErrors++
        }
    }
}
Write-Host ""

# Phase 5: Delete Old Test/Config Files
Write-Host "[Phase 5] Removing old test/config files..." -ForegroundColor Yellow
$oldTestFiles = @(
    "NETLIFY_DEPLOY_GUIDE.txt",
    "connection-test.html",
    "ORFEAS_MAKERS_PORTAL.html",
    "cleanup_report.json"
)

foreach ($file in $oldTestFiles) {
    if (Test-Path $file) {
        try {
            Remove-Item $file -Force
            Write-Host " Deleted: $file" -ForegroundColor Green
            $totalDeleted++
        }
        catch {
            Write-Host " Failed to delete: $file" -ForegroundColor Red
            $totalErrors++
        }
    }
}
Write-Host ""

# Phase 6: Clean Backend Directory
Write-Host "[Phase 6] Cleaning backend directory..." -ForegroundColor Yellow
$backendScripts = @(
    "backend/start_server.bat",
    "backend/start_server.ps1",
    "backend/start_backend.bat",
    "backend/start_backend.ps1",
    "backend/setup_gpu.bat",
    "backend/setup_gpu.ps1"
)

foreach ($script in $backendScripts) {
    if (Test-Path $script) {
        try {
            Remove-Item $script -Force
            Write-Host " Deleted: $script" -ForegroundColor Green
            $totalDeleted++
        }
        catch {
            Write-Host " Failed to delete: $script" -ForegroundColor Red
            $totalErrors++
        }
    }
}
Write-Host ""

# Final Summary
Write-Host "" -ForegroundColor Cyan
Write-Host "                          CLEANUP COMPLETE                                " -ForegroundColor Cyan
Write-Host "" -ForegroundColor Cyan
Write-Host ""
Write-Host " CLEANUP STATISTICS:" -ForegroundColor White
Write-Host "    Files deleted: $totalDeleted" -ForegroundColor Green
Write-Host "    Errors: $totalErrors" -ForegroundColor Red
Write-Host ""
Write-Host " Essential files preserved:" -ForegroundColor White
Write-Host "    README.md" -ForegroundColor Green
Write-Host "    SESSION_6_COMPLETE_SUCCESS.md" -ForegroundColor Green
Write-Host "    PORT_FIX_SUCCESS_REPORT.md" -ForegroundColor Green
Write-Host "    START_ORFEAS_AUTO.ps1 (PRIMARY startup script)" -ForegroundColor Green
Write-Host "    START_ORFEAS_AUTO.bat (wrapper)" -ForegroundColor Green
Write-Host "    orfeas-studio.html" -ForegroundColor Green
Write-Host "    frontend_server.py" -ForegroundColor Green
Write-Host "    orfeas_service.py" -ForegroundColor Green
Write-Host ""
Write-Host " Archived files moved to: ARCHIVE/" -ForegroundColor Cyan
Write-Host ""
Write-Host " ORFEAS is now clean and organized!" -ForegroundColor Green
Write-Host ""
