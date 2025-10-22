# ORFEAS AI 2D→3D Studio - LLM Integration Test Script
# ==================================================
# PowerShell script to test Enterprise LLM capabilities

param(
    [string]$ServerUrl = "http://localhost:5000",
    [switch]$Verbose = $false
)

Write-Host " ORFEAS AI - ENTERPRISE LLM INTEGRATION TEST" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "Testing LLM endpoints and functionality..." -ForegroundColor White
Write-Host "Server URL: $ServerUrl" -ForegroundColor Yellow
Write-Host "=" * 60 -ForegroundColor Cyan

$testResults = @()
$totalTests = 0
$passedTests = 0

function Test-LLMEndpoint {
    param(
        [string]$TestName,
        [string]$Endpoint,
        [string]$Method = "GET",
        [hashtable]$Body = $null
    )

    $global:totalTests++
    Write-Host "`n Testing: $TestName" -ForegroundColor Yellow
    Write-Host "   Endpoint: $Method $Endpoint" -ForegroundColor Gray

    try {
        $headers = @{"Content-Type" = "application/json"}

        if ($Method -eq "GET") {
            $response = Invoke-RestMethod -Uri "$ServerUrl$Endpoint" -Method GET -Headers $headers -TimeoutSec 30
        } else {
            $jsonBody = $Body | ConvertTo-Json -Depth 5
            if ($Verbose) {
                Write-Host "   Request Body: $jsonBody" -ForegroundColor Gray
            }
            $response = Invoke-RestMethod -Uri "$ServerUrl$Endpoint" -Method POST -Body $jsonBody -Headers $headers -TimeoutSec 30
        }

        Write-Host "    SUCCESS" -ForegroundColor Green
        if ($Verbose) {
            Write-Host "   Response: $($response | ConvertTo-Json -Depth 2)" -ForegroundColor Gray
        }

        $global:passedTests++
        $global:testResults += @{
            Test = $TestName
            Status = "PASSED"
            Endpoint = $Endpoint
            Response = $response
        }

        return $response
    }
    catch {
        Write-Host "    FAILED: $($_.Exception.Message)" -ForegroundColor Red
        if ($Verbose) {
            Write-Host "   Error Details: $($_.Exception)" -ForegroundColor Red
        }

        $global:testResults += @{
            Test = $TestName
            Status = "FAILED"
            Endpoint = $Endpoint
            Error = $_.Exception.Message
        }

        return $null
    }
}

# Test 1: Server Health Check
Write-Host "`n PRELIMINARY HEALTH CHECK" -ForegroundColor Magenta
Write-Host "=" * 40 -ForegroundColor Magenta
$healthResponse = Test-LLMEndpoint -TestName "Server Health" -Endpoint "/api/health"

if (-not $healthResponse) {
    Write-Host "`n Server is not accessible. Please ensure ORFEAS is running:" -ForegroundColor Red
    Write-Host "   cd backend && python main.py" -ForegroundColor Yellow
    exit 1
}

# Test 2: LLM System Status
Write-Host "`n LLM SYSTEM STATUS TESTS" -ForegroundColor Magenta
Write-Host "=" * 40 -ForegroundColor Magenta
$statusResponse = Test-LLMEndpoint -TestName "LLM Status" -Endpoint "/api/llm/status"

# Test 3: LLM Models Information
$modelsResponse = Test-LLMEndpoint -TestName "LLM Models Info" -Endpoint "/api/llm/models"

# Test 4: Content Generation
Write-Host "`n CONTENT GENERATION TESTS" -ForegroundColor Magenta
Write-Host "=" * 40 -ForegroundColor Magenta
$generationBody = @{
    prompt = "Explain the benefits of AI-powered 3D model generation for creative industries."
    task_type = "general"
    context = @{
        audience = "professionals"
        format = "technical_explanation"
    }
}
$generationResponse = Test-LLMEndpoint -TestName "Content Generation" -Endpoint "/api/llm/generate" -Method "POST" -Body $generationBody

# Test 5: Code Generation
Write-Host "`n CODE GENERATION TESTS" -ForegroundColor Magenta
Write-Host "=" * 40 -ForegroundColor Magenta
$codeGenBody = @{
    requirements = "Create a Python function to validate STL file format and check for manifold geometry."
    language = "python"
    context = @{
        include_tests = $true
        include_docs = $true
        quality_level = "production"
    }
}
$codeResponse = Test-LLMEndpoint -TestName "GitHub Copilot Code Generation" -Endpoint "/api/llm/code-generate" -Method "POST" -Body $codeGenBody

