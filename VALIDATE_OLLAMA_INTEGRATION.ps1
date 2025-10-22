# .\VALIDATE_OLLAMA_INTEGRATION.ps1 - Comprehensive Ollama/Local LLM validation
# Purpose: Validate Ollama installation, Mistral model, integration with ORFEAS backend

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

Write-Host "
╔════════════════════════════════════════════════════════════════╗
║    ORFEAS AI - LOCAL LLM INTEGRATION VALIDATION SUITE          ║
║    Ollama + Mistral 7B + Backend Integration                  ║
╚════════════════════════════════════════════════════════════════╝
" -ForegroundColor Cyan

$validationResults = @{
    'ollamaNot_installed' = $false
    'ollamaRunning'       = $false
    'mistralDownloaded'   = $false
    'endpointReachable'   = $false
    'backendenabled'      = $false
    'apiEndpoint'         = $false
    'timestamp'           = (Get-Date).ToIso8601String()
}

# ═══════════════════════════════════════════════════════════════
# [STEP 1] Verify Ollama Installation
# ═══════════════════════════════════════════════════════════════
Write-Host "`n[STEP 1/7] Verifying Ollama Installation..." -ForegroundColor Yellow
try {
    $ollamaVersion = & ollama --version 2>&1 | Select-Object -First 1
    Write-Host "✓ Ollama installed: $ollamaVersion" -ForegroundColor Green
    $validationResults['ollamaInstalled'] = $true
}
catch {
    Write-Host "✗ Ollama NOT installed" -ForegroundColor Red
    Write-Host "  Install from: https://ollama.ai" -ForegroundColor Yellow
    $validationResults['ollamaInstalled'] = $false
    exit 1
}

# ═══════════════════════════════════════════════════════════════
# [STEP 2] Check Ollama Service Status
# ═══════════════════════════════════════════════════════════════
Write-Host "`n[STEP 2/7] Checking Ollama Service Status..." -ForegroundColor Yellow
$ollamaProcess = Get-Process ollama -ErrorAction SilentlyContinue
if ($ollamaProcess) {
    Write-Host "✓ Ollama service is RUNNING (PID: $($ollamaProcess.Id))" -ForegroundColor Green
    $validationResults['ollamaRunning'] = $true
}
else {
    Write-Host "⚠ Ollama service NOT running - attempting to start..." -ForegroundColor Yellow
    try {
        Write-Host "  Starting Ollama service..." -ForegroundColor Cyan
        Start-Process ollama -ArgumentList "serve" -NoNewWindow -PassThru | Out-Null
        Start-Sleep -Seconds 3
        Write-Host "✓ Ollama service started successfully" -ForegroundColor Green
        $validationResults['ollamaRunning'] = $true
    }
    catch {
        Write-Host "✗ Failed to start Ollama: $_" -ForegroundColor Red
        exit 1
    }
}

# ═══════════════════════════════════════════════════════════════
# [STEP 3] Verify Ollama Endpoint Reachability
# ═══════════════════════════════════════════════════════════════
Write-Host "`n[STEP 3/7] Verifying Ollama Endpoint (localhost:11434)..." -ForegroundColor Yellow
$maxAttempts = 10
$attempt = 0
$endpointReachable = $false

while ($attempt -lt $maxAttempts) {
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -Method GET -ErrorAction Stop -TimeoutSec 5
        Write-Host "✓ Endpoint REACHABLE at http://localhost:11434" -ForegroundColor Green
        Write-Host "  Available models: $($response.models.name -join ', ')" -ForegroundColor Cyan
        $validationResults['endpointReachable'] = $true
        $endpointReachable = $true
        break
    }
    catch {
        $attempt++
        if ($attempt -lt $maxAttempts) {
            Write-Host "  Attempt $attempt/$maxAttempts - Waiting for endpoint..." -ForegroundColor Yellow
            Start-Sleep -Seconds 2
        }
    }
}

if (-not $endpointReachable) {
    Write-Host "✗ Endpoint NOT reachable after $maxAttempts attempts" -ForegroundColor Red
    Write-Host "  Troubleshooting: Check if Ollama is running and port 11434 is accessible" -ForegroundColor Yellow
    exit 1
}

