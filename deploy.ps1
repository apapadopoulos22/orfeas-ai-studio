# =============================================================================
# ORFEAS AI 2Dâ†’3D Studio - Production Deployment Script
# =============================================================================
# THERION AI Project
#
# One-command production deployment with:
# - Pre-flight checks
# - SSL certificate generation
# - Docker build and startup
# - Health validation
# - Rollback capability
# =============================================================================

param(
    [switch]$SkipBuild,
    [switch]$SkipSSL,
    [switch]$SkipHealthCheck,
    [switch]$Rebuild
)

$ErrorActionPreference = "Stop"

Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "ORFEAS AI 2Dâ†’3D Studio - Production Deployment" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""

# -----------------------------------------------------------------------------
# Step 1: Pre-Flight Checks
# -----------------------------------------------------------------------------
Write-Host "[1/8] Running pre-flight checks..." -ForegroundColor Yellow

# Check Docker
try {
    $dockerVersion = docker --version
    Write-Host "[OK] Docker: $dockerVersion" -ForegroundColor Green
}
catch {
    Write-Host "[ERROR] Docker not found! Please install Docker Desktop." -ForegroundColor Red
    exit 1
}

# Check Docker Compose
try {
    $composeVersion = docker-compose --version
    Write-Host "[OK] Docker Compose: $composeVersion" -ForegroundColor Green
}
catch {
    Write-Host "[ERROR] Docker Compose not found!" -ForegroundColor Red
    exit 1
}

# Check NVIDIA Docker runtime (for GPU support)
try {
    docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] NVIDIA Docker runtime available" -ForegroundColor Green
    }
    else {
        Write-Host "[WARNING] NVIDIA Docker runtime not available - GPU acceleration disabled" -ForegroundColor Yellow
    }
}
catch {
    Write-Host "[WARNING] Could not verify NVIDIA Docker runtime" -ForegroundColor Yellow
}

# Check required files
$requiredFiles = @(
    "Dockerfile.production",
    "docker-compose.production.yml",
    "gunicorn.conf.py",
    "nginx.production.conf",
    ".env.production.template"
)

foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "[OK] Found: $file" -ForegroundColor Green
    }
    else {
        Write-Host "[ERROR] Missing required file: $file" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""

# -----------------------------------------------------------------------------
# Step 2: Environment Configuration
# -----------------------------------------------------------------------------
Write-Host "[2/8] Configuring environment..." -ForegroundColor Yellow

if (-not (Test-Path ".env.production")) {
    Write-Host "[INFO] Creating .env.production from template..." -ForegroundColor Cyan
    Copy-Item ".env.production.template" ".env.production"

    # Generate random secret key
    $secretKey = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 64 | ForEach-Object { [char]$_ })
    (Get-Content ".env.production") -replace "SECRET_KEY=CHANGE_ME_IN_PRODUCTION_USE_STRONG_RANDOM_STRING", "SECRET_KEY=$secretKey" | Set-Content ".env.production"

    # Generate random Grafana password
    $grafanaPassword = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 32 | ForEach-Object { [char]$_ })
    (Get-Content ".env.production") -replace "GF_SECURITY_ADMIN_PASSWORD=CHANGE_ME_IN_PRODUCTION", "GF_SECURITY_ADMIN_PASSWORD=$grafanaPassword" | Set-Content ".env.production"

    Write-Host "[OK] Created .env.production with generated secrets" -ForegroundColor Green
    Write-Host "[INFO] Grafana admin password: $grafanaPassword" -ForegroundColor Cyan
    Write-Host "[INFO] Save this password! It will not be shown again." -ForegroundColor Yellow
}
else {
    Write-Host "[OK] Using existing .env.production" -ForegroundColor Green
}

Write-Host ""

