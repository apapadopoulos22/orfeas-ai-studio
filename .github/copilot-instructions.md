# ORFEAS AI 2D3D STUDIO - GitHub Copilot Instructions

**Project:** Enterprise AI multimedia platform for 2D3D generation

**Stack:** Python 3.10+/Flask/PyTorch + Next.js + Docker GPU (RTX 3090)

**Quality:** 92% Grade A (ISO 9001/27001, 464 tests, 50K+ LOC)

## Architecture Overview

ORFEAS uses a 3-layer service architecture:

```
Frontend (HTML5/Next.js) -> REST + WebSocket
Backend (Flask + SocketIO + PyTorch)
  - Hunyuan3D-2.1 (3D generation)
  - GPU Manager (VRAM allocation)
  - Progress Tracker (real-time updates)
  - LLM Router (local + cloud)
Hunyuan3D Model (submodule)
  - ShapeGen (mesh generation)
  - TexGen (texture synthesis)
```

**Key Design Principle**: Defer model loading until first request (avoid startup crash).

## 5-MINUTE QUICKSTART

```powershell
cd backend
python main.py  # http://127.0.0.1:5000
```

## CRITICAL PATTERNS (MUST KNOW)

### 0. Environment Initialization (MUST be first, BEFORE any imports)

**This is the most critical pattern in the entire codebase.**

In `backend/main.py`, **before importing torch, hy3dgen, or any ML libraries**:

```python
import os
import sys
from pathlib import Path

# 1. Set BEFORE any imports to prevent ONNX Runtime crash
os.environ['ORT_TENSORRT_UNAVAILABLE'] = '1'

# 2. Set BEFORE any imports to prevent xformers Windows DLL error
os.environ['XFORMERS_DISABLED'] = '1'
os.environ['DISABLE_XFORMERS'] = '1'

# 3. Set BEFORE hy3dgen import (it reads at module load time)
hy3dgen_models = os.getenv('HY3DGEN_MODELS')
if hy3dgen_models:
    os.environ['HY3DGEN_MODELS'] = hy3dgen_models

# 4. Set HOME for Windows path resolution (critical on Windows)
home_dir = os.getenv('HOME', os.path.expanduser('~'))
os.environ['HOME'] = home_dir

# 5. THEN load .env and other settings
from dotenv import load_dotenv
load_dotenv()

# 6. THEN import heavy libraries
import torch
from hunyuan_integration import get_3d_processor
```

**Why this matters:**

- `ORT_TENSORRT_UNAVAILABLE=1` prevents ONNX Runtime from trying TensorRT (Error E)
- `XFORMERS_DISABLED=1` prevents Windows DLL crash during torch initialization
- `HY3DGEN_MODELS` must be set before hy3dgen module import (reads at import time)
- `HOME` must be set for proper ~/.cache resolution on Windows
- **Wrong order = startup failures that look unrelated**

### 1. Lazy Model Loading (prevents 50s startup delays)

Models load on first request, not at startup.

**In hunyuan_integration.py:**

- Hunyuan3DProcessor._model_cache - thread-safe singleton
- Cache initialized on first generate_3d() call via_load_from_cache()
- TORCH_AVAILABLE flag handles environments without GPU

**Critical init sequence in main.py:**

```python
os.environ['ORT_TENSORRT_UNAVAILABLE'] = '1'
os.environ['XFORMERS_DISABLED'] = '1'
os.environ['HY3DGEN_MODELS'] = model_path
home_dir = os.getenv('HOME', os.path.expanduser('~'))
os.environ['HOME'] = home_dir
```

### 2. GPU Memory Management (24GB RTX 3090)

Pattern: Try-finally with explicit cleanup.

```python
from gpu_manager import get_gpu_manager
gpu_mgr = get_gpu_manager()

try:
    if not gpu_mgr.can_process_job(estimated_vram=6000):
        raise ResourceError('Insufficient VRAM')
    result = processor.generate_3d(image)
finally:
    torch.cuda.empty_cache()  # ALWAYS cleanup
```

### 3. WebSocket Real-Time Progress (for 10s+ operations)

Flow: Client subscribes -> Progress events stream -> UI updates

Backend (main.py):

```python
from websocket_manager import initialize_websocket_manager
from progress_tracker import ProgressTracker

ws_manager = initialize_websocket_manager(socketio)
tracker = ProgressTracker(job_id, total_steps=100)

tracker.start_stage('shape_generation', weight=0.60)
tracker.update_stage_progress('shape_generation', 45)
tracker.complete_stage('shape_generation')
```

Frontend (JavaScript):

