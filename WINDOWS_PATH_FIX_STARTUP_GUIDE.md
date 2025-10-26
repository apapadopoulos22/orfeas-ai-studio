# ORFEAS AI - Windows Path Separator Fix & Startup Guide

## Problem Solved

**Issue:** Hunyuan3D model loading failed with "Model path not exists" error, triggering 15-30 GB downloads

- **Root Cause:** Mixed path separators (`C:\Users\johng/.cache/hy3dgen\tencent/Hunyuan3D-2`)
- **Impact:** 15-30 minute startup delays on every server restart
- **Status:** ✅ FIXED

---

## The Fix (3-Layer Solution)

### Layer 1: Environment Variables (.env file)

All paths now use **Windows backslashes only** - NO forward slashes:

```text
HOME=C:\Users\johng\Documents\oscar
HF_HOME=C:\Users\johng\Documents\oscar\models\.cache\huggingface
TRANSFORMERS_CACHE=C:\Users\johng\Documents\oscar\models\.cache\huggingface\transformers
HY3DGEN_CACHE=C:\Users\johng\Documents\oscar\models\.cache\huggingface\hy3dgen
HY3DGEN_MODELS=C:\Users\johng\Documents\oscar\models\.cache\huggingface\hub\models--tencent--Hunyuan3D-2
```

**Key:** `HY3DGEN_MODELS` points to the actual model hub directory where models are cached.

### Layer 2: Backend Initialization (main.py)

**Lines 31-46** set environment variables BEFORE imports:

```python
from dotenv import load_dotenv
load_dotenv()  # Load .env FIRST

# Set HOME before any hy3dgen imports
home_dir = os.getenv('HOME', os.path.expanduser('~'))
os.environ['HOME'] = home_dir

# Set HY3DGEN_MODELS BEFORE hy3dgen import (read at module import time!)
hy3dgen_models = os.getenv('HY3DGEN_MODELS')
if hy3dgen_models:
    os.environ['HY3DGEN_MODELS'] = hy3dgen_models
```

**Critical:** hy3dgen reads these variables at MODULE IMPORT TIME, not at runtime!

### Layer 3: Source Code Fixes (hy3dgen module)

**File 1:** `Hunyuan3D-2.1/Hunyuan3D-2/hy3dgen/shapegen/utils.py` (Lines 97-103)

```python
# OLD (BUGGY): Creates mixed separators like C:\Users\johng/.cache/hy3dgen\tencent/Hunyuan3D-2
base_dir = os.environ.get('HY3DGEN_MODELS', '~/.cache/hy3dgen')
model_path = os.path.expanduser(os.path.join(base_dir, model_path, subfolder))

# NEW (FIXED): Creates clean backslash paths like C:\Users\johng\Documents\oscar\models\.cache\...
home_dir = os.path.expanduser('~')
hy3dgen_default = os.path.join(home_dir, '.cache', 'hy3dgen')
base_dir = os.environ.get('HY3DGEN_MODELS', hy3dgen_default)
model_path_normalized = model_path.replace('/', os.sep)  # Convert / to \
subfolder_normalized = subfolder.replace('/', os.sep) if subfolder else ''
model_path = os.path.join(base_dir, model_path_normalized, subfolder_normalized)
```

**File 2:** `Hunyuan3D-2.1/Hunyuan3D-2/hy3dgen/texgen/pipelines.py` (Lines 57-65)

Same logic applied to texture generation module.

---

## How to Start the Server

### Option 1: Double-Click (Easiest)

Double-click `START_SERVER.bat` in the project root directory.

The batch file will:

1. ✅ Validate `.env` configuration
2. ✅ Check model cache directory
3. ✅ Clear Python `__pycache__` (forces fresh imports)
4. ✅ Stop any existing Python processes
5. ✅ Start the backend server

### Option 2: Command Line

```powershell
cd C:\Users\johng\Documents\oscar\backend
python main.py
```

### Option 3: From Project Root

```powershell
cd C:\Users\johng\Documents\oscar
python backend\main.py
```

---

## What to Expect

### First Startup (With Model Cache Already Downloaded)

```text
[ORFEAS] Dual logging initialized: console + logs/backend_requests.log
[ORFEAS] File rotation: 10MB per file, 5 backups (50MB total)
...
Try to load model from local path: C:\Users\johng\.cache\hy3dgen\tencent\Hunyuan3D-2\hunyuan3d-dit-v2-0
Loading model from C:\Users\johng\.cache\huggingface\hub\models--tencent--Hunyuan3D-2\...
[SUCCESS] ✅ Hunyuan3D model FULLY LOADED and ready

Server running on http://127.0.0.1:5000
```

**Duration:** ~20-40 seconds (model loading from cache)

### First Startup (Model Cache Not Present)

```text
Try to load model from local path: C:\Users\johng\.cache\hy3dgen\tencent\Hunyuan3D-2\hunyuan3d-dit-v2-0
Model path not exists, try to download from huggingface
Fetching 6 files: 100%|███████████████| 6/6 [10:45<00:00, ...]
Loading model from C:\Users\johng\.cache\huggingface\hub\models--tencent--Hunyuan3D-2\...
```

