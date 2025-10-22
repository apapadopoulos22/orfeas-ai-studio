# ============================================================================
# ORFEAS - Local LLM (Ollama) Integration Validation & Debugging
# ============================================================================
# Purpose: Validate Ollama connectivity, Mistral model, and LLM endpoints
# Target: RTX 3090, Mistral 7B via Ollama, <500ms latency
# ============================================================================

$ErrorActionPreference = "Continue"
$timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$logFile = "C:\Users\johng\Documents\oscar\logs\llm_validation_$timestamp.log"

# Ensure logs directory exists
if (!(Test-Path "C:\Users\johng\Documents\oscar\logs")) {
    New-Item -ItemType Directory -Path "C:\Users\johng\Documents\oscar\logs" -Force | Out-Null
}

function Log-Message {
    param([string]$Message, [string]$Level = "INFO", [string]$Color = "White")
    $timestamp = Get-Date -Format "HH:mm:ss"
    $logEntry = "[$timestamp] [$Level] $Message"
    Write-Host $logEntry -ForegroundColor $Color
    Add-Content -Path $logFile -Value $logEntry
}

function Test-OllamaConnectivity {
    Log-Message "=" * 80 -Level "TEST"
    Log-Message "1. TESTING OLLAMA CONNECTIVITY" -Level "TEST" -Color "Cyan"
    Log-Message "=" * 80 -Level "TEST"

    try {
        $response = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" `
            -TimeoutSec 5 -ErrorAction Stop

        if ($response.StatusCode -eq 200) {
            Log-Message "✓ Ollama server is running and responding" -Level "SUCCESS" -Color "Green"

            $data = $response.Content | ConvertFrom-Json
            Log-Message "Available models:" -Level "INFO" -Color "Green"

            foreach ($model in $data.models) {
                Log-Message "  - $($model.name) (Size: $($model.size / 1GB)GB)" -Level "INFO" -Color "Green"
            }

            return $true
        }
    }
    catch {
        Log-Message "✗ Ollama connection failed: $_" -Level "ERROR" -Color "Red"
        Log-Message "  Ensure Ollama is running: ollama serve" -Level "INFO" -Color "Yellow"
        return $false
    }
}

