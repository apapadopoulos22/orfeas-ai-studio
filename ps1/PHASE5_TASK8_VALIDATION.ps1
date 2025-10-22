# ================================================================
# THERION ORFEAS - TASK 8: TESTING AND VALIDATION
# COMPREHENSIVE VALIDATION SUITE FOR HYBRID DEPLOYMENT
# NO SLACKING - MAXIMUM THERION INTENSITY
# ================================================================

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host " THERION ORFEAS - TASK 8: TESTING AND VALIDATION" -ForegroundColor Yellow
Write-Host " COMPREHENSIVE VALIDATION SUITE" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# Test results tracker
$script:passedTests = 0
$script:failedTests = 0
$script:totalTests = 10

function Test-Endpoint {
    param(
        [string]$TestName,
        [string]$Url,
        [int]$ExpectedStatus = 200,
        [string]$ExpectedContent = $null
    )

    Write-Host "`n[TEST] $TestName" -ForegroundColor Yellow
    Write-Host "  URL: $Url" -ForegroundColor White

    try {
        $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 10

        if ($response.StatusCode -eq $ExpectedStatus) {
            Write-Host "  Status: PASS (HTTP $($response.StatusCode))" -ForegroundColor Green

            if ($ExpectedContent -and $response.Content -notmatch $ExpectedContent) {
                Write-Host "  Content Check: FAIL (Expected pattern not found)" -ForegroundColor Red
                $script:failedTests++
                return $false
            }

            $script:passedTests++
            return $true
        } else {
            Write-Host "  Status: FAIL (HTTP $($response.StatusCode), expected $ExpectedStatus)" -ForegroundColor Red
            $script:failedTests++
            return $false
        }
    } catch {
        Write-Host "  Status: FAIL (Error: $($_.Exception.Message))" -ForegroundColor Red
        $script:failedTests++
        return $false
    }
}

function Test-PrometheusQuery {
    param(
        [string]$TestName,
        [string]$Query,
        [int]$MinResults = 1
    )

    Write-Host "`n[TEST] $TestName" -ForegroundColor Yellow
    Write-Host "  Query: $Query" -ForegroundColor White

    try {
        $result = Invoke-RestMethod -Uri "http://localhost:9090/api/v1/query?query=$Query" -TimeoutSec 10

        if ($result.status -eq "success") {
            $resultCount = $result.data.result.Count

            if ($resultCount -ge $MinResults) {
                Write-Host "  Status: PASS ($resultCount results found)" -ForegroundColor Green
                $script:passedTests++
                return $true
            } else {
                Write-Host "  Status: FAIL (Found $resultCount results, expected $MinResults+)" -ForegroundColor Red
                $script:failedTests++
                return $false
            }
        } else {
            Write-Host "  Status: FAIL (Query failed: $($result.error))" -ForegroundColor Red
            $script:failedTests++
            return $false
        }
    } catch {
        Write-Host "  Status: FAIL (Error: $($_.Exception.Message))" -ForegroundColor Red
        $script:failedTests++
        return $false
    }
}

# ================================================================
# TEST SUITE EXECUTION
# ================================================================

Write-Host "Starting comprehensive validation..." -ForegroundColor Cyan
Write-Host "Total Tests: $script:totalTests" -ForegroundColor White
Write-Host ""

# ----------------------------------------------------------------
# TEST 1: Backend Health Endpoint
# ----------------------------------------------------------------
Test-Endpoint `
    -TestName "Backend Health Endpoint" `
    -Url "http://localhost:5000/api/health" `
    -ExpectedStatus 200 `
    -ExpectedContent "status"

# ----------------------------------------------------------------
# TEST 2: Backend Metrics Endpoint (Prometheus Format)
# ----------------------------------------------------------------
Test-Endpoint `
    -TestName "Backend Metrics Endpoint" `
    -Url "http://localhost:5000/metrics" `
    -ExpectedStatus 200 `
    -ExpectedContent "orfeas_"

