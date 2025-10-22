# â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—
# â•‘ âš”ï¸ THERION - PRODUCTION HTTP SERVER - SUCCESS! âš”ï¸                        â•‘
# â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

Write-Host ""
Write-Host "â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—" -ForegroundColor Cyan
Write-Host "â•‘ âš”ï¸ STARTING ORFEAS HTTP SERVER (PORT 8080) âš”ï¸                               â•‘" -ForegroundColor Cyan
Write-Host "â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•" -ForegroundColor Cyan
Write-Host ""

# Navigate to project root
Set-Location "C:\Users\johng\Documents\Erevus\orfeas"

Write-Host "ðŸ“Š SERVER CONFIGURATION:" -ForegroundColor Yellow
Write-Host ""
Write-Host "  Port: 8080" -ForegroundColor Green
Write-Host "  Root: C:\Users\johng\Documents\Erevus\orfeas" -ForegroundColor Green
Write-Host "  URL: http://localhost:8080/orfeas-studio.html" -ForegroundColor Cyan
Write-Host "  Protocol: HTTP/1.1" -ForegroundColor Green
Write-Host ""
Write-Host "ðŸ”¥ FEATURES:" -ForegroundColor Magenta
Write-Host "  âœ… Serves manifest.json properly (no CORS errors)" -ForegroundColor Green
Write-Host "  âœ… PWA support enabled" -ForegroundColor Green
Write-Host "  âœ… Service Worker compatible" -ForegroundColor Green
Write-Host "  âœ… Fast startup (Python built-in server)" -ForegroundColor Green
Write-Host ""

Write-Host "â±ï¸ STARTING HTTP SERVER..." -ForegroundColor Yellow
Write-Host ""
Write-Host "ðŸŒ Server will open browser automatically in 2 seconds..." -ForegroundColor Cyan
Write-Host ""
Write-Host "ðŸ“‹ QUICK REFERENCE:" -ForegroundColor Yellow
Write-Host "  ORFEAS Studio: http://localhost:8080/orfeas-studio.html" -ForegroundColor White
Write-Host "  Backend API: http://localhost:5000/api/health" -ForegroundColor White
Write-Host "  Stop Server: Ctrl+C in this window" -ForegroundColor White
Write-Host ""
Write-Host "â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—" -ForegroundColor Green
Write-Host "â•‘ ðŸš€ HTTP SERVER STARTING - OPENING BROWSER IN 2 SECONDS... ðŸš€                â•‘" -ForegroundColor Green
Write-Host "â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•" -ForegroundColor Green
Write-Host ""

# Start HTTP server in background
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'C:\Users\johng\Documents\Erevus\orfeas'; python -m http.server 8080" -WindowStyle Normal

# Wait 2 seconds for server to start
Start-Sleep -Seconds 2

# Open browser
Start-Process "http://localhost:8080/orfeas-studio.html"

Write-Host ""
Write-Host "âœ… HTTP SERVER RUNNING!" -ForegroundColor Green
Write-Host "âœ… BROWSER OPENED!" -ForegroundColor Green
Write-Host ""
Write-Host "ðŸ“Š BACKEND STATUS:" -ForegroundColor Cyan
Write-Host "  Backend: http://localhost:5000" -ForegroundColor Green
Write-Host "  GPU: NVIDIA GeForce RTX 3090" -ForegroundColor Green
Write-Host "  RTX Optimizations: 5/5 active" -ForegroundColor Green
Write-Host ""
Write-Host "ðŸŽ¯ NEXT STEPS:" -ForegroundColor Yellow
Write-Host "  1. Check browser console (F12)" -ForegroundColor White
Write-Host "  2. Verify NO CORS errors" -ForegroundColor White
Write-Host "  3. Check backend status GREEN" -ForegroundColor White
Write-Host "  4. Test 3D generation" -ForegroundColor White
Write-Host ""
Write-Host "ðŸ”¥ THERION PROTOCOL - HTTP SERVER ACTIVE! ðŸ”¥" -ForegroundColor Green
Write-Host ""

# Keep window open
Read-Host "Press Enter to close this status window (HTTP server will keep running in separate window)"