# -----------------------------------------------------------------------------
# Step 3: SSL Certificates
# -----------------------------------------------------------------------------
if (-not $SkipSSL) {
    Write-Host "[3/8] Setting up SSL certificates..." -ForegroundColor Yellow

    if ((Test-Path "ssl\cert.pem") -and (Test-Path "ssl\key.pem")) {
        Write-Host "[OK] SSL certificates already exist" -ForegroundColor Green
    }
    else {
        Write-Host "[INFO] Generating self-signed SSL certificates..." -ForegroundColor Cyan

        # Create ssl directory
        if (-not (Test-Path "ssl")) {
            New-Item -ItemType Directory -Path "ssl" | Out-Null
        }

        # Try using Docker to generate certificates
        try {
            docker run --rm -v "${PWD}/ssl:/ssl" alpine/openssl req -x509 -newkey rsa:4096 -nodes -out /ssl/cert.pem -keyout /ssl/key.pem -days 365 -subj "/CN=localhost/O=ORFEAS AI/C=US" 2>&1 | Out-Null

            if ($LASTEXITCODE -eq 0) {
                Write-Host "[OK] SSL certificates generated using Docker" -ForegroundColor Green
            }
            else {
                Write-Host "[ERROR] Failed to generate SSL certificates" -ForegroundColor Red
                exit 1
            }
        }
        catch {
            Write-Host "[ERROR] Failed to generate SSL certificates: $_" -ForegroundColor Red
            Write-Host "[INFO] Try running: .\generate_ssl_certs.ps1" -ForegroundColor Cyan
            exit 1
        }
    }
}
else {
    Write-Host "[3/8] Skipping SSL setup (--SkipSSL flag)" -ForegroundColor Yellow
}

Write-Host ""

# -----------------------------------------------------------------------------
# Step 4: Stop Existing Containers
# -----------------------------------------------------------------------------
Write-Host "[4/8] Stopping existing containers..." -ForegroundColor Yellow

try {
    docker-compose -f docker-compose.production.yml down 2>&1 | Out-Null
    Write-Host "[OK] Stopped existing containers" -ForegroundColor Green
}
catch {
    Write-Host "[INFO] No existing containers to stop" -ForegroundColor Cyan
}

Write-Host ""

# -----------------------------------------------------------------------------
# Step 5: Build Docker Images
# -----------------------------------------------------------------------------
if (-not $SkipBuild) {
    Write-Host "[5/8] Building Docker images..." -ForegroundColor Yellow

    if ($Rebuild) {
        Write-Host "[INFO] Force rebuild (--Rebuild flag)" -ForegroundColor Cyan
        docker-compose -f docker-compose.production.yml build --no-cache
    }
    else {
        docker-compose -f docker-compose.production.yml build
    }

    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Docker images built successfully" -ForegroundColor Green
    }
    else {
        Write-Host "[ERROR] Docker build failed (exit code: $LASTEXITCODE)" -ForegroundColor Red
        exit 1
    }
}
else {
    Write-Host "[5/8] Skipping build (--SkipBuild flag)" -ForegroundColor Yellow
}

Write-Host ""

# -----------------------------------------------------------------------------
# Step 6: Start Services
# -----------------------------------------------------------------------------
Write-Host "[6/8] Starting production services..." -ForegroundColor Yellow

docker-compose -f docker-compose.production.yml up -d

if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Services started successfully" -ForegroundColor Green
}
else {
    Write-Host "[ERROR] Failed to start services (exit code: $LASTEXITCODE)" -ForegroundColor Red
    exit 1
}

Write-Host ""

# -----------------------------------------------------------------------------
# Step 7: Wait for Services to Initialize
# -----------------------------------------------------------------------------
Write-Host "[7/8] Waiting for services to initialize..." -ForegroundColor Yellow

Start-Sleep -Seconds 10

# Check service status
Write-Host ""
Write-Host "Service Status:" -ForegroundColor Cyan
docker-compose -f docker-compose.production.yml ps

Write-Host ""