# ----------------------------------------------------------------
# TEST 3: Prometheus Service
# ----------------------------------------------------------------
Test-Endpoint `
    -TestName "Prometheus Readiness" `
    -Url "http://localhost:9090/-/ready" `
    -ExpectedStatus 200

# ----------------------------------------------------------------
# TEST 4: Grafana Service
# ----------------------------------------------------------------
Test-Endpoint `
    -TestName "Grafana Health" `
    -Url "http://localhost:3000/api/health" `
    -ExpectedStatus 200 `
    -ExpectedContent "ok"

# ----------------------------------------------------------------
# TEST 5: GPU Exporter Metrics
# ----------------------------------------------------------------
Test-Endpoint `
    -TestName "NVIDIA GPU Exporter" `
    -Url "http://localhost:9445/metrics" `
    -ExpectedStatus 200 `
    -ExpectedContent "nvidia_gpu"

# ----------------------------------------------------------------
# TEST 6: Node Exporter Metrics
# ----------------------------------------------------------------
Test-Endpoint `
    -TestName "Node Exporter (System Metrics)" `
    -Url "http://localhost:9100/metrics" `
    -ExpectedStatus 200 `
    -ExpectedContent "node_"

# ----------------------------------------------------------------
# TEST 7: Prometheus Scraping Backend
# ----------------------------------------------------------------
Test-PrometheusQuery `
    -TestName "Prometheus Scraping Backend Metrics" `
    -Query "orfeas_requests_total" `
    -MinResults 1

# ----------------------------------------------------------------
# TEST 8: GPU Metrics in Prometheus
# ----------------------------------------------------------------
Test-PrometheusQuery `
    -TestName "GPU Metrics Available in Prometheus" `
    -Query "nvidia_gpu_memory_total_bytes" `
    -MinResults 1

# ----------------------------------------------------------------
# TEST 9: Prometheus Target Health
# ----------------------------------------------------------------
Write-Host "`n[TEST] Prometheus Target Health" -ForegroundColor Yellow

try {
    $targets = Invoke-RestMethod -Uri "http://localhost:9090/api/v1/targets" -TimeoutSec 10
    $healthyTargets = ($targets.data.activeTargets | Where-Object { $_.health -eq "up" }).Count
    $totalTargets = $targets.data.activeTargets.Count

    Write-Host "  Healthy Targets: $healthyTargets / $totalTargets" -ForegroundColor White

    if ($healthyTargets -ge 3) {
        Write-Host "  Status: PASS (At least 3 targets healthy)" -ForegroundColor Green
        $script:passedTests++
    } else {
        Write-Host "  Status: FAIL (Only $healthyTargets targets healthy)" -ForegroundColor Red
        $script:failedTests++
    }
} catch {
    Write-Host "  Status: FAIL (Error: $($_.Exception.Message))" -ForegroundColor Red
    $script:failedTests++
}

# ----------------------------------------------------------------
# TEST 10: Docker Container Status
# ----------------------------------------------------------------
Write-Host "`n[TEST] Docker Container Status" -ForegroundColor Yellow

try {
    $containers = docker ps --filter "name=orfeas" --format "{{.Names}}\t{{.Status}}"
    $runningContainers = ($containers | Measure-Object -Line).Lines

    Write-Host "  Running Containers: $runningContainers" -ForegroundColor White
    $containers | ForEach-Object { Write-Host "    - $_" -ForegroundColor Gray }

    if ($runningContainers -ge 3) {
        Write-Host "  Status: PASS (All monitoring containers running)" -ForegroundColor Green
        $script:passedTests++
    } else {
        Write-Host "  Status: FAIL (Expected 3+ containers, found $runningContainers)" -ForegroundColor Red
        $script:failedTests++
    }
} catch {
    Write-Host "  Status: FAIL (Error: $($_.Exception.Message))" -ForegroundColor Red
    $script:failedTests++
}