**Duration:** ~15-30 minutes (first time model download + initialization)

---

## Verification Checklist

After starting the server, verify everything works:

- [ ] Backend started without "Model path not exists" errors
- [ ] Model loading shows path with ALL backslashes (no mixed separators)
- [ ] "[SUCCESS] Hunyuan3D model FULLY LOADED" message appears
- [ ] Server listening on `http://127.0.0.1:5000`
- [ ] No CUDA or GPU errors in logs
- [ ] Model load time under 1 minute (indicates cache hit)

---

## Troubleshooting

### Problem: "Model path not exists" Error

**Cause:** Environment variables not being set properly

**Solution:**

1. Verify `.env` file exists in project root
2. Check `.env` has `HY3DGEN_MODELS` line (should NOT be commented out)
3. Use `START_SERVER.bat` which automatically validates `.env`
4. Run: `python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('HY3DGEN_MODELS:', os.environ.get('HY3DGEN_MODELS'))"`

### Problem: Mixed Path Separators in Logs

**Example:** `C:\Users\johng/.cache/hy3dgen\tencent/Hunyuan3D-2`

**Cause:** hy3dgen using hardcoded path logic

**Solution:**

1. Verify you have the latest `hy3dgen/shapegen/utils.py` with the fix
2. Verify you have the latest `hy3dgen/texgen/pipelines.py` with the fix
3. Clear Python cache: `START_SERVER.bat` does this automatically
4. Restart backend

### Problem: Slow Startup (15-30 minutes)

**Cause:** Models being downloaded instead of loaded from cache

**Solution:**

1. Check if cache directory exists: `C:\Users\johng\Documents\oscar\models\.cache\huggingface\hub\models--tencent--Hunyuan3D-2`
2. If missing, first startup will download models (normal for first run)
3. Subsequent startups will be 20-40 seconds (cached)

### Problem: Python Process Hangs

**Solution:** `START_SERVER.bat` automatically kills old Python processes before starting

Manual fix:

```powershell
taskkill /F /IM python.exe
```

---

## Performance Comparison

| Scenario | Before Fix | After Fix |
|----------|-----------|-----------|
| **First Startup** | N/A (crashed) | ~15-30 min (download) |
| **Subsequent Startups** | 15-30 min (re-download every time!) | 20-40 seconds (cache) |
| **Path Separators** | Mixed `/\` causing failures | All backslashes ✅ |
| **Model Load Success** | ❌ Failed | ✅ Success |

**Result:** 30-60x faster startup after first initialization!

---

## Key Files Modified

1. **`backend/main.py`** (Lines 31-46)
   - Loads `.env` and sets HOME/HY3DGEN_MODELS before imports

2. **`.env`** (Project root)
   - All paths use Windows backslashes only
   - `HY3DGEN_MODELS` points to correct cache directory

3. **`Hunyuan3D-2.1/Hunyuan3D-2/hy3dgen/shapegen/utils.py`** (Lines 97-103)
   - Fixed path joining to use `os.path.join()` properly
   - Normalizes forward slashes to backslashes

4. **`Hunyuan3D-2.1/Hunyuan3D-2/hy3dgen/texgen/pipelines.py`** (Lines 57-65)
   - Same fix as shapegen

5. **`START_SERVER.bat`** (Updated)
   - Validates `.env` configuration
   - Clears Python cache
   - Stops existing processes
   - Enhanced error messages

---

## Technical Deep Dive

### Why This Bug Existed

The hy3dgen module used literal forward slashes in path strings:

```python
# This creates a problem on Windows!
default_path = '~/.cache/hy3dgen'  # Literal string with forward slashes
expanded = os.path.expanduser(default_path)
# Result: C:\Users\johng/.cache/hy3dgen (MIXED SEPARATORS!)

# Windows filesystem rejects mixed separators
os.path.exists(path)  # Returns False even if path exists!
```

### Why the Fix Works

```python
# Use os.path.join() which handles platform-specific separators
home = os.path.expanduser('~')  # C:\Users\johng
path = os.path.join(home, '.cache', 'hy3dgen')
# Result: C:\Users\johng\.cache\hy3dgen (ALL BACKSLASHES!)

os.path.exists(path)  # Returns True!
```

### Environment Variable Import Timing

**Critical Issue:** hy3dgen reads environment variables at **MODULE IMPORT TIME**:

```python
# In hy3dgen/__init__.py (approximate)
base_dir = os.environ.get('HY3DGEN_MODELS', default)  # Read at import time!
```

**Solution:** Set environment variables BEFORE importing hy3dgen:

```python
# backend/main.py
load_dotenv()  # Load .env
os.environ['HY3DGEN_MODELS'] = value  # Set variable

from hunyuan_integration import ...  # Import (reads the variable)
```

---

## Support

If issues persist:

1. Check logs: `backend/logs/backend_requests.log`
2. Verify Python version: `python --version` (should be 3.10+)
3. Verify CUDA available: `python -c "import torch; print(torch.cuda.is_available())"`
4. Clear all cache and restart: Run `START_SERVER.bat`