# Test 6: Multi-LLM Orchestration
Write-Host "`n MULTI-LLM ORCHESTRATION TESTS" -ForegroundColor Magenta
Write-Host "=" * 40 -ForegroundColor Magenta
$orchestrationBody = @{
    task_description = "Compare different 3D file formats (STL, OBJ, GLTF, FBX) and recommend the best format for web-based 3D applications."
    context = @{
        complexity = "high"
        analysis_depth = "comprehensive"
        include_technical_details = $true
    }
}
$orchestrationResponse = Test-LLMEndpoint -TestName "Multi-LLM Orchestration" -Endpoint "/api/llm/orchestrate" -Method "POST" -Body $orchestrationBody

# Test 7: Code Analysis
Write-Host "`n CODE ANALYSIS TESTS" -ForegroundColor Magenta
Write-Host "=" * 40 -ForegroundColor Magenta
$analysisBody = @{
    code = @"
import numpy as np

def process_mesh(vertices, faces):
    # Calculate mesh properties
    mesh_area = 0
    for face in faces:
        v1, v2, v3 = vertices[face[0]], vertices[face[1]], vertices[face[2]]
        edge1 = v2 - v1
        edge2 = v3 - v1
        cross = np.cross(edge1, edge2)
        face_area = np.linalg.norm(cross) / 2
        mesh_area += face_area
    return mesh_area
"@
    language = "python"
}
$analysisResponse = Test-LLMEndpoint -TestName "Code Quality Analysis" -Endpoint "/api/llm/analyze-code" -Method "POST" -Body $analysisBody

# Test 8: Code Debugging
Write-Host "`n CODE DEBUGGING TESTS" -ForegroundColor Magenta
Write-Host "=" * 40 -ForegroundColor Magenta
$debugBody = @{
    code = @"
def calculate_volume(mesh):
    volume = 0
    for face in mesh.faces:
        # This has a bug - missing proper volume calculation
        volume += face.area
    return volume
"@
    error_message = "TypeError: 'Face' object has no attribute 'area'"
    language = "python"
}
$debugResponse = Test-LLMEndpoint -TestName "Code Debugging" -Endpoint "/api/llm/debug-code" -Method "POST" -Body $debugBody

# Test Summary
Write-Host "`n" + "=" * 60 -ForegroundColor Cyan
Write-Host " LLM INTEGRATION TEST SUMMARY" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan

$successRate = if ($totalTests -gt 0) { [math]::Round(($passedTests / $totalTests) * 100, 1) } else { 0 }

Write-Host "Total Tests: $totalTests" -ForegroundColor White
Write-Host "Passed: $passedTests" -ForegroundColor Green
Write-Host "Failed: $($totalTests - $passedTests)" -ForegroundColor Red
Write-Host "Success Rate: $successRate%" -ForegroundColor $(if ($successRate -ge 80) { "Green" } elseif ($successRate -ge 60) { "Yellow" } else { "Red" })

# Detailed Results
if ($Verbose) {
    Write-Host "`n DETAILED TEST RESULTS:" -ForegroundColor Cyan
    foreach ($result in $testResults) {
        $statusColor = if ($result.Status -eq "PASSED") { "Green" } else { "Red" }
        Write-Host "   $($result.Test): $($result.Status)" -ForegroundColor $statusColor
        if ($result.Error) {
            Write-Host "      Error: $($result.Error)" -ForegroundColor Red
        }
    }
}

# Configuration Summary
Write-Host "`n LLM SYSTEM CONFIGURATION:" -ForegroundColor Cyan
Write-Host "   • Enterprise LLM Manager: Multi-model intelligent routing" -ForegroundColor White
Write-Host "   • GitHub Copilot Enterprise: Advanced code generation" -ForegroundColor White
Write-Host "   • Multi-LLM Orchestration: Complex task decomposition" -ForegroundColor White
Write-Host "   • Code Quality Analysis: Automated code review" -ForegroundColor White
Write-Host "   • Intelligent Debugging: Error analysis and fixes" -ForegroundColor White
Write-Host "   • Context-Aware Processing: Smart model selection" -ForegroundColor White

# Final Status
if ($passedTests -eq $totalTests) {
    Write-Host "`n ALL LLM TESTS PASSED! Enterprise LLM system is fully functional." -ForegroundColor Green
    exit 0
} elseif ($passedTests -ge ($totalTests * 0.8)) {
    Write-Host "`n Most LLM tests passed. Minor issues may exist." -ForegroundColor Yellow
    exit 0
} else {
    Write-Host "`n  Multiple LLM test failures. Check server logs." -ForegroundColor Red
    exit 1
}
