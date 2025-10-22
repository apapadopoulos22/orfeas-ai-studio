# ORFEAS Hunyuan3D Full GPU Setup Guide

## Complete instructions to enable real AI 3D model generation

## [TARGET] OVERVIEW

This guide will help you set up the complete Hunyuan3D pipeline with GPU acceleration,
enabling real AI-powered 3D model generation instead of fallback placeholders.

##  PREREQUISITES

- Windows 10/11 with compatible NVIDIA GPU (GTX 1060+ or RTX series recommended)
- At least 8GB VRAM for optimal performance (6GB minimum)
- 16GB+ system RAM recommended
- 50GB+ free disk space for models and dependencies

## [CONFIG] STEP 1: CUDA TOOLKIT INSTALLATION

### 1.1 Check GPU Compatibility

```powershell

## Check your GPU

nvidia-smi

```text

### 1.2 Install CUDA Toolkit 12.1 or 11.8

### Option A: CUDA 12.1 (Recommended for RTX series)

1. Download from: https://developer.nvidia.com/cuda-12-1-0-download-archive

2. Select: Windows → x86_64 → 10/11 → exe (network)

3. Run installer with default settings

4. Verify installation:

```powershell
nvcc --version

```text

### Option B: CUDA 11.8 (Better compatibility)

1. Download from: https://developer.nvidia.com/cuda-11-8-0-download-archive

2. Follow same process as above

### 1.3 Add CUDA to PATH (if not automatic)

```powershell

## Add to System Environment Variables

## CUDA_PATH = C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.1

## PATH += %CUDA_PATH%\bin

## PATH += %CUDA_PATH%\libnvvp

```text

##  STEP 2: PYTORCH WITH CUDA SUPPORT

### 2.1 Uninstall CPU PyTorch

```powershell
cd "C:\Users\johng\ORFEAS_AI_LOCAL\backend"
pip uninstall torch torchvision torchaudio

```text

### 2.2 Install PyTorch with CUDA

### For CUDA 12.1

```powershell
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

```text

### For CUDA 11.8

```powershell
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

```text

### 2.3 Verify PyTorch CUDA Installation

```powershell
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}'); print(f'CUDA version: {torch.version.cuda}'); print(f'GPU count: {torch.cuda.device_count()}')"

```text

## [FAST] STEP 3: XFORMERS WITH CUDA SUPPORT

### 3.1 Uninstall Current xFormers

```powershell
pip uninstall xformers

```text

### 3.2 Install Compatible xFormers

### For CUDA 12.1

```powershell
pip install xformers --index-url https://download.pytorch.org/whl/cu121

```text

### For CUDA 11.8

```powershell
pip install xformers --index-url https://download.pytorch.org/whl/cu118

```text

### 3.3 Alternative: Build from Source (if pre-built fails)

```powershell

## This takes 30+ minutes but ensures compatibility

pip install ninja
pip install -v -U git+https://github.com/facebookresearch/xformers.git@main#egg=xformers

```text

##  STEP 4: HUNYUAN3D MODEL DOWNLOADS

### 4.1 Install Hugging Face Hub

```powershell
pip install huggingface-hub[cli]

```text

### 4.2 Login to Hugging Face (Required for Model Access)

```powershell

## Get free account at https://huggingface.co/join

## Get token at https://huggingface.co/settings/tokens

huggingface-cli login

```text

### 4.3 Download Hunyuan3D-2 Models

```powershell

## Main 3D generation model (~15GB)

huggingface-cli download tencent/Hunyuan3D-2 --local-dir "C:\Users\johng\ORFEAS_AI_LOCAL\models\Hunyuan3D-2"

## Text-to-image model (~5GB)

huggingface-cli download Tencent-Hunyuan/HunyuanDiT-Diffusers --local-dir "C:\Users\johng\ORFEAS_AI_LOCAL\models\HunyuanDiT-Diffusers"

```text

### 4.4 Verify Model Downloads

```powershell

## Check model files exist

dir "C:\Users\johng\ORFEAS_AI_LOCAL\models\Hunyuan3D-2"
dir "C:\Users\johng\ORFEAS_AI_LOCAL\models\HunyuanDiT-Diffusers"

```text

##  STEP 5: UPDATE ORFEAS CONFIGURATION

### 5.1 Update Model Paths in Integration

