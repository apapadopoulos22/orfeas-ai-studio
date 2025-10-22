# ORFEAS Linux Deployment Helper - PowerShell
# For Windows users deploying to Linux systems
# Usage: .\deploy_linux_fixed.ps1 -RemoteHost "user@linux-server" -Action Initialize

param(
    [string]$RemoteHost = "localhost",
    [ValidateSet("Initialize", "Start", "Stop", "View-Logs", "Get-Status", "Test")]
    [string]$Action = "Initialize",
    [string]$OurfeasDir = "/opt/orfeas"
)

$ErrorActionPreference = "Stop"

# Color functions
function Write-Success {
    Write-Host "[PASS] $args" -ForegroundColor Green
}

function Write-Info {
    Write-Host "[INFO] $args" -ForegroundColor Cyan
}

function Write-WarningMsg {
    Write-Host "[WARN] $args" -ForegroundColor Yellow
}

function Write-ErrorMsg {
    Write-Host "[FAIL] $args" -ForegroundColor Red
}

# SSH helper
function Invoke-RemoteCommand {
    param(
        [string]$ComputerName,
        [string]$Command
    )

    if ($ComputerName -eq "localhost") {
        Invoke-Expression $Command
    }
    else {
        ssh $ComputerName $Command
    }
}

# ============================================================================
# ACTION: INITIALIZE
# ============================================================================
function Invoke-Initialize {
    Write-Info "Deploying ORFEAS to $RemoteHost"
    Write-Info "Installation directory: $OurfeasDir"

    # 1. Check prerequisites
    Write-Info "Checking prerequisites on remote system..."
    $prereqs = @"
# Check prerequisites
echo "Checking NVIDIA driver..."
nvidia-smi > /dev/null 2>&1 || { echo "FAIL: NVIDIA driver not found"; exit 1; }

echo "Checking Docker..."
docker --version > /dev/null 2>&1 || { echo "FAIL: Docker not installed"; exit 1; }

echo "Checking NVIDIA Container Toolkit..."
docker run --rm --gpus all nvidia/cuda:12.1.0-runtime-ubuntu22.04 nvidia-smi > /dev/null 2>&1 || { echo "FAIL: NVIDIA Container Toolkit not configured"; exit 1; }

echo "PASS: All prerequisites met"
"@

    Invoke-RemoteCommand -ComputerName $RemoteHost -Command "bash -c '$($prereqs)'"
    Write-Success "Prerequisites verified"

    # 2. Create directories
    Write-Info "Creating directories..."
    Invoke-RemoteCommand -ComputerName $RemoteHost -Command "mkdir -p $OurfeasDir && cd $OurfeasDir && mkdir -p models outputs uploads temp logs"
    Write-Success "Directories created"

    # 3. Download repository
    Write-Info "Cloning ORFEAS repository..."
    Invoke-RemoteCommand -ComputerName $RemoteHost -Command "cd $(Split-Path $OurfeasDir) && git clone <YOUR_REPO_URL> $(Split-Path -Leaf $OurfeasDir) 2>/dev/null || echo 'Repository already exists'"
    Write-Success "Repository ready"

    # 4. Create .env
    Write-Info "Creating .env with Linux optimizations..."
    $env_content = @"
# ORFEAS Linux Production Configuration
ORFEAS_MODE=full_ai
FLASK_ENV=production
LOG_LEVEL=INFO
DEBUG=false

# GPU Configuration
DEVICE=cuda
CUDA_VISIBLE_DEVICES=0
XFORMERS_DISABLED=0
GPU_MEMORY_LIMIT=0.85
PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512,expandable_segments:True

# Server
HOST=0.0.0.0
PORT=5000
WORKERS=4

# Model
HUNYUAN3D_PRECISION=float16
MAX_CONCURRENT_JOBS=3
"@

    $env_file = $OurfeasDir + "/.env"
    Invoke-RemoteCommand -ComputerName $RemoteHost -Command "cat > $env_file << 'ENVEOF'`n$env_content`nENVEOF"
    Write-Success ".env created"

    # 5. Build image
    Write-Info "Building Docker image (this may take 5-10 minutes)..."
    Invoke-RemoteCommand -ComputerName $RemoteHost -Command "cd $OurfeasDir && docker-compose build --no-cache"
    Write-Success "Docker image built"

    # 6. Start services
    Write-Info "Starting services..."
    Invoke-RemoteCommand -ComputerName $RemoteHost -Command "cd $OurfeasDir && docker-compose up -d"
    Write-Success "Services started"

    # 7. Wait for health check
    Write-Info "Waiting for services to be healthy (up to 2 minutes)..."
    for ($i = 0; $i -lt 120; $i++) {
        try {
            $response = Invoke-WebRequest -Uri "http://$($RemoteHost):5000/api/health" -UseBasicParsing -TimeoutSec 2 -ErrorAction SilentlyContinue
            if ($response.StatusCode -eq 200) {
                Write-Success "Services are healthy!"
                break
            }
        }
        catch {
            # Still loading, continue
        }
        Write-Host -NoNewline "."
        Start-Sleep -Seconds 1
    }

    Write-Info "Setup complete!"
    Write-Info "Access at: http://$($RemoteHost):5000"
}

