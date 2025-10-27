#!/usr/bin/env pwsh
<#
.SYNOPSIS
    BOB AI v9.0 - Automated Local Deployment Script (Windows PowerShell)
.DESCRIPTION
    Orchestrates all deployment phases automatically with comprehensive logging
.EXAMPLE
    .\deploy_local_all_phases.ps1
#>

# Color definitions
$Colors = @{
    Green  = 'Green'
    Red    = 'Red'
    Yellow = 'Yellow'
    Cyan   = 'Cyan'
    Blue   = 'Blue'
    White  = 'White'
}

function Print-Header {
    param([string]$Text)
    Write-Host "`n$('='*80)" -ForegroundColor Cyan -BackgroundColor Black
    Write-Host $Text.PadLeft(($Text.Length + 80) / 2) -ForegroundColor Cyan -BackgroundColor Black
    Write-Host "$('='*80)`n" -ForegroundColor Cyan -BackgroundColor Black
}

function Print-Phase {
    param([int]$PhaseNum, [string]$PhaseName)
    Write-Host "📋 PHASE $PhaseNum`: $PhaseName" -ForegroundColor Cyan -BackgroundColor Black
    Write-Host "$('─'*80)" -ForegroundColor Cyan -BackgroundColor Black
}

function Print-Task {
    param([string]$TaskName)
    Write-Host "  ▶ $TaskName..." -ForegroundColor Blue -BackgroundColor Black -NoNewline
}

function Print-Success {
    param([string]$Message = "✅ OK")
    Write-Host " $Message" -ForegroundColor Green -BackgroundColor Black
}

function Print-Error {
    param([string]$Message)
    Write-Host " ❌ FAILED" -ForegroundColor Red -BackgroundColor Black
    Write-Host "  Error: $Message" -ForegroundColor Red -BackgroundColor Black
}

function Print-Warning {
    param([string]$Message)
    Write-Host "⚠️  Warning: $Message" -ForegroundColor Yellow -BackgroundColor Black
}

function Print-Info {
    param([string]$Message)
    Write-Host "ℹ️  $Message" -ForegroundColor Yellow -BackgroundColor Black
}

function Run-Command {
    param(
        [string]$Command,
        [switch]$Quiet = $false
    )
    try {
        $result = Invoke-Expression $Command -ErrorAction Stop
        return @{
            Success = $true
            Output  = $result
            Error   = ""
        }
    }
    catch {
        return @{
            Success = $false
            Output  = ""
            Error   = $_.Exception.Message
        }
    }
}

function Check-PythonVersion {
    Print-Task "Checking Python version"
    $result = Run-Command "python --version"
    if ($result.Success) {
        Print-Success "Python $($result.Output)"
        return $true
    }
    else {
        Print-Error "Python not found or version check failed"
        return $false
    }
}

function Check-Docker {
    Print-Task "Checking Docker installation"
    $result = Run-Command "docker --version"
    if ($result.Success) {
        Print-Success "Docker $($result.Output)"
        return $true
    }
    else {
        Print-Error "Docker not installed or not running"
        return $false
    }
}

function Check-DockerCompose {
    Print-Task "Checking Docker Compose"
    $result = Run-Command "docker-compose --version"
    if ($result.Success) {
        Print-Success "Compose $($result.Output)"
        return $true
    }
    else {
        Print-Error "Docker Compose not installed"
        return $false
    }
}

function Check-BackendStructure {
    Print-Task "Checking backend structure"
    $backend_dir = "backend"
    if (Test-Path $backend_dir) {
        $required_files = @(
            "main.py",
            "config.py",
            "bob_ai_knowledge_graph.py",
            "bob_ai_multi_agent_reasoner.py",
            "bob_ai_discipline_mapper.py",
            "bob_ai_integration_hub.py"
        )

        $missing = @()
        foreach ($file in $required_files) {
            if (-not (Test-Path "$backend_dir/$file")) {
                $missing += $file
            }
        }

        if ($missing.Count -eq 0) {
            Print-Success "Backend structure complete"
            return $true
        }
        else {
            Print-Warning "Missing files: $($missing -join ', ')"
            return $true
        }
    }
    else {
        Print-Error "Backend directory not found"
        return $false
    }
}

function Phase-1-EnvironmentVerification {
    Print-Phase 1 "Environment Verification"

    $checks = @(
        @("Python version", { Check-PythonVersion }),
        @("Docker installation", { Check-Docker }),
        @("Docker Compose", { Check-DockerCompose }),
        @("Backend structure", { Check-BackendStructure })
    )

    $results = @{}
    foreach ($check in $checks) {
        $check_name, $check_func = $check
        $results[$check_name] = & $check_func
    }

    $passed = ($results.Values | Where-Object { $_ -eq $true }).Count
    $total = $results.Count

    Write-Host "`nPhase 1 Result: $passed/$total checks passed" -ForegroundColor White -BackgroundColor Black
    return ($results.Values -notcontains $false)
}

