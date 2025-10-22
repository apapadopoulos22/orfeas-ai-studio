<#
.SYNOPSIS
  Run remediation across all Markdown files under md\ and summarize changes.

.USAGE
  powershell -ExecutionPolicy Bypass -File .\RUN_MARKDOWN_REMEDIATION_ALL.ps1
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $repoRoot

if (-not (Test-Path 'md')) {
    Write-Error "md/ directory not found at $repoRoot"
    exit 1
}

# Collect all .md files under md\ (recursively)
$files = Get-ChildItem -Path 'md' -Recurse -File -Include *.md | ForEach-Object { $_.FullName }
if (-not $files -or $files.Count -eq 0) {
    Write-Host "No Markdown files found under md/." -ForegroundColor Yellow
    exit 0
}

Write-Host "[remediation] Running fixer on $($files.Count) files..." -ForegroundColor Cyan

# Run the fixer with JSON output to aggregate results
$tempOut = New-TemporaryFile
try {
    & python .\scripts\fix_markdown_offenders.py --json @files | Out-File -FilePath $tempOut -Encoding utf8
}
catch {
    Remove-Item $tempOut -ErrorAction SilentlyContinue
    throw
}

# Parse results
$fixed = 0
$clean = 0
$agg = [ordered]@{
    demoted_h1               = 0
    labeled_fences           = 0
    blanks_collapsed         = 0
    bold_promoted            = 0
    fixed_heading_punct      = 0
    normalized_heading_level = 0
    dedup_headings           = 0
    fence_lang_relabelled    = 0
}

$changedFiles = @()
$cleanFiles = @()

Get-Content $tempOut | ForEach-Object {
    if (-not $_) { return }
    try { $obj = $_ | ConvertFrom-Json } catch { return }
    if ($null -eq $obj) { return }

    if ($obj.status -eq 'fixed') {
        $fixed += 1
        $changedFiles += $obj.path
    }
    elseif ($obj.status -eq 'clean') {
        $clean += 1
        $cleanFiles += $obj.path
    }

    if ($null -ne $obj.stats) {
        $keys = @($agg.Keys)
        foreach ($k in $keys) {
            $val = $obj.stats.$k
            if ($null -ne $val) { $agg[$k] += [int]$val }
        }
    }
}

Remove-Item $tempOut -ErrorAction SilentlyContinue

Write-Host "[summary] Files fixed: $fixed | Clean: $clean | Total: $($files.Count)" -ForegroundColor Green

# Optional: lint all md files
Write-Host "[remediation] Linting md/ directory..." -ForegroundColor Cyan
if (Get-Command npx -ErrorAction SilentlyContinue) {
    npx --yes markdownlint-cli@0.41.0 md/**/*.md
}
elseif (Get-Command markdownlint -ErrorAction SilentlyContinue) {
    markdownlint md/**/*.md
}
else {
    Write-Warning 'markdownlint not found (npx/markdownlint). Install Node.js or markdownlint-cli to verify.'
}

Write-Host "[aggregates]`n  demoted_h1=$($agg.demoted_h1)`n  labeled_fences=$($agg.labeled_fences)`n  blanks_collapsed=$($agg.blanks_collapsed)`n  bold_promoted=$($agg.bold_promoted)`n  fixed_heading_punct=$($agg.fixed_heading_punct)`n  normalized_heading_level=$($agg.normalized_heading_level)`n  dedup_headings=$($agg.dedup_headings)`n  fence_lang_relabelled=$($agg.fence_lang_relabelled)" -ForegroundColor Cyan

# Show a compact list of changed files (if any)
if ($fixed -gt 0) {
    Write-Host "[changed]" -ForegroundColor Cyan
    $changedFiles | Sort-Object | ForEach-Object { Write-Host "  - $_" }
}
else {
    Write-Host "[changed] none" -ForegroundColor DarkGray
}
