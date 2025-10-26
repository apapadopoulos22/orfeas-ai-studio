#!/usr/bin/env pwsh
<#
.SYNOPSIS
    ORFEAS Backend Startup Script with Model Cache Configuration

.DESCRIPTION
    Sets up model cache paths and starts the backend server.
    Ensures all paths use correct separators for Windows.

.EXAMPLE
    .\start_backend.ps1

.NOTES
    Automatically configures HuggingFace cache paths before startup
#>

param(
    [switch]$NoValidation = $false
)

# Colors
$colors = @{
    Success = 'Green'
    Error   = 'Red'
    Info    = 'Cyan'
    Warning = 'Yellow'
}

function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = 'White'
    )
    Write-Host $Message -ForegroundColor $Color
}

# Get the directory of this script
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$BackendDir = $ScriptDir
$ProjectRoot = Split-Path -Parent $BackendDir

Write-ColorOutput "`n" + ("=" * 80) $colors.Info
Write-ColorOutput "[START] ORFEAS Backend with Model Cache Configuration" $colors.Info
Write-ColorOutput ("=" * 80) $colors.Info
Write-ColorOutput "`n"

# Step 1: Configure model cache paths
Write-ColorOutput "[SETUP] Configuring model cache paths..." $colors.Info

# Create cache directories
$CacheDir = "$ProjectRoot\models\.cache\huggingface"
$TransformersCache = "$CacheDir\transformers"
$DatasetsCache = "$CacheDir\datasets"
$Hy3dgenCache = "$CacheDir\hy3dgen"

foreach ($dir in @($CacheDir, $TransformersCache, $DatasetsCache, $Hy3dgenCache)) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-ColorOutput "  ✅ Created: $dir" $colors.Success
    }
}

# Set environment variables (proper Windows paths with backslashes)
$env:HF_HOME = $CacheDir
$env:TRANSFORMERS_CACHE = $TransformersCache
$env:HF_DATASETS_CACHE = $DatasetsCache
$env:HY3DGEN_CACHE = $Hy3dgenCache
$env:HOME = $ProjectRoot

Write-ColorOutput "  ✅ HF_HOME = $env:HF_HOME" $colors.Success
Write-ColorOutput "  ✅ TRANSFORMERS_CACHE = $env:TRANSFORMERS_CACHE" $colors.Success
Write-ColorOutput "  ✅ HY3DGEN_CACHE = $env:HY3DGEN_CACHE" $colors.Success

Write-ColorOutput "`n"

# Step 2: Optional validation
if (-not $NoValidation) {
    Write-ColorOutput "[VALIDATE] Checking cache configuration..." $colors.Info

    $AllValid = $true
    foreach ($dir in @($CacheDir, $TransformersCache, $DatasetsCache, $Hy3dgenCache)) {
        if (Test-Path $dir) {
            Write-ColorOutput "  ✅ $([System.IO.Path]::GetFileName($dir))/ exists" $colors.Success
        }
        else {
            Write-ColorOutput "  ❌ $([System.IO.Path]::GetFileName($dir))/ missing" $colors.Error
            $AllValid = $false
        }
    }

    if (-not $AllValid) {
        Write-ColorOutput "`n  ⚠️  Some directories could not be created." $colors.Warning
        Write-ColorOutput "  This may cause issues on first model load." $colors.Warning
    }

    Write-ColorOutput "`n"
}

# Step 3: Start backend
Write-ColorOutput "[START] Starting ORFEAS Backend Server..." $colors.Info
Write-ColorOutput "  Backend directory: $BackendDir" $colors.Info
Write-ColorOutput "  Model cache: $env:HF_HOME" $colors.Info
Write-ColorOutput "`n"

Write-ColorOutput "=" * 80 $colors.Info
Write-ColorOutput "Backend is starting. Press Ctrl+C to stop." $colors.Warning
Write-ColorOutput "=" * 80 $colors.Info
Write-ColorOutput "`n"

# Change to backend directory and start
cd $BackendDir

# Run Python main.py
python main.py

# If Python exits, show result
if ($LASTEXITCODE -eq 0) {
    Write-ColorOutput "`n✅ Backend stopped gracefully" $colors.Success
}
else {
    Write-ColorOutput "`n❌ Backend exited with error code: $LASTEXITCODE" $colors.Error
}

Write-ColorOutput "`n"