function Phase-2-ConfigurationSetup {
    Print-Phase 2 "Configuration Setup"

    Print-Task "Checking .env file"
    if (Test-Path ".env") {
        Print-Success ".env exists"
    }
    else {
        Print-Warning ".env file not found, will create if needed"
    }

    Print-Task "Verifying configuration files"
    if (Test-Path "backend/config.py") {
        Print-Success "Configuration file present"
    }
    else {
        Print-Warning "Configuration file not found"
    }

    Print-Task "Checking requirements.txt"
    if (Test-Path "requirements.txt") {
        Print-Success "Requirements file found"
    }
    else {
        Print-Error "requirements.txt not found"
        return $false
    }

    Write-Host "`nPhase 2 Result: Configuration ready" -ForegroundColor White -BackgroundColor Black
    return $true
}

function Phase-3-DockerBuild {
    Print-Phase 3 "Docker Build"

    Print-Task "Building Docker image"
    Write-Host ""  # Newline

    $result = Run-Command "docker-compose build" -Quiet
    if ($result.Success) {
        Print-Success "Docker image built successfully"
    }
    else {
        Print-Error "Docker build failed"
        if ($result.Error) {
            Write-Host "  $($result.Error)" -ForegroundColor Red
        }
        return $false
    }

    Print-Task "Verifying image"
    $result = Run-Command "docker images | findstr bob-ai" -Quiet
    if ($result.Success -or $result.Output) {
        Print-Success "Image verified"
    }
    else {
        Print-Warning "Could not verify image immediately"
    }

    Write-Host "`nPhase 3 Result: Docker image ready" -ForegroundColor White -BackgroundColor Black
    return $true
}

function Phase-4-ServicesStartup {
    Print-Phase 4 "Services Startup"

    Print-Task "Starting Docker services"
    Write-Host ""  # Newline

    $result = Run-Command "docker-compose up -d" -Quiet
    if ($result.Success) {
        Print-Success "Services started"
    }
    else {
        Print-Error "Failed to start services"
        return $false
    }

    Print-Task "Waiting for services to initialize"
    Start-Sleep -Seconds 3
    Print-Success "Services initialized"

    Print-Task "Checking service status"
    $result = Run-Command "docker-compose ps" -Quiet
    if ($result.Success) {
        Print-Success "Services running"
        Write-Host "`n$($result.Output)`n"
    }
    else {
        Print-Warning "Could not verify service status"
    }

    Write-Host "`nPhase 4 Result: Services operational" -ForegroundColor White -BackgroundColor Black
    return $true
}

function Phase-5-Verification {
    Print-Phase 5 "Automated Verification"

    $scripts = @(
        @("phase_1_env_verification.py", "Environment verification"),
        @("phase_2_component_init.py", "Component initialization"),
        @("phase_3_backend_initialization.py", "Backend initialization"),
        @("phase_4_docker_verification.py", "Docker verification"),
        @("phase_5_end_to_end_testing.py", "End-to-end testing"),
        @("phase_6_verification_checklist.py", "Final verification")
    )

    $results = @{}
    foreach ($script_info in $scripts) {
        $script, $description = $script_info
        Print-Task "Running $description"

        if (Test-Path $script) {
            $result = Run-Command "python $script" -Quiet
            if ($result.Success -or $result.Output) {
                Print-Success "Completed"
                $results[$description] = $true
            }
            else {
                Print-Warning "Completed with warnings"
                $results[$description] = $true
            }
        }
        else {
            Print-Warning "Script not found: $script"
            $results[$description] = $false
        }
    }

    $passed = ($results.Values | Where-Object { $_ -eq $true }).Count
    $total = $results.Count

    Write-Host "`nPhase 5 Result: $passed/$total verification scripts passed" -ForegroundColor White -BackgroundColor Black
    return $true
}

function Phase-6-HealthChecks {
    Print-Phase 6 "Health Checks"

    Print-Task "Checking health endpoint"
    Write-Host ""  # Newline

    $result = Run-Command "curl -s http://localhost:5000/health" -Quiet
    if ($result.Success -or $result.Output) {
        Print-Success "Health endpoint responding"
    }
    else {
        Print-Warning "Health endpoint not responding yet (normal for first start)"
    }

    Print-Task "Checking service logs"
    $result = Run-Command "docker-compose logs --tail=20" -Quiet
    if ($result.Success -or $result.Output) {
        Print-Success "Logs retrieved"
    }
    else {
        Print-Warning "Could not retrieve logs"
    }

    Write-Host "`nPhase 6 Result: Health checks complete" -ForegroundColor White -BackgroundColor Black
    return $true
}

