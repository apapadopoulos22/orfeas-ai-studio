#requires -Version 5.1
[CmdletBinding()]
param(
    [switch]$NoBrowser,
    [int]$WaitSeconds = 3,
    [string]$Mode = 'powerful_3d'
)

# ===========================
# ORFEAS - Start Backend + UI
# ===========================
$ErrorActionPreference = 'Stop'
$PSDefaultParameterValues['Out-File:Encoding'] = 'utf8'

$root    = Split-Path -Parent $MyInvocation.MyCommand.Path
$backend = Join-Path $root 'backend'
$studioUrl = 'http://127.0.0.1:5000/studio'

Write-Host "[ORFEAS] Launching server..." -ForegroundColor Cyan
Write-Host "  Root:    $root"
Write-Host "  Backend: $backend"
Write-Host "  Mode:    $Mode"

# Prefer venv Python if available
$python = Join-Path $root 'venv\\Scripts\\python.exe'
if (-not (Test-Path $python)) {
    $pyCmd = Get-Command python -ErrorAction SilentlyContinue
    if ($pyCmd) { $python = $pyCmd.Source } else { $python = $null }
}
if (-not $python) {
    $pyLauncher = Get-Command py -ErrorAction SilentlyContinue
    if ($pyLauncher) { $python = 'py -3' }
}
if (-not $python) {
    Write-Error "Python 3.x not found. Install Python 3.10+ or create venv at $($root)\venv"
    exit 1
}

# Env vars
$env:ORFEAS_MODE = $Mode
$env:FLASK_ENV   = 'development'
$env:PYTHONUTF8  = '1'

# Logs folder
$logs = Join-Path $root 'logs'
if (-not (Test-Path $logs)) { New-Item -ItemType Directory -Path $logs | Out-Null }
$logFile = Join-Path $logs ("server_" + (Get-Date -Format 'yyyyMMdd_HHmmss') + ".log")

# Start backend
$startCmd = "cd `"$backend`"; `"$python`" main.py"
Write-Host "[START] $startCmd" -ForegroundColor Green
$proc = Start-Process -FilePath powershell.exe -ArgumentList "-NoLogo -NoExit -Command $startCmd" -PassThru -WorkingDirectory $backend

# Basic boot wait and health probe
Start-Sleep -Seconds $WaitSeconds
$healthOk = $false
try {
    $resp = Invoke-WebRequest -Uri 'http://127.0.0.1:5000/health' -UseBasicParsing -TimeoutSec 3
    if ($resp.StatusCode -eq 200) { $healthOk = $true }
} catch { }

if ($healthOk) {
    Write-Host "[OK] Backend responding. Logs: $logFile" -ForegroundColor Green
    if (-not $NoBrowser) {
        Start-Process $studioUrl | Out-Null
    }
} else {
    Write-Warning "Backend not reachable yet. You can open $studioUrl manually once it starts."
}

# Tail recent server output to file for troubleshooting
"[$(Get-Date -Format o)] STARTED - Mode=$Mode" | Out-File -FilePath $logFile -Encoding utf8 -Append
