# ORFEAS Enterprise Agent System Startup Script
# PowerShell script for Windows deployment of enterprise agent framework

param(
    [Parameter(Mandatory = $false)]
    [string]$Mode = "production",

    [Parameter(Mandatory = $false)]
    [switch]$ValidateOnly = $false,

    [Parameter(Mandatory = $false)]
    [switch]$SkipValidation = $false,

    [Parameter(Mandatory = $false)]
    [switch]$SetupRedis = $false
)

# Set error action preference
$ErrorActionPreference = "Stop"

Write-Host "" -ForegroundColor Cyan
Write-Host "  ORFEAS ENTERPRISE AGENT SYSTEM STARTUP                                " -ForegroundColor Cyan
Write-Host "                                                                              " -ForegroundColor Cyan
Write-Host "  Multi-Agent Orchestration Framework                                      " -ForegroundColor Cyan
Write-Host "  Intelligent Quality Assessment & Workflow Optimization                   " -ForegroundColor Cyan
Write-Host "  Advanced Communication Protocols & Service Discovery                     " -ForegroundColor Cyan
Write-Host "  Ultra-Performance Integration with 100x Speed Optimization               " -ForegroundColor Cyan
Write-Host "                                                                              " -ForegroundColor Cyan
Write-Host "" -ForegroundColor Cyan
Write-Host ""

