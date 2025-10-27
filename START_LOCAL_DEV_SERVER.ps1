================================================================================
ORFEAS Local Development Server Setup
================================================================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "ORFEAS Local Dev Server" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is available
$pythonCheck = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Python not found! Please install Python 3.11+" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Python: $pythonCheck" -ForegroundColor Green

# Get to workspace root
$workspaceRoot = "c:\Users\johng\Documents\oscar"
Set-Location $workspaceRoot

Write-Host ""
Write-Host "========================================" -ForegroundColor Yellow
Write-Host "Starting Local Dev Environment" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Yellow
Write-Host ""

# Check if http.server module is available (built-in)
Write-Host "[1/3] Starting HTTP Server on port 8000..." -ForegroundColor Cyan
Write-Host "      This will serve your HTML files locally" -ForegroundColor Gray
Write-Host ""

# Start the Python HTTP server in background
$process = Start-Process `
    -FilePath "python" `
    -ArgumentList "-m http.server 8000 --directory `"$workspaceRoot`"" `
    -NoNewWindow `
    -PassThru

Write-Host "✅ HTTP Server started (PID: $($process.Id))" -ForegroundColor Green
Write-Host "   Access at: http://localhost:8000" -ForegroundColor Green
Write-Host ""

# Verify backend is running
Write-Host "[2/3] Checking backend..." -ForegroundColor Cyan
$backendCheck = netstat -ano | Select-String "5000.*LISTENING" | Measure-Object
if ($backendCheck.Count -gt 0) {
    Write-Host "✅ Backend running on port 5000" -ForegroundColor Green
}
else {
    Write-Host "⚠️  Backend not running on port 5000" -ForegroundColor Yellow
    Write-Host "   Start it separately: cd backend ; python main.py" -ForegroundColor Gray
}

# Verify ngrok is running
Write-Host "[3/3] Checking ngrok tunnel..." -ForegroundColor Cyan
$ngrokCheck = netstat -ano | Select-String "4040.*LISTENING" | Measure-Object
if ($ngrokCheck.Count -gt 0) {
    Write-Host "✅ ngrok tunnel running on port 4040" -ForegroundColor Green
}
else {
    Write-Host "⚠️  ngrok not running" -ForegroundColor Yellow
    Write-Host "   Start it separately: ngrok http 5000" -ForegroundColor Gray
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "✅ LOCAL DEV SERVER READY" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

Write-Host "📍 LOCAL DEVELOPMENT URLS:" -ForegroundColor Cyan
Write-Host ""
Write-Host "   Main Studio:          http://localhost:8000/orfeas-ai-studio.html" -ForegroundColor Green
Write-Host "   Synexa Studio:        http://localhost:8000/synexa-style-studio.html" -ForegroundColor Green
Write-Host "   Batch Studio:         http://localhost:8000/batch-studio.html" -ForegroundColor Green
Write-Host "   Bob AI Chat:          http://localhost:8000/bob-ai-chat.html" -ForegroundColor Green
Write-Host ""

Write-Host "🔗 BACKEND CONNECTIONS:" -ForegroundColor Cyan
Write-Host ""
Write-Host "   Backend Direct:       http://127.0.0.1:5000" -ForegroundColor Green
Write-Host "   Backend via ngrok:    https://unsaid-ellsworth-uncorrespondingly.ngrok-free.dev" -ForegroundColor Green
Write-Host "   ngrok Dashboard:      http://localhost:4040" -ForegroundColor Green
Write-Host ""

Write-Host "💡 QUICK TEST:" -ForegroundColor Cyan
Write-Host ""
Write-Host "   1. Open browser tab: http://localhost:8000/orfeas-ai-studio.html" -ForegroundColor White
Write-Host "   2. Open F12 Console" -ForegroundColor White
Write-Host "   3. Look for [HEALTH] Response status: 200 ✅" -ForegroundColor White
Write-Host "   4. Make edits to HTML files" -ForegroundColor White
Write-Host "   5. Refresh browser to see changes instantly" -ForegroundColor White
Write-Host ""

Write-Host "🛑 TO STOP:" -ForegroundColor Cyan
Write-Host ""
Write-Host "   Press Ctrl+C in this terminal" -ForegroundColor White
Write-Host ""

# Keep the process running
$process | Wait-Process
