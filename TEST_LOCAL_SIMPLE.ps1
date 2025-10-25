# ORFEAS AI - Simple Local Testing Script

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "ORFEAS AI - Local Testing" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Stop backend
Write-Host "[1/5] Stopping existing backend..." -ForegroundColor Yellow
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2
Write-Host "[OK] Backend stopped" -ForegroundColor Green

# Step 2: Start Docker
Write-Host "[2/5] Starting Docker services..." -ForegroundColor Yellow
docker-compose up -d redis
Start-Sleep -Seconds 3
Write-Host "[OK] Docker services started" -ForegroundColor Green

# Step 3: Install dependencies
Write-Host "[3/5] Installing dependencies..." -ForegroundColor Yellow
cd backend
pip install -q flask flask-cors flask-socketio psutil torch redis sqlalchemy psycopg2-binary
Write-Host "[OK] Dependencies installed" -ForegroundColor Green

# Step 4: Start backend
Write-Host "[4/5] Starting backend server..." -ForegroundColor Yellow
$backendJob = Start-Job -ScriptBlock {
    Set-Location "C:\Users\johng\Documents\oscar\backend"
    python main.py
}
Start-Sleep -Seconds 10

# Step 5: Check health
Write-Host "[5/5] Checking backend health..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "http://localhost:5000/health" -TimeoutSec 5
    Write-Host "[OK] Backend is running: http://localhost:5000" -ForegroundColor Green
    Write-Host ""
    Write-Host "Backend Status:" -ForegroundColor White
    Write-Host "  URL: http://localhost:5000" -ForegroundColor Cyan
    Write-Host "  Health: OK" -ForegroundColor Green
    Write-Host ""
    Write-Host "To stop: Get-Process python | Stop-Process -Force" -ForegroundColor Yellow
}
catch {
    Write-Host "[ERROR] Backend failed to start" -ForegroundColor Red
    Stop-Job $backendJob -ErrorAction SilentlyContinue
    Remove-Job $backendJob -ErrorAction SilentlyContinue
    exit 1
}