# ============================================================================
# ACTION: START
# ============================================================================
function Invoke-Start {
    Write-Info "Starting ORFEAS on $RemoteHost..."
    Invoke-RemoteCommand -ComputerName $RemoteHost -Command "cd $OurfeasDir && docker-compose up -d"
    Write-Success "Services started"

    # Check status
    Start-Sleep -Seconds 5
    Invoke-GetStatus
}

# ============================================================================
# ACTION: STOP
# ============================================================================
function Invoke-Stop {
    Write-Info "Stopping ORFEAS on $RemoteHost..."
    Invoke-RemoteCommand -ComputerName $RemoteHost -Command "cd $OurfeasDir && docker-compose down"
    Write-Success "Services stopped"
}

# ============================================================================
# ACTION: VIEW-LOGS
# ============================================================================
function Invoke-ViewLogs {
    Write-Info "Fetching logs from $RemoteHost..."

    if ($RemoteHost -eq "localhost") {
        docker-compose -f "$OurfeasDir/docker-compose.yml" logs -f backend
    }
    else {
        ssh $RemoteHost "cd $OurfeasDir && docker-compose logs -f backend"
    }
}

# ============================================================================
# ACTION: GET-STATUS
# ============================================================================
function Invoke-GetStatus {
    Write-Info "Checking status on $RemoteHost..."

    # Health check
    try {
        $response = Invoke-WebRequest -Uri "http://$($RemoteHost):5000/api/health" -UseBasicParsing -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            $health = $response.Content | ConvertFrom-Json
            Write-Success "Backend: Online"
            Write-Info "  Status: $($health.status)"
            if ($health.model) {
                Write-Info "  Model: $($health.model)"
            }
            if ($health.gpu_memory) {
                Write-Info "  GPU Memory: $($health.gpu_memory.used_gb) GB / $($health.gpu_memory.total_gb) GB"
            }
        }
        else {
            Write-WarningMsg "Backend: Offline or unresponsive"
        }
    }
    catch {
        Write-WarningMsg "Backend: Cannot connect"
    }

    # Docker status
    Write-Info "Docker services:"
    Invoke-RemoteCommand -ComputerName $RemoteHost -Command "cd $OurfeasDir && docker-compose ps"
}

# ============================================================================
# ACTION: TEST
# ============================================================================
function Invoke-Test {
    Write-Info "Testing ORFEAS 3D generation on $RemoteHost..."

    # Use a built-in test image
    if (-not (Test-Path "backend/test_images/test_image.png")) {
        Write-ErrorMsg "Test image not found at backend/test_images/test_image.png"
        return
    }

    Write-Info "Sending test image for 3D generation..."

    $testScript = @"
import requests
import json
from pathlib import Path

img = Path('backend/test_images/test_image.png')
with open(img, 'rb') as f:
    resp = requests.post('http://localhost:5000/api/generate/3d', files={'image': f}, timeout=180)
    print(f'Status: {resp.status_code}')
    data = resp.json()
    print(f'Response: {json.dumps(data, indent=2)}')
    if resp.status_code == 200 and 'mesh_url' in data:
        print('PASS: 3D generation successful!')
    else:
        print('FAIL: Generation failed')
"@

    Invoke-RemoteCommand -ComputerName $RemoteHost -Command "cd $OurfeasDir && python3 -c '$testScript'"
}

# ============================================================================
# MAIN EXECUTION
# ============================================================================

Write-Info "ORFEAS Linux Deployment Helper"
Write-Info "Host: $RemoteHost"
Write-Info "Action: $Action"
Write-Info ""

try {
    switch ($Action) {
        "Initialize" {
            Invoke-Initialize
        }
        "Start" {
            Invoke-Start
        }
        "Stop" {
            Invoke-Stop
        }
        "View-Logs" {
            Invoke-ViewLogs
        }
        "Get-Status" {
            Invoke-GetStatus
        }
        "Test" {
            Invoke-Test
        }
        default {
            Write-ErrorMsg "Unknown action: $Action"
        }
    }
}
catch {
    Write-ErrorMsg "Operation failed: $_"
    exit 1
}

Write-Success "Operation completed!"
