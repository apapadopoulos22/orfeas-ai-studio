# ORFEAS AI Studio - Auto Startup Script
# PowerShell version for better error handling and cross-platform support

$Host.UI.RawUI.WindowTitle = "ORFEAS AI Studio - Auto Startup"

# Color functions
function Write-Header {
    param([string]$Text)
    Write-Host ""
    Write-Host "================================================================================" -ForegroundColor Cyan
    Write-Host "  $Text" -ForegroundColor Cyan
    Write-Host "================================================================================" -ForegroundColor Cyan
    Write-Host ""
}

function Write-Success {
    param([string]$Text)
    Write-Host "[OK] $Text" -ForegroundColor Green
}

function Write-ErrorMsg {
    param([string]$Text)
    Write-Host "[ERROR] $Text" -ForegroundColor Red
}

function Write-WarningMsg {
    param([string]$Text)
    Write-Host "[WARN] $Text" -ForegroundColor Yellow
}

function Write-Info {
    param([string]$Text)
    Write-Host "[INFO] $Text" -ForegroundColor Cyan
}

# Main startup sequence
Clear-Host
Write-Header "ORFEAS AI STUDIO - AUTO STARTUP"
Write-Host "    2D to 3D Generation with Preview Fix" -ForegroundColor White
Write-Host ""

# Step 1: Check Python
Write-Host "[1/5] Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Python found: $pythonVersion"
    }
    else {
        throw "Python not found"
    }
}
catch {
    Write-ErrorMsg "Python is not installed or not in PATH"
    Write-Host ""
    Write-Host "Please install Python 3.8+ from: https://www.python.org/downloads/" -ForegroundColor White
    Write-Host "Make sure to check 'Add Python to PATH' during installation" -ForegroundColor White
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host ""

# Step 2: Check backend directory
Write-Host "[2/5] Checking backend directory..." -ForegroundColor Yellow
$backendPath = Join-Path $PSScriptRoot "backend\main.py"
if (Test-Path $backendPath) {
    Write-Success "Backend directory found: backend\main.py"
}
else {
    Write-ErrorMsg "Backend main.py not found"
    Write-Host "Expected: $backendPath" -ForegroundColor White
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host ""

# Step 3: Check frontend
Write-Host "[3/5] Checking frontend..." -ForegroundColor Yellow
$frontendPath = Join-Path $PSScriptRoot "orfeas-studio.html"
$frontendExists = Test-Path $frontendPath
if ($frontendExists) {
    Write-Success "Frontend HTML found: orfeas-studio.html"
}
else {
    Write-WarningMsg "orfeas-studio.html not found (frontend will not open automatically)"
}
Write-Host ""

# Step 4: Start backend server
Write-Host "[4/5] Starting backend server..." -ForegroundColor Yellow
Write-Host ""
Write-Info "Opening backend server in new window..."

$backendDir = Join-Path $PSScriptRoot "backend"
$startProcess = Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$backendDir'; Write-Host 'ORFEAS Backend Server' -ForegroundColor Green; python main.py" -PassThru -WindowStyle Normal

if ($startProcess) {
    Write-Success "Backend server started (PID: $($startProcess.Id))"
}
else {
    Write-ErrorMsg "Failed to start backend server"
}
Write-Host ""

# Step 5: Wait for server to start
Write-Host "[5/5] Waiting for backend to initialize..." -ForegroundColor Yellow
Write-Host "[INFO] Giving backend 8 seconds to fully start..." -ForegroundColor Cyan
Start-Sleep -Seconds 8

# Check if server is running
try {
    $response = Invoke-WebRequest -Uri "http://127.0.0.1:5000/api/health" -UseBasicParsing -TimeoutSec 10 -ErrorAction Stop
    if ($response.StatusCode -eq 200) {
        Write-Success "Backend server is running on http://127.0.0.1:5000"
        Write-Host ""
        $healthData = $response.Content | ConvertFrom-Json
        Write-Info "Server Status: $($healthData.status)"
        Write-Info "GPU Available: $($healthData.gpu_available)"
    }
}
catch {
    Write-WarningMsg "Backend server may still be starting..."
    Write-Host "Check the backend window for any errors" -ForegroundColor White
    Write-Info "The backend window should show 'Running on http://127.0.0.1:5000'" -ForegroundColor Cyan
}
Write-Host ""

# Display success message
Write-Header "STARTUP COMPLETE!"

Write-Host "Backend Server:    " -NoNewline -ForegroundColor White
Write-Host "http://127.0.0.1:5000" -ForegroundColor Cyan

Write-Host "API Health:        " -NoNewline -ForegroundColor White
Write-Host "http://127.0.0.1:5000/api/health" -ForegroundColor Cyan

Write-Host "Preview Endpoint:  " -NoNewline -ForegroundColor White
Write-Host "http://127.0.0.1:5000/api/preview/<filename>" -ForegroundColor Cyan
Write-Host ""

# Automatically open frontend (NO USER INPUT)
if ($frontendExists) {
    Write-Host ""
    Write-Info "Opening frontend in default browser..."
    Start-Sleep -Seconds 1
    Start-Process $frontendPath
    Write-Success "Frontend opened automatically"
    Write-Host ""
}
else {
    Write-WarningMsg "Frontend file not found - skipping auto-open"
    Write-Host "   • Or run: " -NoNewline -ForegroundColor White
    Write-Host "python -m http.server 8000" -ForegroundColor Cyan
    Write-Host "   • Then visit: " -NoNewline -ForegroundColor White
    Write-Host "http://localhost:8000/orfeas-studio.html" -ForegroundColor Cyan
    Write-Host ""
}

# Quick commands reference
Write-Header "QUICK COMMANDS"
Write-Host "  • Test Backend:       " -NoNewline -ForegroundColor White
Write-Host "curl http://127.0.0.1:5000/api/health" -ForegroundColor Cyan

Write-Host "  • Run Tests:          " -NoNewline -ForegroundColor White
Write-Host "cd backend; python test_preview_endpoints.py" -ForegroundColor Cyan

Write-Host "  • View Docs:          " -NoNewline -ForegroundColor White
Write-Host "Open PREVIEW_FIX_COMPLETE.md" -ForegroundColor Cyan

Write-Host "  • Stop Backend:       " -NoNewline -ForegroundColor White
Write-Host "Close the backend server window" -ForegroundColor Cyan
Write-Host ""

Write-Header "SYSTEM READY FOR USE"

Write-Host "[NOTE] Backend server is running in a separate window" -ForegroundColor Yellow
Write-Host "[NOTE] To stop the backend, close that window or press Ctrl+C in it" -ForegroundColor Yellow
Write-Host "[NOTE] This startup window will auto-close in 5 seconds..." -ForegroundColor Yellow
Write-Host ""

# Auto-close after 5 seconds (fully automatic - no user input required)
Start-Sleep -Seconds 5
