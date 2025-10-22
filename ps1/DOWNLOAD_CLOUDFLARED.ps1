# THERION - CLOUDFLARED DOWNLOAD SCRIPT
# Downloads Cloudflare Tunnel executable

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  DOWNLOADING CLOUDFLARED (~50MB)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"
$output = "cloudflared.exe"

if (Test-Path $output) {
    Write-Host "[SKIP] Cloudflared already exists" -ForegroundColor Green
    Write-Host ""
} else {
    Write-Host "Downloading from GitHub..." -ForegroundColor Yellow
    Write-Host "(This may take 30-60 seconds)" -ForegroundColor White
    Write-Host ""

    try {
        Invoke-WebRequest -Uri $url -OutFile $output
        Write-Host ""
        Write-Host "[SUCCESS] Cloudflared downloaded!" -ForegroundColor Green
        Write-Host ""
    } catch {
        Write-Host ""
        Write-Host "[ERROR] Download failed: $_" -ForegroundColor Red
        Write-Host ""
        Write-Host "ALTERNATIVE DOWNLOAD:" -ForegroundColor Yellow
        Write-Host "1. Go to: https://github.com/cloudflare/cloudflared/releases/latest" -ForegroundColor White
        Write-Host "2. Download: cloudflared-windows-amd64.exe" -ForegroundColor White
        Write-Host "3. Rename to: cloudflared.exe" -ForegroundColor White
        Write-Host "4. Place in: C:\Users\johng\Documents\Erevus\orfeas\" -ForegroundColor White
        Write-Host ""
        exit 1
    }
}

Write-Host "========================================" -ForegroundColor Green
Write-Host "  READY TO START TUNNEL" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "RUN THIS NEXT:" -ForegroundColor Cyan
Write-Host "  .\cloudflared.exe tunnel --url http://localhost:5000" -ForegroundColor Yellow
Write-Host ""
