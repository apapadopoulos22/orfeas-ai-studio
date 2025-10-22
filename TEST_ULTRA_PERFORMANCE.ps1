#!/usr/bin/env powershell
<#
.SYNOPSIS
    ORFEAS AI Ultra-Performance Integration Test Script

.DESCRIPTION
    Comprehensive test script for ultra-performance optimization protocols
    Tests all components including backend integration and API endpoints

.NOTES
    Author: ORFEAS AI Development Team
    Version: 1.0
    Requires: Python 3.8+, ORFEAS Backend Environment
#>

param(
    [switch]$QuickTest = $false,
    [switch]$FullValidation = $false,
    [switch]$ApiTest = $false,
    [switch]$Verbose = $false
)

# Colors for output
$Colors = @{
    Success = "Green"
    Warning = "Yellow"
    Error   = "Red"
    Info    = "Cyan"
    Header  = "Magenta"
}

function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Colors[$Color]
}

function Test-Prerequisites {
    Write-ColorOutput " Checking prerequisites..." "Info"

    # Check Python
    try {
        $pythonVersion = python --version 2>&1
        Write-ColorOutput " Python: $pythonVersion" "Success"
    }
    catch {
        Write-ColorOutput " Python not found or not in PATH" "Error"
        return $false
    }

    # Check backend directory
    if (Test-Path "backend") {
        Write-ColorOutput " Backend directory found" "Success"
    }
    else {
        Write-ColorOutput " Backend directory not found" "Error"
        return $false
    }

    # Check ultra-performance integration
    if (Test-Path "backend\ultra_performance_integration.py") {
        Write-ColorOutput " Ultra-performance integration file found" "Success"
    }
    else {
        Write-ColorOutput " Ultra-performance integration file not found" "Error"
        return $false
    }

    return $true
}

function Test-UltraPerformanceValidation {
    Write-ColorOutput " Running ultra-performance validation..." "Info"

    Push-Location backend
    try {
        $result = python validate_ultra_performance.py
        $exitCode = $LASTEXITCODE

        Write-Output $result

        if ($exitCode -eq 0) {
            Write-ColorOutput " Ultra-performance validation PASSED" "Success"
            return $true
        }
        else {
            Write-ColorOutput " Ultra-performance validation FAILED" "Error"
            return $false
        }
    }
    catch {
        Write-ColorOutput " Error running validation: $_" "Error"
        return $false
    }
    finally {
        Pop-Location
    }
}

function Test-BackendImport {
    Write-ColorOutput " Testing backend import..." "Info"

    Push-Location backend
    try {
        $importTest = @"
import sys
try:
    from ultra_performance_integration import UltraPerformanceManager
    print(" UltraPerformanceManager import successful")

    manager = UltraPerformanceManager()
    print(" UltraPerformanceManager initialization successful")

    status = manager.get_status()
    print(f" Status: {status}")

    print("SUCCESS")
except Exception as e:
    print(f" Error: {e}")
    print("FAILED")
    sys.exit(1)
"@

        $result = echo $importTest | python

        if ($result -match "SUCCESS") {
            Write-ColorOutput " Backend import test PASSED" "Success"
            return $true
        }
        else {
            Write-ColorOutput " Backend import test FAILED" "Error"
            Write-Output $result
            return $false
        }
    }
    catch {
        Write-ColorOutput " Error testing backend import: $_" "Error"
        return $false
    }
    finally {
        Pop-Location
    }
}

function Test-MainIntegration {
    Write-ColorOutput " Testing main.py integration..." "Info"

    Push-Location backend
    try {
        $integrationTest = @"
import sys
try:
    from main import OrfeasMain
    print(" OrfeasMain import successful")

    # Test in test mode
    main_instance = OrfeasMain(test_mode=True)
    print(" OrfeasMain initialization successful")

    if hasattr(main_instance, 'ultra_performance_manager'):
        if main_instance.ultra_performance_manager:
            print(" Ultra-performance manager integrated")
        else:
            print(" Ultra-performance manager is None (expected in test mode)")
    else:
        print(" Ultra-performance manager not found")
        sys.exit(1)

    print("SUCCESS")
except Exception as e:
    print(f" Error: {e}")
    import traceback
    traceback.print_exc()
    print("FAILED")
    sys.exit(1)
"@

        $result = echo $integrationTest | python

        if ($result -match "SUCCESS") {
            Write-ColorOutput " Main integration test PASSED" "Success"
            return $true
        }
        else {
            Write-ColorOutput " Main integration test FAILED" "Error"
            Write-Output $result
            return $false
        }
    }
    catch {
        Write-ColorOutput " Error testing main integration: $_" "Error"
        return $false
    }
    finally {
        Pop-Location
    }
}

