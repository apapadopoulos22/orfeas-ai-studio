Write-Host "" -ForegroundColor Red
Write-Host "                                                                              " -ForegroundColor Red
Write-Host "            THERION PROTOCOL - HARD REFRESH REQUIRED!                     " -ForegroundColor Red
Write-Host "                                                                              " -ForegroundColor Red
Write-Host "" -ForegroundColor Red
Write-Host ""
Write-Host " CRITICAL: Browser cache causing issues!" -ForegroundColor Yellow
Write-Host ""
Write-Host "DO THIS NOW:" -ForegroundColor Cyan
Write-Host "1. In the browser with test page open" -ForegroundColor White
Write-Host "2. Press CTRL+SHIFT+R (hard reload)" -ForegroundColor Yellow -BackgroundColor Black
Write-Host "3. Or press F5 multiple times" -ForegroundColor White
Write-Host "4. Or close tab and reopen file" -ForegroundColor White
Write-Host ""
Write-Host "Opening fresh copy now..." -ForegroundColor Green
Start-Sleep -Seconds 2
Start-Process test-orfeas-studio-ultimate.html
Write-Host " File opened - Now press CTRL+SHIFT+R in browser!" -ForegroundColor Green
