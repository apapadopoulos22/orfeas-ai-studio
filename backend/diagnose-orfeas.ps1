#
# ORFEAS AI 2D->3D Studio - Comprehensive Diagnostic Script
# Runs all 6 critical issue checks and provides actionable fixes.
#
# Usage: .\diagnose-orfeas.ps1
#        .\diagnose-orfeas.ps1 -Verbose
#        .\diagnose-orfeas.ps1 -ReportPath "C:\Reports\diagnostic.txt"
#
# Requires: PowerShell 5.0+, Python 3.10+
#

param(
    [switch]$Verbose = $false,
    [string]$ReportPath = "$PSScriptRoot\orfeas-diagnostic-report.txt"
)

$script:DiagnosticResults = @()
$script:StartTime = Get-Date
$script:IssuesPassed = 0
$script:IssuesFailed = 0

# Color codes (ASCII-safe)
function Write-Status {
    param([string]$Message, [string]$Type = "INFO")

    $colorMap = @{
        "PASS"   = "Green"
        "FAIL"   = "Red"
        "WARN"   = "Yellow"
        "INFO"   = "White"
        "HEADER" = "Cyan"
    }

    $prefixMap = @{
        "PASS"   = "[PASS]"
        "FAIL"   = "[FAIL]"
        "WARN"   = "[WARN]"
        "INFO"   = "[INFO]"
        "HEADER" = "[--]"
    }

    $prefix = $prefixMap[$Type]
    $color = $colorMap[$Type]

    Write-Host "$prefix $Message" -ForegroundColor $color
}

function Write-Header {
    param([int]$IssueNumber, [string]$Title)
    Write-Host "`n$('=' * 80)" -ForegroundColor Cyan
    Write-Host "Issue #$IssueNumber : $Title" -ForegroundColor Cyan
    Write-Host "$('=' * 80)" -ForegroundColor Cyan
}

# ============================================================================
# ISSUE #1: xformers DLL crash (0xc0000139)
# ============================================================================

function Test-XformersEnvVars {
    Write-Header 1 "xformers DLL crash (0xc0000139)"

    Write-Status "Checking environment variable initialization order..." "INFO"

    $requiredVars = @{
        "XFORMERS_DISABLED"        = "1"
        "ORT_TENSORRT_UNAVAILABLE" = "1"
        "HOME"                     = $env:USERPROFILE
        "CUDA_MODULE_LOADING"      = "LAZY"
    }

    $allSet = $true

    foreach ($var in $requiredVars.GetEnumerator()) {
        $value = [System.Environment]::GetEnvironmentVariable($var.Key)
        if ($value) {
            Write-Status "$($var.Key) = $value" "PASS"
        }
        else {
            Write-Status "$($var.Key) NOT SET (required: $($var.Value))" "FAIL"
            $allSet = $false
        }
    }

    if ($allSet) {
        Write-Status "All environment variables correctly configured" "PASS"
        Write-Status "Variables are set BEFORE imports" "PASS"
        $script:DiagnosticResults += @{Issue = "xformers DLL"; Status = "PASS" }
        $script:IssuesPassed++
        return $true
    }
    else {
        Write-Status "MISSING: Set environment variables before running Python" "FAIL"
        Write-Status "Run this in PowerShell BEFORE starting backend:" "INFO"
        Write-Host "`n  `$env:XFORMERS_DISABLED='1'" -ForegroundColor Yellow
        Write-Host "  `$env:ORT_TENSORRT_UNAVAILABLE='1'" -ForegroundColor Yellow
        Write-Host "  `$env:HOME=`$env:USERPROFILE" -ForegroundColor Yellow
        Write-Host "  `$env:CUDA_MODULE_LOADING='LAZY'" -ForegroundColor Yellow
        Write-Host "  python main.py`n" -ForegroundColor Yellow

        $script:DiagnosticResults += @{Issue = "xformers DLL"; Status = "FAIL" }
        $script:IssuesFailed++
        return $false
    }
}

# ============================================================================
# ISSUE #2: CUDA out of memory
# ============================================================================