```javascript
const socket = io('http://localhost:5000');
socket.emit('subscribe_to_job', {job_id: 'xyz'});
socket.on('generation_progress', (data) => {
    updateProgressBar(data.progress);
    updateStage(data.stage);
    updateETA(data.eta_seconds);
});
```

### 4. Error Handling & Fallbacks

All GPU operations degrade gracefully.

```python
from hunyuan_integration import get_3d_processor, FallbackProcessor

try:
    processor = get_3d_processor()
    result = processor.generate_3d(image)
except Exception as e:
    logger.warning(f"Full generation failed: {e}, using fallback")
    fallback = FallbackProcessor()
    result = fallback.generate_shape(image)
```

## Key Files & Responsibilities

- main.py (6000+ lines) - Flask app, WebSocket init
- hunyuan_integration.py (886 lines) - 3D generation (lazy-loaded)
- gpu_manager.py (566 lines) - VRAM tracking, device selection
- websocket_manager.py (350+ lines) - Connection pool, room messaging
- progress_tracker.py (400+ lines) - Job tracking, ETA calculation
- batch_processor.py - Async job queue
- validation.py - 6-layer image validation

## Environment Variables (Critical)

DEVICE=cuda
XFORMERS_DISABLED=1
ORT_TENSORRT_UNAVAILABLE=1
GPU_MEMORY_LIMIT=0.8
HY3DGEN_MODELS=/path/to/models
HOME=/path/to/home
FLASK_ENV=production
CORS_ORIGINS=*
LOCAL_LLM_ENABLED=true
LOCAL_LLM_ENDPOINT=<http://localhost:11434>
LOCAL_LLM_MODEL=mistral
LOG_LEVEL=INFO
ENABLE_MONITORING=true

## Testing & Validation

```powershell
curl http://localhost:5000/health
pytest backend/tests/ -m unit -v
pytest backend/tests/ -m integration -v
python backend/test_websocket_progress.py --with-generation
locust -f load/locustfile.py --host http://localhost:5000
```

## Common Issues & Solutions

### TensorRT Error + Model Path Not Found

**Error Pattern:**

```
onnxruntime::python::RegisterTensorRTPluginsAsCustomOps
Please install TensorRT libraries...
Falling back to ['CPUExecutionProvider']
Model path not exists, try to download from huggingface
```

**Root Cause:** ONNX Runtime tries TensorRT first (unavailable on most systems),
then falls back to CPU. Model path resolution fails on Windows due to mixed
path separators (/ and \).

**Solution:**

1. Ensure `ORT_TENSORRT_UNAVAILABLE=1` is set BEFORE any imports
2. Ensure `HY3DGEN_MODELS` environment variable points to valid model directory
3. Ensure `HOME` is set to proper Windows path (backslashes only, no forward slashes)
4. Verify model files exist at `$HY3DGEN_MODELS/shapegen` and `$HY3DGEN_MODELS/texgen`

**Check in main.py (before any imports):**

```python
# These MUST be before: import torch, import hy3dgen, etc.
os.environ['ORT_TENSORRT_UNAVAILABLE'] = '1'
os.environ['XFORMERS_DISABLED'] = '1'
home_dir = os.getenv('HOME', os.path.expanduser('~'))
os.environ['HOME'] = home_dir
hy3dgen_models = os.getenv('HY3DGEN_MODELS')
if hy3dgen_models:
    os.environ['HY3DGEN_MODELS'] = hy3dgen_models
```

### Other Common Issues

- Startup hangs (50s) - Models load on first request
- CUDA OOM during generation - Use torch.cuda.empty_cache()
- xformers DLL crash - Set XFORMERS_DISABLED=1
- WebSocket timeout - Check /socket.io endpoint
- STL export corruption - Use stl_processor.py

## Development Workflow

1. Make changes in isolated backend module
2. Run unit tests: pytest backend/tests/unit/test_xyz.py -v
3. Test with real generation: python backend/test_xyz.py
4. Check WebSocket logs: docker-compose logs -f backend | grep WebSocket
5. Do not modify hunyuan_integration.py lightly

## Advanced: Progressive Rendering (4-6x speedup)

ORFEAS returns results in 3 progressive stages:

```python
from progressive_renderer import get_progressive_renderer
renderer = get_progressive_renderer()
# Stage 1: Low-quality mesh (0.5s)
# Stage 2: Medium-quality (15s)
# Stage 3: High-quality final (60s)
```

Files: backend/progressive_renderer.py, backend/intelligent_cache.py

## Documentation References

- Advanced Patterns: md/COPILOT_ADVANCED_PATTERNS.md
- Deployment: md/COPILOT_DEPLOYMENT_GUIDE.md
- LLM Integration: md/COPILOT_LLM_PATTERNS.md
- Full Instructions: .github/copilot-instructions-full.md

---

Last Updated: October 26, 2025
