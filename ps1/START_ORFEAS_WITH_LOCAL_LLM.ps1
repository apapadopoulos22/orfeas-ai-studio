# ⚡ ORFEAS + LOCAL LLM INTEGRATED STARTUP SCRIPT
# Starts both Ollama service and ORFEAS backend for ultra-performance AI generation
# Purpose: Full-stack local AI with zero cloud API dependencies
# Performance: <500ms LLM latency + 30-60s 3D generation

$ErrorActionPreference = "Stop"

Write-Host "════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  ORFEAS AI + LOCAL LLM - INTEGRATED STARTUP" -ForegroundColor Green
Write-Host "  2D→3D Generation + Local Code Intelligence" -ForegroundColor Green
Write-Host "════════════════════════════════════════════════════" -ForegroundColor Cyan

# Step 1: Start Local LLM (Ollama + Mistral)
Write-Host "`n[1/3] Starting Local LLM service..." -ForegroundColor Yellow

try {
    & ".\ps1\START_LOCAL_LLM_AUTO.ps1"
    Write-Host "[✓] Local LLM online at localhost:11434" -ForegroundColor Green
}
catch {
    Write-Host "[ERROR] Local LLM startup failed: $_" -ForegroundColor Red
    exit 1
}

# Step 2: Prepare Python environment
Write-Host "`n[2/3] Preparing Python environment..." -ForegroundColor Yellow

# Check for virtual environment
if (-not (Test-Path ".venv\Scripts\Activate.ps1")) {
    Write-Host "  Creating Python virtual environment..." -ForegroundColor Cyan
    python -m venv .venv
    & ".\.venv\Scripts\Activate.ps1"
    Write-Host "[✓] Virtual environment created and activated" -ForegroundColor Green
}
else {
    & ".\.venv\Scripts\Activate.ps1"
    Write-Host "[✓] Virtual environment activated" -ForegroundColor Green
}

# Step 3: Start ORFEAS backend with local LLM
Write-Host "`n[3/3] Starting ORFEAS backend..." -ForegroundColor Yellow

$env:LOCAL_LLM_ENABLED = "true"
$env:LOCAL_LLM_ENDPOINT = "http://localhost:11434"
$env:LOCAL_LLM_MODEL = "mistral"
$env:FLASK_ENV = "development"
$env:DEVICE = "cuda"
$env:GPU_MEMORY_LIMIT = "0.8"
$env:MAX_CONCURRENT_JOBS = "3"

Write-Host "`nLaunching ORFEAS backend..." -ForegroundColor Cyan
Write-Host "  - Port: 5000" -ForegroundColor Cyan
Write-Host "  - GPU: Auto-detected RTX 3090 (24GB)" -ForegroundColor Cyan
Write-Host "  - Local LLM: Mistral 7B @ localhost:11434" -ForegroundColor Cyan
Write-Host "  - 3D Models: Hunyuan3D-2.1 (Shape + Texture)" -ForegroundColor Cyan

Set-Location backend
python main.py

Write-Host "`nORFEAS stopped" -ForegroundColor Yellow

