<#
.SYNOPSIS
  Runs automated remediation for common Markdown offenses on key files and then lints them.

.USAGE
  powershell -ExecutionPolicy Bypass -File .\RUN_MARKDOWN_REMEDIATION.ps1
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $repoRoot

$targets = @(
    'md/TQM_MASTER_OPTIMIZATION_PLAN.md',
    'md/TQM_VISUAL_DASHBOARD.md'
)

Write-Host "[remediation] Running fixer on:`n  - " ($targets -join "`n  - ") -ForegroundColor Cyan

python .\scripts\fix_markdown_offenders.py @targets

Write-Host "[remediation] Linting remediated files..." -ForegroundColor Cyan
if (Get-Command npx -ErrorAction SilentlyContinue) {
    npx --yes markdownlint-cli@0.41.0 @targets
}
elseif (Get-Command markdownlint -ErrorAction SilentlyContinue) {
    markdownlint @targets
}
else {
    Write-Warning 'markdownlint not found (npx/markdownlint). Install Node.js or markdownlint-cli to verify.'
}

Write-Host "[remediation] Done." -ForegroundColor Green
