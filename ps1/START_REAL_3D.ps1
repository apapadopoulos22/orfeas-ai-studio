# 
#   THERION QUICK START - REAL 3D GENERATION - SUCCESS!            
# 

Write-Host "`n" -ForegroundColor Cyan
Write-Host "  THERION QUICK START - ONE-COMMAND ACTIVATION                             " -ForegroundColor Cyan
Write-Host "`n" -ForegroundColor Cyan

Set-Location "C:\Users\johng\Documents\Erevus\orfeas"

Write-Host "âš¡ STEP 1: Verifying System Requirements`n" -ForegroundColor Yellow

# Check Python
$python = python --version 2>&1
Write-Host " $python" -ForegroundColor Green

# Check CUDA
$cuda = python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}, GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"N/A\"}')" 2>&1
Write-Host " $cuda" -ForegroundColor Green

Write-Host "`nâš¡ STEP 2: Testing Hunyuan3D Import (Quick Test)`n" -ForegroundColor Yellow

python -c "import sys; sys.path.append('Hunyuan3D-2.1/Hunyuan3D-2'); sys.path.append('Hunyuan3D-2.1/Hunyuan3D-2/hy3dgen'); from hy3dgen.rembg import BackgroundRemover; print(' Hunyuan3D modules can be imported')"

if ($LASTEXITCODE -ne 0) {
    Write-Host "`n Hunyuan3D import failed - trying full diagnostic...`n" -ForegroundColor Red
    python test_real_3d_generation.py
    exit 1
}

Write-Host "`nâš¡ STEP 3: Starting Backend with Real 3D Generation`n" -ForegroundColor Yellow

# Kill any existing Python processes
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue

Write-Host "" -ForegroundColor Green
Write-Host "â•'  BACKEND STARTING - REAL 3D GENERATION ACTIVE                         â•'" -ForegroundColor Green
Write-Host "`n" -ForegroundColor Green

Write-Host " WATCH FOR THESE LOG MESSAGES:" -ForegroundColor Cyan
Write-Host "   • 'Loading Hunyuan3D models...' - AI models initializing" -ForegroundColor Gray
Write-Host "   • ' Shape generation pipeline initialized' - Success!" -ForegroundColor Gray
Write-Host "   • 'Running on http://127.0.0.1:5000' - Server ready" -ForegroundColor Gray
Write-Host "`n`n" -ForegroundColor Cyan

Set-Location "backend"
python main.py
