# =============================================================================
# ORFEAS AI 2Dâ†’3D Studio - Restore Script
# =============================================================================
# THERION AI Project
#
# Restores from backup created by backup.ps1
# =============================================================================

param(
    [Parameter(Mandatory = $true)]
    [string]$BackupFile,
    [switch]$SkipModels,
    [switch]$Force
)

$ErrorActionPreference = "Stop"

Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "ORFEAS AI 2Dâ†’3D Studio - Restore" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""

# Validate backup file
if (-not (Test-Path $BackupFile)) {
    Write-Host "[ERROR] Backup file not found: $BackupFile" -ForegroundColor Red
    exit 1
}

Write-Host "[INFO] Backup file: $BackupFile" -ForegroundColor Cyan
$backupSize = (Get-Item $BackupFile).Length / 1MB
Write-Host "[INFO] Backup size: $([math]::Round($backupSize, 2)) MB" -ForegroundColor Cyan
Write-Host ""

# Warning
if (-not $Force) {
    Write-Host "[WARNING] This will overwrite existing data!" -ForegroundColor Yellow
    Write-Host "[WARNING] Current outputs, logs, and configuration will be replaced." -ForegroundColor Yellow
    Write-Host ""
    $confirm = Read-Host "Continue with restore? (yes/no)"

    if ($confirm -ne "yes") {
        Write-Host "[CANCELLED] Restore cancelled by user" -ForegroundColor Yellow
        exit 0
    }
}

Write-Host ""

# Create temporary extraction directory
$tempDir = "temp_restore_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
New-Item -ItemType Directory -Path $tempDir | Out-Null

Write-Host "[INFO] Extracting backup..." -ForegroundColor Cyan
Expand-Archive -Path $BackupFile -DestinationPath $tempDir -Force

# Find the backup directory inside
$backupDir = Get-ChildItem -Path $tempDir -Directory | Select-Object -First 1
if (-not $backupDir) {
    Write-Host "[ERROR] Invalid backup archive structure" -ForegroundColor Red
    Remove-Item -Path $tempDir -Recurse -Force
    exit 1
}

Write-Host "[OK] Backup extracted" -ForegroundColor Green
Write-Host ""

# -----------------------------------------------------------------------------
# 1. Restore Outputs
# -----------------------------------------------------------------------------
Write-Host "[1/6] Restoring outputs..." -ForegroundColor Yellow

if (Test-Path "$backupDir\outputs") {
    if (-not (Test-Path "outputs")) {
        New-Item -ItemType Directory -Path "outputs" | Out-Null
    }

    Copy-Item -Path "$backupDir\outputs\*" -Destination "outputs" -Recurse -Force
    $outputCount = (Get-ChildItem -Path "$backupDir\outputs" -Recurse -File).Count
    Write-Host "[OK] Restored $outputCount output files" -ForegroundColor Green
}
else {
    Write-Host "[SKIP] No outputs in backup" -ForegroundColor Yellow
}

Write-Host ""

# -----------------------------------------------------------------------------
# 2. Restore Logs
# -----------------------------------------------------------------------------
Write-Host "[2/6] Restoring logs..." -ForegroundColor Yellow

if (Test-Path "$backupDir\logs") {
    if (-not (Test-Path "logs")) {
        New-Item -ItemType Directory -Path "logs" | Out-Null
    }

    Copy-Item -Path "$backupDir\logs\*" -Destination "logs" -Recurse -Force
    $logCount = (Get-ChildItem -Path "$backupDir\logs" -Recurse -File).Count
    Write-Host "[OK] Restored $logCount log files" -ForegroundColor Green
}
else {
    Write-Host "[SKIP] No logs in backup" -ForegroundColor Yellow
}

Write-Host ""

# -----------------------------------------------------------------------------
# 3. Restore Model Cache (Optional)
# -----------------------------------------------------------------------------
Write-Host "[3/6] Restoring model cache..." -ForegroundColor Yellow

