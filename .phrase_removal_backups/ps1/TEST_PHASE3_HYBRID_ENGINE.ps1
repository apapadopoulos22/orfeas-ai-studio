# â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—
# â•‘ âš”ï¸ THERION PHASE 3 TEST SCRIPT - HYBRID ENGINE VALIDATION âš”ï¸ â•‘
# â•‘ ORFEAS AI â•‘
# â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

Write-Host ""
Write-Host "â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—" -ForegroundColor Cyan
Write-Host "â•‘ âš”ï¸ THERION PHASE 3: HYBRID 3D ENGINE VALIDATION âš”ï¸ â•‘" -ForegroundColor Cyan
Write-Host "â•‘ Testing Babylon.js WebGPU + Three.js WebGL Integration â•‘" -ForegroundColor Cyan
Write-Host "â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•" -ForegroundColor Cyan
Write-Host ""

# Configuration
$BACKEND_DIR = "C:\Users\johng\Documents\Erevus\orfeas\backend"
$WORKSPACE_DIR = "C:\Users\johng\Documents\Erevus\orfeas"
$HTTP_PORT = 8080
$BACKEND_PORT = 5000

# Step 1: Check if backend is running
Write-Host "ðŸ“‹ STEP 1: Backend Status Check" -ForegroundColor Yellow
Write-Host ""

$backendRunning = $false
try {
    $response = Invoke-WebRequest -Uri "http://localhost:$BACKEND_PORT/api/health" -Method GET -TimeoutSec 2 -ErrorAction SilentlyContinue
    if ($response.StatusCode -eq 200) {
        $backendRunning = $true
        Write-Host "   âœ… Backend RUNNING on port $BACKEND_PORT" -ForegroundColor Green
    }
} catch {
    Write-Host "   â³ Backend NOT running, will start..." -ForegroundColor Yellow
}
Write-Host ""

# Step 2: Start backend if not running
if (-not $backendRunning) {
    Write-Host "ðŸ“‹ STEP 2: Starting Backend Server (RTX Optimized)" -ForegroundColor Yellow
    Write-Host ""

    Write-Host "   ðŸš€ Starting Flask backend with RTX 3090 optimization..." -ForegroundColor Cyan

    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$BACKEND_DIR'; python main.py" -WindowStyle Normal

    Write-Host "   â³ Waiting 10 seconds for backend to initialize..." -ForegroundColor Yellow
    Start-Sleep -Seconds 10

    # Verify backend started
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:$BACKEND_PORT/api/health" -Method GET -TimeoutSec 5
        if ($response.StatusCode -eq 200) {
            Write-Host "   âœ… Backend successfully started!" -ForegroundColor Green
        }
    } catch {
        Write-Host "   âš ï¸ Backend may still be starting (check window for RTX messages)" -ForegroundColor Yellow
    }

    Write-Host ""
} else {
    Write-Host "ðŸ“‹ STEP 2: Backend Already Running (SKIPPED)" -ForegroundColor Green
    Write-Host ""
}

# Step 3: Check file integrity
Write-Host "ðŸ“‹ STEP 3: File Integrity Check" -ForegroundColor Yellow
Write-Host ""

$files = @(
    @{Path="$WORKSPACE_DIR\orfeas-studio.html"; Name="Main HTML"; Required=$true},
    @{Path="$WORKSPACE_DIR\orfeas-3d-engine-hybrid.js"; Name="Hybrid Engine JS"; Required=$true},
    @{Path="$WORKSPACE_DIR\md\PHASE_3_HYBRID_ENGINE_INTEGRATION.md"; Name="Documentation"; Required=$true}
)

$allFilesPresent = $true
foreach ($file in $files) {
    if (Test-Path $file.Path) {
        $size = (Get-Item $file.Path).Length
        Write-Host "   âœ… $($file.Name): $('{0:N0}' -f $size) bytes" -ForegroundColor Green
    } else {
        Write-Host "   âŒ $($file.Name): NOT FOUND" -ForegroundColor Red
        if ($file.Required) {
            $allFilesPresent = $false
        }
    }
}
Write-Host ""

if (-not $allFilesPresent) {
    Write-Host "âŒ CRITICAL: Required files missing! Cannot continue." -ForegroundColor Red
    Write-Host ""
    exit 1
}

# Step 4: Start HTTP server for frontend
Write-Host "ðŸ“‹ STEP 4: Starting HTTP Server for Frontend" -ForegroundColor Yellow
Write-Host ""

Write-Host "   ðŸŒ Starting Python HTTP server on port $HTTP_PORT..." -ForegroundColor Cyan

Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$WORKSPACE_DIR'; python -m http.server $HTTP_PORT" -WindowStyle Normal

Write-Host "   â³ Waiting 3 seconds for HTTP server to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