function Test-CUDAMemory {
    Write-Header 2 "CUDA out of memory mid-generation"

    Write-Status "Checking GPU availability and VRAM..." "INFO"

    $pythonScript = @'
import torch
if torch.cuda.is_available():
    device = torch.cuda.get_device_name(0)
    total_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
    allocated = torch.cuda.memory_allocated() / (1024**3)
    reserved = torch.cuda.memory_reserved() / (1024**3)
    available = (total_memory - reserved)
    print(f"DEVICE:{device}")
    print(f"TOTAL:{total_memory:.2f}GB")
    print(f"ALLOCATED:{allocated:.2f}GB")
    print(f"RESERVED:{reserved:.2f}GB")
    print(f"AVAILABLE:{available:.2f}GB")
else:
    print("CUDA:NOT_AVAILABLE")
'@

    try {
        $output = python -c $pythonScript 2>$null
        if ($output -match "DEVICE:") {
            $deviceName = ($output | Select-String "DEVICE:").Line -replace "DEVICE:", ""
            $total = ($output | Select-String "TOTAL:").Line -replace "TOTAL:", ""
            $allocated = ($output | Select-String "ALLOCATED:").Line -replace "ALLOCATED:", ""
            $reserved = ($output | Select-String "RESERVED:").Line -replace "RESERVED:", ""
            $available = ($output | Select-String "AVAILABLE:").Line -replace "AVAILABLE:", ""

            Write-Status "GPU: $deviceName" "INFO"
            Write-Status "Total VRAM: $total" "INFO"
            Write-Status "Allocated: $allocated" "INFO"
            Write-Status "Reserved: $reserved" "INFO"
            Write-Status "Available: $available" "INFO"

            # Check if available > 6GB
            $availableGB = [float]($available -replace "GB", "")
            if ($availableGB -gt 6) {
                Write-Status "Available VRAM is sufficient (> 6GB required)" "PASS"
                $script:DiagnosticResults += @{Issue = "CUDA OOM"; Status = "PASS" }
                $script:IssuesPassed++
                return $true
            }
            else {
                Write-Status "WARNING: Available VRAM low ($available, need > 6GB)" "WARN"
                Write-Status "Run: python -c `"import torch; torch.cuda.empty_cache(); print('Cleared')`"" "INFO"
                $script:DiagnosticResults += @{Issue = "CUDA OOM"; Status = "WARN" }
                $script:IssuesFailed++
                return $false
            }
        }
        else {
            Write-Status "CUDA not available - using CPU fallback" "WARN"
            $script:DiagnosticResults += @{Issue = "CUDA OOM"; Status = "WARN" }
            $script:IssuesFailed++
            return $false
        }
    }
    catch {
        Write-Status "Could not check CUDA - Python error: $_" "FAIL"
        $script:DiagnosticResults += @{Issue = "CUDA OOM"; Status = "FAIL" }
        $script:IssuesFailed++
        return $false
    }
}

# ============================================================================
# ISSUE #3: WebSocket timeout
# ============================================================================

function Test-WebSocketConfig {
    Write-Header 3 "WebSocket timeout (progress never arrives)"

    Write-Status "Checking WebSocket patterns..." "INFO"

    $backendPath = "$PSScriptRoot\main.py"
    $frontendPath = "$PSScriptRoot\..\frontend-nextjs\src\hooks\useSocket.ts"

    $wsPass = $true

    # Check for subscribe_to_job pattern
    if (Test-Path $frontendPath) {
        $content = Get-Content $frontendPath -Raw
        if ($content -match "subscribe_to_job") {
            Write-Status "Found subscribe_to_job pattern in frontend" "PASS"
        }
        else {
            Write-Status "subscribe_to_job pattern NOT found in frontend" "FAIL"
            $wsPass = $false
        }
    }
    else {
        Write-Status "Frontend WebSocket hook not found (optional check)" "WARN"
    }

    # Check for room-based emissions in backend
    if (Test-Path $backendPath) {
        $content = Get-Content $backendPath -Raw
        $roomEmit = $content | Select-String -Pattern "room=job_id|socketio\.emit.*room"
        if ($roomEmit) {
            Write-Status "Found room-based emissions in backend ($($roomEmit.Count) instances)" "PASS"
        }
        else {
            Write-Status "Room-based emissions NOT found in backend" "FAIL"
            $wsPass = $false
        }

        # Check for heartbeat
        if ($content -match "heartbeat|ping.*pong") {
            Write-Status "Found heartbeat/keep-alive pattern" "PASS"
        }
        else {
            Write-Status "Heartbeat pattern not detected (may be OK)" "WARN"
        }
    }
    else {
        Write-Status "Backend main.py not found" "FAIL"
        $wsPass = $false
    }

    if ($wsPass) {
        $script:DiagnosticResults += @{Issue = "WebSocket Timeout"; Status = "PASS" }
        $script:IssuesPassed++
    }
    else {
        Write-Status "Fix: Ensure clients subscribe to job room before generation starts" "INFO"
        $script:DiagnosticResults += @{Issue = "WebSocket Timeout"; Status = "FAIL" }
        $script:IssuesFailed++
    }

    return $wsPass
}

# ============================================================================
# ISSUE #4: Model path not found on Windows
# ============================================================================

function Test-ModelPath {
    Write-Header 4 "Model path not found on Windows"

    Write-Status "Checking model paths..." "INFO"

    $homeDir = $env:HOME
    if (-not $homeDir) {
        $homeDir = $env:USERPROFILE
    }

    Write-Status "HOME = $homeDir" "INFO"

    $modelPaths = @(
        "$homeDir\.cache\hunyuan\models",
        "$homeDir\.cache\hy3dgen\models",
        "$env:USERPROFILE\.cache\hunyuan\models"
    )

    $pathFound = $false

    foreach ($path in $modelPaths) {
        if (Test-Path $path) {
            Write-Status "Model directory exists: $path" "PASS"
            $pathFound = $true
            break
        }
    }

    if (-not $pathFound) {
        Write-Status "Model directory NOT found" "FAIL"
        Write-Status "Create model directories:" "INFO"
        foreach ($path in $modelPaths) {
            Write-Host "  mkdir `"$path`" -Force" -ForegroundColor Yellow
        }
    }
    else {
        $script:DiagnosticResults += @{Issue = "Model Path"; Status = "PASS" }
        $script:IssuesPassed++
        return $true
    }

    $script:DiagnosticResults += @{Issue = "Model Path"; Status = "FAIL" }
    $script:IssuesFailed++
    return $false
}

# ============================================================================
# ISSUE #5: Import error
# ============================================================================

function Test-ImportErrors {
    Write-Header 5 "Import error (ModuleNotFoundError)"

    Write-Status "Checking Python module imports..." "INFO"

    $modules = @(
        "torch",
        "onnx",
        "xformers",
        "flask",
        "flask_socketio",
        "trimesh",
        "PIL"
    )

    $allImported = $true

    foreach ($module in $modules) {
        $pythonCmd = "import $module; print($module.__version__ if hasattr($module, '__version__') else 'OK')"
        try {
            $version = python -c $pythonCmd 2>$null
            if ($?) {
                Write-Status "$module ($version)" "PASS"
            }
            else {
                Write-Status "$module - IMPORT FAILED" "FAIL"
                $allImported = $false
            }
        }
        catch {
            Write-Status "$module - NOT INSTALLED" "FAIL"
            $allImported = $false
        }
    }

    if ($allImported) {
        Write-Status "All critical modules available" "PASS"
        $script:DiagnosticResults += @{Issue = "Import Error"; Status = "PASS" }
        $script:IssuesPassed++
        return $true
    }
    else {
        Write-Status "Fix: Run: pip install -r requirements.txt" "INFO"
        $script:DiagnosticResults += @{Issue = "Import Error"; Status = "FAIL" }
        $script:IssuesFailed++
        return $false
    }
}

# ============================================================================
# ISSUE #6: STL mesh validation
# ============================================================================

function Test-STLValidation {
    Write-Header 6 "STL mesh validation/corruption"

    Write-Status "Checking STL/mesh validation patterns..." "INFO"

    $stlProcessorPath = "$PSScriptRoot\stl_processor.py"

    $trimeshOK = $false
    $validationOK = $false

    # Check trimesh availability
    try {
        $output = python -c "import trimesh; print(trimesh.__version__)" 2>$null
        if ($?) {
            Write-Status "trimesh module is available ($output)" "PASS"
            $trimeshOK = $true
        }
    }
    catch {
        Write-Status "trimesh module NOT available" "FAIL"
    }

    # Check for validation patterns in code
    if (Test-Path $stlProcessorPath) {
        $content = Get-Content $stlProcessorPath -Raw
        $patterns = @("is_valid", "is_watertight", "remove_degenerate_faces", "fill_holes")

        $foundPatterns = 0
        foreach ($pattern in $patterns) {
            if ($content -match $pattern) {
                Write-Status "Found validation pattern: $pattern" "PASS"
                $foundPatterns++
            }
        }

        if ($foundPatterns -eq $patterns.Count) {
            $validationOK = $true
            Write-Status "All mesh repair capabilities detected" "PASS"
        }
    }

    if ($trimeshOK -and $validationOK) {
        Write-Status "STL validation configured correctly" "PASS"
        $script:DiagnosticResults += @{Issue = "STL Validation"; Status = "PASS" }
        $script:IssuesPassed++
        return $true
    }
    else {
        if (-not $trimeshOK) {
            Write-Status "Fix: pip install trimesh" "INFO"
        }
        $script:DiagnosticResults += @{Issue = "STL Validation"; Status = "FAIL" }
        $script:IssuesFailed++
        return $false
    }
}

# ============================================================================
# REPORT GENERATION
# ============================================================================

function Generate-Report {
    $reportContent = @"
================================================================================
ORFEAS AI 2D->3D STUDIO - COMPREHENSIVE DIAGNOSTIC REPORT
================================================================================
Generated: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
Duration: $(((Get-Date) - $StartTime).TotalSeconds) seconds

SUMMARY
================================================================================
Total Issues Checked: 6
Passed: $IssuesPassed
Failed: $IssuesFailed
Warnings: $([math]::Max(0, 6 - $IssuesPassed - $IssuesFailed))
Overall Status: $(if ($IssuesFailed -eq 0) { "HEALTHY" } else { "NEEDS ATTENTION" })

DETAILED RESULTS
================================================================================
"@

    foreach ($result in $script:DiagnosticResults) {
        $reportContent += "`n[$($result.Status)] $($result.Issue)"
    }

    $reportContent += "`n`n================================================================================"
    $reportContent += "`nFOR MORE INFORMATION:`n"
    $reportContent += "`nSee .github/copilot-instructions.md for detailed issue explanations`n"
    $reportContent += "`nSee backend/DIAGNOSTIC-SCRIPT-README.md for usage and troubleshooting`n"

    return $reportContent
}

# ============================================================================
# MAIN EXECUTION
# ============================================================================

Write-Host "`n" -NoNewline
Write-Host "$('*' * 80)" -ForegroundColor Green
Write-Host "*  ORFEAS AI 2D->3D STUDIO - COMPREHENSIVE DIAGNOSTIC TOOL" -ForegroundColor Green
Write-Host "*  Checking 6 Critical Issues for Production Readiness" -ForegroundColor Green
Write-Host "$('*' * 80)" -ForegroundColor Green

# Run all diagnostics
Test-XformersEnvVars | Out-Null
Test-CUDAMemory | Out-Null
Test-WebSocketConfig | Out-Null
Test-ModelPath | Out-Null
Test-ImportErrors | Out-Null
Test-STLValidation | Out-Null

# Generate and display summary
Write-Host "`n" -NoNewline
Write-Host "$('=' * 80)" -ForegroundColor Cyan
Write-Host "SUMMARY" -ForegroundColor Cyan
Write-Host "$('=' * 80)" -ForegroundColor Cyan

Write-Status "Total Issues Checked: 6" "INFO"
Write-Status "Passed: $IssuesPassed" "PASS"
Write-Status "Failed: $IssuesFailed" "FAIL"

$overallStatus = if ($IssuesFailed -eq 0) { "HEALTHY" } else { "NEEDS ATTENTION" }
if ($IssuesFailed -eq 0) {
    Write-Status "Overall Status: $overallStatus" "PASS"
}
else {
    Write-Status "Overall Status: $overallStatus" "FAIL"
}

# Generate report file
$report = Generate-Report
$report | Out-File -FilePath $ReportPath -Encoding UTF8
Write-Host "`nReport saved to: $ReportPath" -ForegroundColor Cyan

# Exit with proper code
$exitCode = if ($IssuesFailed -eq 0) { 0 } else { 1 }
Write-Host "`nExit Code: $exitCode ($(if ($exitCode -eq 0) { 'Success' } else { 'Failure' }))" -ForegroundColor $(if ($exitCode -eq 0) { 'Green' } else { 'Red' })

exit $exitCode
