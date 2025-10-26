# ORFEAS TensorRT + Model Path Error - Quick Fix

## Error You're Seeing

```
EP Error E:\_work\1\s\onnxruntime\python\onnxruntime_pybind_state.cc:559
onnxruntime::python::RegisterTensorRTPluginsAsCustomOps
Please install TensorRT libraries...
Falling back to ['CPUExecutionProvider']

Model path not exists, try to download from huggingface
```

## Root Cause Analysis

This is a **2-part error**:

1. **ONNX Runtime Error E** - TensorRT not available (normal, expected fallback)
2. **Model Path Not Found** - Windows path separator issue

## The Fix

### Step 1: Verify Environment Variables

Check your `.env` file in the `backend/` directory:

```bash
# CRITICAL - Must be set
HOME=C:\Users\johng
HY3DGEN_MODELS=C:\Users\johng\Documents\oscar\Hunyuan3D-2.1\Hunyuan3D-2\hy3dgen\models
DEVICE=cuda
XFORMERS_DISABLED=1
ORT_TENSORRT_UNAVAILABLE=1
```

**Important**: Use **backslashes only** (C:\...), never mixed (C:/...)

### Step 2: Verify Model Directory Exists

Open PowerShell and check:

```powershell
# Check if model directory exists
Test-Path "C:\Users\johng\Documents\oscar\Hunyuan3D-2.1\Hunyuan3D-2\hy3dgen\models"

# List what's inside
Get-ChildItem "C:\Users\johng\Documents\oscar\Hunyuan3D-2.1\Hunyuan3D-2\hy3dgen\models"

# Should contain subdirectories like: shapegen, texgen, etc.
```

### Step 3: Check main.py Initialization Order

In `backend/main.py`, verify these lines appear BEFORE all imports:

```python
import os
import sys

# MUST be set BEFORE any torch/hy3dgen imports
os.environ['ORT_TENSORRT_UNAVAILABLE'] = '1'
os.environ['XFORMERS_DISABLED'] = '1'

# Set HOME for Windows path fix
home_dir = os.getenv('HOME', os.path.expanduser('~'))
os.environ['HOME'] = home_dir

# Set HY3DGEN_MODELS BEFORE hy3dgen import
hy3dgen_models = os.getenv('HY3DGEN_MODELS')
if hy3dgen_models:
    os.environ['HY3DGEN_MODELS'] = hy3dgen_models

# THEN load dotenv
from dotenv import load_dotenv
load_dotenv()

# THEN import torch and other heavy libraries
import torch
from hunyuan_integration import get_3d_processor
```

### Step 4: Clear Python Cache

Sometimes cached modules cause issues:

```powershell
# Kill all Python processes
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force

# Clear Python cache
Get-ChildItem -Path "C:\Users\johng\Documents\oscar\Hunyuan3D-2.1" `
  -Filter "__pycache__" -Recurse -Force | `
  Remove-Item -Recurse -Force -ErrorAction SilentlyContinue

# Wait for processes to fully stop
Start-Sleep -Seconds 2
```

### Step 5: Start Backend

```powershell
cd C:\Users\johng\Documents\oscar\backend
python main.py
```

**Expected Output:**

```
[OK] GPU Manager initialized: NVIDIA GeForce RTX 3090
[OK] Hunyuan3D loaded from cache
```

**NOT expected:**

- Hanging (>10s)
- TensorRT error without fallback message
- Model path error

## Why This Happens

On Windows, Python's environment variable initialization and path handling are fragile:

1. **ONNX Runtime** tries TensorRT first (not available) → Error E → Falls back to CPU (OK)
2. **hy3dgen** reads `HY3DGEN_MODELS` at import time, not at runtime
3. **Path separators** get mixed (/ vs \) during import resolution
4. **HOME directory** must resolve correctly for ~/.cache paths

The **initialization order matters because:**

- If you set env vars AFTER importing hy3dgen, it uses old values
- If HOME is not set, Windows can't resolve home directory paths
- Mixed path separators cause "not found" errors even if file exists

## Verification Checklist

- [ ] `.env` file has proper Windows paths (backslashes only)
- [ ] Model directory exists: `HY3DGEN_MODELS/shapegen`, `HY3DGEN_MODELS/texgen`
- [ ] `main.py` sets env vars BEFORE any torch/hy3dgen imports
- [ ] Python cache cleared (`__pycache__` removed)
- [ ] No Python processes left running
- [ ] Backend starts without hanging (>10s indicates stuck on model loading)

## If Still Not Working

1. Run diagnostic command:

```powershell
cd backend
python -c "
import os
print('HOME:', os.environ.get('HOME'))
print('HY3DGEN_MODELS:', os.environ.get('HY3DGEN_MODELS'))
print('ORT_TENSORRT_UNAVAILABLE:', os.environ.get('ORT_TENSORRT_UNAVAILABLE'))
print('XFORMERS_DISABLED:', os.environ.get('XFORMERS_DISABLED'))
"
```

2. Check if paths are valid:

```powershell
$home = $env:HOME
$models = $env:HY3DGEN_MODELS
Write-Host "HOME exists: $(Test-Path $home)"
Write-Host "Models exist: $(Test-Path $models)"
Write-Host "ShapeGen exists: $(Test-Path $models/shapegen)"
Write-Host "TexGen exists: $(Test-Path $models/texgen)"
```

3. Run with debug logging:

```powershell
$env:LOG_LEVEL="DEBUG"
python main.py 2>&1 | Select-String "model|Model|MODEL|path|Path|PATH" | head -20
```

## Reference

For more details, see:

- `.github/copilot-instructions.md` - Section "Environment Initialization (MUST be first)"
- `backend/main.py` - Lines 1-50 (critical setup)
- `backend/hunyuan_integration.py` - Lazy model loading pattern
