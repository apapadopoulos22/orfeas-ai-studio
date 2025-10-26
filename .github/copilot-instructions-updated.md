# ORFEAS AI 2D→3D STUDIO - GitHub Copilot Instructions

**Project:** Enterprise AI multimedia platform (2D→3D generation, video composition, code development)
**Stack:** Python 3.10+/Flask/PyTorch + Next.js + Docker GPU (RTX 3090 CUDA 12.0)
**Quality:** 92% Grade A (ISO 9001/27001, 464 tests, 50K+ LOC, 750+ backend modules)

## Architecture Overview

ORFEAS uses a **3-layer service architecture**:

```
Frontend (HTML5/Next.js)
    ↓ REST + WebSocket
Backend (Flask + SocketIO + PyTorch)
    ├─ Hunyuan3D-2.1 (3D generation)
    ├─ GPU Manager (VRAM allocation)
    ├─ Progress Tracker (real-time updates)
    └─ LLM Router (local + cloud)
    ↓
Hunyuan3D Model (submodule)
    ├─ ShapeGen (mesh generation)
    └─ TexGen (texture synthesis)
```

**Key Design Principle**: Defer model loading until first request (avoid startup crash).

## 5-MINUTE QUICKSTART

```powershell
# Start backend (loads models on first request, ~10s)
cd backend
python main.py  # http://127.0.0.1:5000

# In another terminal, start frontend
python -m http.server 8000 -b 127.0.0.1

# Access at http://127.0.0.1:8000
```

## CRITICAL PATTERNS (MUST KNOW)

### 1. **Lazy Model Loading** (prevents 50s startup delays)

Models load on **first request**, not at startup. This requires understanding two flows:

**In `hunyuan_integration.py`:**

- `Hunyuan3DProcessor._model_cache` - thread-safe singleton (uses `threading.RLock()`)
- Cache initialized on first `generate_3d()` call via `_load_from_cache()`
- `TORCH_AVAILABLE` flag handles environments without GPU

**Critical init sequence in `main.py`:**

```python
# MUST be set BEFORE any torch/hy3dgen imports
os.environ['ORT_TENSORRT_UNAVAILABLE'] = '1'    # Prevent ONNX/TensorRT crash
os.environ['XFORMERS_DISABLED'] = '1'            # Prevent xformers DLL error
os.environ['HY3DGEN_MODELS'] = model_path        # Set BEFORE hy3dgen import
home_dir = os.getenv('HOME', os.path.expanduser('~'))
os.environ['HOME'] = home_dir                    # Windows path fix (backslashes)
```

### 2. **GPU Memory Management** (24GB RTX 3090)

**Pattern**: Try-finally with explicit cleanup.

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

**Key files**:

- `backend/gpu_manager.py` - Memory allocation tracker, device selection
- `backend/gpu_optimization_advanced.py` - Dynamic VRAM manager with precision modes
- Check `gpu_mgr.get_memory_stats()` for current usage

### 3. **WebSocket Real-Time Progress** (for 10s+ operations)

**Flow**: Client subscribes → Progress events stream → UI updates in real-time

**Backend side (`main.py` integration):**

```python
from websocket_manager import initialize_websocket_manager
from progress_tracker import ProgressTracker

ws_manager = initialize_websocket_manager(socketio)
tracker = ProgressTracker(job_id, total_steps=100)

# During generation (in hunyuan_integration.py):
tracker.start_stage('shape_generation', weight=0.60)
tracker.update_stage_progress('shape_generation', 45)  # Auto-emits via WebSocket
tracker.complete_stage('shape_generation')
```

**Frontend side (JavaScript):**

```javascript
const socket = io('http://localhost:5000');
socket.emit('subscribe_to_job', {job_id: 'xyz'});
socket.on('generation_progress', (data) => {
    updateProgressBar(data.progress);      // 0-100%
    updateStage(data.stage);               // Current stage
    updateETA(data.eta_seconds);           // ETA with historical learning
});
```

**Key files**:

- `backend/websocket_manager.py` - Connection pool + room-based messaging
- `backend/progress_tracker.py` - 5-stage pipeline, ETA calculation (85-95% accuracy)
- Stage weights calibrated from production profiling

### 4. **Error Handling & Fallbacks**

All GPU operations degrade gracefully:

```python
from hunyuan_integration import get_3d_processor, FallbackProcessor

try:
    processor = get_3d_processor()
    result = processor.generate_3d(image)
except Exception as e:
    logger.warning(f"Full generation failed: {e}, using fallback")
    fallback = FallbackProcessor()
    result = fallback.generate_shape(image)  # Lightweight MiDaS-based mesh
```

**Design**: Prefer "fail-safe with fallback" over strict validation. Users get results,
not errors.

