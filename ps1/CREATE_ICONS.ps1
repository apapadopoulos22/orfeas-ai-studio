Write-Host "Creating placeholder PWA icons..." -ForegroundColor Cyan

# Simple SVG placeholder icon
$svgContent = @"
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
  <rect width="512" height="512" fill="#e74c3c"/>
  <text x="50%" y="50%" font-family="Arial" font-size="120" fill="white" text-anchor="middle" dominant-baseline="middle" font-weight="bold">ORFEAS</text>
</svg>
"@

# Save SVG
$svgContent | Out-File -FilePath "icon.svg" -Encoding UTF8

Write-Host " Icon created: icon.svg" -ForegroundColor Green
Write-Host ""
Write-Host "To convert to PNG (optional):" -ForegroundColor Yellow
Write-Host "  1. Open icon.svg in browser" -ForegroundColor White
Write-Host "  2. Screenshot or use online converter" -ForegroundColor White
Write-Host "  3. Save as icon-192x192.png and icon-512x512.png" -ForegroundColor White
Write-Host ""
Write-Host "Or just ignore - icons are optional for testing!" -ForegroundColor Green
