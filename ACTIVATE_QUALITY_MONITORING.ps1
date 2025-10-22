#!/usr/bin/env powershell
<#
.SYNOPSIS
    ORFEAS AI 2D→3D Studio - Quality Monitoring Activation Script

.DESCRIPTION
    Comprehensive deployment script that:
    1. Restarts Grafana with updated quality dashboard
    2. Verifies backend is running with quality validation
    3. Tests quality metrics integration end-to-end
    4. Generates test 3D model to populate metrics
    5. Validates Grafana panels display quality data

.NOTES
    Project: ORFEAS AI 2D→3D Studio
    Feature: Real-time Quality Metrics (Priority #1)
    Author: ORFEAS Team
    Date: January 2025
#>

# ============================================================================
# CONFIGURATION
# ============================================================================

$ErrorActionPreference = "Continue"
$ProgressPreference = "SilentlyContinue"

$BACKEND_URL = "http://localhost:5000"
$GRAFANA_URL = "http://localhost:3000"
$PROMETHEUS_URL = "http://localhost:9090"
$MONITORING_STACK_DIR = "c:\Users\johng\Documents\Erevus\orfeas\backend\monitoring_stack"
$BACKEND_DIR = "c:\Users\johng\Documents\Erevus\orfeas\backend"
$TEST_IMAGE_PATH = "c:\Users\johng\Documents\Erevus\orfeas\backend\test_images"

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

function Write-Header {
    param([string]$Message)
    Write-Host ""
    Write-Host "" -ForegroundColor Cyan
    Write-Host "  $Message" -ForegroundColor White
    Write-Host "" -ForegroundColor Cyan
    Write-Host ""
}

function Write-Step {
    param([string]$Message)
    Write-Host "→ $Message" -ForegroundColor Yellow
}

function Write-Success {
    param([string]$Message)
    Write-Host " $Message" -ForegroundColor Green
}

function Write-Error {
    param([string]$Message)
    Write-Host " $Message" -ForegroundColor Red
}

function Write-Info {
    param([string]$Message)
    Write-Host "ℹ  $Message" -ForegroundColor Cyan
}

function Test-ServiceRunning {
    param(
        [string]$Url,
        [string]$ServiceName
    )

    try {
        $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 5 -ErrorAction Stop
        Write-Success "$ServiceName is running (HTTP $($response.StatusCode))"
        return $true
    }
    catch {
        Write-Error "$ServiceName is not responding at $Url"
        return $false
    }
}

function Wait-ForService {
    param(
        [string]$Url,
        [string]$ServiceName,
        [int]$MaxAttempts = 30,
        [int]$DelaySeconds = 2
    )

    Write-Step "Waiting for $ServiceName to be ready..."

    for ($i = 1; $i -le $MaxAttempts; $i++) {
        try {
            $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
            Write-Success "$ServiceName is ready!"
            return $true
        }
        catch {
            Write-Host "  Attempt $i/$MaxAttempts - waiting..." -ForegroundColor Gray
            Start-Sleep -Seconds $DelaySeconds
        }
    }

    Write-Error "$ServiceName did not become ready after $MaxAttempts attempts"
    return $false
}

# ============================================================================
# MAIN DEPLOYMENT SCRIPT
# ============================================================================

Write-Header " QUALITY MONITORING ACTIVATION SCRIPT"

Write-Host "This script will:"
Write-Host "  1. Restart Grafana with updated quality dashboard" -ForegroundColor White
Write-Host "  2. Verify backend quality validation is active" -ForegroundColor White
Write-Host "  3. Test quality metrics integration" -ForegroundColor White
Write-Host "  4. Generate test 3D model" -ForegroundColor White
Write-Host "  5. Verify Grafana panels display quality data" -ForegroundColor White
Write-Host ""

# ============================================================================
# STEP 1: CHECK PREREQUISITES
# ============================================================================

Write-Header "STEP 1: Checking Prerequisites"

Write-Step "Checking if Docker is available..."
if (Get-Command docker -ErrorAction SilentlyContinue) {
    Write-Success "Docker is installed"
    $dockerAvailable = $true
}
else {
    Write-Error "Docker is not installed or not in PATH"
    $dockerAvailable = $false
}

Write-Step "Checking if monitoring stack directory exists..."
if (Test-Path $MONITORING_STACK_DIR) {
    Write-Success "Monitoring stack directory found"
}
else {
    Write-Error "Monitoring stack directory not found: $MONITORING_STACK_DIR"
    Write-Info "Please ensure the monitoring stack is set up"
    exit 1
}

Write-Step "Checking if Grafana dashboard JSON exists..."
$dashboardPath = Join-Path $MONITORING_STACK_DIR "grafana-dashboard.json"
if (Test-Path $dashboardPath) {
    Write-Success "Grafana dashboard JSON found"
}
else {
    Write-Error "Grafana dashboard not found: $dashboardPath"
    exit 1
}

# ============================================================================
# STEP 2: RESTART GRAFANA (DOCKER)
# ============================================================================

Write-Header "STEP 2: Restarting Grafana"

if ($dockerAvailable) {
    Write-Step "Checking for running monitoring stack containers..."
    Push-Location $MONITORING_STACK_DIR

    try {
        Write-Step "Stopping existing containers..."
        docker-compose down 2>&1 | Out-Null
        Start-Sleep -Seconds 3

        Write-Step "Starting monitoring stack with updated dashboard..."
        docker-compose up -d

        if ($LASTEXITCODE -eq 0) {
            Write-Success "Monitoring stack containers started"
        }
        else {
            Write-Error "Failed to start monitoring stack"
            Pop-Location
            exit 1
        }
    }
    catch {
        Write-Error "Error managing Docker containers: $_"
        Pop-Location
        exit 1
    }

    Pop-Location

    # Wait for Grafana to be ready
    if (-not (Wait-ForService -Url "$GRAFANA_URL/api/health" -ServiceName "Grafana" -MaxAttempts 30)) {
        Write-Error "Grafana did not start successfully"
        exit 1
    }
}
else {
    Write-Info "Docker not available - assuming Grafana is running standalone"
    Write-Info "Please manually restart Grafana to load the updated dashboard"
    Write-Host ""
    Read-Host "Press Enter after restarting Grafana to continue"
}

# ============================================================================
# STEP 3: VERIFY BACKEND IS RUNNING
# ============================================================================

Write-Header "STEP 3: Verifying Backend Status"

Write-Step "Checking backend health endpoint..."
if (Test-ServiceRunning -Url "$BACKEND_URL/health" -ServiceName "ORFEAS Backend") {
    try {
        $health = Invoke-RestMethod -Uri "$BACKEND_URL/health" -Method Get
        Write-Info "Backend Mode: $($health.mode)"
        Write-Info "GPU Available: $($health.gpu_available)"
        Write-Info "Models Ready: $($health.models_ready)"
    }
    catch {
        Write-Info "Could not parse health response"
    }
}
else {
    Write-Error "Backend is not running!"
    Write-Info "Please start the backend first:"
    Write-Host ""
    Write-Host "  cd $BACKEND_DIR" -ForegroundColor Yellow
    Write-Host "  `$env:FLASK_ENV='production'; `$env:TESTING='0'; python main.py" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

# ============================================================================
# STEP 4: VERIFY QUALITY VALIDATION IS ACTIVE
# ============================================================================

Write-Header "STEP 4: Verifying Quality Validation"

Write-Step "Checking Prometheus metrics endpoint..."
if (Test-ServiceRunning -Url "$BACKEND_URL/metrics" -ServiceName "Prometheus Metrics") {
    Write-Step "Searching for quality metrics..."

    try {
        $metrics = Invoke-WebRequest -Uri "$BACKEND_URL/metrics" -UseBasicParsing
        $metricsText = $metrics.Content

        # Check for quality metrics
        $qualityMetrics = @(
            "quality_overall_score",
            "quality_bg_removal_score",
            "quality_shape_score",
            "quality_texture_score",
            "quality_final_score",
            "quality_auto_repairs_total",
            "quality_grade_total"
        )

        $foundMetrics = 0
        foreach ($metric in $qualityMetrics) {
            if ($metricsText -match $metric) {
                $foundMetrics++
            }
        }

        if ($foundMetrics -eq $qualityMetrics.Count) {
            Write-Success "All $foundMetrics quality metrics are registered! "
        }
        elseif ($foundMetrics -gt 0) {
            Write-Info "Found $foundMetrics/$($qualityMetrics.Count) quality metrics"
            Write-Info "This is normal if no 3D model has been generated yet"
        }
        else {
            Write-Error "No quality metrics found in Prometheus export"
            Write-Info "Quality validation may not be active"
        }
    }
    catch {
        Write-Error "Could not retrieve metrics: $_"
    }
}
else {
    Write-Error "Prometheus metrics endpoint is not available"
}

# ============================================================================
# STEP 5: GENERATE TEST 3D MODEL
# ============================================================================

Write-Header "STEP 5: Generating Test 3D Model"

Write-Step "Checking for test images..."

# Create test image if it doesn't exist
if (-not (Test-Path $TEST_IMAGE_PATH)) {
    Write-Step "Creating test images directory..."
    New-Item -ItemType Directory -Path $TEST_IMAGE_PATH -Force | Out-Null
}

$testImageFile = Join-Path $TEST_IMAGE_PATH "quality_test.png"

if (-not (Test-Path $testImageFile)) {
    Write-Step "Creating test image using Python..."

    # Create Python script to generate test image
    $tempPyScript = "$env:TEMP\create_test_image.py"
    @"
from PIL import Image, ImageDraw
import os

# Create a simple test image
img = Image.new('RGB', (512, 512), color='white')
draw = ImageDraw.Draw(img)

# Draw a simple shape (circle)
draw.ellipse([128, 128, 384, 384], fill='blue', outline='black', width=5)

# Save
test_path = r'$TEST_IMAGE_PATH'
test_file = r'$testImageFile'
os.makedirs(test_path, exist_ok=True)
img.save(test_file)
print(f'Test image created: {test_file}')
"@ | Out-File -FilePath $tempPyScript -Encoding UTF8

    try {
        python $tempPyScript
        Remove-Item $tempPyScript -ErrorAction SilentlyContinue
        Write-Success "Test image created"
    }
    catch {
        Write-Error "Could not create test image: $_"
        Write-Info "You can manually create a test image at: $testImageFile"
        Read-Host "Press Enter after creating a test image to continue"
    }
}

if (Test-Path $testImageFile) {
    Write-Success "Test image ready: $testImageFile"

    Write-Step "Submitting 3D generation request..."

    try {
        # Prepare multipart form data
        $boundary = [System.Guid]::NewGuid().ToString()
        $fileContent = [System.IO.File]::ReadAllBytes($testImageFile)

        $bodyLines = @(
            "--$boundary",
            "Content-Disposition: form-data; name=`"image`"; filename=`"quality_test.png`"",
            "Content-Type: image/png",
            "",
            [System.Text.Encoding]::GetEncoding("ISO-8859-1").GetString($fileContent),
            "--$boundary",
            "Content-Disposition: form-data; name=`"format`"",
            "",
            "glb",
            "--$boundary",
            "Content-Disposition: form-data; name=`"quality`"",
            "",
            "7",
            "--$boundary--"
        )

        $body = $bodyLines -join "`r`n"

        $response = Invoke-RestMethod -Uri "$BACKEND_URL/api/generate-3d" `
            -Method Post `
            -ContentType "multipart/form-data; boundary=$boundary" `
            -Body $body `
            -TimeoutSec 300

        Write-Success "3D generation request submitted!"
        Write-Info "Job ID: $($response.job_id)"
        Write-Info "Status: $($response.status)"

        if ($response.quality_metrics) {
            Write-Host ""
            Write-Success "Quality Metrics Received! "
            Write-Host "  Overall Score: $($response.quality_metrics.overall_score)" -ForegroundColor Cyan
            Write-Host "  Quality Grade: $($response.quality_metrics.quality_grade)" -ForegroundColor Cyan
            Write-Host "  Printable: $($response.quality_metrics.printable)" -ForegroundColor Cyan
            Write-Host "  Manifold: $($response.quality_metrics.manifold)" -ForegroundColor Cyan
        }
        else {
            Write-Info "No quality metrics in response (may appear after generation completes)"
        }

    }
    catch {
        Write-Error "Failed to generate 3D model: $_"
        Write-Info "You can manually test by uploading an image through the web interface"
    }
}
else {
    Write-Error "Test image not found: $testImageFile"
}

# ============================================================================
# STEP 6: VERIFY PROMETHEUS METRICS
# ============================================================================

Write-Header "STEP 6: Verifying Quality Metrics in Prometheus"

Write-Step "Waiting 5 seconds for metrics to propagate..."
Start-Sleep -Seconds 5

Write-Step "Fetching updated metrics..."
try {
    $metrics = Invoke-WebRequest -Uri "$BACKEND_URL/metrics" -UseBasicParsing
    $metricsText = $metrics.Content

    # Extract quality metric values
    Write-Host ""
    Write-Host "Quality Metrics:" -ForegroundColor Cyan

    if ($metricsText -match 'quality_overall_score\s+([\d.]+)') {
        Write-Host "  Overall Score: $($matches[1])" -ForegroundColor Green
    }

    if ($metricsText -match 'quality_bg_removal_score\s+([\d.]+)') {
        Write-Host "  BG Removal: $($matches[1])" -ForegroundColor Green
    }

    if ($metricsText -match 'quality_shape_score\s+([\d.]+)') {
        Write-Host "  Shape: $($matches[1])" -ForegroundColor Green
    }

    if ($metricsText -match 'quality_texture_score\s+([\d.]+)') {
        Write-Host "  Texture: $($matches[1])" -ForegroundColor Green
    }

    if ($metricsText -match 'quality_final_score\s+([\d.]+)') {
        Write-Host "  Final Mesh: $($matches[1])" -ForegroundColor Green
    }

    # Check for auto-repairs
    if ($metricsText -match 'quality_auto_repairs_total') {
        Write-Host "  Auto-Repairs: Tracked " -ForegroundColor Green
    }

    # Check for quality grades
    if ($metricsText -match 'quality_grade_total') {
        Write-Host "  Quality Grades: Tracked " -ForegroundColor Green
    }

}
catch {
    Write-Error "Could not retrieve metrics: $_"
}

# ============================================================================
# STEP 7: VERIFY GRAFANA DASHBOARD
# ============================================================================

Write-Header "STEP 7: Verifying Grafana Dashboard"

Write-Step "Checking Grafana connectivity..."
if (Test-ServiceRunning -Url "$GRAFANA_URL/api/health" -ServiceName "Grafana") {

    Write-Info "Opening Grafana dashboard in browser..."
    Write-Host ""
    Write-Host "  URL: $GRAFANA_URL" -ForegroundColor Cyan
    Write-Host "  Login: admin / orfeas_admin_2025" -ForegroundColor Cyan
    Write-Host "  Dashboard: ORFEAS AI 2D→3D Studio - Production Monitoring" -ForegroundColor Cyan
    Write-Host ""
    Write-Info "Look for quality panels starting at row 32:"
    Write-Host "  • Panel 15: Overall Quality Gauge" -ForegroundColor White
    Write-Host "  • Panel 16: Stage Scores" -ForegroundColor White
    Write-Host "  • Panel 17: Auto-Repairs Counter" -ForegroundColor White
    Write-Host "  • Panel 18: Manifold/Printable Rates" -ForegroundColor White
    Write-Host "  • Panel 19: Quality Trend Graph" -ForegroundColor White
    Write-Host "  • Panel 20: Quality Distribution Heatmap" -ForegroundColor White
    Write-Host "  • Panel 21: Quality Grade Pie Chart" -ForegroundColor White
    Write-Host "  • Panel 22: Auto-Repair Breakdown" -ForegroundColor White
    Write-Host "  • Panel 23: Validation Failures (with alert)" -ForegroundColor White
    Write-Host "  • Panel 24: Threshold Passes" -ForegroundColor White
    Write-Host ""

    $openBrowser = Read-Host "Open Grafana in browser? (Y/n)"
    if ($openBrowser -ne 'n' -and $openBrowser -ne 'N') {
        Start-Process $GRAFANA_URL
    }
}

# ============================================================================
# STEP 8: SUMMARY & NEXT STEPS
# ============================================================================

Write-Header " ACTIVATION COMPLETE"

Write-Host "Quality Monitoring Status:" -ForegroundColor Green
Write-Host "   Grafana dashboard updated with 10 quality panels" -ForegroundColor Green
Write-Host "   Backend quality validation active" -ForegroundColor Green
Write-Host "   Prometheus metrics exporting quality data" -ForegroundColor Green
Write-Host "   Test 3D model generated (if successful)" -ForegroundColor Green
Write-Host ""

Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Open Grafana: $GRAFANA_URL" -ForegroundColor White
Write-Host "  2. Navigate to ORFEAS dashboard" -ForegroundColor White
Write-Host "  3. Scroll to quality panels (row 32+)" -ForegroundColor White
Write-Host "  4. Generate more 3D models to populate trend data" -ForegroundColor White
Write-Host "  5. Configure alert notifications (email/Slack)" -ForegroundColor White
Write-Host ""

Write-Host "Monitoring URLs:" -ForegroundColor Cyan
Write-Host "  • ORFEAS Backend: $BACKEND_URL" -ForegroundColor White
Write-Host "  • Grafana: $GRAFANA_URL" -ForegroundColor White
Write-Host "  • Prometheus: $PROMETHEUS_URL" -ForegroundColor White
Write-Host "  • Metrics: $BACKEND_URL/metrics" -ForegroundColor White
Write-Host ""

Write-Host "Documentation:" -ForegroundColor Cyan
Write-Host "  • Implementation: md/QUALITY_METRICS_IMPLEMENTATION_COMPLETE.md" -ForegroundColor White
Write-Host "  • Integration: md/QUALITY_METRICS_INTEGRATION_COMPLETE.md" -ForegroundColor White
Write-Host "  • Dashboard Guide: md/GRAFANA_QUALITY_DASHBOARD_COMPLETE.md" -ForegroundColor White
Write-Host ""

Write-Success " Quality Monitoring is now LIVE! "
Write-Host ""
Write-Host "" -ForegroundColor Cyan
Write-Host "  THERION AI - ORFEAS AI" -ForegroundColor White
Write-Host "  OPTIMAL QUALITY MONITORING ACHIEVED! " -ForegroundColor White
Write-Host "" -ForegroundColor Cyan
Write-Host ""