## Key Files & Their Responsibilities

| File | Lines | Purpose | Dependencies |
|------|-------|---------|--------------|
| `main.py` | 6000+ | Flask app, WebSocket init, route handlers | All below |
| `hunyuan_integration.py` | 886 | 3D generation (lazy-loaded) | GPU, torch, hy3dgen |
| `gpu_manager.py` | 566 | VRAM tracking, device selection | torch, psutil |
| `websocket_manager.py` | 350+ | Connection pool, room messaging | SocketIO |
| `progress_tracker.py` | 400+ | Job tracking, ETA, stage weights | websocket_manager |
| `batch_processor.py` | ? | Async job queue | Threading |
| `validation.py`, `validation_enhanced.py` | ? | 6-layer image validation | Pillow, scipy |

## Environment Variables (Critical)

```bash
# GPU & Model Loading
DEVICE=cuda                              # "cuda" or "cpu"
XFORMERS_DISABLED=1                      # MUST be 1 (prevents DLL crash)
ORT_TENSORRT_UNAVAILABLE=1               # MUST be 1 (ONNX crash prevention)
GPU_MEMORY_LIMIT=0.8                     # 0.0-1.0 of total VRAM
HY3DGEN_MODELS=/path/to/models           # Set BEFORE import
HOME=/path/to/home                       # Windows path fix

# WebSocket
FLASK_ENV=production
CORS_ORIGINS=*

# LLM (Optional)
LOCAL_LLM_ENABLED=true
LOCAL_LLM_ENDPOINT=http://localhost:11434
LOCAL_LLM_MODEL=mistral

# Monitoring
LOG_LEVEL=INFO
ENABLE_MONITORING=true
```

## Testing & Validation

```powershell
# Quick health check
curl http://localhost:5000/health

# Run unit tests
pytest backend/tests/ -m unit -v

# Integration tests (with real GPU operations)
pytest backend/tests/ -m integration -v

# WebSocket real-time test
python backend/test_websocket_progress.py --with-generation

# Load testing
locust -f load/locustfile.py --host http://localhost:5000
```

## Common Issues & Solutions

| Problem | Root Cause | Solution |
|---------|-----------|----------|
| Startup hangs (50s) | Model loading at startup | Disabled in current code; models load on first request |
| "Model not found" on Windows | Path separator mismatch (/ vs \\) | Always use `os.environ['HOME']` and backslashes |
| CUDA OOM during generation | Insufficient cleanup | Ensure `torch.cuda.empty_cache()` in finally block |
| xformers DLL crash | Windows CUDA initialization issue | Set `XFORMERS_DISABLED=1` BEFORE torch import |
| WebSocket timeout | Client disconnected or no heartbeat | Check `/socket.io` endpoint, verify Port 5000 open |
| STL export corruption | Encoding issues on Windows | Use `stl_processor.py` with proper encoding handling |

## Development Workflow

1. **Make changes** in isolated backend module
2. **Run unit tests** on that module only: `pytest backend/tests/unit/test_xyz.py -v`
3. **Test with real generation** (if GPU-related): `python backend/test_xyz.py`
4. **Check WebSocket logs** if real-time: `docker-compose logs -f backend | grep WebSocket`
5. **Don't modify** `hunyuan_integration.py` lightly—test thoroughly (affects all 3D generation)

## Advanced: Progressive Rendering (4-6x speedup)

ORFEAS returns results in 3 progressive stages instead of waiting 60s:

```python
from progressive_renderer import get_progressive_renderer

renderer = get_progressive_renderer()
# Stage 1: Low-quality mesh (0.5s) - render immediately
# Stage 2: Medium-quality (15s) - update UI
# Stage 3: High-quality final (60s) - final result
```

Files: `backend/progressive_renderer.py`, `backend/intelligent_cache.py`

## Documentation References

- **Advanced Patterns**: `md/COPILOT_ADVANCED_PATTERNS.md` (thread-safe caching, orchestration)
- **Deployment**: `md/COPILOT_DEPLOYMENT_GUIDE.md` (Docker, K8s, production)
- **LLM Integration**: `md/COPILOT_LLM_PATTERNS.md` (multi-LLM routing)
- **Full Instructions**: `.github/copilot-instructions-full.md`

## Markdownlint Compliance

This repo enforces strict markdown formatting:

```powershell
# Check markdown
.\fix_markdown_lint.ps1 -Mode check

# Auto-fix
.\fix_markdown_lint.ps1 -Mode fix
```

**Rules**: Blank lines above/below headings, fenced code blocks with language tags,
<80 char lines, no trailing spaces.

---

**Last Updated**: October 26, 2025 | **Maintained By**: ORFEAS AI Team