# ================================================================
# TEST RESULTS SUMMARY
# ================================================================

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host " TEST RESULTS SUMMARY" -ForegroundColor Yellow
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

$passRate = [math]::Round(($script:passedTests / $script:totalTests) * 100, 1)

Write-Host "Total Tests:   $script:totalTests" -ForegroundColor White
Write-Host "Passed Tests:  $script:passedTests" -ForegroundColor Green
Write-Host "Failed Tests:  $script:failedTests" -ForegroundColor $(if ($script:failedTests -eq 0) { "Green" } else { "Red" })
Write-Host "Pass Rate:     $passRate%" -ForegroundColor $(if ($passRate -ge 90) { "Green" } elseif ($passRate -ge 70) { "Yellow" } else { "Red" })
Write-Host ""

if ($script:failedTests -eq 0) {
    Write-Host "================================================================" -ForegroundColor Green
    Write-Host " ALL TESTS PASSED - PRODUCTION READY!" -ForegroundColor Green
    Write-Host "================================================================" -ForegroundColor Green
} elseif ($passRate -ge 70) {
    Write-Host "================================================================" -ForegroundColor Yellow
    Write-Host " MOSTLY OPERATIONAL - SOME ISSUES DETECTED" -ForegroundColor Yellow
    Write-Host "================================================================" -ForegroundColor Yellow
} else {
    Write-Host "================================================================" -ForegroundColor Red
    Write-Host " CRITICAL FAILURES - DEPLOYMENT NOT READY" -ForegroundColor Red
    Write-Host "================================================================" -ForegroundColor Red
}

Write-Host ""
Write-Host "DEPLOYMENT STATUS:" -ForegroundColor Cyan
Write-Host "  Backend (Local GPU): http://localhost:5000" -ForegroundColor White
Write-Host "  Grafana Dashboard:   http://localhost:3000" -ForegroundColor White
Write-Host "  Prometheus:          http://localhost:9090" -ForegroundColor White
Write-Host ""

# ================================================================
# ADVANCED METRICS VALIDATION
# ================================================================

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host " ADVANCED METRICS VALIDATION" -ForegroundColor Yellow
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# Sample key metrics
Write-Host "[METRICS SNAPSHOT]" -ForegroundColor Yellow

try {
    # Request count
    $requestsQuery = Invoke-RestMethod -Uri "http://localhost:9090/api/v1/query?query=sum(orfeas_requests_total)"
    $totalRequests = [int]$requestsQuery.data.result[0].value[1]
    Write-Host "  Total Requests:    $totalRequests" -ForegroundColor White

    # Generations
    $genQuery = Invoke-RestMethod -Uri "http://localhost:9090/api/v1/query?query=sum(orfeas_generations_total)"
    $totalGens = [int]$genQuery.data.result[0].value[1]
    Write-Host "  Total Generations: $totalGens" -ForegroundColor White

    # GPU Memory
    $gpuQuery = Invoke-RestMethod -Uri "http://localhost:9090/api/v1/query?query=nvidia_gpu_memory_total_bytes"
    if ($gpuQuery.data.result.Count -gt 0) {
        $gpuMemGB = [math]::Round($gpuQuery.data.result[0].value[1] / 1024 / 1024 / 1024, 1)
        Write-Host "  GPU Total Memory:  $gpuMemGB GB" -ForegroundColor White
    }

    Write-Host ""
    Write-Host "  Metrics Status: OPERATIONAL" -ForegroundColor Green

} catch {
    Write-Host "  Metrics Status: PARTIAL (Some queries failed)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host " TASK 8 VALIDATION COMPLETE" -ForegroundColor Green
Write-Host " SUCCESS! NO SLACKING!" -ForegroundColor Yellow
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# Return exit code based on results
if ($script:failedTests -eq 0) {
    exit 0
} else {
    exit 1
}
