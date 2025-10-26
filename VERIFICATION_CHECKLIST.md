# Quick Verification Checklist ✅

## 1. Verify the Fix Was Applied

```powershell
cd C:\Users\johng\Documents\oscar\backend

# Check first 50 lines of main.py
Get-Content main.py -TotalCount 50 | Select-String "ORT_TENSORRT_UNAVAILABLE"
```

**Should show**: Line containing `os.environ.setdefault('ORT_TENSORRT_UNAVAILABLE', '1')`
appearing **before** `import torch`

## 2. Verify Environment Variables Are Set

```powershell
# Check .env file exists
Test-Path ".\..\.env"

# View critical environment variables
$env:HOME
$env:HY3DGEN_MODELS
$env:ORT_TENSORRT_UNAVAILABLE
$env:XFORMERS_DISABLED

# Expected output:
# HOME: C:\Users\johng
# HY3DGEN_MODELS: C:\Users\johng\Documents\oscar\Hunyuan3D-2.1\Hunyuan3D-2\hy3dgen\models
# ORT_TENSORRT_UNAVAILABLE: 1
# XFORMERS_DISABLED: 1
```

## 3. Verify Model Directory Exists

```powershell
# Check Hunyuan3D models exist
Test-Path "C:\Users\johng\Documents\oscar\Hunyuan3D-2.1\Hunyuan3D-2\hy3dgen\models\shapegen"
Test-Path "C:\Users\johng\Documents\oscar\Hunyuan3D-2.1\Hunyuan3D-2\hy3dgen\models\texgen"

# Should return: True for both
```

## 4. Clear Python Cache (Important!)

```powershell
# Kill all Python processes
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force

# Wait a moment
Start-Sleep -Seconds 2

# Clear __pycache__ directories
Get-ChildItem -Path "C:\Users\johng\Documents\oscar\Hunyuan3D-2.1" `
  -Filter "__pycache__" -Recurse -Force | `
  Remove-Item -Recurse -Force -ErrorAction SilentlyContinue

Write-Host "Cache cleared"
```

## 5. Start Backend and Verify

```powershell
cd C:\Users\johng\Documents\oscar\backend

# Start backend
python main.py

# EXPECTED OUTPUT (first 30 seconds):
# [OK] GPU Manager initialized: NVIDIA GeForce RTX 3090
# [OK] SocketIO initialized (async_mode=threading)
# [ORFEAS] WebSocket Manager and Progress Tracker initialized
#  * Serving Flask app 'main'
#  * Debug mode: off
#  * Running on http://127.0.0.1:5000
```

## 6. Verify API Health

In another PowerShell window:

```powershell
# Test health endpoint
curl http://localhost:5000/health

# Should return: 200 OK with JSON response
```

## Troubleshooting: If Still Getting TensorRT Error

### Check 1: Environment Variables Order

```powershell
# View the critical section of main.py
Get-Content backend/main.py -TotalCount 60 | Select-Object -First 50 |
  Select-String "ORT_TENSORRT|XFORMERS|HOME|HY3DGEN|load_dotenv|import torch" -Context 1,1
```

Should show this order:

1. ORT_TENSORRT_UNAVAILABLE
2. XFORMERS_DISABLED
3. HOME
4. HY3DGEN_MODELS
5. load_dotenv()
6. import torch

### Check 2: Verify .env File Syntax

```powershell
# View .env file
Get-Content backend\.env | Select-String "HOME|HY3DGEN_MODELS|ORT_TENSORRT|XFORMERS"

# Should show:
# HOME=C:\Users\johng
# HY3DGEN_MODELS=C:\Users\johng\Documents\oscar\...
# ORT_TENSORRT_UNAVAILABLE=1
# XFORMERS_DISABLED=1
```

### Check 3: Run Diagnostic

```powershell
cd backend

python -c "
import os
print('Environment Variables Status:')
print('  ORT_TENSORRT_UNAVAILABLE:', os.environ.get('ORT_TENSORRT_UNAVAILABLE'))
print('  XFORMERS_DISABLED:', os.environ.get('XFORMERS_DISABLED'))
print('  HOME:', os.environ.get('HOME'))
print('  HY3DGEN_MODELS:', os.environ.get('HY3DGEN_MODELS'))
print()
print('Path Resolution:')
home = os.environ.get('HOME')
models = os.environ.get('HY3DGEN_MODELS')
print('  HOME exists:', os.path.exists(home) if home else 'NOT SET')
print('  Models exist:', os.path.exists(models) if models else 'NOT SET')
if models:
    print('  ShapeGen exists:', os.path.exists(os.path.join(models, 'shapegen')))
    print('  TexGen exists:', os.path.exists(os.path.join(models, 'texgen')))
"
```

## Success Indicators

✅ **Backend starts without hanging** (within 10 seconds)
✅ **No "Model path not exists" error**
✅ **TensorRT fallback message appears** (normal, expected)
✅ **Health endpoint responds** with 200 OK
✅ **GPU Manager initializes** successfully
✅ **WebSocket Manager initializes** successfully

## If Error Still Occurs

1. Share the exact error output
2. Run diagnostic check above and share results
3. Check that main.py lines 31-50 match the pattern shown in `MAIN_PY_FIX_APPLIED.md`
4. Verify .env file has proper Windows paths (backslashes only)

---

**The fix is complete and ready to test!** 🚀
