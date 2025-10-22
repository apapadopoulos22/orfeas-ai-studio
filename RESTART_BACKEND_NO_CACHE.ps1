# RESTART BACKEND WITH CACHING DISABLED (FOR QUALITY TEST)
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host " RESTARTING BACKEND - CACHING DISABLED FOR QUALITY TEST" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[INFO] Stopping any existing backend processes..." -ForegroundColor Yellow
Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.Path -like "*backend*" } | Stop-Process -Force
Start-Sleep -Seconds 2

Write-Host "[INFO] Starting backend in production mode with caching OFF..." -ForegroundColor Yellow
Write-Host "       Environment:" -ForegroundColor Gray
Write-Host "         - FLASK_ENV=production" -ForegroundColor Gray
Write-Host "         - TESTING=0" -ForegroundColor Gray
Write-Host "         - GPU_MEMORY_LIMIT=0.8" -ForegroundColor Gray
Write-Host "         - DISABLE_RESULT_CACHE=1  (NEW)" -ForegroundColor Green
Write-Host ""

cd backend
$env:FLASK_ENV = 'production'
$env:TESTING = '0'
$env:GPU_MEMORY_LIMIT = '0.8'
$env:DISABLE_RESULT_CACHE = '1'

Write-Host "[STARTING] Backend server..." -ForegroundColor Cyan
Write-Host ""
python main.py
