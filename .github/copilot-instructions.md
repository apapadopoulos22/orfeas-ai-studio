# ORFEAS AI 2D→3D STUDIO - GitHub Copilot Instructions

**Project:** Enterprise AI multimedia platform for 2D→3D model generation
**Stack:** Python 3.10+/Flask/PyTorch + Next.js 15/TypeScript + Docker GPU (RTX 3090)
**Quality:** 92% Grade A | ISO 9001/27001 | 464 tests | 50K+ LOC

## Quick Architecture Map

```text
Frontend (orfeas-ai-studio.html + Next.js)
  ├─ Three.js 3D viewer (THREE.r128 for stable legacy support)
  ├─ Socket.IO client (real-time progress updates)
  └─ WebGL canvas with orbit controls

Backend (Flask + PyTorch)
  ├─ main.py (7279 lines) - Core server, routes, WebSocket init
  ├─ hunyuan_integration.py - 3D model inference with lazy loading
  ├─ gpu_manager.py - VRAM tracking & device selection
  ├─ websocket_manager.py - Connection pool & job room messaging
  ├─ progress_tracker.py - Job tracking with weighted stages & ETA
  └─ stl_processor.py - Mesh export, repair & validation

WebSocket (Socket.IO)
  ├─ subscribe_to_job - Client joins job room
  ├─ generation_progress - Progress events streamed per stage
  ├─ generation_complete/error - Final result notifications
  └─ heartbeat - Connection keep-alive with ping/pong
```

## CRITICAL PATTERNS (Must Read First)

### Pattern 1: Environment Initialization (lines 1-50 in `backend/main.py`)

**Critical ordering issue**: Settings are read at **import time**, not runtime. Wrong order causes cryptic startup failures.

```python
# FIRST: Set env vars BEFORE any heavy imports
import os
os.environ['ORT_TENSORRT_UNAVAILABLE'] = '1'      # Prevent ONNX crash (Error E)
os.environ['XFORMERS_DISABLED'] = '1'              # Prevent Windows DLL 0xc0000139
os.environ['HOME'] = os.path.expanduser('~')       # Windows path for hy3dgen
os.environ['CUDA_MODULE_LOADING'] = 'LAZY'         # Don't load all CUDA at once

# SECOND: Load .env file (can override above)
from dotenv import load_dotenv
load_dotenv()

# THIRD: Import torch and model libraries
import torch
from hunyuan_integration import get_3d_processor
```

Why? `hy3dgen` module reads `HY3DGEN_MODELS` at import time. `xformers` loads at import time. Reordering breaks everything.

### Pattern 2: Lazy Model Loading (30s → 3s startup)

**Discovery insight**: The system doesn't load 3D models on startup. It uses a thread-safe cache pattern.

```python
# backend/hunyuan_integration.py (lines 48-150)
class Hunyuan3DProcessor:
    _model_cache = {"initialized": False, "shapegen_pipeline": None}
    _lock = threading.Lock()

    @classmethod
    def generate_3d(cls, image_path, output_path, **kwargs):
        # Load models ONLY on first call, not startup
        if not cls._model_cache["initialized"]:
            with cls._lock:  # Thread-safe singleton pattern
                if not cls._model_cache["initialized"]:
                    cls._load_from_cache()  # ~30s
        # Subsequent calls use cached models
        return cls._process(image_path, output_path)
```

**Impact**: Startup is now ~3s (instant dev feedback). First image takes ~35s. Subsequent images ~5s.

### Pattern 3: GPU Memory Management (24GB RTX 3090)

**Discovery**: Hunyuan3D-2.1 requires aggressive VRAM management. The system checks VRAM before each job.

```python
# backend/gpu_manager.py (lines ~100-150)
from gpu_manager import get_gpu_manager

gpu_mgr = get_gpu_manager()

try:
    # Check VRAM BEFORE job starts (not during)
    required_vram_mb = 6000  # Empirically measured
    if not gpu_mgr.can_process_job(estimated_vram=required_vram_mb):
        return jsonify({"error": "Insufficient VRAM"}), 503

    result = processor.generate_3d(image_path, output_path)

finally:
    # CRITICAL: Always cleanup, even on error
    torch.cuda.empty_cache()
    logger.info(f"GPU memory freed. Current: {gpu_mgr.get_current_vram()}MB")
```

**Key pattern**: Pre-check → Execute → Cleanup. No try-catch errors because GPU can be reused immediately after cleanup.