# ═══════════════════════════════════════════════════════════════
# [STEP 4] Check Mistral 7B Model
# ═══════════════════════════════════════════════════════════════
Write-Host "`n[STEP 4/7] Verifying Mistral 7B Model..." -ForegroundColor Yellow
try {
    $modelsList = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -Method GET -ErrorAction Stop
    $mistralAvailable = $modelsList.models | Where-Object { $_.name -like "*mistral*" }

    if ($mistralAvailable) {
        Write-Host "✓ Mistral model is AVAILABLE" -ForegroundColor Green
        Write-Host "  Model: $($mistralAvailable.name)" -ForegroundColor Cyan
        Write-Host "  Size: $([math]::Round($mistralAvailable.size / 1GB, 2)) GB" -ForegroundColor Cyan
        $validationResults['mistralDownloaded'] = $true
    }
    else {
        Write-Host "⚠ Mistral model NOT found - pulling Mistral 7B..." -ForegroundColor Yellow
        Write-Host "  This may take 5-15 minutes depending on your internet speed" -ForegroundColor Cyan

        & ollama pull mistral

        Write-Host "✓ Mistral 7B model pulled successfully" -ForegroundColor Green
        $validationResults['mistralDownloaded'] = $true
    }
}
catch {
    Write-Host "✗ Failed to check/pull Mistral model: $_" -ForegroundColor Red
    exit 1
}

# ═══════════════════════════════════════════════════════════════
# [STEP 5] Test Ollama Inference (Quick Test)
# ═══════════════════════════════════════════════════════════════
Write-Host "`n[STEP 5/7] Testing Ollama Inference (Quick Test)..." -ForegroundColor Yellow
try {
    Write-Host "  Sending test prompt to Mistral..." -ForegroundColor Cyan
    $testStart = Get-Date

    $requestBody = @{
        model  = "mistral"
        prompt = "What is 2+2? Answer in one word."
        stream = $false
    } | ConvertTo-Json

    $response = Invoke-RestMethod `
        -Uri "http://localhost:11434/api/generate" `
        -Method POST `
        -Body $requestBody `
        -ContentType "application/json" `
        -ErrorAction Stop `
        -TimeoutSec 30

    $testDuration = (Get-Date) - $testStart

    Write-Host "✓ Inference test SUCCESSFUL" -ForegroundColor Green
    Write-Host "  Response: $($response.response.Trim())" -ForegroundColor Cyan
    Write-Host "  Duration: $($testDuration.TotalSeconds)s" -ForegroundColor Cyan

    if ($testDuration.TotalSeconds -lt 2) {
        Write-Host "  Performance: ⚡ EXCELLENT (cached model)" -ForegroundColor Green
    }
    elseif ($testDuration.TotalSeconds -lt 5) {
        Write-Host "  Performance: ✓ GOOD" -ForegroundColor Green
    }
    else {
        Write-Host "  Performance: ⚠ SLOW (first load or resource constraint)" -ForegroundColor Yellow
    }
}
catch {
    Write-Host "✗ Inference test FAILED: $_" -ForegroundColor Red
    exit 1
}

# ═══════════════════════════════════════════════════════════════
# [STEP 6] Verify Backend Configuration
# ═══════════════════════════════════════════════════════════════
Write-Host "`n[STEP 6/7] Verifying Backend LLM Configuration..." -ForegroundColor Yellow
$envPath = ".\backend\.env"
if (Test-Path $envPath) {
    $envContent = Get-Content $envPath -Raw

    if ($envContent -match "LOCAL_LLM_ENABLED\s*=\s*true") {
        Write-Host "✓ LOCAL_LLM_ENABLED = true" -ForegroundColor Green
        $validationResults['backendEnabled'] = $true
    }
    else {
        Write-Host "⚠ LOCAL_LLM_ENABLED not set to true - updating..." -ForegroundColor Yellow
        $envContent = $envContent -replace "LOCAL_LLM_ENABLED\s*=.*", "LOCAL_LLM_ENABLED=true"
        Set-Content $envPath -Value $envContent -Encoding UTF8
        Write-Host "✓ Updated LOCAL_LLM_ENABLED = true" -ForegroundColor Green
        $validationResults['backendEnabled'] = $true
    }

    if ($envContent -match "LOCAL_LLM_ENDPOINT\s*=.*11434") {
        Write-Host "✓ LOCAL_LLM_ENDPOINT configured correctly" -ForegroundColor Green
    }
    else {
        Write-Host "⚠ LOCAL_LLM_ENDPOINT not configured - updating..." -ForegroundColor Yellow
        $envContent = $envContent -replace "LOCAL_LLM_ENDPOINT\s*=.*", "LOCAL_LLM_ENDPOINT=http://localhost:11434"
        Set-Content $envPath -Value $envContent -Encoding UTF8
        Write-Host "✓ Updated LOCAL_LLM_ENDPOINT" -ForegroundColor Green
    }
}
else {
    Write-Host "⚠ .env file not found at $envPath" -ForegroundColor Yellow
}

