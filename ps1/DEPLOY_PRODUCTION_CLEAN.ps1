# THERION ORFEAS - PRODUCTION DEPLOYMENT SCRIPT
# One-command deployment for LOCAL GPU production environment
# MAXIMUM PERFORMANCE 

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  THERION ORFEAS - PHASE 5 PRODUCTION DEPLOYMENT" -ForegroundColor Cyan
Write-Host "  LOCAL GPU INFRASTRUCTURE ACTIVATION" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# Check Docker installation
Write-Host "[1/8] Checking Docker installation..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version
    Write-Host "[OK] Docker installed: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Docker not found! Install Docker Desktop for Windows." -ForegroundColor Red
    Write-Host "Download: https://www.docker.com/products/docker-desktop/" -ForegroundColor Yellow
    exit 1
}

# Check Docker Compose
Write-Host "[2/8] Checking Docker Compose..." -ForegroundColor Yellow
try {
    $composeVersion = docker-compose --version
    Write-Host "[OK] Docker Compose installed: $composeVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Docker Compose not found!" -ForegroundColor Red
    exit 1
}

# Check NVIDIA Docker runtime
Write-Host "[3/8] Checking NVIDIA Docker runtime..." -ForegroundColor Yellow
try {
    $nvidiaRuntime = docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] NVIDIA Docker runtime available" -ForegroundColor Green
    } else {
        Write-Host "[WARNING] NVIDIA Docker runtime may have issues" -ForegroundColor Yellow
    }
} catch {
    Write-Host "[WARNING] Cannot verify NVIDIA Docker runtime" -ForegroundColor Yellow
    Write-Host "Install NVIDIA Container Toolkit if you have NVIDIA GPU" -ForegroundColor Yellow
}

# Stop existing containers
Write-Host "[4/8] Stopping existing containers..." -ForegroundColor Yellow
docker-compose down 2>$null
Write-Host "[OK] Existing containers stopped" -ForegroundColor Green

# Build Docker images
Write-Host "[5/8] Building Docker images (this may take 10-15 minutes)..." -ForegroundColor Yellow
docker-compose build --no-cache
if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Docker images built successfully" -ForegroundColor Green
} else {
    Write-Host "[ERROR] Docker build failed!" -ForegroundColor Red
    exit 1
}

# Create necessary directories
Write-Host "[6/8] Creating required directories..." -ForegroundColor Yellow
$directories = @(
    "outputs",
    "uploads",
    "temp",
    "models"
)

foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "   Created: $dir" -ForegroundColor Gray
    }
}
Write-Host "[OK] Directories ready" -ForegroundColor Green

# Start production environment
Write-Host "[7/8] Starting production environment..." -ForegroundColor Yellow
docker-compose up -d

if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] All services started successfully!" -ForegroundColor Green
} else {
    Write-Host "[ERROR] Failed to start services" -ForegroundColor Red
    exit 1
}

# Wait for services to be ready
Write-Host "[8/8] Waiting for services to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Check service health
Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  SERVICE STATUS CHECK" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

$services = @(
    @{ Name = "Backend API"; URL = "http://localhost:5000/health"; Port = 5000 },
    @{ Name = "Frontend"; URL = "http://localhost:8000"; Port = 8000 },
    @{ Name = "Prometheus"; URL = "http://localhost:9090"; Port = 9090 },
    @{ Name = "Grafana"; URL = "http://localhost:3000"; Port = 3000 },
    @{ Name = "Redis"; Port = 6379; NoHTTP = $true }
)

foreach ($service in $services) {
    Write-Host "Checking $($service.Name)..." -ForegroundColor Yellow

    if ($service.NoHTTP) {
        $container = docker ps --filter "expose=$($service.Port)" --format "{{.Names}}"
        if ($container) {
            Write-Host "[OK] $($service.Name) is running" -ForegroundColor Green
        } else {
            Write-Host "[ERROR] $($service.Name) is not running" -ForegroundColor Red
        }
    } else {
        try {
            $response = Invoke-WebRequest -Uri $service.URL -TimeoutSec 5 -UseBasicParsing
            if ($response.StatusCode -eq 200) {
                Write-Host "[OK] $($service.Name) is healthy: $($service.URL)" -ForegroundColor Green
            }
        } catch {
            Write-Host "[WARNING] $($service.Name) may still be starting: $($service.URL)" -ForegroundColor Yellow
        }
    }
}

# Display access information
Write-Host ""
Write-Host "================================================================" -ForegroundColor Green
Write-Host "  THERION ORFEAS PRODUCTION DEPLOYMENT COMPLETE!" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "ACCESS URLS:" -ForegroundColor Cyan
Write-Host "   Frontend:    http://localhost:8000" -ForegroundColor White
Write-Host "   Backend API: http://localhost:5000" -ForegroundColor White
Write-Host "   Grafana:     http://localhost:3000 (admin / orfeas_admin_2025)" -ForegroundColor White
Write-Host "   Prometheus:  http://localhost:9090" -ForegroundColor White
Write-Host ""
Write-Host "MANAGEMENT COMMANDS:" -ForegroundColor Cyan
Write-Host "   View logs:    docker-compose logs -f" -ForegroundColor White
Write-Host "   Stop all:     docker-compose down" -ForegroundColor White
Write-Host "   Restart:      docker-compose restart" -ForegroundColor White
Write-Host "   GPU stats:    docker exec orfeas-backend-production nvidia-smi" -ForegroundColor White
Write-Host ""
Write-Host "PRODUCTION READY!" -ForegroundColor Green
Write-Host ""