# Function to check if running as administrator
function Test-Administrator {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# Function to install Redis on Windows (if needed)
function Install-Redis {
    Write-Host " Setting up Redis for agent message bus..." -ForegroundColor Yellow

    if (Get-Command "redis-server" -ErrorAction SilentlyContinue) {
        Write-Host " Redis already installed" -ForegroundColor Green
        return
    }

    Write-Host " Installing Redis via Chocolatey..." -ForegroundColor Yellow

    # Check if Chocolatey is installed
    if (-not (Get-Command "choco" -ErrorAction SilentlyContinue)) {
        Write-Host " Chocolatey not found. Please install Chocolatey first:" -ForegroundColor Red
        Write-Host "   https://chocolatey.org/install" -ForegroundColor Red
        return $false
    }

    try {
        choco install redis-64 -y
        Write-Host " Redis installed successfully" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host " Redis installation failed: $_" -ForegroundColor Red
        return $false
    }
}

# Function to start Redis service
function Start-RedisService {
    Write-Host " Starting Redis service..." -ForegroundColor Yellow

    try {
        # Try to start Redis as a service
        $redisService = Get-Service -Name "Redis" -ErrorAction SilentlyContinue
        if ($redisService) {
            if ($redisService.Status -ne "Running") {
                Start-Service -Name "Redis"
                Write-Host " Redis service started" -ForegroundColor Green
            }
            else {
                Write-Host " Redis service already running" -ForegroundColor Green
            }
        }
        else {
            # Try to start Redis manually
            Write-Host " Starting Redis manually..." -ForegroundColor Yellow
            Start-Process -FilePath "redis-server" -WindowStyle Minimized
            Start-Sleep -Seconds 3
            Write-Host " Redis started manually" -ForegroundColor Green
        }
        return $true
    }
    catch {
        Write-Host " Failed to start Redis: $_" -ForegroundColor Red
        return $false
    }
}

# Function to validate Python environment
function Test-PythonEnvironment {
    Write-Host " Validating Python environment..." -ForegroundColor Yellow

    # Check Python version
    try {
        $pythonVersion = python --version 2>&1
        Write-Host " $pythonVersion" -ForegroundColor Green
    }
    catch {
        Write-Host " Python not found in PATH" -ForegroundColor Red
        return $false
    }

    # Check if in virtual environment
    if ($env:VIRTUAL_ENV) {
        Write-Host " Virtual environment active: $env:VIRTUAL_ENV" -ForegroundColor Green
    }
    else {
        Write-Host " No virtual environment detected" -ForegroundColor Yellow
    }

    return $true
}

# Function to install enterprise agent dependencies
function Install-AgentDependencies {
    Write-Host " Installing enterprise agent dependencies..." -ForegroundColor Yellow

    $requirementsFile = "backend\requirements-enterprise-agents.txt"

    if (-not (Test-Path $requirementsFile)) {
        Write-Host " Requirements file not found: $requirementsFile" -ForegroundColor Red
        return $false
    }

    try {
        pip install -r $requirementsFile
        Write-Host " Enterprise agent dependencies installed" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host " Failed to install dependencies: $_" -ForegroundColor Red
        return $false
    }
}

# Function to setup environment variables
function Set-EnvironmentVariables {
    Write-Host " Setting up environment variables..." -ForegroundColor Yellow

    # Load enterprise agent environment variables
    $envFile = "backend\.env.enterprise-agents"
    if (Test-Path $envFile) {
        Write-Host " Loading enterprise agent configuration..." -ForegroundColor Yellow
        Get-Content $envFile | ForEach-Object {
            if ($_ -match "^([^#][^=]+)=(.+)$") {
                $name = $matches[1].Trim()
                $value = $matches[2].Trim()
                [Environment]::SetEnvironmentVariable($name, $value, "Process")
            }
        }
        Write-Host " Enterprise agent environment variables loaded" -ForegroundColor Green
    }
    else {
        Write-Host " Enterprise agent env file not found: $envFile" -ForegroundColor Yellow
    }

    # Set default environment variables
    if (-not $env:ENABLE_ENTERPRISE_AGENTS) {
        [Environment]::SetEnvironmentVariable("ENABLE_ENTERPRISE_AGENTS", "true", "Process")
    }

    if (-not $env:ENTERPRISE_AGENT_MODE) {
        [Environment]::SetEnvironmentVariable("ENTERPRISE_AGENT_MODE", $Mode, "Process")
    }

    Write-Host " Environment variables configured" -ForegroundColor Green
}

# Function to run startup validation
function Invoke-StartupValidation {
    Write-Host " Running enterprise agent startup validation..." -ForegroundColor Yellow

    try {
        python backend\startup_enterprise_agents.py
        if ($LASTEXITCODE -eq 0) {
            Write-Host " Startup validation passed" -ForegroundColor Green
            return $true
        }
        else {
            Write-Host " Startup validation failed" -ForegroundColor Red
            return $false
        }
    }
    catch {
        Write-Host " Startup validation error: $_" -ForegroundColor Red
        return $false
    }
}

# Function to start ORFEAS with enterprise agents
function Start-OrfeasWithAgents {
    Write-Host " Starting ORFEAS with Enterprise Agent System..." -ForegroundColor Green
    Write-Host ""

    # Set environment variables for agent system
    [Environment]::SetEnvironmentVariable("ENABLE_ENTERPRISE_AGENTS", "true", "Process")
    [Environment]::SetEnvironmentVariable("ENTERPRISE_AGENT_MODE", $Mode, "Process")

    # Start ORFEAS server
    python backend\main.py
}

# Main execution flow
try {
    Write-Host " Startup Mode: $Mode" -ForegroundColor Cyan
    Write-Host ""

    # Validate Python environment
    if (-not (Test-PythonEnvironment)) {
        Write-Host " Python environment validation failed" -ForegroundColor Red
        exit 1
    }

    # Setup Redis if requested
    if ($SetupRedis) {
        if (-not (Install-Redis)) {
            Write-Host " Redis setup failed, continuing without Redis..." -ForegroundColor Yellow
        }
    }

    # Start Redis service
    if (-not (Start-RedisService)) {
        Write-Host " Redis not available, using in-memory message bus..." -ForegroundColor Yellow
    }

    # Install dependencies if not skipping validation
    if (-not $SkipValidation) {
        if (-not (Install-AgentDependencies)) {
            Write-Host " Dependency installation failed" -ForegroundColor Red
            exit 1
        }
    }

    # Setup environment variables
    Set-EnvironmentVariables

    # Run startup validation if not skipping
    if (-not $SkipValidation) {
        if (-not (Invoke-StartupValidation)) {
            Write-Host " Enterprise agent system validation failed" -ForegroundColor Red
            exit 1
        }
    }

    # If validate-only mode, exit here
    if ($ValidateOnly) {
        Write-Host " Validation completed successfully!" -ForegroundColor Green
        Write-Host "   Enterprise agent system is ready to start" -ForegroundColor Green
        exit 0
    }

    # Start ORFEAS with enterprise agents
    Write-Host ""
    Write-Host "=" * 80 -ForegroundColor Green
    Write-Host " ENTERPRISE AGENT SYSTEM READY!" -ForegroundColor Green
    Write-Host "=" * 80 -ForegroundColor Green
    Write-Host ""

    Start-OrfeasWithAgents

}
catch {
    Write-Host ""
    Write-Host " STARTUP FAILED: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Troubleshooting:" -ForegroundColor Yellow
    Write-Host "  1. Ensure Python 3.8+ is installed and in PATH" -ForegroundColor Yellow
    Write-Host "  2. Activate your Python virtual environment" -ForegroundColor Yellow
    Write-Host "  3. Install dependencies: pip install -r backend\requirements-enterprise-agents.txt" -ForegroundColor Yellow
    Write-Host "  4. Run validation only: .\START_ENTERPRISE_AGENTS.ps1 -ValidateOnly" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}