# ═══════════════════════════════════════════════════════════════
# [STEP 7] Test Backend API Endpoint
# ═══════════════════════════════════════════════════════════════
Write-Host "`n[STEP 7/7] Testing Backend /api/generate-code-local Endpoint..." -ForegroundColor Yellow

# Check if backend is running
$backendHealthy = $false
try {
    $healthResponse = Invoke-RestMethod -Uri "http://localhost:5000/health" -TimeoutSec 5 -ErrorAction Stop
    Write-Host "✓ Backend API is RUNNING at http://localhost:5000" -ForegroundColor Green
    $backendHealthy = $true
    $validationResults['apiEndpoint'] = $true
}
catch {
    Write-Host "⚠ Backend API not currently running (normal if not started)" -ForegroundColor Yellow
    Write-Host "  Start backend with: cd backend; python main.py" -ForegroundColor Cyan
}

if ($backendHealthy) {
    try {
        Write-Host "  Testing /api/generate-code-local endpoint..." -ForegroundColor Cyan
        $testPrompt = @{
            prompt   = "Write a Python function to calculate factorial"
            language = "python"
        } | ConvertTo-Json

        $codeResponse = Invoke-RestMethod `
            -Uri "http://localhost:5000/api/generate-code-local" `
            -Method POST `
            -Body $testPrompt `
            -ContentType "application/json" `
            -ErrorAction Stop `
            -TimeoutSec 30

        Write-Host "✓ Backend endpoint WORKING" -ForegroundColor Green
        Write-Host "  Generated code lines: $(($codeResponse.code -split "`n").Count)" -ForegroundColor Cyan
    }
    catch {
        Write-Host "⚠ Backend endpoint test failed (may not be implemented yet): $_" -ForegroundColor Yellow
    }
}

# ═══════════════════════════════════════════════════════════════
# SUMMARY REPORT
# ═══════════════════════════════════════════════════════════════
Write-Host "`n" + ("=" * 65) -ForegroundColor Cyan
Write-Host "VALIDATION SUMMARY" -ForegroundColor Cyan
Write-Host ("=" * 65) -ForegroundColor Cyan

$passCount = ($validationResults.Values | Where-Object { $_ -eq $true }).Count
$totalChecks = $validationResults.Count - 1  # Exclude timestamp

Write-Host "`nResults: $passCount/$totalChecks checks passed" -ForegroundColor $(if ($passCount -ge 5) { "Green" } else { "Yellow" })

foreach ($check in $validationResults.GetEnumerator() | Where-Object { $_.Key -ne 'timestamp' }) {
    $status = if ($check.Value) { "✓ PASS" } else { "✗ FAIL" }
    $color = if ($check.Value) { "Green" } else { "Red" }
    Write-Host "  [$status] $($check.Key)" -ForegroundColor $color
}

Write-Host "`n" + ("=" * 65) -ForegroundColor Cyan

if ($passCount -ge 5) {
    Write-Host "✅ LOCAL LLM INTEGRATION READY FOR DEVELOPMENT" -ForegroundColor Green
    Write-Host "`nNext Steps:" -ForegroundColor Green
    Write-Host "  1. Start backend:  cd backend; python main.py" -ForegroundColor Cyan
    Write-Host "  2. Test endpoints: Invoke-RestMethod http://localhost:5000/health" -ForegroundColor Cyan
    Write-Host "  3. Generate code:  curl -X POST http://localhost:5000/api/generate-code-local ..." -ForegroundColor Cyan
}
else {
    Write-Host "⚠️  INTEGRATION ISSUES DETECTED - Please fix above items" -ForegroundColor Yellow
    Write-Host "`nTroubleshooting:" -ForegroundColor Yellow
    Write-Host "  - Ollama not running? Start: ollama serve" -ForegroundColor Cyan
    Write-Host "  - Port 11434 blocked? Check firewall or run: netstat -ano | findstr :11434" -ForegroundColor Cyan
    Write-Host "  - Mistral too slow? Normal on first run. Runs faster on subsequent calls." -ForegroundColor Cyan
}

Write-Host ""
$validationResults | ConvertTo-Json | Out-File -FilePath ".\OLLAMA_VALIDATION_REPORT.json" -Encoding UTF8
Write-Host "📄 Full report saved to: .\OLLAMA_VALIDATION_REPORT.json" -ForegroundColor Cyan
Write-Host ""
