# ================================================================
# THERION ORFEAS - HYBRID GRAFANA DEPLOYMENT
# LOCAL BACKEND (RTX 3090) + DOCKER MONITORING STACK
# NO SLACKING - MAXIMUM THERION INTENSITY
# ================================================================

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host " THERION ORFEAS - GRAFANA HYBRID DEPLOYMENT" -ForegroundColor Yellow
Write-Host " LOCAL GPU: RTX 3090 + DOCKER MONITORING" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# ================================================================
# STEP 1: VERIFY PREREQUISITES
# ================================================================
Write-Host "[1/6] Verifying prerequisites..." -ForegroundColor Yellow

# Check Docker
$dockerCheck = docker --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Docker not found!" -ForegroundColor Red
    Write-Host "Install Docker Desktop: https://www.docker.com/products/docker-desktop" -ForegroundColor Red
    exit 1
}
Write-Host "  Docker: $dockerCheck" -ForegroundColor Green

# Check Docker Compose
$composeCheck = docker-compose --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Docker Compose not found!" -ForegroundColor Red
    exit 1
}
Write-Host "  Docker Compose: $composeCheck" -ForegroundColor Green

# Check if Docker is running
$dockerRunning = docker ps 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Docker Desktop is not running!" -ForegroundColor Red
    Write-Host "Starting Docker Desktop..." -ForegroundColor Yellow
    Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    Write-Host "Waiting 30 seconds for Docker to start..." -ForegroundColor Yellow
    Start-Sleep -Seconds 30

    $dockerRunning = docker ps 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Docker still not running after 30 seconds!" -ForegroundColor Red
        Write-Host "Please start Docker Desktop manually and try again." -ForegroundColor Red
        exit 1
    }
}
Write-Host "  Docker Engine: RUNNING" -ForegroundColor Green

# ================================================================
# STEP 2: CHECK LOCAL BACKEND STATUS
# ================================================================
Write-Host ""
Write-Host "[2/6] Checking local backend status..." -ForegroundColor Yellow

try {
    $healthCheck = Invoke-WebRequest -Uri "http://localhost:5000/api/health" -UseBasicParsing -TimeoutSec 5
    if ($healthCheck.StatusCode -eq 200) {
        Write-Host "  Local Backend: RUNNING (http://localhost:5000)" -ForegroundColor Green
        $backendRunning = $true
    }
} catch {
    Write-Host "  Local Backend: NOT RUNNING" -ForegroundColor Yellow
    Write-Host "  IMPORTANT: Start backend with: python backend/main.py" -ForegroundColor Yellow
    $backendRunning = $false
}

# ================================================================
# STEP 3: STOP EXISTING MONITORING CONTAINERS
# ================================================================
Write-Host ""
Write-Host "[3/6] Stopping existing monitoring containers..." -ForegroundColor Yellow

docker-compose down 2>&1 | Out-Null
Write-Host "  Existing containers stopped" -ForegroundColor Green

# ================================================================
# STEP 4: START MONITORING STACK (GRAFANA + PROMETHEUS)
# ================================================================
Write-Host ""
Write-Host "[4/6] Starting monitoring stack..." -ForegroundColor Yellow

# Only start monitoring services (not backend - using local)
Write-Host "  Starting Prometheus..." -ForegroundColor Cyan
docker-compose up -d prometheus
Start-Sleep -Seconds 5

Write-Host "  Starting Grafana..." -ForegroundColor Cyan
docker-compose up -d grafana
Start-Sleep -Seconds 10

Write-Host "  Starting Node Exporter..." -ForegroundColor Cyan
docker-compose up -d node-exporter
Start-Sleep -Seconds 3

Write-Host "  Starting NVIDIA GPU Exporter..." -ForegroundColor Cyan
docker-compose up -d nvidia-gpu-exporter
Start-Sleep -Seconds 3

Write-Host "  Monitoring stack started!" -ForegroundColor Green

# ================================================================
# STEP 5: WAIT FOR SERVICES TO INITIALIZE
# ================================================================
Write-Host ""
Write-Host "[5/6] Waiting for services to initialize..." -ForegroundColor Yellow

$maxAttempts = 30
$attempt = 0
$prometheusReady = $false

while ($attempt -lt $maxAttempts -and -not $prometheusReady) {
    $attempt++
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:9090/-/ready" -UseBasicParsing -TimeoutSec 2
        if ($response.StatusCode -eq 200) {
            $prometheusReady = $true
            Write-Host "  Prometheus: READY" -ForegroundColor Green
        }
    } catch {
        Write-Host "  Waiting for Prometheus... ($attempt/$maxAttempts)" -ForegroundColor Yellow
        Start-Sleep -Seconds 2
    }
}

