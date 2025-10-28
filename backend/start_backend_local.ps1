# Local Backend Startup Script for ORFEAS AI Studio (Windows PowerShell)
# Run from backend directory: .\start_backend_local.ps1

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "ORFEAS AI - Local Backend Startup" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Check Python version
Write-Host "[1/4] Checking Python version..." -ForegroundColor Yellow
try {
    $python_version = python --version 2>&1
    Write-Host "✓ $python_version" -ForegroundColor Green
}
catch {
    Write-Host "✗ Python not found. Please install Python 3.10+" -ForegroundColor Red
    exit 1
}

# Install dependencies
Write-Host "[2/4] Installing dependencies..." -ForegroundColor Yellow
python -m pip install --upgrade pip wheel setuptools | Out-Null
pip install -r requirements.txt | Out-Null
Write-Host "✓ Dependencies installed" -ForegroundColor Green

# Set environment variables
Write-Host "[3/4] Configuring environment..." -ForegroundColor Yellow
$env:DEVICE = if ($env:DEVICE) { $env:DEVICE } else { "cpu" }
$env:FLASK_ENV = if ($env:FLASK_ENV) { $env:FLASK_ENV } else { "development" }
$env:FLASK_DEBUG = if ($env:FLASK_DEBUG) { $env:FLASK_DEBUG } else { "1" }
$env:LOCAL_LLM_ENABLED = if ($env:LOCAL_LLM_ENABLED) { $env:LOCAL_LLM_ENABLED } else { "false" }
$env:REDIS_CACHE_ENABLED = if ($env:REDIS_CACHE_ENABLED) { $env:REDIS_CACHE_ENABLED } else { "false" }
$env:ENABLE_MONITORING = if ($env:ENABLE_MONITORING) { $env:ENABLE_MONITORING } else { "false" }
$env:PORT = if ($env:PORT) { $env:PORT } else { "5000" }

Write-Host "  - DEVICE: $($env:DEVICE)" -ForegroundColor Cyan
Write-Host "  - FLASK_ENV: $($env:FLASK_ENV)" -ForegroundColor Cyan
Write-Host "  - PORT: $($env:PORT)" -ForegroundColor Cyan
Write-Host "✓ Environment configured" -ForegroundColor Green

# Start backend
Write-Host "[4/4] Starting backend server..." -ForegroundColor Yellow
Write-Host ""
Write-Host "Backend starting on http://127.0.0.1:$($env:PORT)" -ForegroundColor Green
Write-Host "Press Ctrl+C to stop" -ForegroundColor Gray
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

python main.py