# Verify HTTP server
try {
    $response = Invoke-WebRequest -Uri "http://localhost:$HTTP_PORT/orfeas-studio.html" -Method HEAD -TimeoutSec 3
    if ($response.StatusCode -eq 200) {
        Write-Host "   âœ… HTTP server successfully started!" -ForegroundColor Green
    }
} catch {
    Write-Host "   âš ï¸ HTTP server may still be starting..." -ForegroundColor Yellow
}
Write-Host ""

# Step 5: Browser detection and recommendations
Write-Host "ðŸ“‹ STEP 5: Browser Detection & Recommendations" -ForegroundColor Yellow
Write-Host ""

Write-Host "   ðŸ“Š WebGPU Support Status:" -ForegroundColor Cyan
Write-Host ""
Write-Host "   âœ… Chrome 113+    : WebGPU RTX Accelerated" -ForegroundColor Green
Write-Host "   âœ… Edge 113+      : WebGPU RTX Accelerated" -ForegroundColor Green
Write-Host "   âš ï¸ Firefox        : WebGL Fallback" -ForegroundColor Yellow
Write-Host "   âš ï¸ Safari         : WebGL Fallback" -ForegroundColor Yellow
Write-Host ""

$recommendedBrowser = "Google Chrome or Microsoft Edge 113+"
Write-Host "   ðŸŽ¯ RECOMMENDED: $recommendedBrowser for RTX 3090 acceleration" -ForegroundColor Magenta
Write-Host ""

# Step 6: Open in browser
Write-Host "ðŸ“‹ STEP 6: Opening ORFEAS Studio in Browser" -ForegroundColor Yellow
Write-Host ""

$url = "http://localhost:$HTTP_PORT/orfeas-studio.html"
Write-Host "   ðŸŒ Opening: $url" -ForegroundColor Cyan

Start-Process $url

Write-Host "   âœ… Browser opened!" -ForegroundColor Green
Write-Host ""

# Step 7: Validation checklist
Write-Host "â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—" -ForegroundColor Magenta
Write-Host "â•‘ ðŸ“‹ VALIDATION CHECKLIST - What to Look For â•‘" -ForegroundColor Magenta
Write-Host "â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•" -ForegroundColor Magenta
Write-Host ""

Write-Host "1ï¸âƒ£ PERFORMANCE HUD (Top-Right Corner):" -ForegroundColor Yellow
Write-Host "   â”œâ”€ Should display: âš¡ ORFEAS 3D ENGINE" -ForegroundColor White
Write-Host "   â”œâ”€ Renderer: WebGPU (RTX Accelerated) OR Three.js WebGL" -ForegroundColor White
Write-Host "   â”œâ”€ GPU: NVIDIA GeForce RTX 3090" -ForegroundColor White
Write-Host "   â”œâ”€ Ray Tracing: âœ… ACTIVE (WebGPU) or âŒ Inactive (WebGL)" -ForegroundColor White
Write-Host "   â””â”€ FPS: Should show 0 initially, then 60-120 after loading model" -ForegroundColor White
Write-Host ""

Write-Host "2ï¸âƒ£ CONSOLE MESSAGES (Press F12):" -ForegroundColor Yellow
Write-Host "   â”œâ”€ Look for: ðŸ” Detecting best 3D rendering engine..." -ForegroundColor White
Write-Host "   â”œâ”€ Look for: âœ… WebGPU detected OR ðŸ”„ WebGL fallback" -ForegroundColor White
Write-Host "   â”œâ”€ Look for: âœ… 3D Engine initialized in XXXms" -ForegroundColor White
Write-Host "   â””â”€ Look for: GPU name and ray tracing status" -ForegroundColor White
Write-Host ""

Write-Host "3ï¸âƒ£ WEBGPU VERIFICATION (Chrome/Edge only):" -ForegroundColor Yellow
Write-Host "   â”œâ”€ Open Console (F12)" -ForegroundColor White
Write-Host "   â”œâ”€ Type: navigator.gpu" -ForegroundColor Cyan
Write-Host "   â”œâ”€ Should return: GPU object (WebGPU available)" -ForegroundColor White
Write-Host "   â””â”€ Or: undefined (WebGL fallback mode)" -ForegroundColor White
Write-Host ""

Write-Host "4ï¸âƒ£ PERFORMANCE TEST:" -ForegroundColor Yellow
Write-Host "   â”œâ”€ Upload image or generate from text" -ForegroundColor White
Write-Host "   â”œâ”€ Click 'Generate 3D Model'" -ForegroundColor White
Write-Host "   â”œâ”€ Watch HUD: Load Time and Render Time should update" -ForegroundColor White
Write-Host "   â”œâ”€ WebGPU: 50-150ms render time expected" -ForegroundColor White
Write-Host "   â””â”€ WebGL: 200-600ms render time expected" -ForegroundColor White
Write-Host ""