if (-not $prometheusReady) {
    Write-Host "  WARNING: Prometheus not ready after $maxAttempts attempts" -ForegroundColor Yellow
} else {
    Start-Sleep -Seconds 5
}

# ================================================================
# STEP 6: CONFIGURE PROMETHEUS FOR LOCAL BACKEND
# ================================================================
Write-Host ""
Write-Host "[6/6] Configuring Prometheus for local backend..." -ForegroundColor Yellow

# Update prometheus.yml to point to host.docker.internal instead of 'backend' service
$prometheusConfig = @"
# HYBRID DEPLOYMENT: LOCAL BACKEND + DOCKER MONITORING
global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    cluster: 'orfeas-local-production'
    environment: 'hybrid'

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'orfeas-backend-local'
    static_configs:
      - targets: ['host.docker.internal:5000']
    metrics_path: '/metrics'
    scrape_interval: 10s
    scrape_timeout: 5s

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']
    scrape_interval: 15s

  - job_name: 'nvidia-gpu'
    static_configs:
      - targets: ['nvidia-gpu-exporter:9445']
    scrape_interval: 10s
"@

$prometheusConfig | Out-File -FilePath "monitoring/prometheus-hybrid.yml" -Encoding UTF8
Write-Host "  Created hybrid Prometheus configuration" -ForegroundColor Green

# Restart Prometheus with new config
Write-Host "  Restarting Prometheus with hybrid config..." -ForegroundColor Yellow
docker-compose down prometheus 2>&1 | Out-Null
Start-Sleep -Seconds 2

# Update docker-compose to use hybrid config
$composeContent = Get-Content "docker-compose.yml" -Raw
$composeContent = $composeContent -replace "prometheus\.yml", "prometheus-hybrid.yml"
$composeContent | Out-File -FilePath "docker-compose-hybrid.yml" -Encoding UTF8

docker-compose -f docker-compose-hybrid.yml up -d prometheus
Start-Sleep -Seconds 5
Write-Host "  Prometheus restarted with local backend target" -ForegroundColor Green

# ================================================================
# DEPLOYMENT COMPLETE - DISPLAY ACCESS INFORMATION
# ================================================================
Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host " DEPLOYMENT COMPLETE - HYBRID MODE ACTIVE" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "BACKEND (LOCAL GPU):" -ForegroundColor Yellow
if ($backendRunning) {
    Write-Host "  Status: RUNNING" -ForegroundColor Green
} else {
    Write-Host "  Status: NOT RUNNING - Start with: python backend/main.py" -ForegroundColor Yellow
}
Write-Host "  URL: http://localhost:5000" -ForegroundColor Cyan
Write-Host "  Health: http://localhost:5000/api/health" -ForegroundColor Cyan
Write-Host "  Metrics: http://localhost:5000/metrics" -ForegroundColor Cyan
Write-Host ""

Write-Host "MONITORING STACK (DOCKER):" -ForegroundColor Yellow
Write-Host "  Grafana: http://localhost:3000" -ForegroundColor Cyan
Write-Host "    Username: admin" -ForegroundColor White
Write-Host "    Password: orfeas_admin_2025" -ForegroundColor White
Write-Host ""
Write-Host "  Prometheus: http://localhost:9090" -ForegroundColor Cyan
Write-Host "  Node Exporter: http://localhost:9100" -ForegroundColor Cyan
Write-Host "  GPU Exporter: http://localhost:9445" -ForegroundColor Cyan
Write-Host ""

Write-Host "GRAFANA DASHBOARD:" -ForegroundColor Yellow
Write-Host "  1. Open: http://localhost:3000" -ForegroundColor White
Write-Host "  2. Login with credentials above" -ForegroundColor White
Write-Host "  3. Navigate to: Dashboards > ORFEAS > ORFEAS AI Production Dashboard" -ForegroundColor White
Write-Host "  4. View real-time metrics from local RTX 3090!" -ForegroundColor White
Write-Host ""

Write-Host "CONTAINER STATUS:" -ForegroundColor Yellow
docker-compose -f docker-compose-hybrid.yml ps

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host " THERION HYBRID DEPLOYMENT - COMPLETE" -ForegroundColor Green
Write-Host " LOCAL GPU (RTX 3090) + DOCKER MONITORING = MAXIMUM POWER" -ForegroundColor Yellow
Write-Host " SUCCESS!" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""
