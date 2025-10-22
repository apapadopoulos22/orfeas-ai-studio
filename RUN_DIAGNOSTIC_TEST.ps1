# DIAGNOSTIC TEST - Quality Integration
# This script restarts the backend with diagnostic logging enabled and runs quality test

Write-Host "" -ForegroundColor Cyan
Write-Host "     ORFEAS QUALITY INTEGRATION - DIAGNOSTIC TEST                     " -ForegroundColor Cyan
Write-Host "" -ForegroundColor Cyan
Write-Host ""

Write-Host "[STEP 1] Stopping any existing backend processes..." -ForegroundColor Yellow
Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.Path -like "*backend*" } | Stop-Process -Force
Start-Sleep -Seconds 2
Write-Host "    Backend processes stopped" -ForegroundColor Green
Write-Host ""

Write-Host "[STEP 2] Clearing output cache..." -ForegroundColor Yellow
Remove-Item backend/outputs/* -Recurse -Force -ErrorAction SilentlyContinue
Write-Host "    Cache cleared" -ForegroundColor Green
Write-Host ""

Write-Host "[STEP 3] Creating unique test image..." -ForegroundColor Yellow
python create_test_image.py temp/test_images/diagnostic_test.png
Write-Host ""

Write-Host "[STEP 4] Starting backend with DIAGNOSTIC LOGGING..." -ForegroundColor Yellow
Write-Host "   Environment:" -ForegroundColor Gray
Write-Host "     - FLASK_ENV=production" -ForegroundColor Gray
Write-Host "     - TESTING=0" -ForegroundColor Gray
Write-Host "     - GPU_MEMORY_LIMIT=0.8" -ForegroundColor Gray
Write-Host "     - DISABLE_RESULT_CACHE=1" -ForegroundColor Gray
Write-Host "     - LOG_LEVEL=INFO (diagnostic logs added to code)" -ForegroundColor Green
Write-Host ""

Write-Host "    WATCH FOR THESE LOG ENTRIES:" -ForegroundColor Cyan
Write-Host "     [DIAGNOSTIC] Processor loaded: <type>" -ForegroundColor Gray
Write-Host "     [DIAGNOSTIC] Full AI processor ready for requests!" -ForegroundColor Gray
Write-Host "     [DIAGNOSTIC] Using processor: <type>" -ForegroundColor Gray
Write-Host "     [DIAGNOSTIC] Quality metrics present: [...]" -ForegroundColor Gray
Write-Host ""

Write-Host "[STARTING] Backend server in new window..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", @"
cd backend
`$env:FLASK_ENV='production'
`$env:TESTING='0'
`$env:GPU_MEMORY_LIMIT='0.8'
`$env:DISABLE_RESULT_CACHE='1'
Write-Host '' -ForegroundColor Cyan
Write-Host '                   BACKEND - DIAGNOSTIC MODE                          ' -ForegroundColor Cyan
Write-Host '' -ForegroundColor Cyan
Write-Host ''
python main.py
"@

Write-Host ""
Write-Host "    Backend starting in new window" -ForegroundColor Green
Write-Host ""

Write-Host "[STEP 5] Waiting for backend to initialize..." -ForegroundColor Yellow
Write-Host "   Waiting 10 seconds for server to start..." -ForegroundColor Gray
Start-Sleep -Seconds 10

# Check if backend is responding
$backendReady = $false
for ($i = 1; $i -le 5; $i++) {
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:5000/health" -ErrorAction Stop
        if ($response.status -eq "healthy") {
            Write-Host "    Backend is responding!" -ForegroundColor Green
            $backendReady = $true
            break
        }
    }
    catch {
        Write-Host "   ⏳ Attempt $i/5 - Backend not ready yet..." -ForegroundColor Gray
        Start-Sleep -Seconds 2
    }
}

if (-not $backendReady) {
    Write-Host "    Backend failed to respond after 20 seconds" -ForegroundColor Red
    Write-Host "   Check backend window for errors" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "[STEP 6] Waiting for models to load..." -ForegroundColor Yellow
Write-Host "   Hunyuan3D models take 30-40 seconds to load" -ForegroundColor Gray
Write-Host "   Waiting 45 seconds to be safe..." -ForegroundColor Gray
Write-Host ""

for ($i = 45; $i -gt 0; $i--) {
    Write-Host "   ⏳ $i seconds remaining..." -ForegroundColor Gray
    Start-Sleep -Seconds 1
}

Write-Host ""
Write-Host "    Wait complete - models should be loaded" -ForegroundColor Green
Write-Host ""

Write-Host "[STEP 7] Running quality integration test..." -ForegroundColor Yellow
Write-Host ""
Write-Host "" -ForegroundColor Green
Write-Host "                  EXECUTING QUALITY TEST                              " -ForegroundColor Green
Write-Host "" -ForegroundColor Green
Write-Host ""

# Update test to use diagnostic image
$testScript = Get-Content test_quality_quick.py -Raw
$testScript = $testScript -replace "temp/test_images/quality_final_test\.png", "temp/test_images/diagnostic_test.png"
$testScript = $testScript -replace "quality_final\.png", "diagnostic.png"
$testScript | Set-Content test_quality_quick_diagnostic.py

python test_quality_quick_diagnostic.py

Write-Host ""
Write-Host "" -ForegroundColor Cyan
Write-Host "                     DIAGNOSTIC TEST COMPLETE                         " -ForegroundColor Cyan
Write-Host "" -ForegroundColor Cyan
Write-Host ""
Write-Host "NEXT STEPS:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Check test output above for quality_metrics" -ForegroundColor White
Write-Host "2. Review backend window for [DIAGNOSTIC] log entries" -ForegroundColor White
Write-Host "3. Look for:" -ForegroundColor White
Write-Host "   - Which processor type was used?" -ForegroundColor Gray
Write-Host "   - Were quality metrics generated?" -ForegroundColor Gray
Write-Host "   - Any errors during generation?" -ForegroundColor Gray
Write-Host ""
Write-Host "The backend is still running in the other window." -ForegroundColor Yellow
Write-Host "Keep it open to run additional tests if needed." -ForegroundColor Yellow
Write-Host ""
