# ORFEAS AI - Ollama Local LLM Setup Script
# Properly encoded for PowerShell 5.1 compatibility
# No Unicode special characters - ASCII-safe for all Windows versions

param(
    [string]$OllamaUrl = "http://localhost:11434",
    [string]$Model = "mistral",
    [int]$TimeoutSeconds = 60
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "ORFEAS AI - Ollama LLM Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check if Ollama is installed
Write-Host "[1/5] Checking Ollama installation..." -ForegroundColor Yellow
$ollamaExists = $null
try {
    $ollamaExists = Get-Command ollama -ErrorAction SilentlyContinue
    if ($ollamaExists) {
        Write-Host "  [OK] Ollama found at: $($ollamaExists.Source)" -ForegroundColor Green
    }
}
catch {
    Write-Host "  [WARN] Ollama command not found in PATH" -ForegroundColor Yellow
    Write-Host "  Please install Ollama from: https://ollama.ai" -ForegroundColor Yellow
    exit 1
}

# Step 2: Check if Ollama service is running
Write-Host "[2/5] Checking Ollama service..." -ForegroundColor Yellow
$processExists = Get-Process ollama -ErrorAction SilentlyContinue
if ($processExists) {
    Write-Host "  [OK] Ollama process running" -ForegroundColor Green
}
else {
    Write-Host "  [INFO] Starting Ollama service..." -ForegroundColor Cyan
    try {
        Start-Process ollama -ArgumentList "serve" -NoNewWindow -PassThru | Out-Null
        Start-Sleep -Seconds 3
        Write-Host "  [OK] Ollama service started" -ForegroundColor Green
    }
    catch {
        Write-Host "  [ERROR] Failed to start Ollama: $_" -ForegroundColor Red
        exit 1
    }
}

# Step 3: Verify Ollama endpoint
Write-Host "[3/5] Verifying Ollama endpoint..." -ForegroundColor Yellow
$maxAttempts = 20
$attempt = 0
$endpointReady = $false

while ($attempt -lt $maxAttempts) {
    try {
        $response = Invoke-RestMethod -Uri "$OllamaUrl/api/tags" -Method GET -TimeoutSec 5 -ErrorAction Stop
        Write-Host "  [OK] Ollama endpoint responsive at $OllamaUrl" -ForegroundColor Green
        $endpointReady = $true

        if ($response.models) {
            Write-Host "  Available models:" -ForegroundColor Green
            foreach ($m in $response.models) {
                Write-Host "    - $($m.name)" -ForegroundColor Green
            }
        }
        break
    }
    catch {
        $attempt++
        if ($attempt -lt $maxAttempts) {
            Write-Host "  [WAIT] Endpoint not ready, retrying... ($attempt/$maxAttempts)" -ForegroundColor Yellow
            Start-Sleep -Seconds 2
        }
    }
}

if (-not $endpointReady) {
    Write-Host "  [ERROR] Ollama endpoint failed to respond after $maxAttempts attempts" -ForegroundColor Red
    exit 1
}

# Step 4: Pull Mistral model
Write-Host "[4/5] Pulling $Model model..." -ForegroundColor Yellow
try {
    Write-Host "  This may take several minutes on first run..." -ForegroundColor Cyan
    & ollama pull $Model
    Write-Host "  [OK] $Model model pulled successfully" -ForegroundColor Green
}
catch {
    Write-Host "  [ERROR] Failed to pull $Model model: $_" -ForegroundColor Red
    exit 1
}

# Step 5: Configure environment variables
Write-Host "[5/5] Configuring environment variables..." -ForegroundColor Yellow
$envVars = @{
    "LOCAL_LLM_ENABLED"  = "true"
    "LOCAL_LLM_ENDPOINT" = $OllamaUrl
    "LOCAL_LLM_MODEL"    = $Model
    "LOCAL_LLM_TIMEOUT"  = "30"
    "OLLAMA_NUM_GPU"     = "1"
    "XFORMERS_DISABLED"  = "1"
}

# Set environment variables for current session
foreach ($key in $envVars.Keys) {
    [Environment]::SetEnvironmentVariable($key, $envVars[$key], "Process")
    Write-Host "  SET $key=$($envVars[$key])" -ForegroundColor Green
}

# Display summary
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Local LLM Configuration:" -ForegroundColor Yellow
Write-Host "  Endpoint: $OllamaUrl" -ForegroundColor Green
Write-Host "  Model: $Model" -ForegroundColor Green
Write-Host "  Status: READY" -ForegroundColor Green
Write-Host ""
Write-Host "Test the endpoint with:" -ForegroundColor Cyan
Write-Host "  curl http://localhost:11434/api/tags" -ForegroundColor White
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Start ORFEAS backend: .\START_ORFEAS_WITH_LOCAL_LLM.ps1" -ForegroundColor White
Write-Host "  2. Monitor progress: docker-compose logs -f backend" -ForegroundColor White
Write-Host "  3. Access UI: http://localhost:5000" -ForegroundColor White
Write-Host ""
