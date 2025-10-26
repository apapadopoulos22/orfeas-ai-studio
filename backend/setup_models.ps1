#!/usr/bin/env pwsh
<#
.SYNOPSIS
    ORFEAS Model Cache Setup - Fix HuggingFace paths for Windows

.DESCRIPTION
    Configures proper HuggingFace cache paths to prevent mixed path separators
    and "Model path not exists, try to download from huggingface" errors.

.EXAMPLE
    .\setup_models.ps1

.NOTES
    Run from backend directory
#>

param(
    [switch]$DownloadModels = $false,
    [switch]$VerifyOnly = $false
)

# Color output
function Write-Success { Write-Host "[✅] $args" -ForegroundColor Green }
function Write-Error { Write-Host "[❌] $args" -ForegroundColor Red }
function Write-Info { Write-Host "[ℹ️ ] $args" -ForegroundColor Cyan }
function Write-Warning { Write-Host "[⚠️ ] $args" -ForegroundColor Yellow }

Write-Host ""
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host "[SETUP] ORFEAS Model Cache Configuration" -ForegroundColor Cyan
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host ""

# Get script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$BackendDir = $ScriptDir

Write-Info "Backend directory: $BackendDir"

# Run Python setup
Write-Info "Running Python setup script..."
Write-Host ""

python "$BackendDir\setup_model_cache.py"

if ($LASTEXITCODE -ne 0) {
    Write-Error "Python setup failed!"
    exit 1
}

Write-Success "Model cache configuration complete!"
Write-Host ""

# Show next steps
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host "[NEXT STEPS]" -ForegroundColor Cyan
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host ""

if ($DownloadModels) {
    Write-Info "Option 1: Pre-download models (recommended for first run)"
    Write-Host "  cd $BackendDir"
    Write-Host "  python download_models.py"
    Write-Host ""
}

Write-Info "Start the backend server:"
Write-Host "  python $BackendDir\main.py"
Write-Host ""

Write-Info "The server will now load models with correct Windows paths!"
Write-Info "No more mixed path separators (/ and \\)"
Write-Host ""

Write-Success "Setup complete!"
Write-Host ""