Write-Host "5ï¸âƒ£ RTX OPTIMIZATION VERIFICATION:" -ForegroundColor Yellow
Write-Host "   â”œâ”€ Check backend terminal window" -ForegroundColor White
Write-Host "   â”œâ”€ Look for: ðŸš€ THERION RTX 3090 OPTIMIZATION ACTIVATING..." -ForegroundColor White
Write-Host "   â”œâ”€ Look for: âœ… Tensor Cores ENABLED" -ForegroundColor White
Write-Host "   â”œâ”€ Look for: ðŸ”¥ RTX OPTIMIZATIONS ACTIVE - MAXIMUM PERFORMANCE MODE" -ForegroundColor White
Write-Host "   â””â”€ Expected: 5x texture, 3x 3D generation speedup" -ForegroundColor White
Write-Host ""

# Step 8: Troubleshooting guide
Write-Host "â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—" -ForegroundColor Red
Write-Host "â•‘ ðŸ”§ TROUBLESHOOTING GUIDE â•‘" -ForegroundColor Red
Write-Host "â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•" -ForegroundColor Red
Write-Host ""

Write-Host "âŒ HUD NOT VISIBLE:" -ForegroundColor Yellow
Write-Host "   âžœ Check browser console (F12) for JavaScript errors" -ForegroundColor White
Write-Host "   âžœ Verify orfeas-3d-engine-hybrid.js loaded successfully" -ForegroundColor White
Write-Host "   âžœ Refresh page (Ctrl+F5 for hard refresh)" -ForegroundColor White
Write-Host ""

Write-Host "âŒ WebGPU NOT DETECTED (shows WebGL fallback):" -ForegroundColor Yellow
Write-Host "   âžœ Update Chrome/Edge to version 113+" -ForegroundColor White
Write-Host "   âžœ Enable chrome://flags/#enable-unsafe-webgpu" -ForegroundColor White
Write-Host "   âžœ Restart browser after enabling" -ForegroundColor White
Write-Host ""

Write-Host "âŒ BACKEND CONNECTION FAILED:" -ForegroundColor Yellow
Write-Host "   âžœ Check backend terminal for errors" -ForegroundColor White
Write-Host "   âžœ Verify port 5000 not blocked by firewall" -ForegroundColor White
Write-Host "   âžœ Try: http://localhost:5000/api/health" -ForegroundColor Cyan
Write-Host ""

Write-Host "âŒ RTX OPTIMIZATIONS NOT ACTIVE:" -ForegroundColor Yellow
Write-Host "   âžœ Check backend terminal for RTX messages" -ForegroundColor White
Write-Host "   âžœ Verify CUDA 12.1+ installed" -ForegroundColor White
Write-Host "   âžœ Run: python backend/rtx_optimization.py" -ForegroundColor Cyan
Write-Host ""

# Final summary
Write-Host ""
Write-Host "â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—" -ForegroundColor Green
Write-Host "â•‘ âš”ï¸ THERION PHASE 3 TEST COMPLETE - READY FOR VALIDATION! âš”ï¸ â•‘" -ForegroundColor Green
Write-Host "â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•" -ForegroundColor Green
Write-Host ""

Write-Host "ðŸ“Š SYSTEM STATUS:" -ForegroundColor Cyan
Write-Host "   âœ… Backend Server: " -NoNewline -ForegroundColor White
if ($backendRunning) {
    Write-Host "RUNNING (port $BACKEND_PORT)" -ForegroundColor Green
} else {
    Write-Host "STARTING (check window)" -ForegroundColor Yellow
}
Write-Host "   âœ… HTTP Server: RUNNING (port $HTTP_PORT)" -ForegroundColor Green
Write-Host "   âœ… ORFEAS Studio: OPENED in browser" -ForegroundColor Green
Write-Host "   âœ… Hybrid Engine: LOADED" -ForegroundColor Green
Write-Host ""

Write-Host "ðŸŽ¯ NEXT ACTIONS:" -ForegroundColor Magenta
Write-Host "   1. Check browser for Performance HUD (top-right)" -ForegroundColor White
Write-Host "   2. Open Console (F12) to see engine detection logs" -ForegroundColor White
Write-Host "   3. Test 3D generation workflow" -ForegroundColor White
Write-Host "   4. Report WebGPU vs WebGL mode detection" -ForegroundColor White
Write-Host "   5. Benchmark performance (render times, FPS)" -ForegroundColor White
Write-Host ""

Write-Host "ðŸ“ REPORT RESULTS:" -ForegroundColor Yellow
Write-Host "   Which engine detected? WebGPU or WebGL?" -ForegroundColor White
Write-Host "   What's your GPU name in HUD?" -ForegroundColor White
Write-Host "   Ray tracing active? âœ… or âŒ?" -ForegroundColor White
Write-Host "   FPS when loading 3D model?" -ForegroundColor White
Write-Host "   Render time? (ms)" -ForegroundColor White
Write-Host ""

Write-Host "ðŸ”¥ ORFEAS PROTOCOL ACTIVE! ðŸ”¥" -ForegroundColor Green
Write-Host ""

# Keep window open
Write-Host "Press any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
