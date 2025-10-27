# â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—
# â•‘ âš”ï¸ THERION ORFEAS - PRODUCTION DEPLOYMENT SCRIPT âš”ï¸                        â•‘
# â•‘ One-command deployment for LOCAL GPU production environment                â•‘
# â•‘ MAXIMUM PERFORMANCE                                             â•‘
# â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

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
    $nvidiaRuntime = docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi
    if ($LASTEXITCODE -eq 0) {
        Write-Host "âœ… NVIDIA Docker runtime available" -ForegroundColor Green
    } else {
        Write-Host "âš ï¸ NVIDIA Docker runtime may have issues" -ForegroundColor Yellow
    }
} catch {
    Write-Host "âš ï¸ Cannot verify NVIDIA Docker runtime" -ForegroundColor Yellow
    Write-Host "Install NVIDIA Container Toolkit if you have NVIDIA GPU" -ForegroundColor Yellow
}

# Stop existing containers
Write-Host "[4/8] Stopping existing containers..." -ForegroundColor Yellow
docker-compose down 2>$null
Write-Host "âœ… Existing containers stopped" -ForegroundColor Green

# Build Docker images
Write-Host "[5/8] Building Docker images (this may take 10-15 minutes)..." -ForegroundColor Yellow
docker-compose build --no-cache
if ($LASTEXITCODE -eq 0) {
    Write-Host "âœ… Docker images built successfully" -ForegroundColor Green
} else {
    Write-Host "âŒ Docker build failed!" -ForegroundColor Red
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
Write-Host "âœ… Directories ready" -ForegroundColor Green

# Start production environment
Write-Host "[7/8] Starting production environment..." -ForegroundColor Yellow
docker-compose up -d

if ($LASTEXITCODE -eq 0) {
    Write-Host "âœ… All services started successfully!" -ForegroundColor Green
} else {
    Write-Host "âŒ Failed to start services" -ForegroundColor Red
    exit 1
}

# Wait for services to be ready
Write-Host "[8/8] Waiting for services to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Check service health
Write-Host ""
Write-Host "â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—" -ForegroundColor Cyan
Write-Host "â•‘                        ðŸŽ¯ SERVICE STATUS CHECK                              â•‘" -ForegroundColor Cyan
Write-Host "â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•" -ForegroundColor Cyan
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
            Write-Host "âœ… $($service.Name) is running" -ForegroundColor Green
        } else {
            Write-Host "âŒ $($service.Name) is not running" -ForegroundColor Red
        }
    } else {
        try {
            $response = Invoke-WebRequest -Uri $service.URL -TimeoutSec 5 -UseBasicParsing
            if ($response.StatusCode -eq 200) {
                Write-Host "âœ… $($service.Name) is healthy: $($service.URL)" -ForegroundColor Green
            }
        } catch {
            Write-Host "âš ï¸ $($service.Name) may still be starting: $($service.URL)" -ForegroundColor Yellow
        }
    }
}

# Display access information
Write-Host ""
Write-Host "â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—" -ForegroundColor Green
Write-Host "â•‘              ðŸš€ THERION ORFEAS PRODUCTION DEPLOYMENT COMPLETE! ðŸš€           â•‘" -ForegroundColor Green
Write-Host "â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•" -ForegroundColor Green
Write-Host ""
Write-Host "ðŸ“Š ACCESS URLS:" -ForegroundColor Cyan
Write-Host "   Frontend:    http://localhost:8000" -ForegroundColor White
Write-Host "   Backend API: http://localhost:5000" -ForegroundColor White
Write-Host "   Grafana:     http://localhost:3000 (admin / orfeas_admin_2025)" -ForegroundColor White
Write-Host "   Prometheus:  http://localhost:9090" -ForegroundColor White
Write-Host ""
Write-Host "ðŸ”§ MANAGEMENT COMMANDS:" -ForegroundColor Cyan
Write-Host "   View logs:    docker-compose logs -f" -ForegroundColor White
Write-Host "   Stop all:     docker-compose down" -ForegroundColor White
Write-Host "   Restart:      docker-compose restart" -ForegroundColor White
Write-Host "   GPU stats:    docker exec orfeas-backend-production nvidia-smi" -ForegroundColor White
Write-Host ""
Write-Host "PRODUCTION READY!" -ForegroundColor Green
Write-Host ""