if ($SkipModels) {
    Write-Host "[SKIP] Model cache restore skipped (--SkipModels flag)" -ForegroundColor Yellow
}
else {
    if (Test-Path "$backupDir\models\huggingface") {
        Write-Host "[INFO] Restoring HuggingFace model cache..." -ForegroundColor Cyan

        $cacheDir = "$env:USERPROFILE\.cache\huggingface"
        if (-not (Test-Path $cacheDir)) {
            New-Item -ItemType Directory -Path $cacheDir -Force | Out-Null
        }

        Copy-Item -Path "$backupDir\models\huggingface\*" -Destination $cacheDir -Recurse -Force
        Write-Host "[OK] Restored HuggingFace model cache" -ForegroundColor Green
    }
    else {
        Write-Host "[SKIP] No model cache in backup" -ForegroundColor Yellow
    }

    if (Test-Path "$backupDir\models\hy3dgen") {
        Write-Host "[INFO] Restoring Hy3DGen model cache..." -ForegroundColor Cyan

        $cacheDir = "$env:USERPROFILE\.cache\hy3dgen"
        if (-not (Test-Path $cacheDir)) {
            New-Item -ItemType Directory -Path $cacheDir -Force | Out-Null
        }

        Copy-Item -Path "$backupDir\models\hy3dgen\*" -Destination $cacheDir -Recurse -Force
        Write-Host "[OK] Restored Hy3DGen model cache" -ForegroundColor Green
    }
}

Write-Host ""

# -----------------------------------------------------------------------------
# 4. Restore Monitoring Data
# -----------------------------------------------------------------------------
Write-Host "[4/6] Restoring monitoring data..." -ForegroundColor Yellow

# Restore Prometheus data
if (Test-Path "$backupDir\monitoring\prometheus_data.tar.gz") {
    Write-Host "[INFO] Restoring Prometheus data..." -ForegroundColor Cyan
    try {
        docker run --rm -v orfeas_prometheus-data:/data -v "${PWD}/${backupDir}/monitoring:/backup" alpine tar xzf /backup/prometheus_data.tar.gz -C /data 2>&1 | Out-Null
        Write-Host "[OK] Restored Prometheus data" -ForegroundColor Green
    }
    catch {
        Write-Host "[WARNING] Could not restore Prometheus data" -ForegroundColor Yellow
    }
}
else {
    Write-Host "[SKIP] No Prometheus data in backup" -ForegroundColor Yellow
}

# Restore Grafana data
if (Test-Path "$backupDir\monitoring\grafana_data.tar.gz") {
    Write-Host "[INFO] Restoring Grafana data..." -ForegroundColor Cyan
    try {
        docker run --rm -v orfeas_grafana-data:/data -v "${PWD}/${backupDir}/monitoring:/backup" alpine tar xzf /backup/grafana_data.tar.gz -C /data 2>&1 | Out-Null
        Write-Host "[OK] Restored Grafana data" -ForegroundColor Green
    }
    catch {
        Write-Host "[WARNING] Could not restore Grafana data" -ForegroundColor Yellow
    }
}
else {
    Write-Host "[SKIP] No Grafana data in backup" -ForegroundColor Yellow
}

Write-Host ""

# -----------------------------------------------------------------------------
# 5. Restore Configuration Files
# -----------------------------------------------------------------------------
Write-Host "[5/6] Restoring configuration files..." -ForegroundColor Yellow

if (Test-Path "$backupDir\config") {
    $configFiles = Get-ChildItem -Path "$backupDir\config" -File

    foreach ($file in $configFiles) {
        # Determine destination
        $destination = $file.Name
        if ($file.Name -eq "config.py") {
            $destination = "backend\config.py"
        }

        # Backup existing file
        if (Test-Path $destination) {
            $backupName = "$destination.backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
            Move-Item -Path $destination -Destination $backupName -Force
            Write-Host "[INFO] Backed up existing: $destination -> $backupName" -ForegroundColor Cyan
        }

        # Restore from backup
        Copy-Item -Path $file.FullName -Destination $destination -Force
        Write-Host "[OK] Restored: $destination" -ForegroundColor Green
    }
}
else {
    Write-Host "[SKIP] No configuration files in backup" -ForegroundColor Yellow
}

Write-Host ""

# -----------------------------------------------------------------------------
# 6. Cleanup
# -----------------------------------------------------------------------------
Write-Host "[6/6] Cleaning up..." -ForegroundColor Yellow

Remove-Item -Path $tempDir -Recurse -Force
Write-Host "[OK] Temporary files removed" -ForegroundColor Green

Write-Host ""

# -----------------------------------------------------------------------------
# Restore Summary
# -----------------------------------------------------------------------------
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "RESTORE COMPLETE!" -ForegroundColor Green
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "  1. Review restored configuration files" -ForegroundColor White
Write-Host "  2. Restart services: docker-compose -f docker-compose.production.yml restart" -ForegroundColor White
Write-Host "  3. Verify functionality: https://localhost" -ForegroundColor White
Write-Host ""
Write-Host "=" * 80 -ForegroundColor Cyan
