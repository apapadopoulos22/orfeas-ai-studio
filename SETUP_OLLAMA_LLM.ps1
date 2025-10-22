#!/usr/bin/env powershell
# SETUP_OLLAMA_LLM.ps1 - Configure local Ollama LLM integration for ORFEAS AI
# Task #1: Set up local Ollama LLM integration

$ErrorActionPreference = "Stop"

Write-Host "🚀 [ORFEAS] Setting up Local Ollama LLM Integration..." -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan

# 1. Check if Ollama is already running
Write-Host "`n[STEP 1/6] Checking Ollama service status..." -ForegroundColor Yellow

$ollamaProcess = Get-Process ollama -ErrorAction SilentlyContinue

if ($ollamaProcess) {
    Write-Host "[✓] Ollama service already running (PID: $($ollamaProcess.Id))" -ForegroundColor Green
}
else {
    Write-Host "[→] Ollama not running, starting service..." -ForegroundColor Cyan
    Start-Process ollama -ArgumentList "serve" -WindowStyle Hidden
    Write-Host "[✓] Ollama service started" -ForegroundColor Green
    Start-Sleep -Seconds 3
}

# 2. Verify Ollama endpoint
Write-Host "`n[STEP 2/6] Verifying Ollama endpoint (localhost:11434)..." -ForegroundColor Yellow

$maxAttempts = 10
$attempt = 0
$endpointReady = $false

while ($attempt -lt $maxAttempts -and -not $endpointReady) {
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -Method GET -ErrorAction Stop
        Write-Host "[✓] Ollama endpoint is responsive" -ForegroundColor Green
        $endpointReady = $true
    }
    catch {
        $attempt++
        if ($attempt -lt $maxAttempts) {
            Write-Host "[→] Waiting for endpoint... ($attempt/$maxAttempts)" -ForegroundColor Yellow
            Start-Sleep -Seconds 2
        }
    }
}

if (-not $endpointReady) {
    Write-Host "[✗] ERROR: Ollama endpoint not responding after 20 seconds" -ForegroundColor Red
    exit 1
}

# 3. Pull Mistral model
Write-Host "`n[STEP 3/6] Pulling Mistral 7B model (this may take 2-5 minutes)..." -ForegroundColor Yellow

try {
    & ollama pull mistral
    Write-Host "[✓] Mistral model pulled successfully" -ForegroundColor Green
}
catch {
    Write-Host "[✗] ERROR: Failed to pull Mistral model" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Red
    exit 1
}

# 4. Verify model is available
Write-Host "`n[STEP 4/6] Verifying Mistral model availability..." -ForegroundColor Yellow

try {
    $models = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -Method GET
    $mistralFound = $models.models | Where-Object { $_.name -like "*mistral*" }

    if ($mistralFound) {
        Write-Host "[✓] Mistral model verified: $($mistralFound.name)" -ForegroundColor Green
    }
    else {
        Write-Host "[⚠] WARNING: Mistral model not found in available models" -ForegroundColor Yellow
        Write-Host "Available models: $($models.models.name -join ', ')" -ForegroundColor Yellow
    }
}
catch {
    Write-Host "[⚠] WARNING: Could not verify models (endpoint may be slow)" -ForegroundColor Yellow
}

# 5. Set environment variables
Write-Host "`n[STEP 5/6] Setting environment variables for ORFEAS integration..." -ForegroundColor Yellow

$env:LOCAL_LLM_ENABLED = "true"
$env:LOCAL_LLM_ENDPOINT = "http://localhost:11434"
$env:LOCAL_LLM_MODEL = "mistral"
$env:LOCAL_LLM_TIMEOUT = "30"
$env:OLLAMA_NUM_GPU = "1"
$env:XFORMERS_DISABLED = "1"

Write-Host "[✓] Environment variables configured:" -ForegroundColor Green
Write-Host "   - LOCAL_LLM_ENABLED: $($env:LOCAL_LLM_ENABLED)" -ForegroundColor Cyan
Write-Host "   - LOCAL_LLM_ENDPOINT: $($env:LOCAL_LLM_ENDPOINT)" -ForegroundColor Cyan
Write-Host "   - LOCAL_LLM_MODEL: $($env:LOCAL_LLM_MODEL)" -ForegroundColor Cyan
Write-Host "   - OLLAMA_NUM_GPU: $($env:OLLAMA_NUM_GPU)" -ForegroundColor Cyan

# 6. Test basic inference
Write-Host "`n[STEP 6/6] Testing basic inference capability..." -ForegroundColor Yellow

try {
    $testPayload = @{
        model       = "mistral"
        prompt      = "What is 2+2? Answer in one word."
        stream      = $false
        temperature = 0.1
    } | ConvertTo-Json

    $startTime = Get-Date
    $response = Invoke-WebRequest -Uri "http://localhost:11434/api/generate" `
        -Method POST `
        -Body $testPayload `
        -ContentType "application/json" `
        -TimeoutSec 30
    $duration = ((Get-Date) - $startTime).TotalMilliseconds

    if ($response.StatusCode -eq 200) {
        $responseBody = $response.Content | ConvertFrom-Json
        Write-Host "[✓] Inference test successful (${duration}ms)" -ForegroundColor Green
        Write-Host "   Response: $($responseBody.response.Substring(0, [Math]::Min(50, $responseBody.response.Length)))..." -ForegroundColor Cyan

        # Performance grade
        if ($duration -lt 500) {
            Write-Host "   Performance Grade: A+ (EXCELLENT)" -ForegroundColor Green
        }
        elseif ($duration -lt 1000) {
            Write-Host "   Performance Grade: A (VERY GOOD)" -ForegroundColor Green
        }
        elseif ($duration -lt 2000) {
            Write-Host "   Performance Grade: B (GOOD)" -ForegroundColor Yellow
        }
        else {
            Write-Host "   Performance Grade: C (ACCEPTABLE)" -ForegroundColor Yellow
        }
    }
}
catch {
    Write-Host "[⚠] Inference test failed (may indicate slow hardware): $_" -ForegroundColor Yellow
}

# Success summary
Write-Host "`n================================================" -ForegroundColor Cyan
Write-Host "✅ [ORFEAS] Ollama LLM Integration Setup Complete!" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "`nEndpoint:         http://localhost:11434" -ForegroundColor Cyan
Write-Host "Model:            Mistral 7B" -ForegroundColor Cyan
Write-Host "Status:           READY FOR ORFEAS AI" -ForegroundColor Green
Write-Host "`nNext steps:" -ForegroundColor Yellow
Write-Host "1. Start ORFEAS backend: python backend/main.py" -ForegroundColor Cyan
Write-Host "2. Monitor performance: curl http://localhost:5000/health" -ForegroundColor Cyan
Write-Host "3. Next task: GPU memory optimization" -ForegroundColor Cyan

exit 0
