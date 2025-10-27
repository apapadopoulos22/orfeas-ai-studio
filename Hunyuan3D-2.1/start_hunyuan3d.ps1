#  AI 2D STUDIO - Hunyuan3D 2.1 Launcher
Write-Host " AI 2D STUDIO - Hunyuan3D 2.1 Launcher" -ForegroundColor Green
Write-Host " - MAXIMUM EFFORT!" -ForegroundColor Yellow
Write-Host ""

Set-Location "C:\Users\johng\_AI_LOCAL\Hunyuan3D-2.1"

Write-Host "Activating virtual environment..." -ForegroundColor Cyan
& "C:\Users\johng\_AI_LOCAL\Hunyuan3D-2.1\venv\Scripts\Activate.ps1"

Write-Host "Starting API server..." -ForegroundColor Cyan
& python enhanced_api_server.py

Read-Host "Press Enter to continue"