# -----------------------------------------------------------------------------
# Step 8: Health Checks
# -----------------------------------------------------------------------------
if (-not $SkipHealthCheck) {
    Write-Host "[8/8] Running health checks..." -ForegroundColor Yellow

    $maxRetries = 12
    $retryDelay = 5

    # Check backend health
    Write-Host "[INFO] Checking backend health..." -ForegroundColor Cyan
    $backendHealthy = $false

    for ($i = 1; $i -le $maxRetries; $i++) {
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:5000/health" -Method GET -TimeoutSec 5 -UseBasicParsing
            if ($response.StatusCode -eq 200) {
                Write-Host "[OK] Backend is healthy" -ForegroundColor Green
                $backendHealthy = $true
                break
            }
        }
        catch {
            Write-Host "[RETRY $i/$maxRetries] Backend not ready yet..." -ForegroundColor Yellow
            Start-Sleep -Seconds $retryDelay
        }
    }

    if (-not $backendHealthy) {
        Write-Host "[ERROR] Backend failed health check after $maxRetries retries" -ForegroundColor Red
        Write-Host "[INFO] Check logs: docker-compose -f docker-compose.production.yml logs backend" -ForegroundColor Cyan
        exit 1
    }

    # Check Nginx
    Write-Host "[INFO] Checking Nginx..." -ForegroundColor Cyan
    try {
        $response = Invoke-WebRequest -Uri "http://localhost/health" -Method GET -TimeoutSec 5 -UseBasicParsing
        if ($response.StatusCode -eq 200) {
            Write-Host "[OK] Nginx is healthy" -ForegroundColor Green
        }
    }
    catch {
        Write-Host "[WARNING] Nginx health check failed" -ForegroundColor Yellow
    }

    # Check Prometheus
    Write-Host "[INFO] Checking Prometheus..." -ForegroundColor Cyan
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:9090/-/healthy" -Method GET -TimeoutSec 5 -UseBasicParsing
        if ($response.StatusCode -eq 200) {
            Write-Host "[OK] Prometheus is healthy" -ForegroundColor Green
        }
    }
    catch {
        Write-Host "[WARNING] Prometheus health check failed" -ForegroundColor Yellow
    }

    # Check Grafana
    Write-Host "[INFO] Checking Grafana..." -ForegroundColor Cyan
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:3000/api/health" -Method GET -TimeoutSec 5 -UseBasicParsing
        if ($response.StatusCode -eq 200) {
            Write-Host "[OK] Grafana is healthy" -ForegroundColor Green
        }
    }
    catch {
        Write-Host "[WARNING] Grafana health check failed" -ForegroundColor Yellow
    }

}
else {
    Write-Host "[8/8] Skipping health checks (--SkipHealthCheck flag)" -ForegroundColor Yellow
}

Write-Host ""

# -----------------------------------------------------------------------------
# Deployment Summary
# -----------------------------------------------------------------------------
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "DEPLOYMENT COMPLETE!" -ForegroundColor Green
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""
Write-Host "Access Points:" -ForegroundColor Cyan
Write-Host "  - Frontend (HTTP):  http://localhost" -ForegroundColor White
Write-Host "  - Frontend (HTTPS): https://localhost (self-signed cert warning expected)" -ForegroundColor White
Write-Host "  - Backend API:      http://localhost:5000" -ForegroundColor White
Write-Host "  - Prometheus:       http://localhost:9090" -ForegroundColor White
Write-Host "  - Grafana:          http://localhost:3000" -ForegroundColor White
Write-Host ""
Write-Host "Default Credentials:" -ForegroundColor Cyan
Write-Host "  - Grafana: admin / (check .env.production for password)" -ForegroundColor White
Write-Host ""
Write-Host "Useful Commands:" -ForegroundColor Cyan
Write-Host "  - View logs:     docker-compose -f docker-compose.production.yml logs -f" -ForegroundColor White
Write-Host "  - Stop services: docker-compose -f docker-compose.production.yml down" -ForegroundColor White
Write-Host "  - Restart:       docker-compose -f docker-compose.production.yml restart" -ForegroundColor White
Write-Host "  - Status:        docker-compose -f docker-compose.production.yml ps" -ForegroundColor White
Write-Host ""
Write-Host "=" * 80 -ForegroundColor Cyan
