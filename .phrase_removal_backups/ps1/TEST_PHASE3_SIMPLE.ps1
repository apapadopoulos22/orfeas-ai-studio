# THERION PHASE 3 - Quick Test Script
# Simplified version without special characters

Write-Host ""
Write-Host "THERION PHASE 3: HYBRID 3D ENGINE TEST" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Start backend if not running
Write-Host "1. Checking backend status..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5000/api/health" -Method GET -TimeoutSec 2 -ErrorAction SilentlyContinue
    Write-Host "   Backend RUNNING" -ForegroundColor Green
} catch {
    Write-Host "   Starting backend..." -ForegroundColor Yellow
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'C:\Users\johng\Documents\Erevus\orfeas\backend'; python main.py"
    Start-Sleep -Seconds 8
}

# Start HTTP server
Write-Host ""
Write-Host "2. Starting HTTP server on port 8080..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'C:\Users\johng\Documents\Erevus\orfeas'; python -m http.server 8080"
Start-Sleep -Seconds 3
Write-Host "   HTTP server RUNNING" -ForegroundColor Green

# Open browser
Write-Host ""
Write-Host "3. Opening ORFEAS Studio in browser..." -ForegroundColor Yellow
Start-Process "http://localhost:8080/orfeas-studio.html"
Write-Host "   Browser OPENED" -ForegroundColor Green

# Instructions
Write-Host ""
Write-Host "VALIDATION CHECKLIST:" -ForegroundColor Magenta
Write-Host "=====================" -ForegroundColor Magenta
Write-Host ""
Write-Host "1. Look for Performance HUD (top-right corner)" -ForegroundColor White
Write-Host "   - Should show: ORFEAS 3D ENGINE" -ForegroundColor Gray
Write-Host "   - Renderer type (WebGPU or WebGL)" -ForegroundColor Gray
Write-Host "   - GPU name" -ForegroundColor Gray
Write-Host "   - Ray tracing status" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Open Console (F12) and check for:" -ForegroundColor White
Write-Host "   - Detecting best 3D rendering engine..." -ForegroundColor Gray
Write-Host "   - WebGPU detected OR WebGL fallback" -ForegroundColor Gray
Write-Host "   - 3D Engine initialized message" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Test WebGPU detection (Console):" -ForegroundColor White
Write-Host "   Type: navigator.gpu" -ForegroundColor Cyan
Write-Host "   Result: Should show GPU object or undefined" -ForegroundColor Gray
Write-Host ""
Write-Host "4. Test performance:" -ForegroundColor White
Write-Host "   - Upload image or generate from text" -ForegroundColor Gray
Write-Host "   - Click Generate 3D Model" -ForegroundColor Gray
Write-Host "   - Watch HUD update with times" -ForegroundColor Gray
Write-Host ""
Write-Host "RECOMMENDED BROWSER:" -ForegroundColor Yellow
Write-Host "  Chrome 113+ or Edge 113+ for WebGPU support" -ForegroundColor White
Write-Host ""
Write-Host "PHASE 3 TEST READY!" -ForegroundColor Green
Write-Host ""
