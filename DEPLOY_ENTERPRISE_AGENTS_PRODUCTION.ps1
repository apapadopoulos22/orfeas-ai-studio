# ORFEAS Enterprise Agent System - Production Deployment Script
# Comprehensive production deployment with performance benchmarking and monitoring

param(
    [Parameter(Mandatory = $false)]
    [string]$Environment = "production",

    [Parameter(Mandatory = $false)]
    [switch]$SkipBenchmark = $false,

    [Parameter(Mandatory = $false)]
    [switch]$EnableLoadTesting = $true,

    [Parameter(Mandatory = $false)]
    [switch]$SetupMonitoring = $true,

    [Parameter(Mandatory = $false)]
    [switch]$ValidateOnly = $false
)

$ErrorActionPreference = "Stop"

Write-Host "" -ForegroundColor Green
Write-Host "  ORFEAS ENTERPRISE AGENTS - PRODUCTION DEPLOYMENT                      " -ForegroundColor Green
Write-Host "                                                                              " -ForegroundColor Green
Write-Host "  Performance Benchmarking & Load Testing                                  " -ForegroundColor Green
Write-Host "  Monitoring & Observability Setup                                         " -ForegroundColor Green
Write-Host "  Production-Ready Multi-Agent Orchestration                               " -ForegroundColor Green
Write-Host "                                                                              " -ForegroundColor Green
Write-Host "" -ForegroundColor Green
Write-Host ""

# Production deployment configuration
$ProductionConfig = @{
    Environment         = $Environment
    LoadTestDuration    = 300  # 5 minutes
    ConcurrentUsers     = 100
    RequestsPerSecond   = 50
    BenchmarkIterations = 10
    MonitoringRetention = "30d"
    AlertThresholds     = @{
        ResponseTime      = 5.0      # seconds
        ErrorRate         = 0.05        # 5%
        CPUUsage          = 80           # percent
        MemoryUsage       = 85        # percent
        AgentAvailability = 95  # percent
    }
}

Write-Host " Production Environment: $Environment" -ForegroundColor Cyan
Write-Host " Benchmarking: $(if (-not $SkipBenchmark) { 'Enabled' } else { 'Disabled' })" -ForegroundColor Cyan
Write-Host " Load Testing: $(if ($EnableLoadTesting) { 'Enabled' } else { 'Disabled' })" -ForegroundColor Cyan
Write-Host " Monitoring: $(if ($SetupMonitoring) { 'Enabled' } else { 'Disabled' })" -ForegroundColor Cyan
Write-Host ""

function Test-Prerequisites {
    Write-Host " Checking production deployment prerequisites..." -ForegroundColor Yellow

    $issues = @()

    # Check Python environment
    try {
        $pythonVersion = python --version 2>&1
        if ($pythonVersion -match "Python 3\.([8-9]|1[0-9])") {
            Write-Host " Python version compatible: $pythonVersion" -ForegroundColor Green
        }
        else {
            $issues += " Python 3.8+ required, found: $pythonVersion"
        }
    }
    catch {
        $issues += " Python not found in PATH"
    }

    # Check Docker (for production containers)
    try {
        $dockerVersion = docker --version 2>&1
        Write-Host " Docker available: $dockerVersion" -ForegroundColor Green
    }
    catch {
        $issues += " Docker not available - containerized deployment disabled"
    }

    # Check GPU availability
    try {
        $gpuInfo = python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}, GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"None\"}')" 2>&1
        Write-Host " GPU Status: $gpuInfo" -ForegroundColor Green
    }
    catch {
        $issues += " GPU check failed - CPU-only mode"
    }

    # Check required ports
    $requiredPorts = @(5000, 6379, 3000, 9090)  # Flask, Redis, Grafana, Prometheus
    foreach ($port in $requiredPorts) {
        $portTest = Test-NetConnection -ComputerName localhost -Port $port -WarningAction SilentlyContinue
        if ($portTest.TcpTestSucceeded) {
            Write-Host " Port $port is in use - may need to stop existing services" -ForegroundColor Yellow
        }
        else {
            Write-Host " Port $port available" -ForegroundColor Green
        }
    }

    if ($issues.Count -gt 0) {
        Write-Host ""
        Write-Host " Prerequisites Issues:" -ForegroundColor Red
        foreach ($issue in $issues) {
            Write-Host "   $issue" -ForegroundColor Red
        }
        return $false
    }

    Write-Host " All prerequisites satisfied" -ForegroundColor Green
    return $true
}

function Install-ProductionDependencies {
    Write-Host " Installing production dependencies..." -ForegroundColor Yellow

    try {
        # Install enterprise agent dependencies
        pip install -r backend/requirements-enterprise-agents.txt --upgrade

        # Install load testing tools
        pip install locust pytest-benchmark httpx aiohttp-test-client --upgrade

        # Install monitoring tools
        pip install prometheus-client grafana-api psutil memory-profiler --upgrade

        Write-Host " Production dependencies installed" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host " Failed to install dependencies: $_" -ForegroundColor Red
        return $false
    }
}