### Pattern 4: WebSocket Real-Time Progress (7 Stages)

**Discovery**: System tracks progress through 7 weighted stages. Each stage has estimated duration.

```python
# backend/progress_tracker.py (lines ~50-150)
tracker = ProgressTracker(job_id)
stages = {
    'image_loading': {'weight': 0.01, 'estimated_secs': 0.5},
    'shape_generation': {'weight': 0.70, 'estimated_secs': 30},  # Bottleneck
    'texture_synthesis': {'weight': 0.20, 'estimated_secs': 8},
    'mesh_export': {'weight': 0.05, 'estimated_secs': 2},
    # ... 3 more internal stages
}

# Weighted progress: if at 50% of shape_generation:
# overall_progress = 0.01 (loaded) + 0.70 * 0.5 (halfway through big stage) = 36%
tracker.start_stage('shape_generation', weight=0.70)
tracker.update_stage_progress('shape_generation', 50)  # 50% through this stage
```

**Frontend integration**: Client subscribes to job, receives realtime updates:

```typescript
// frontend-nextjs/src/hooks/useSocket.ts (lines ~30-60)
const socket = io(BACKEND_URL);

socket.emit('subscribe_to_job', {job_id: currentJobId});

socket.on('generation_progress', (data) => {
    // {progress: 36, stage: 'shape_generation', stage_progress: 50, eta_seconds: 28}
    setProgress(data.progress);           // Overall 0-100%
    setCurrentStage(data.stage);
    setEta(data.eta_seconds);              // Calculated from historical samples
});

socket.on('generation_complete', (data) => {
    if (data.success) {
        downloadModel(data.result.output_path);
    }
});
```

### Pattern 5: Error Handling & Graceful Fallback

**Discovery**: All GPU operations have CPU fallback. This keeps system alive even when GPU fails.

```python
# backend/hunyuan_integration.py (lines ~491-600)
try:
    processor = get_3d_processor()  # GPU-based
    result = processor.generate_3d(image_path, output_path)

except OutOfMemoryError:
    logger.warning(f"GPU OOM, trying fallback processor")
    fallback = FallbackProcessor()  # CPU-based, ~5x slower
    result = fallback.generate_3d(image_path, output_path)

except Exception as e:
    logger.error(f"Generation failed: {e}")
    # Return error to client - frontend shows retry UI
    raise
```

**Key**: Fallback produces valid (but lower quality) output. Never leave client hanging.

## Core Module Discovery Map

| Module | Lines | Purpose | Key Discovery |
|--------|-------|---------|---|
| **main.py** | 7279 | Flask server, routes, WebSocket | Env initialization lines 1-50. Routes use `/api/generate-3d` pattern. SocketIO initialized after Flask. |
| **hunyuan_integration.py** | 886 | 3D inference, model caching | Thread-safe singleton pattern. Two classes: `Hunyuan3DProcessor` (GPU) + `FallbackProcessor` (CPU). Load models on first call, not startup. |
| **gpu_manager.py** | 566 | VRAM tracking, device selection | Singleton instance. Pre-checks VRAM before jobs. Always call `torch.cuda.empty_cache()` after generation in finally block. |
| **websocket_manager.py** | 350+ | Connection pool, room messaging | Manages job rooms. Clients subscribe with `subscribe_to_job`, emit events to specific job_ids. Thread-safe room/client tracking. |
| **progress_tracker.py** | 400+ | Job lifecycle, ETA calculation | Weighted stages (7 total). Stores last 100 samples per stage for accurate ETA. Calculates: overall_progress = Σ(completed_stages) + (current_stage_weight × stage_progress). |
| **batch_processor.py** | — | Async job queue | Queue-based async processing. Use for jobs >10s. Polls job status separately. |
| **validation.py** | — | 6-layer image validation | Pre-processes all uploads. Checks: size, format, dimensions, EXIF, encoding, safety. Returns sanitized image or error. |
| **stl_processor.py** | — | Mesh export, repair, validation | Handles STL binary encoding. Auto-repairs invalid meshes. Supports export to OBJ/GLB/PLY. |
| **prometheus_metrics.py** | 800+ | Metrics collection | Tracks generation times, GPU usage, WebSocket events, quality scores. Enabled at startup if `ENABLE_MONITORING=true`. |

## API Endpoints (Discovery Map)