function Test-ApiEndpoints {
    Write-ColorOutput " Testing API endpoints..." "Info"

    # This would require the server to be running
    # For now, just test if the endpoints are defined in main.py

    $apiEndpoints = @(
        "/api/ultra-generate-3d",
        "/api/ultra-performance/status",
        "/api/ultra-performance/config",
        "/api/ultra-performance/enable",
        "/api/ultra-performance/disable"
    )

    $mainContent = Get-Content "backend\main.py" -Raw

    $allFound = $true
    foreach ($endpoint in $apiEndpoints) {
        if ($mainContent -match [regex]::Escape($endpoint)) {
            Write-ColorOutput " Endpoint found: $endpoint" "Success"
        }
        else {
            Write-ColorOutput " Endpoint missing: $endpoint" "Error"
            $allFound = $false
        }
    }

    return $allFound
}

function Show-Summary {
    param(
        [hashtable]$Results
    )

    Write-ColorOutput "`n" + "=" * 80 "Header"
    Write-ColorOutput " ULTRA-PERFORMANCE INTEGRATION TEST SUMMARY" "Header"
    Write-ColorOutput "=" * 80 "Header"

    $passed = 0
    $total = 0

    foreach ($test in $Results.Keys) {
        $total++
        if ($Results[$test]) {
            $passed++
            Write-ColorOutput " $test" "Success"
        }
        else {
            Write-ColorOutput " $test" "Error"
        }
    }

    Write-ColorOutput "`n Results: $passed/$total tests passed" "Info"

    if ($passed -eq $total) {
        Write-ColorOutput " ALL TESTS PASSED! Ultra-performance integration is ready!" "Success"
        return $true
    }
    else {
        Write-ColorOutput " Some tests failed. Please review issues above." "Warning"
        return $false
    }
}

# Main execution
try {
    Write-ColorOutput " ORFEAS AI Ultra-Performance Integration Test" "Header"
    Write-ColorOutput "=" * 60 "Header"

    # Check prerequisites
    if (-not (Test-Prerequisites)) {
        Write-ColorOutput " Prerequisites check failed. Cannot continue." "Error"
        exit 1
    }

    # Initialize results
    $testResults = @{}

    # Run tests based on parameters
    if ($QuickTest) {
        Write-ColorOutput "`n Running QUICK TEST mode..." "Info"
        $testResults["Backend Import"] = Test-BackendImport
        $testResults["API Endpoints"] = Test-ApiEndpoints
    }
    elseif ($ApiTest) {
        Write-ColorOutput "`n Running API TEST mode..." "Info"
        $testResults["API Endpoints"] = Test-ApiEndpoints
    }
    elseif ($FullValidation) {
        Write-ColorOutput "`n Running FULL VALIDATION mode..." "Info"
        $testResults["Backend Import"] = Test-BackendImport
        $testResults["Main Integration"] = Test-MainIntegration
        $testResults["Ultra-Performance Validation"] = Test-UltraPerformanceValidation
        $testResults["API Endpoints"] = Test-ApiEndpoints
    }
    else {
        # Default: Quick validation
        Write-ColorOutput "`n Running DEFAULT validation..." "Info"
        $testResults["Backend Import"] = Test-BackendImport
        $testResults["Main Integration"] = Test-MainIntegration
        $testResults["API Endpoints"] = Test-ApiEndpoints
    }

    # Show summary
    $overallSuccess = Show-Summary -Results $testResults

    if ($overallSuccess) {
        Write-ColorOutput "`n Ready to deploy ultra-performance optimizations!" "Success"
        exit 0
    }
    else {
        Write-ColorOutput "`n Please fix issues before deployment." "Error"
        exit 1
    }
}
catch {
    Write-ColorOutput " Unexpected error: $_" "Error"
    exit 1
}
finally {
    Write-ColorOutput "`n Test completed at $(Get-Date)" "Info"
}