The system will automatically use local models if available, otherwise downloads from HuggingFace.

### 5.2 Test GPU Detection

```powershell
cd "C:\Users\johng\ORFEAS_AI_LOCAL\backend"
python -c "
import torch
print(f'PyTorch version: {torch.__version__}')
print(f'CUDA available: {torch.cuda.is_available()}')
print(f'CUDA version: {torch.version.cuda}')
if torch.cuda.is_available():
    print(f'GPU: {torch.cuda.get_device_name(0)}')
    print(f'GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f}GB')
"

```text

## [LAUNCH] STEP 6: RESTART ORFEAS WITH FULL AI

### 6.1 Stop Current Server

```powershell

## Press Ctrl+C in the terminal running the server

```text

### 6.2 Restart with GPU Support

```powershell
cd "C:\Users\johng\ORFEAS_AI_LOCAL\backend"
python integrated_server.py

```text

### 6.3 Verify AI Models Loading

Look for these messages in the console:

```text
[OK] GPU detected: [Your GPU Name]
[OK] Background remover initialized
[OK] Shape generation pipeline initialized
[OK] Texture generation pipeline initialized
[OK] Text-to-image pipeline initialized
[OK] All Hunyuan3D models initialized successfully

```text

## [LAB] STEP 7: TEST FULL AI PIPELINE

### 7.1 Access ORFEAS Studio

Open: http://localhost:5000/studio

### 7.2 Test Text-to-Image Generation

1. Enter prompt: "A beautiful red sports car"

2. Click "Generate Image"

3. Should see real AI generation (not placeholder)

### 7.3 Test Image-to-3D Generation

1. Upload or generate an image

2. Click "Generate 3D Model"

3. Should see real 3D mesh generation with textures

### 7.4 Check API Status

Open: http://localhost:5000/api/models-info
Should show:

```json
{
  "hunyuan3d": {
    "status": "loaded",
    "model_type": "Hunyuan3D-2.1",
    "has_text2image": true,
    "capabilities": ["image_to_3d", "text_to_image"]
  }
}

```text

## [WARN] TROUBLESHOOTING

### Issue: CUDA Out of Memory

### Solution

- Reduce batch size in model loading
- Close other GPU applications
- Use lower precision (float16 instead of float32)

### Issue: Model Download Fails

### Solution

```powershell

## Use git-lfs for large files

git lfs install
git clone https://huggingface.co/tencent/Hunyuan3D-2

```text

### Issue: xFormers Still Not Working

### Solution

```powershell

## Force reinstall with specific CUDA version

pip uninstall xformers torch torchvision torchaudio
pip install torch torchvision torchaudio xformers --index-url https://download.pytorch.org/whl/cu118

```text

### Issue: Import Errors

### Solution

```powershell

## Clear Python cache

python -c "import sys; import shutil; shutil.rmtree(sys.path[0] + '/__pycache__', ignore_errors=True)"

## Restart Python/server

```text

## [STATS] PERFORMANCE EXPECTATIONS

### With Full GPU Setup

- **Text-to-Image**: 10-30 seconds (512x512)
- **Image-to-3D**: 2-5 minutes (depends on complexity)
- **Background Removal**: 1-3 seconds
- **Memory Usage**: 6-12GB VRAM

### Current Fallback Mode

- **Text-to-Image**: Instant placeholder generation
- **Image-to-3D**: Instant simple geometry
- **Memory Usage**: <1GB RAM

##  SUCCESS INDICATORS

When everything is working correctly, you should see:

1. [OK] GPU detection in startup logs

2. [OK] All Hunyuan3D pipelines loaded

3. [OK] Real AI-generated images (not gradients)

4. [OK] Complex 3D meshes with textures (not simple cubes)
5. [OK] WebSocket progress updates during generation
6. [OK] Download links for GLB/OBJ files with textures

##  SUPPORT

If you encounter issues:

1. Check the console logs for specific error messages

2. Verify CUDA installation: `nvidia-smi` and `nvcc --version`

3. Test PyTorch CUDA: `python -c "import torch; print(torch.cuda.is_available())"`

4. Check model files exist in the expected directories
5. Ensure sufficient VRAM for model loading

The system is designed to gracefully fall back to CPU/placeholder mode if any component fails,
so you can always use the basic functionality while troubleshooting the full AI setup.