```text
GET    /health                System status + GPU info
GET    /ready                 Readiness check (models loaded?)
GET    /metrics               Prometheus metrics (enabled if ENABLE_MONITORING=true)
POST   /api/generate-3d       Image→3D generation (main endpoint, returns job_id, not result)
       Params: image_path, output_format (stl/obj/glb/ply), quality (1-10)
       Returns: {job_id, status, websocket_url}
POST   /api/upload-image      File upload (max 16MB, validates EXIF/encoding)
       Returns: {file_path, image_id, dimensions}
POST   /api/batch-process     Batch operations (queues >10 jobs)
GET    /api/job-status/<id>   Poll job progress (alternative to WebSocket)
GET    /api/download/<id>     Download result as binary
WS     /socket.io             WebSocket events:
        - subscribe_to_job: Join job room
        - generation_progress: Real-time updates
        - generation_complete: Job finished
        - generation_error: Failure notification
```

## Frontend Structure (Next.js 15)

```text
src/
├── app/
│   ├── page.tsx              Main UI
│   ├── api/
│   │   ├── generate-3d/      Backend proxy for 3D generation
│   │   ├── upload-image/     File upload proxy
│   │   └── health/           Health check proxy
│   └── diagnostics/          System diagnostics page
├── components/
│   ├── ImageUploader.tsx     Upload + preview
│   ├── ModelViewer3D.tsx     Three.js 3D viewer
│   ├── WebSocketDiagnostics.tsx  Connection status
│   └── DownloadManager.tsx   STL/OBJ downloads
└── hooks/
    └── useSocket.ts          Socket.IO wrapper
```

**Key dependency:** `socket.io-client` for real-time updates

## HTML Frontend (`orfeas-ai-studio.html`)

**Discovery**: Monolithic 3000+ line HTML file with embedded Three.js, CSS, and JavaScript.
Used for quick prototyping and demo purposes.

```html
<!-- Key sections -->
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/build/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/STLLoader.js"></script>

<!-- 3D Studio Section (3Dstudio id) -->
<section id="3Dstudio" class="section">
  <div class="studio-workspace">
    <!-- Left Panel: Controls (350px) -->
    <!-- Main Area: Upload, Preview, 3D Viewer -->
  </div>
</section>

<!-- Image Processing Section (image id) -->
<section id="image" class="section">
  <!-- Text-to-Image, Filters, Export -->
</section>

<!-- 2.5D Studio Section (2.5Dstudio id) -->
<section id="2.5Dstudio" class="section">
  <!-- Laser design, Vector conversion -->
</section>
```

**Pattern**: Use `showSection('sectionId')` to navigate. Sections have `display: none` by
default, activated with `display: block`.

## Environment Variables (Critical)

```bash
# GPU & Model (MUST be set BEFORE imports)
DEVICE=cuda
XFORMERS_DISABLED=1              # Windows DLL crash prevention
ORT_TENSORRT_UNAVAILABLE=1       # ONNX Runtime fallback
GPU_MEMORY_LIMIT=0.8             # Safety margin on 24GB
HY3DGEN_MODELS=/path/to/models   # Hunyuan3D model directory

# Server
FLASK_ENV=production
CORS_ORIGINS=*                   # Update for production
LOCAL_LLM_ENABLED=true
LOCAL_LLM_ENDPOINT=http://localhost:11434
LOCAL_LLM_MODEL=mistral

# Monitoring
LOG_LEVEL=INFO
ENABLE_MONITORING=true
```

## Development Workflow

```powershell
# Start backend with local LLM (assumes Ollama running)
cd backend
python main.py                   # Starts on http://localhost:5000

# In another terminal: Start frontend
cd frontend-nextjs
npm run dev                      # http://localhost:3000

# Run tests
pytest backend/tests/ -m unit -v
pytest backend/tests/ -m integration -v

# Check health
curl http://localhost:5000/health

# WebSocket progress test
python test_websocket_progress.py --with-generation
```

**Key pattern**: Backend initialization order is CRITICAL. If tests fail with import errors,
check environment variables are set BEFORE module imports (lines 1-50 of main.py).

## Common Issues & Solutions