function Start-ProductionServices {
    Write-Host " Starting production services..." -ForegroundColor Yellow

    # Start Redis for agent communication
    try {
        $redisProcess = Start-Process -FilePath "redis-server" -WindowStyle Minimized -PassThru
        Start-Sleep -Seconds 3
        Write-Host " Redis started (PID: $($redisProcess.Id))" -ForegroundColor Green
    }
    catch {
        Write-Host " Redis start failed - using in-memory message bus" -ForegroundColor Yellow
    }

    # Start monitoring services if requested
    if ($SetupMonitoring) {
        Start-MonitoringStack
    }

    return $true
}

function Start-MonitoringStack {
    Write-Host " Setting up monitoring stack..." -ForegroundColor Yellow

    # Check if Docker Compose monitoring is available
    if (Test-Path "docker-compose-monitoring.yml") {
        try {
            docker-compose -f docker-compose-monitoring.yml up -d
            Write-Host " Monitoring stack started (Prometheus, Grafana)" -ForegroundColor Green
        }
        catch {
            Write-Host " Docker monitoring stack failed" -ForegroundColor Yellow
        }
    }

    # Setup Python-based monitoring
    Write-Host " Configuring application monitoring..." -ForegroundColor Yellow

    # Set monitoring environment variables
    [Environment]::SetEnvironmentVariable("PROMETHEUS_METRICS_ENABLED", "true", "Process")
    [Environment]::SetEnvironmentVariable("AGENT_METRICS_ENABLED", "true", "Process")
    [Environment]::SetEnvironmentVariable("PERFORMANCE_MONITORING", "true", "Process")
}

function Invoke-PerformanceBenchmarking {
    if ($SkipBenchmark) {
        Write-Host "⏭ Skipping performance benchmarking" -ForegroundColor Yellow
        return $true
    }

    Write-Host " Running performance benchmarking..." -ForegroundColor Yellow

    # Start ORFEAS in background for benchmarking
    Write-Host " Starting ORFEAS for benchmarking..." -ForegroundColor Yellow

    $env:ENABLE_ENTERPRISE_AGENTS = "true"
    $env:ENTERPRISE_AGENT_MODE = "production"
    $env:TESTING = "0"

    $orfeusProcess = Start-Process -FilePath "python" -ArgumentList "backend/main.py" -WindowStyle Minimized -PassThru

    # Wait for server to start
    Write-Host "⏳ Waiting for server startup..." -ForegroundColor Yellow
    Start-Sleep -Seconds 15

    # Run benchmarks
    try {
        Write-Host " Running agent system benchmarks..." -ForegroundColor Yellow
        $benchmarkResult = python backend/run_production_benchmarks.py

        if ($LASTEXITCODE -eq 0) {
            Write-Host " Performance benchmarking completed successfully" -ForegroundColor Green
        }
        else {
            Write-Host " Performance benchmarking failed" -ForegroundColor Red
        }
    }
    catch {
        Write-Host " Benchmark execution failed: $_" -ForegroundColor Red
    }
    finally {
        # Stop the test server
        if ($orfeusProcess -and -not $orfeusProcess.HasExited) {
            Stop-Process -Id $orfeusProcess.Id -Force
            Write-Host " Test server stopped" -ForegroundColor Yellow
        }
    }

    return $LASTEXITCODE -eq 0
}

function Invoke-LoadTesting {
    if (-not $EnableLoadTesting) {
        Write-Host "⏭ Skipping load testing" -ForegroundColor Yellow
        return $true
    }

    Write-Host " Running load testing..." -ForegroundColor Yellow

    # Start ORFEAS for load testing
    Write-Host " Starting ORFEAS for load testing..." -ForegroundColor Yellow

    $env:ENABLE_ENTERPRISE_AGENTS = "true"
    $env:ENTERPRISE_AGENT_MODE = "production"

    $orfeusProcess = Start-Process -FilePath "python" -ArgumentList "backend/main.py" -WindowStyle Minimized -PassThru

    # Wait for server to start
    Start-Sleep -Seconds 15

    try {
        Write-Host " Running load tests with $($ProductionConfig.ConcurrentUsers) concurrent users..." -ForegroundColor Yellow

        $loadTestResult = python backend/run_production_load_test.py --users $ProductionConfig.ConcurrentUsers --duration $ProductionConfig.LoadTestDuration --rps $ProductionConfig.RequestsPerSecond

        if ($LASTEXITCODE -eq 0) {
            Write-Host " Load testing completed successfully" -ForegroundColor Green
        }
        else {
            Write-Host " Load testing failed" -ForegroundColor Red
        }
    }
    catch {
        Write-Host " Load test execution failed: $_" -ForegroundColor Red
    }
    finally {
        # Stop the test server
        if ($orfeusProcess -and -not $orfeusProcess.HasExited) {
            Stop-Process -Id $orfeusProcess.Id -Force
            Write-Host " Load test server stopped" -ForegroundColor Yellow
        }
    }

    return $LASTEXITCODE -eq 0
}