function Test-MistralModel {
    Log-Message "`n" + ("=" * 80) -Level "TEST"
    Log-Message "2. TESTING MISTRAL 7B MODEL" -Level "TEST" -Color "Cyan"
    Log-Message "=" * 80 -Level "TEST"

    try {
        $payload = @{
            model       = "mistral"
            prompt      = "Say 'Ollama is working'"
            stream      = $false
            num_predict = 10
        } | ConvertTo-Json

        $response = Invoke-WebRequest -Uri "http://localhost:11434/api/generate" `
            -Method Post `
            -ContentType "application/json" `
            -Body $payload `
            -TimeoutSec 30 `
            -ErrorAction Stop

        if ($response.StatusCode -eq 200) {
            $data = $response.Content | ConvertFrom-Json
            Log-Message "✓ Mistral model is working" -Level "SUCCESS" -Color "Green"
            Log-Message "  Response: $($data.response.Trim())" -Level "INFO" -Color "Green"
            Log-Message "  Eval time: $($data.eval_duration / 1000000)ms" -Level "INFO" -Color "Green"
            Log-Message "  Tokens/sec: $($data.eval_count / ($data.eval_duration / 1000000000))" -Level "INFO" -Color "Green"
            return $true
        }
    }
    catch {
        Log-Message "✗ Mistral model test failed: $_" -Level "ERROR" -Color "Red"
        Log-Message "  Pull model: ollama pull mistral" -Level "INFO" -Color "Yellow"
        return $false
    }
}

function Test-PerformanceMetrics {
    Log-Message "`n" + ("=" * 80) -Level "TEST"
    Log-Message "3. TESTING PERFORMANCE METRICS" -Level "TEST" -Color "Cyan"
    Log-Message "=" * 80 -Level "TEST"

    try {
        $latencies = @()
        $throughputs = @()

        Log-Message "Running 5 test requests to establish baseline..." -Level "INFO"

        for ($i = 1; $i -le 5; $i++) {
            $start = Get-Date

            $payload = @{
                model       = "mistral"
                prompt      = "Generate a Python function: def hello():"
                stream      = $false
                num_predict = 50
                temperature = 0.3
            } | ConvertTo-Json

            $response = Invoke-WebRequest -Uri "http://localhost:11434/api/generate" `
                -Method Post `
                -ContentType "application/json" `
                -Body $payload `
                -TimeoutSec 30 `
                -ErrorAction Stop

            $elapsed = (Get-Date) - $start
            $latency = $elapsed.TotalMilliseconds

            if ($response.StatusCode -eq 200) {
                $data = $response.Content | ConvertFrom-Json
                $throughput = $data.eval_count / ($data.eval_duration / 1000000000)

                $latencies += $latency
                $throughputs += $throughput

                Log-Message "  Request $i: ${latency}ms latency, ${throughput} tokens/sec" -Level "INFO"
            }
        }

        if ($latencies.Count -gt 0) {
            $avgLatency = ($latencies | Measure-Object -Average).Average
            $avgThroughput = ($throughputs | Measure-Object -Average).Average
            $maxLatency = ($latencies | Measure-Object -Maximum).Maximum
            $minLatency = ($latencies | Measure-Object -Minimum).Minimum

            Log-Message "`n✓ Performance Metrics:" -Level "SUCCESS" -Color "Green"
            Log-Message "  Average Latency: ${avgLatency}ms (Target: <500ms)" -Level "INFO" -Color $(if ($avgLatency -lt 500) { "Green" } else { "Yellow" })
            Log-Message "  Min/Max Latency: ${minLatency}ms / ${maxLatency}ms" -Level "INFO" -Color "Green"
            Log-Message "  Average Throughput: ${avgThroughput} tokens/sec (Target: >50)" -Level "INFO" -Color $(if ($avgThroughput -gt 50) { "Green" } else { "Yellow" })

            return $true
        }
    }
    catch {
        Log-Message "✗ Performance test failed: $_" -Level "ERROR" -Color "Red"
        return $false
    }
}

function Test-LLMEndpoints {
    Log-Message "`n" + ("=" * 80) -Level "TEST"
    Log-Message "4. TESTING BACKEND LLM ENDPOINTS" -Level "TEST" -Color "Cyan"
    Log-Message "=" * 80 -Level "TEST"

    $endpoints = @(
        @{
            name   = "/api/generate-code-local"
            method = "POST"
            body   = @{
                prompt   = "Write a Python function to add two numbers"
                language = "python"
            }
        }
    )

    foreach ($endpoint in $endpoints) {
        try {
            Log-Message "Testing: $($endpoint.name)" -Level "INFO"

            $response = Invoke-WebRequest -Uri "http://localhost:5000$($endpoint.name)" `
                -Method $endpoint.method `
                -ContentType "application/json" `
                -Body ($endpoint.body | ConvertTo-Json) `
                -TimeoutSec 30 `
                -ErrorAction Stop

            if ($response.StatusCode -eq 200) {
                Log-Message "  ✓ $($endpoint.name) working" -Level "SUCCESS" -Color "Green"
            }
        }
        catch {
            Log-Message "  ⚠ $($endpoint.name): Requires backend running" -Level "WARNING" -Color "Yellow"
        }
    }
}

function Test-EncodingValidation {
    Log-Message "`n" + ("=" * 80) -Level "TEST"
    Log-Message "5. TESTING FILE ENCODING VALIDATION" -Level "TEST" -Color "Cyan"
    Log-Message "=" * 80 -Level "TEST"

    try {
        $pythonScript = @"
import chardet
import os

files_to_check = [
    'backend/main.py',
    'backend/local_llm_router.py',
    '.github/copilot-instructions.md'
]

for file_path in files_to_check:
    if os.path.exists(file_path):
        with open(file_path, 'rb') as f:
            raw = f.read(10000)
        detection = chardet.detect(raw)
        print(f"✓ {file_path}: {detection['encoding']} (confidence: {detection['confidence']:.2f})")
    else:
        print(f"✗ {file_path}: Not found")
"@

        $scriptPath = "C:\Users\johng\Documents\oscar\temp_encoding_check.py"
        $pythonScript | Out-File -FilePath $scriptPath -Encoding UTF8

        Push-Location "C:\Users\johng\Documents\oscar"
        $output = python $scriptPath 2>&1
        Pop-Location

        Log-Message $output -Level "INFO"
        Remove-Item -Path $scriptPath -Force -ErrorAction SilentlyContinue
    }
    catch {
        Log-Message "Encoding check requires Python: $_" -Level "WARNING" -Color "Yellow"
    }
}

# ============================================================================
# MAIN EXECUTION
# ============================================================================

Log-Message "ORFEAS - Local LLM Integration Validation Started" -Level "INFO" -Color "Cyan"
Log-Message "Timestamp: $timestamp" -Level "INFO"
Log-Message "Log file: $logFile" -Level "INFO"

$results = @()

$results += @{ name = "Ollama Connectivity"; status = Test-OllamaConnectivity }
$results += @{ name = "Mistral Model"; status = Test-MistralModel }
$results += @{ name = "Performance Metrics"; status = Test-PerformanceMetrics }
$results += @{ name = "Backend Endpoints"; status = Test-LLMEndpoints }
$results += @{ name = "Encoding Validation"; status = Test-EncodingValidation }

# Summary
Log-Message "`n" + ("=" * 80) -Level "SUMMARY"
Log-Message "VALIDATION SUMMARY" -Level "SUMMARY" -Color "Cyan"
Log-Message "=" * 80 -Level "SUMMARY"

$passCount = 0
foreach ($result in $results) {
    $status = if ($result.status) { "✓ PASS" } else { "✗ FAIL" }
    $color = if ($result.status) { "Green" } else { "Red" }
    Log-Message "$status - $($result.name)" -Level "SUMMARY" -Color $color
    if ($result.status) { $passCount++ }
}

Log-Message "`nPassed: $passCount/$($results.Count) tests" -Level "SUMMARY" -Color "Cyan"
Log-Message "Log saved: $logFile" -Level "INFO" -Color "Green"

Write-Host "`nValidation complete. View detailed log above." -ForegroundColor Cyan
