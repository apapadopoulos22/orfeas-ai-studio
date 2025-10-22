# ORFEAS AI 2D→3D STUDIO - Batch Markdown Lint Fixer
# Automatically fixes markdown lint errors across all documentation files

Write-Host " ORFEAS Markdown Lint Batch Fixer" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$MarkdownDir = ".\md"
$RootMarkdownFiles = Get-ChildItem -Path . -Filter "*.md" -File
$MarkdownFiles = Get-ChildItem -Path $MarkdownDir -Filter "*.md" -File -Recurse -ErrorAction SilentlyContinue

# Check if markdownlint-cli is installed
Write-Host " Checking dependencies..." -ForegroundColor Yellow
try {
    $version = markdownlint --version 2>$null
    Write-Host " markdownlint-cli installed: $version" -ForegroundColor Green
}
catch {
    Write-Host " ERROR: markdownlint-cli is not installed" -ForegroundColor Red
    Write-Host "   Install with: npm install -g markdownlint-cli" -ForegroundColor Yellow
    exit 1
}
Write-Host ""

# Combine all markdown files
$AllMarkdownFiles = @()
$AllMarkdownFiles += $RootMarkdownFiles
if ($MarkdownFiles) {
    $AllMarkdownFiles += $MarkdownFiles
}

if ($AllMarkdownFiles.Count -eq 0) {
    Write-Host "  No markdown files found" -ForegroundColor Yellow
    exit 0
}

Write-Host " Found $($AllMarkdownFiles.Count) markdown file(s)" -ForegroundColor Cyan
Write-Host ""

# Process each file
$FixedCount = 0
$ErrorCount = 0
$SkippedCount = 0

foreach ($file in $AllMarkdownFiles) {
    $relativePath = $file.FullName.Replace($PWD.Path, "").TrimStart("\")
    Write-Host " Processing: $relativePath" -ForegroundColor White

    try {
        # Run markdownlint with --fix flag
        $output = markdownlint --fix $file.FullName 2>&1

        if ($LASTEXITCODE -eq 0) {
            Write-Host "    Fixed/Clean" -ForegroundColor Green
            $FixedCount++
        }
        else {
            Write-Host "     Has remaining errors:" -ForegroundColor Yellow
            Write-Host "   $output" -ForegroundColor Gray
            $ErrorCount++
        }
    }
    catch {
        Write-Host "    Processing failed: $_" -ForegroundColor Red
        $SkippedCount++
    }
}

# Summary
Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host " Batch Processing Complete" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host " Fixed/Clean:      $FixedCount file(s)" -ForegroundColor Green
Write-Host "  Remaining Errors: $ErrorCount file(s)" -ForegroundColor Yellow
Write-Host " Failed:           $SkippedCount file(s)" -ForegroundColor Red
Write-Host ""

if ($ErrorCount -gt 0) {
    Write-Host " Some errors require manual fixing:" -ForegroundColor Yellow
    Write-Host "   - Check VS Code Problems panel" -ForegroundColor White
    Write-Host "   - Review MARKDOWN_LINT_PREVENTION_GUIDE.md" -ForegroundColor White
    Write-Host "   - Run: markdownlint <file> for details" -ForegroundColor White
    exit 1
}
elseif ($SkippedCount -gt 0) {
    Write-Host "  Some files failed processing" -ForegroundColor Yellow
    exit 1
}
else {
    Write-Host " All files processed successfully!" -ForegroundColor Green
    exit 0
}
