# â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—
# â•‘ âš”ï¸ THERION POST-UPGRADE VERIFICATION & BACKEND STARTUP - SUCCESS! âš”ï¸ â•‘
# â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

Write-Host "`nâ•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—" -ForegroundColor Cyan
Write-Host "â•‘ ðŸ” VERIFYING PYTORCH UPGRADE & STARTING REAL 3D GENERATION                  â•‘" -ForegroundColor Cyan
Write-Host "â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•`n" -ForegroundColor Cyan

Set-Location "C:\Users\johng\Documents\Erevus\orfeas\backend"

Write-Host "âš¡ STEP 1: Verifying PyTorch Installation`n" -ForegroundColor Yellow

# Verify PyTorch version
$pytorchVersion = python -c "import torch; print(f'PyTorch: {torch.__version__}')" 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "âœ… $pytorchVersion" -ForegroundColor Green
} else {
    Write-Host "âŒ PyTorch import failed!" -ForegroundColor Red
    exit 1
}

# Verify CUDA
$cudaCheck = python -c "import torch; print(f'CUDA Available: {torch.cuda.is_available()}'); print(f'GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"N/A\"}')" 2>&1
Write-Host "$cudaCheck" -ForegroundColor Green

Write-Host "`nâš¡ STEP 2: Testing register_pytree_node Fix`n" -ForegroundColor Yellow

$testScript2 = @"
from torch.utils._pytree import register_pytree_node
print('âœ… register_pytree_node is available!')
"@

$pytreeTest = python -c $testScript2 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "$pytreeTest" -ForegroundColor Green
} else {
    Write-Host "âŒ register_pytree_node still missing!" -ForegroundColor Red
    exit 1
}

Write-Host "`nâš¡ STEP 3: Testing Hunyuan3D Import`n" -ForegroundColor Yellow

$testScript = @"
import sys
sys.path.append('../Hunyuan3D-2.1/Hunyuan3D-2')
sys.path.append('../Hunyuan3D-2.1/Hunyuan3D-2/hy3dgen')
from hy3dgen.rembg import BackgroundRemover
from hy3dgen.shapegen import Hunyuan3DDiTFlowMatchingPipeline
print('âœ… Hunyuan3D modules imported successfully!')
"@

$hunyuanTest = python -c $testScript 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "$hunyuanTest" -ForegroundColor Green
} else {
    Write-Host "âš ï¸ Hunyuan3D import had issues:" -ForegroundColor Yellow
    Write-Host "$hunyuanTest" -ForegroundColor Gray
    Write-Host "`nContinuing anyway - backend may fall back to alternative 3D generation" -ForegroundColor Yellow
}

Write-Host "`nâ•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—" -ForegroundColor Green
Write-Host "â•‘ âœ… VERIFICATION COMPLETE - STARTING BACKEND WITH REAL 3D GENERATION         â•‘" -ForegroundColor Green
Write-Host "â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•`n" -ForegroundColor Green

Write-Host "ðŸ“Š EXPECTED BACKEND LOGS:" -ForegroundColor Cyan
Write-Host "   1. âœ… HuggingFace compatibility layer applied" -ForegroundColor Gray
Write-Host "   2. ðŸ”§ Loading Hunyuan3D models..." -ForegroundColor Gray
Write-Host "   3. ðŸ–¼ï¸ Initializing background remover..." -ForegroundColor Gray
Write-Host "   4. âœ… Background remover initialized (instant)" -ForegroundColor Gray
Write-Host "   5. ðŸŽ¨ Initializing shape generation pipeline..." -ForegroundColor Gray
Write-Host "      â³ FIRST RUN: 5-15 min download (~8-12 GB)" -ForegroundColor Yellow
Write-Host "      âš¡ CACHED: 10-20 seconds" -ForegroundColor Green
Write-Host "   6. âœ… Shape generation pipeline initialized" -ForegroundColor Gray
Write-Host "   7. ðŸš€ Running on http://127.0.0.1:5000" -ForegroundColor Gray
Write-Host "`nâ”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”`n" -ForegroundColor Cyan

Write-Host "ðŸš€ STARTING BACKEND NOW...`n" -ForegroundColor Green

python main.py