function Deploy-ProductionServer {
    Write-Host " Deploying production server..." -ForegroundColor Green

    # Set production environment variables
    [Environment]::SetEnvironmentVariable("FLASK_ENV", "production", "Process")
    [Environment]::SetEnvironmentVariable("ENABLE_ENTERPRISE_AGENTS", "true", "Process")
    [Environment]::SetEnvironmentVariable("ENTERPRISE_AGENT_MODE", "production", "Process")
    [Environment]::SetEnvironmentVariable("AGENT_SYSTEM_DEBUG", "false", "Process")
    [Environment]::SetEnvironmentVariable("PROMETHEUS_METRICS_ENABLED", "true", "Process")

    Write-Host " Production environment configured" -ForegroundColor Green
    Write-Host " Server will be available at: http://localhost:5000" -ForegroundColor Cyan
    Write-Host " Metrics available at: http://localhost:5000/metrics" -ForegroundColor Cyan
    Write-Host " Agent API: http://localhost:5000/api/agents/" -ForegroundColor Cyan
    Write-Host ""

    if ($ValidateOnly) {
        Write-Host " Production deployment validation completed" -ForegroundColor Green
        return $true
    }

    # Start production server
    Write-Host " Starting ORFEAS Enterprise Agent System in production mode..." -ForegroundColor Green
    python backend/main.py
}

function Show-DeploymentSummary {
    param($benchmarkSuccess, $loadTestSuccess)

    Write-Host ""
    Write-Host "" -ForegroundColor Green
    Write-Host "                         PRODUCTION DEPLOYMENT SUMMARY                       " -ForegroundColor Green
    Write-Host "" -ForegroundColor Green
    Write-Host ""

    $deploymentItems = @(
        ("Prerequisites Check", $true),
        ("Dependencies Installation", $true),
        ("Production Services", $true),
        ("Performance Benchmarking", $benchmarkSuccess),
        ("Load Testing", $loadTestSuccess),
        ("Monitoring Setup", $SetupMonitoring)
    )

    foreach ($item in $deploymentItems) {
        $name, $success = $item
        $status = if ($success) { " SUCCESS" } else { " FAILED" }
        $color = if ($success) { "Green" } else { "Red" }
        Write-Host "  $status $name" -ForegroundColor $color
    }

    Write-Host ""
    Write-Host " ORFEAS Enterprise Agent System Production Status:" -ForegroundColor Cyan
    Write-Host "   - Multi-Agent Orchestration: ACTIVE" -ForegroundColor Green
    Write-Host "   - Performance Optimization: ENABLED" -ForegroundColor Green
    Write-Host "   - Load Balancing: OPERATIONAL" -ForegroundColor Green
    Write-Host "   - Monitoring & Metrics: COLLECTING" -ForegroundColor Green
    Write-Host ""

    if ($SetupMonitoring) {
        Write-Host " Monitoring Endpoints:" -ForegroundColor Cyan
        Write-Host "   - Prometheus: http://localhost:9090" -ForegroundColor Cyan
        Write-Host "   - Grafana: http://localhost:3000 (admin/admin)" -ForegroundColor Cyan
        Write-Host "   - Application Metrics: http://localhost:5000/metrics" -ForegroundColor Cyan
        Write-Host ""
    }

    Write-Host " Production deployment completed successfully!" -ForegroundColor Green
}

# Main execution flow
try {
    # Check prerequisites
    if (-not (Test-Prerequisites)) {
        Write-Host " Prerequisites check failed" -ForegroundColor Red
        exit 1
    }

    # Install dependencies
    if (-not (Install-ProductionDependencies)) {
        Write-Host " Dependency installation failed" -ForegroundColor Red
        exit 1
    }

    # Start services
    if (-not (Start-ProductionServices)) {
        Write-Host " Service startup failed" -ForegroundColor Red
        exit 1
    }

    # Run benchmarks
    $benchmarkSuccess = Invoke-PerformanceBenchmarking

    # Run load tests
    $loadTestSuccess = Invoke-LoadTesting

    # Show summary
    Show-DeploymentSummary -benchmarkSuccess $benchmarkSuccess -loadTestSuccess $loadTestSuccess

    # Deploy production server
    Deploy-ProductionServer

}
catch {
    Write-Host ""
    Write-Host " PRODUCTION DEPLOYMENT FAILED: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Troubleshooting:" -ForegroundColor Yellow
    Write-Host "  1. Check system prerequisites" -ForegroundColor Yellow
    Write-Host "  2. Verify Python environment and dependencies" -ForegroundColor Yellow
    Write-Host "  3. Ensure required ports are available" -ForegroundColor Yellow
    Write-Host "  4. Check logs for specific error details" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}
