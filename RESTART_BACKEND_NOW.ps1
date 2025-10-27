# ============================================================================
# ORFEAS Backend Restart Script
# Purpose: Kill old Python process and start fresh with CORS fixes
# ============================================================================

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "ORFEAS Backend Restart Sequence" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Find and kill old Python processes
Write-Host "[1/4] Finding old Python processes..." -ForegroundColor Yellow
$pythonProcesses = Get-Process -Name python* -ErrorAction SilentlyContinue

if ($pythonProcesses) {
    Write-Host "Found Python processes: $($pythonProcesses.Id -join ', ')" -ForegroundColor Yellow

    foreach ($proc in $pythonProcesses) {
        Write-Host "  Stopping PID $($proc.Id)..." -ForegroundColor Red
        Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
    }

    Write-Host "✓ Old processes killed" -ForegroundColor Green
    Start-Sleep -Seconds 2
}
else {
    Write-Host "No existing Python processes found" -ForegroundColor Green
}

Write-Host ""

# Step 2: Navigate to backend directory
Write-Host "[2/4] Navigating to backend directory..." -ForegroundColor Yellow
$backendPath = "c:\Users\johng\Documents\oscar\backend"
if (Test-Path $backendPath) {
    Set-Location $backendPath
    Write-Host "✓ In backend directory" -ForegroundColor Green
}
else {
    Write-Host "✗ Backend directory not found at $backendPath" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Step 3: Start Python backend
Write-Host "[3/4] Starting backend with Python..." -ForegroundColor Yellow
Write-Host "Running: python main.py" -ForegroundColor Cyan
Write-Host ""
Write-Host "Waiting for startup messages (look for 'Running on http://127.0.0.1:5000')..." -ForegroundColor Yellow
Write-Host ""

# Start Python process and keep it running
python main.py
