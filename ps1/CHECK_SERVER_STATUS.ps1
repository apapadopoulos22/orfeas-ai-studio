# ORFEAS Server Diagnostic Script
# Checks all dependencies and server status

Write-Host "â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—" -ForegroundColor Cyan
Write-Host "â•‘     âš”ï¸ THERION - ORFEAS SERVER DIAGNOSTICS âš”ï¸            â•‘" -ForegroundColor Cyan
Write-Host "â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•" -ForegroundColor Cyan
Write-Host ""

# Change to project directory
Set-Location "C:\Users\johng\Documents\Erevus\orfeas"

Write-Host "ðŸ” CHECKING SYSTEM STATUS..." -ForegroundColor Yellow
Write-Host ""

# Check Python virtual environment
Write-Host "1ï¸âƒ£ Python Virtual Environment:" -ForegroundColor Cyan
if (Test-Path ".\.venv\Scripts\python.exe") {
    Write-Host "   âœ… Virtual environment found" -ForegroundColor Green

    # Get Python version
    $pythonVersion = & ".\.venv\Scripts\python.exe" --version 2>&1
    Write-Host "   ðŸ“Œ Version: $pythonVersion" -ForegroundColor White

    # Count installed packages
    $packageCount = (& ".\.venv\Scripts\python.exe" -m pip list 2>&1 | Measure-Object -Line).Lines - 2
    Write-Host "   ðŸ“¦ Installed packages: $packageCount" -ForegroundColor White

    if ($packageCount -lt 20) {
        Write-Host "   âš ï¸ WARNING: Less than 20 packages installed!" -ForegroundColor Yellow
        Write-Host "   ðŸ’¡ Run: pip install -r backend\requirements.txt" -ForegroundColor Yellow
    }
}
else {
    Write-Host "   âŒ Virtual environment NOT found!" -ForegroundColor Red
    Write-Host "   ðŸ’¡ Run: python -m venv .venv" -ForegroundColor Yellow
}
Write-Host ""

# Check critical files
Write-Host "2ï¸âƒ£ Critical Files:" -ForegroundColor Cyan
$criticalFiles = @(
    "frontend_server.py",
    "orfeas-studio.html",
    "backend\main.py",
    "backend\requirements.txt",
    "backend\gpu_manager.py",
    "backend\hunyuan_integration.py"
)

foreach ($file in $criticalFiles) {
    if (Test-Path $file) {
        Write-Host "   âœ… $file" -ForegroundColor Green
    }
    else {
        Write-Host "   âŒ $file MISSING!" -ForegroundColor Red
    }
}
Write-Host ""

# Check ports
Write-Host "3ï¸âƒ£ Port Availability:" -ForegroundColor Cyan

$ports = @{
    "8000" = "Frontend Server"
    "5000" = "Backend API"
    "9090" = "Prometheus Metrics"
}

foreach ($port in $ports.Keys) {
    $connection = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
    if ($connection) {
        Write-Host "   âš ï¸ Port $port IN USE ($($ports[$port]))" -ForegroundColor Yellow
        Write-Host "      Process: $(Get-Process -Id $connection.OwningProcess -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Name)" -ForegroundColor White
    }
    else {
        Write-Host "   âœ… Port $port available ($($ports[$port]))" -ForegroundColor Green
    }
}
Write-Host ""

# Test Python imports
Write-Host "4ï¸âƒ£ Python Package Tests:" -ForegroundColor Cyan

$testImports = @(
    @{Name = "Flask"; Import = "flask" },
    @{Name = "PyTorch"; Import = "torch" },
    @{Name = "NumPy"; Import = "numpy" },
    @{Name = "OpenCV"; Import = "cv2" },
    @{Name = "Pillow"; Import = "PIL" },
    @{Name = "Trimesh"; Import = "trimesh" },
    @{Name = "Flask-SocketIO"; Import = "flask_socketio" }
)

foreach ($test in $testImports) {
    $result = & ".\.venv\Scripts\python.exe" -c "import $($test.Import); print('OK')" 2>&1
    if ($result -like "*OK*") {
        Write-Host "   âœ… $($test.Name)" -ForegroundColor Green
    }
    else {
        Write-Host "   âŒ $($test.Name) - NOT INSTALLED" -ForegroundColor Red
    }
}
Write-Host ""

# Check GPU
Write-Host "5ï¸âƒ£ GPU Detection:" -ForegroundColor Cyan
$gpuCheck = & ".\.venv\Scripts\python.exe" -c "import torch; print('CUDA:', torch.cuda.is_available()); print('Devices:', torch.cuda.device_count() if torch.cuda.is_available() else 0)" 2>&1

if ($gpuCheck -like "*CUDA: True*") {
    Write-Host "   âœ… CUDA GPU detected" -ForegroundColor Green
    Write-Host "   $gpuCheck" -ForegroundColor White
}
else {
    Write-Host "   âš ï¸ No CUDA GPU detected (will use CPU/DirectML)" -ForegroundColor Yellow
}
Write-Host ""

# Summary
Write-Host "â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—" -ForegroundColor Cyan
Write-Host "â•‘                  ðŸ“Š DIAGNOSTIC SUMMARY                       â•‘" -ForegroundColor Cyan
Write-Host "â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•" -ForegroundColor Cyan
Write-Host ""

Write-Host "ðŸŽ¯ RECOMMENDED ACTIONS:" -ForegroundColor Yellow
Write-Host ""

# Check if ready to run
if ($packageCount -lt 20) {
    Write-Host "âŒ SYSTEM NOT READY" -ForegroundColor Red
    Write-Host ""
    Write-Host "1. Install dependencies:" -ForegroundColor Yellow
    Write-Host "   cd backend" -ForegroundColor White
    Write-Host "   ..\\.venv\Scripts\python.exe -m pip install -r requirements.txt" -ForegroundColor White
    Write-Host ""
    Write-Host "2. Wait for installation to complete (~10-15 minutes)" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "3. Run diagnostics again:" -ForegroundColor Yellow
    Write-Host "   .\CHECK_SERVER_STATUS.ps1" -ForegroundColor White
}
else {
    Write-Host "âœ… SYSTEM READY!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Start server with:" -ForegroundColor Yellow
    Write-Host "   python frontend_server.py" -ForegroundColor White
    Write-Host ""
    Write-Host "Then open browser:" -ForegroundColor Yellow
    Write-Host "   http://localhost:8000" -ForegroundColor White
}

Write-Host ""
Write-Host "â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—" -ForegroundColor Cyan
Write-Host "â•‘              ORFEAS PROTOCOL âš”ï¸              â•‘" -ForegroundColor Cyan
Write-Host "â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•" -ForegroundColor Cyan
Write-Host ""

# Wait for user
Write-Host "Press any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
