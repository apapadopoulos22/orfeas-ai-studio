$ErrorActionPreference = 'SilentlyContinue'
Write-Host "
ORFEAS AI - Netlify Deployment Setup
" -ForegroundColor Green
Write-Host 'Step 1: Checking Git installation...' -ForegroundColor Yellow
git --version | Out-Null
if ($LASTEXITCODE -eq 0) { Write-Host 'OK - Git found' -ForegroundColor Green } else { Write-Host 'ERROR: Git not found' -ForegroundColor Red; exit 1 }

Write-Host "
Step 2: Verifying Netlify files..." -ForegroundColor Yellow
if (Test-Path 'netlify.toml') { Write-Host 'OK - netlify.toml exists' -ForegroundColor Green } else { Write-Host 'ERROR: netlify.toml not found' -ForegroundColor Red; exit 1 }

Write-Host "
Step 3: Initializing Git repository..." -ForegroundColor Yellow
git init
Write-Host 'OK - Git initialized' -ForegroundColor Green

Write-Host "
Step 4: Next Steps Required:" -ForegroundColor Yellow
Write-Host '1. Create repository on GitHub: https://github.com/new' -ForegroundColor Cyan
Write-Host '2. Connect to Netlify: https://app.netlify.com/signup' -ForegroundColor Cyan
Write-Host '3. Deploy with: git push origin main' -ForegroundColor Cyan

Write-Host "
========================================" -ForegroundColor Green
Write-Host 'SETUP COMPLETE - Ready for deployment!' -ForegroundColor Green
Write-Host "========================================
" -ForegroundColor Green