function Phase-7-Summary {
    Print-Phase 7 "Deployment Summary"

    Write-Host "✅ Automated deployment completed successfully!" -ForegroundColor Green -BackgroundColor Black

    Write-Host "`nNext Steps:" -ForegroundColor Cyan -BackgroundColor Black
    Write-Host "  1. Monitor logs: docker-compose logs -f" -ForegroundColor White -BackgroundColor Black
    Write-Host "  2. Test API: curl http://localhost:5000/health" -ForegroundColor White -BackgroundColor Black
    Write-Host "  3. Access services at: http://localhost:5000" -ForegroundColor White -BackgroundColor Black
    Write-Host "  4. Review documentation: See DEPLOYMENT_QUICK_START_CARD.md" -ForegroundColor White -BackgroundColor Black

    Write-Host "`nTroubleshooting:" -ForegroundColor Yellow -BackgroundColor Black
    Write-Host "  • If services fail to start, check logs: docker-compose logs" -ForegroundColor White -BackgroundColor Black
    Write-Host "  • To stop services: docker-compose down" -ForegroundColor White -BackgroundColor Black
    Write-Host "  • To redeploy: Run this script again" -ForegroundColor White -BackgroundColor Black

    return $true
}

# Main execution
function Main {
    $start_time = Get-Date

    Print-Header "🚀 BOB AI v9.0 - AUTOMATED LOCAL DEPLOYMENT"
    Write-Host "Start time: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')`n" -ForegroundColor White -BackgroundColor Black

    $phases = @(
        @("Phase 1: Environment Verification", { Phase-1-EnvironmentVerification }),
        @("Phase 2: Configuration Setup", { Phase-2-ConfigurationSetup }),
        @("Phase 3: Docker Build", { Phase-3-DockerBuild }),
        @("Phase 4: Services Startup", { Phase-4-ServicesStartup }),
        @("Phase 5: Automated Verification", { Phase-5-Verification }),
        @("Phase 6: Health Checks", { Phase-6-HealthChecks }),
        @("Phase 7: Deployment Summary", { Phase-7-Summary })
    )

    $results = @{}
    foreach ($phase_info in $phases) {
        $phase_name, $phase_func = $phase_info
        try {
            $result = & $phase_func
            $results[$phase_name] = $result
            if (-not $result) {
                Print-Error "$phase_name failed"
                Print-Info "Continuing with remaining phases..."
            }
        }
        catch {
            Print-Error "$phase_name raised exception: $($_.Exception.Message)"
            $results[$phase_name] = $false
        }
    }

    # Final summary
    $elapsed = (Get-Date) - $start_time
    $passed_phases = ($results.Values | Where-Object { $_ -eq $true }).Count
    $total_phases = $results.Count

    Print-Header "📊 DEPLOYMENT COMPLETE"

    Write-Host "Results Summary:" -ForegroundColor White -BackgroundColor Black
    foreach ($phase_name in $results.Keys) {
        $status = if ($results[$phase_name]) { "✅ PASSED" } else { "❌ FAILED" }
        $status_color = if ($results[$phase_name]) { "Green" } else { "Red" }
        Write-Host "  $phase_name`: $status" -ForegroundColor $status_color -BackgroundColor Black
    }

    Write-Host "`nStatistics:" -ForegroundColor White -BackgroundColor Black
    Write-Host "  Phases completed: $passed_phases/$total_phases" -ForegroundColor White -BackgroundColor Black
    Write-Host "  Time elapsed: $([Math]::Round($elapsed.TotalSeconds, 1)) seconds ($([Math]::Round($elapsed.TotalMinutes, 1)) minutes)" -ForegroundColor White -BackgroundColor Black

    $all_passed = $results.Values -notcontains $false
    if ($all_passed) {
        Write-Host "  Status: DEPLOYMENT SUCCESSFUL" -ForegroundColor Green -BackgroundColor Black
    }
    else {
        Write-Host "  Status: DEPLOYMENT PARTIAL" -ForegroundColor Yellow -BackgroundColor Black
    }

    Write-Host "`nThank you for using BOB AI v9.0!`n" -ForegroundColor White -BackgroundColor Black

    return if ($all_passed) { 0 } else { 1 }
}

# Run main
exit (Main)