| Issue | Root Cause | Fix | File |
|-------|------------|-----|------|
| `xformers DLL error (0xc0000139)` | xformers imports before env vars set | Move env vars to line 1 in main.py | `backend/main.py:1-50` |
| Startup hangs 50s | Models load at startup | Already fixed: lazy loading on first request | `backend/hunyuan_integration.py:48-150` |
| CUDA OOM mid-generation | Memory not cleaned properly | Add `torch.cuda.empty_cache()` in finally block | `backend/main.py` (generation route) |
| WebSocket timeout | Client disconnects before progress arrives | Increase timeout or check heartbeat events | `frontend-nextjs/src/hooks/useSocket.ts` |
| STL export corrupted | String encoding issue during binary write | Use `stl_processor.py` with proper encoding | `backend/stl_processor.py` |
| Model path not found | Windows backslash/forward slash mismatch | Ensure `HOME` env var set correctly | `backend/main.py:34-37` |
| GPU device not found | CUDA not available or wrong device ID | Check `DEVICE=cuda` env var, fallback to CPU | `backend/gpu_manager.py` |
| Progress events missing | Client not subscribed to job room | Emit `subscribe_to_job` before generation | `frontend-nextjs/src/hooks/useSocket.ts` |

## Testing & Validation

```bash
# Unit tests (fast, no GPU)
pytest backend/tests/unit/ -v

# Integration tests (real generation, needs GPU)
pytest backend/tests/integration/ -v

# Performance validation
python backend/run_production_benchmarks.py

# Load testing
locust -f backend/load/locustfile.py --host http://localhost:5000

# WebSocket test
python backend/test_websocket_progress.py --with-generation
```

## Advanced: Progressive Rendering (4-6x speedup)

Returns results in 3 stages instead of waiting for final quality:

```python
from progressive_renderer import get_progressive_renderer
renderer = get_progressive_renderer()
# Stage 1: Wireframe (0.5s)   - Instant visual feedback
# Stage 2: Base mesh (15s)    - Rough geometry
# Stage 3: Final (60s)        - Production quality
```

Files: `backend/progressive_renderer.py`, `backend/intelligent_cache.py`

## Deployment

```bash
# Docker GPU stack (production-ready)
docker-compose -f docker-compose.production.yml up -d

# Health check
curl https://your-domain/api/health

# View logs
docker-compose logs -f backend
```

See `PRODUCTION_DEPLOYMENT_GUIDE.md` for full deployment checklist.

---

**Last Updated:** October 27, 2025
**Reference:** Full docs in `.github/copilot-instructions-full.md`

## Discovery-Based Insights (What Makes This Project Unique)

### 1. Async-Without-Queues Pattern

Unlike typical async systems, this project doesn't use Redis queues heavily. Instead:

- **Job tracking** happens in memory via `progress_tracker.py` with JSON serialization
- **WebSocket rooms** manage subscriptions per job_id (Socket.IO room feature)
- **ETA calculation** uses last 100 samples per stage (not ML-based forecasting)

**When to use**: For projects <50 concurrent jobs. Scales to ~500 with memory optimization.

### 2. Lazy Loading Over Preloading

The codebase intentionally delays model loading:

- Startup: ~3s (only Flask init)
- First request: +30s (model load)
- Subsequent requests: <5s

**Why**: Developers get instant feedback. Production doesn't waste VRAM on unused models.

### 3. Thread-Safe Singletons Everywhere

All major services use thread-safe singleton patterns:

- `Hunyuan3DProcessor._model_cache`
- `get_gpu_manager()` returns singleton
- `get_3d_processor()` returns singleton with lock

**Discovery**: When modifying these, always check the `_lock` pattern (threading.Lock).

### 4. WebSocket Rooms = Lightweight Subscriptions

Instead of database-backed job tracking:

- Client emits `subscribe_to_job` with job_id
- Server adds client to Socket.IO room named after job_id
- Backend emits to room: `socketio.emit('event', data, room=job_id)`
- Only subscribers receive updates (not global broadcast)

**Impact**: Scales to thousands of concurrent jobs without DB queries.

### 5. Graceful Degradation is Mandatory

Every GPU operation has CPU fallback:

- GPU unavailable → Use `FallbackProcessor` (CPU-based)
- VRAM insufficient → Return 503, don't crash
- Model not loaded → Load on first request, not startup

**Pattern**: Try GPU path, catch specific exceptions, fallback gracefully.

### 6. Progress is Weighted, Not Sequential

The 7-stage pipeline uses weighted percentages:

- Image loading: 1% weight (0.5s estimated)
- Shape generation: 70% weight (30s estimated) ← main bottleneck
- Texture synthesis: 20% weight (8s estimated)
- Other stages: remaining %

**Discovery**: Progress is NOT linear. 30 seconds into shape_generation ≠ 50% done overall.
