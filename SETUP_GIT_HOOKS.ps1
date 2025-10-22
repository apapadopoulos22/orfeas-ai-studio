<#
.SYNOPSIS
  Configure Git to use repo-local hooks and verify markdownlint availability.

.USAGE
  Run in repository root:
    powershell -ExecutionPolicy Bypass -File .\SETUP_GIT_HOOKS.ps1

.NOTES
  - Requires Git for Windows. Hooks will run via bash/sh. Ensure Node.js is installed for npx fallback.
#>

param()

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

Write-Host '[setup] Configuring Git hooks path to .githooks ...'
& git config core.hooksPath .githooks

Write-Host '[setup] Verifying markdownlint availability (via npx or global)...'
$npx = Get-Command npx -ErrorAction SilentlyContinue
$mdl = Get-Command markdownlint -ErrorAction SilentlyContinue
if (-not $npx -and -not $mdl) {
    Write-Warning 'Neither npx nor markdownlint found. Install Node.js (LTS) or markdownlint-cli.'
    Write-Host 'Quick install with npm (requires Node.js):'
    Write-Host '  npm install -g markdownlint-cli'
}
else {
    Write-Host '[setup] markdownlint available.'
}

Write-Host '[setup] Done. The pre-commit hook will lint staged .md files.'
