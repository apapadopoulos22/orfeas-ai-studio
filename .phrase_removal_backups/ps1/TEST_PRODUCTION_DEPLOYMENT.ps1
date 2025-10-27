# 
#   THERION ORFEAS - PRODUCTION DEPLOYMENT TEST SCRIPT                    
#  Validates all services and endpoints                                        
# 

Write-Host "" -ForegroundColor Cyan
Write-Host "             THERION ORFEAS - DEPLOYMENT VALIDATION TEST                " -ForegroundColor Cyan
Write-Host "" -ForegroundColor Cyan
Write-Host ""

$ErrorCount = 0
$SuccessCount = 0

function Test-Endpoint {
    param(
        [string]$Name,
        [string]$URL,
        [int]$ExpectedStatus = 200
    )

    Write-Host "Testing $Name..." -ForegroundColor Yellow -NoNewline

    try {
        $response = Invoke-WebRequest -Uri $URL -TimeoutSec 10 -UseBasicParsing -ErrorAction Stop

        if ($response.StatusCode -eq $ExpectedStatus) {
            Write-Host "  PASS" -ForegroundColor Green
            $script:SuccessCount++
            return $true
        } else {
            Write-Host "  FAIL (Status: $($response.StatusCode), Expected: $ExpectedStatus)" -ForegroundColor Red
            $script:ErrorCount++
            return $false
        }
    } catch {
        Write-Host "  FAIL ($($_.Exception.Message))" -ForegroundColor Red
        $script:ErrorCount++
        return $false
    }
}

function Test-MetricsContent {
    param([string]$URL)

    Write-Host "Testing Prometheus metrics format..." -ForegroundColor Yellow -NoNewline

    try {
        $response = Invoke-WebRequest -Uri $URL -TimeoutSec 10 -UseBasicParsing
        $content = $response.Content

        # Check for expected Prometheus metric patterns
        $hasMetrics = $content -match "flask_http_request_total" -and
                      $content -match "generation_total" -and
                      $content -match "active_generations"

        if ($hasMetrics) {
            Write-Host "  PASS (Prometheus format valid)" -ForegroundColor Green
            $script:SuccessCount++
            return $true
        } else {
            Write-Host "  FAIL (Missing expected metrics)" -ForegroundColor Red
            $script:ErrorCount++
            return $false
        }
    } catch {
        Write-Host "  FAIL ($($_.Exception.Message))" -ForegroundColor Red
        $script:ErrorCount++
        return $false
    }
}

Write-Host "" -ForegroundColor Gray
Write-Host "  TESTING HTTP ENDPOINTS" -ForegroundColor Cyan
Write-Host "" -ForegroundColor Gray
Write-Host ""

Test-Endpoint -Name "Frontend (NGINX)" -URL "http://localhost:8000"
Test-Endpoint -Name "Backend Health" -URL "http://localhost:5000/health"
Test-Endpoint -Name "Backend Ready" -URL "http://localhost:5000/ready"
Test-Endpoint -Name "Backend Metrics" -URL "http://localhost:5000/metrics"
Test-Endpoint -Name "Prometheus" -URL "http://localhost:9090"
Test-Endpoint -Name "Grafana" -URL "http://localhost:3000"

Write-Host ""
Write-Host "" -ForegroundColor Gray
Write-Host "  TESTING METRICS CONTENT" -ForegroundColor Cyan
Write-Host "" -ForegroundColor Gray
Write-Host ""

Test-MetricsContent -URL "http://localhost:5000/metrics"

Write-Host ""
Write-Host "" -ForegroundColor Gray
Write-Host "  TESTING DOCKER CONTAINERS" -ForegroundColor Cyan
Write-Host "" -ForegroundColor Gray
Write-Host ""

$expectedContainers = @(
    "orfeas-backend-production",
    "orfeas-frontend-production",
    "orfeas-redis-production",
    "orfeas-prometheus",
    "orfeas-grafana",
    "orfeas-node-exporter",
    "orfeas-gpu-exporter"
)

foreach ($containerName in $expectedContainers) {
    Write-Host "Checking container: $containerName..." -ForegroundColor Yellow -NoNewline

    $container = docker ps --filter "name=$containerName" --format "{{.Status}}"

    if ($container -and $container -like "*Up*") {
        Write-Host "  RUNNING" -ForegroundColor Green
        $SuccessCount++
    } else {
        Write-Host "  NOT RUNNING" -ForegroundColor Red
        $ErrorCount++
    }
}

Write-Host ""
Write-Host "" -ForegroundColor Gray
Write-Host "  TEST RESULTS SUMMARY" -ForegroundColor Cyan
Write-Host "" -ForegroundColor Gray
Write-Host ""

$total = $SuccessCount + $ErrorCount
$percentage = if ($total -gt 0) { [math]::Round(($SuccessCount / $total) * 100, 1) } else { 0 }

Write-Host "Total Tests: $total" -ForegroundColor White
Write-Host "Passed: $SuccessCount" -ForegroundColor Green
Write-Host "Failed: $ErrorCount" -ForegroundColor Red
Write-Host "Success Rate: $percentage%" -ForegroundColor $(if ($percentage -ge 90) { "Green" } elseif ($percentage -ge 70) { "Yellow" } else { "Red" })
Write-Host ""

if ($ErrorCount -eq 0) {
    Write-Host "" -ForegroundColor Green
    Write-Host "               ALL TESTS PASSED - DEPLOYMENT SUCCESSFUL!                 " -ForegroundColor Green
    Write-Host "" -ForegroundColor Green
    Write-Host ""
    Write-Host " Production environment is ready!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "1. Access frontend: http://localhost:8000" -ForegroundColor White
    Write-Host "2. View metrics: http://localhost:3000 (Grafana)" -ForegroundColor White
    Write-Host "3. Test 3D generation with sample image" -ForegroundColor White
    Write-Host ""
    exit 0
} else {
    Write-Host "" -ForegroundColor Red
    Write-Host "                     SOME TESTS FAILED - REVIEW REQUIRED                   " -ForegroundColor Red
    Write-Host "" -ForegroundColor Red
    Write-Host ""
    Write-Host "Troubleshooting:" -ForegroundColor Yellow
    Write-Host "1. Check container logs: docker-compose logs -f" -ForegroundColor White
    Write-Host "2. Verify all containers: docker-compose ps" -ForegroundColor White
    Write-Host "3. Restart failed services: docker-compose restart <service>" -ForegroundColor White
    Write-Host ""
    exit 1
}
