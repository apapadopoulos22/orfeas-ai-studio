# ORFEAS AI 2D→3D STUDIO - GitHub Copilot Instructions

**Project:** Enterprise AI multimedia platform for 2D→3D model generation
**Stack:** Python 3.10+/Flask/PyTorch + Next.js 15/TypeScript + Docker GPU (RTX 3090)
**Quality:** 92% Grade A | ISO 9001/27001 | 464 tests | 50K+ LOC
**Last Updated:** October 28, 2025

## Quick Start for Coding Agents

**Initial Setup:** Environment must be configured BEFORE starting any Python process.

```powershell
# Windows: Environment setup (CRITICAL - do this first!)
$env:DEVICE='cuda'
$env:XFORMERS_DISABLED='1'
$env:ORT_TENSORRT_UNAVAILABLE='1'
$env:HOME=$env:USERPROFILE
$env:CUDA_MODULE_LOADING='LAZY'

# Then start backend
cd backend
python main.py  # Starts on http://localhost:5000

# In another terminal: Start frontend
cd frontend-nextjs
npm run dev  # http://localhost:3000
```

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

## REASONING & DECISION FRAMEWORK (Explain Everything)

### Principle 1: Transparency in Problem-Solving

**When working on any task, explicitly explain**:

1. **What** you're doing (specific action)
2. **Why** you're doing it (technical reasoning)
3. **How** it solves the problem (root cause analysis)
4. **What** could go wrong (risk assessment)
5. **How** you'll verify success (validation strategy)

**Example template**:

```
TASK: Fix template expression syntax error on line 8574

ANALYSIS:
- Error: ${progre" (incomplete template variable)
- Why: Missing closing } and remaining property access
- Root cause: Developer typo during template literal editing
- Risk: This breaks the entire progress bar rendering

SOLUTION:
- Change ${progre" to ${progressData.progress}%
- Why: progressData object has progress property (0-100)
- Verification: Component should render progress bar dynamically

PREVENTION:
- Add automated template syntax checker
- Use IDE with template literal highlighting
```

### Principle 2: Root Cause Before Symptoms

**When debugging, always ask**:

- Is this the actual error or a symptom?
- What actually changed? (git diff)
- When did this start? (timeline)
- What assumptions am I making?
- What would contradict my hypothesis?

**Example**:

- Symptom: "showSection function undefined"
- Symptom cause: Function called before definition (execution order)
- Root cause: HTML body executes before <head> script loads
- Real fix: Move function to <head>, not just move it later in file

### Principle 3: Evidence-Based Decision Making

**For every decision, collect evidence**:

```python
# REASONING CHECKLIST
DECISION = "Should we use GPU or fallback to CPU?"

EVIDENCE FOR GPU:
✓ GPU available (nvidia-smi returns device)
✓ VRAM sufficient (24GB > 6GB required)
✓ Previous generation successful
✓ No thermal throttling warnings

EVIDENCE AGAINST GPU:
✗ CUDA out of memory error last job
✓ GPU memory not fully cleared (orphaned tensors)
✓ xformers library unstable on Windows

DECISION: Try GPU with pre-check, fall back to CPU on OOM
CONFIDENCE: 85% (evidence is mixed, but fallback is safe)
ACTION: Pre-check VRAM, execute, cleanup in finally block
MONITORING: Log GPU usage and fallback frequency
```

---

**Last Updated:** October 27, 2025
**Reference:** Full docs in `.github/copilot-instructions-full.md`

## MISTAKE LEARNING & ERROR RECOVERY (Learn from Problems)

### Error Pattern 1: Import-Time vs Runtime Configuration

**Mistake Learned**:

```python
# ❌ WRONG: This caused xformers DLL crash (Error: 0xc0000139)
import os
from dotenv import load_dotenv
load_dotenv()

import xformers  # CRASHES HERE - env vars not set!
```

**Why it failed**:

- `xformers` reads environment variables at import time
- By that time, `XFORMERS_DISABLED=1` was not yet set
- DLL collision with CUDA runtime

**Correct pattern** (lessons applied):

```python
# ✅ CORRECT: Set env vars BEFORE any imports
import os
os.environ['XFORMERS_DISABLED'] = '1'          # Set FIRST
os.environ['ORT_TENSORRT_UNAVAILABLE'] = '1'
os.environ['HOME'] = os.path.expanduser('~')

# NOW it's safe to import
from dotenv import load_dotenv
load_dotenv()  # Can override above if needed
import xformers  # Now safe - env var already set
```

**How to detect this pattern**:

- Check if error happens at import time vs runtime
- Review module `__init__.py` for env var reads
- Use `grep -r "os.environ" module_name` to find all reads
- If found, set env vars before importing

**Prevention going forward**:

- Always read copilot-instructions Pattern 1
- Document "import-time dependencies" in module docstrings
- Add pre-import assertion checks

### Error Pattern 2: Inline Styles Hiding Real Issues

**Mistake Learned**:

```html
<!-- ❌ WRONG: This worked but hid accessibility problems -->
<div style="width: 0%">GPU Memory</div>

<!-- Problems hidden by inline style:
  1. No semantic meaning in CSS
  2. Hard to audit at scale (386+ files)
  3. Accessibility tools can't find theme conflicts
  4. Can't apply media queries or responsive design
-->
```

**Why it failed**:

- Inline styles bypass CSS cascade
- Each style is an island - no shared theme
- Linting tools can't catch patterns
- Team can't enforce standards

**Correct pattern** (lessons applied):

```html
<!-- ✅ CORRECT: Use CSS classes for consistency -->
<div class="progress-fill-bar">GPU Memory</div>

<style>
  .progress-fill-bar {
    width: 0%;  /* Centralizes the concern */
    transition: width 0.3s ease;  /* Adds polish */
    background: linear-gradient(90deg, #4CAF50, #45a049);
    border-radius: 4px;
  }

  /* Can now apply responsive design */
  @media (prefers-reduced-motion: reduce) {
    .progress-fill-bar { transition: none; }
  }
</style>
```

**How to detect this pattern**:

- Scan for `style="` in HTML
- Check if same style repeated 3+ times
- Use automated tool: `scan_html_css_syntax.py`
- Review git history for style duplication

**Prevention going forward**:

- Validate: Run `validate_html_css.py` before commits
- Enable: Webhint.io linting in CI/CD
- Document: Add CSS audit checklist to PR template

### Error Pattern 3: Missing Type Hints Cascading

**Mistake Learned**:

```python
# ❌ WRONG: Untyped function creates 5+ downstream errors
def extract_style_properties(element):  # Missing param type
    """Extract inline style properties."""
    # IDE can't infer element type
    # Can't know what methods are available
    # Type checker reports 11 errors total

    properties = {}  # Type unknown
    css_lines = []   # Type unknown

    for key, value in properties.items():  # Can't infer key, value types
        css_lines.append(f"{key}: {value}")

    return css_lines  # Return type unknown
```

**Why it failed**:

- Untyped code → IDE loses context
- Type checker can't validate usage
- Errors cascade through codebase
- Next developer has to guess intent

**Correct pattern** (lessons applied):

```python
# ✅ CORRECT: Full type hints from start
from typing import Dict, List, Tuple, Any

def extract_style_properties(element: str) -> Tuple[str, Dict[str, str]]:
    """Extract inline style properties from HTML element.

    Args:
        element: HTML element string containing style attribute

    Returns:
        Tuple of (class_name, properties_dict)
    """
    properties: Dict[str, str] = {}
    css_lines: List[str] = []

    for key, value in properties.items():
        css_lines.append(f"{key}: {value}")

    return ("generated-class", properties)
```

**How to detect this pattern**:

- Run Pylance: `mcp_pylance_mcp_s_pylanceFileSyntaxErrors`
- Check for "Cannot access member" errors
- Look for Any types in IDE tooltips
- Count type inference cascades

**Prevention going forward**:

- Add `python.analysis.typeCheckingMode: "strict"` to settings
- Require type hints in all new functions
- Use automated type hint generation tools
- Document typing imports at module top

---

## BOB AI KNOWLEDGE BASE INTEGRATION

### What is BOB AI in This Project

BOB AI is an **advanced diagnostic and troubleshooting framework** embedded in this codebase. It represents:

1. **Behavioral observation** - Track what actually happens vs expected
2. **Optimization** - Find bottlenecks and improve performance
3. **Building blocks** - Modular solutions to recurring problems

**BOB AI is NOT**:

- A separate system or agent
- Machine learning inference
- A new framework or library

**BOB AI IS**:

- A methodology for problem-solving
- A knowledge base of proven patterns
- A reasoning framework for debugging

### BOB AI Decision Tree: "How Do I Fix This?"

```
┌─ ERROR OCCURS
│
├─ Step 1: Is it an IMPORT ERROR?
│  └─ YES → Check environment variables FIRST
│  │       (See Pattern 1: lines 1-50 of main.py)
│  │       Reason: Import-time dependencies
│  └─ NO → Go to Step 2
│
├─ Step 2: Is it a RENDERING ERROR?
│  └─ YES → Check HTML structure
│  │       1. Function defined before use? (showSection pattern)
│  │       2. Template syntax valid? (${variable} check)
│  │       3. CSS classes applied? (inline styles check)
│  │       Reason: DOM execution order matters
│  └─ NO → Go to Step 3
│
├─ Step 3: Is it a MEMORY ERROR?
│  └─ YES → Check GPU/VRAM
│  │       1. Pre-check before job (gpu_manager pattern)
│  │       2. Cleanup after job (torch.cuda.empty_cache)
│  │       3. Use fallback processor (graceful degradation)
│  │       Reason: GPU is shared resource
│  └─ NO → Go to Step 4
│
├─ Step 4: Is it a WebSocket/Networking ERROR?
│  └─ YES → Check subscriptions
│  │       1. Client joined room? (subscribe_to_job)
│  │       2. Server emitting to room? (socketio.emit(..., room=id))
│  │       3. Heartbeat working? (ping/pong)
│  │       Reason: WebSocket is stateful
│  └─ NO → Go to Step 5
│
└─ Step 5: Check Common Issues Table (below)
   └─ Still stuck? Check .github/copilot-instructions-full.md
```

### BOB AI Pattern Library: Proven Solutions

**Pattern Set A: Configuration & Initialization**

- ✓ Environment variables must be set before imports
- ✓ Use lazy loading for expensive resources (models, GPU)
- ✓ Thread-safe singletons with locks for shared state
- ✓ Validate configuration early, fail fast

**Pattern Set B: Resource Management**

- ✓ Always pre-check before allocating (VRAM check)
- ✓ Execute in try block, cleanup in finally block
- ✓ Implement graceful degradation (GPU → CPU fallback)
- ✓ Monitor resource usage continuously

**Pattern Set C: Communication & Events**

- ✓ Use WebSocket rooms for subscription-based updates
- ✓ Never broadcast globally when targeted delivery works
- ✓ Implement heartbeat for connection health
- ✓ Use JSON serialization for inter-process communication

**Pattern Set D: Error Handling**

- ✓ Catch specific exceptions, not generic Exception
- ✓ Log context: what state were we in? what were inputs?
- ✓ Provide fallback always - never leave client hanging
- ✓ Return meaningful errors to frontend (not stack traces)

### BOB AI Diagnostic Questions

**When something breaks, ask in order**:

1. **Has this worked before?** (regression or new issue?)
   - If new: Search for recent changes (`git log --oneline -20`)
   - If regression: Compare working version with broken version

2. **What exactly changed?** (identify delta)
   - File changes: `git diff`
   - Dependency changes: `pip list` or `npm list`
   - Environment changes: Check env vars, config files
   - External factors: Disk space, internet, permissions

3. **What does the error message actually say?** (don't skip)
   - Full stack trace or just first line?
   - Line number is accurate?
   - Is this the root cause or symptom?
   - Can I reproduce it consistently?

4. **Which layer is failing?** (narrow scope)
   - Frontend (browser console errors)
   - Backend (Flask/Python errors)
   - WebSocket (connection/message issues)
   - Database/Storage (file not found)
   - GPU (CUDA errors)

5. **What would fix this?** (test hypothesis)
   - Too many things to try? Start with safest bet
   - Rollback last change (safest)
   - Check environment variables (quickest)
   - Restart service (often works)
   - Check logs (reveals truth)

---

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

---

## PESSIMISTIC PROBLEM-SOLVING FRAMEWORK

### Why Pessimism? (The Realistic Approach)

Most developers are optimists. They assume:

- ✗ "It will probably work"
- ✗ "This edge case won't happen"
- ✗ "We don't need to handle this error"
- ✗ "The documentation is up-to-date"
- ✗ "Nobody will use it that way"

**Reality check:** These assumptions are wrong 90% of the time.

**Pessimistic approach:** Assume EVERYTHING will fail. Then solve for that.

```python
# ❌ OPTIMISTIC (NAIVE)
def process_job(job_id):
    data = fetch_data(job_id)
    result = calculate(data)
    return result

# ✅ PESSIMISTIC (REALISTIC)
def process_job(job_id):
    try:
        # Assume data fetch fails
        data = fetch_data(job_id)
        if not data:
            logger.error(f"No data for job {job_id}")
            return None

        # Assume calculation fails
        if len(data) > 100000:  # Data too large
            return graceful_fallback(job_id)

        # Assume format is wrong
        try:
            result = calculate(data)
        except ValueError as e:
            logger.warning(f"Calculation failed: {e}, using cache")
            return get_cached_result(job_id)

        # Assume result is invalid
        if not validate_result(result):
            logger.error(f"Invalid result for {job_id}")
            return fallback_result(job_id)

        return result

    except Exception as e:
        # Assume EVERYTHING can fail
        logger.error(f"Job {job_id} failed catastrophically: {e}", exc_info=True)
        return create_error_response(job_id, str(e))
```

### Pessimistic Principles

**Principle P1: Assume Everything Will Fail**

- Input validation: Check EVERYTHING
- Network calls: Always timeout and retry
- File operations: Disk full, permission denied, corrupted
- Memory: GPU runs out, system runs out
- Users: Will do the wrong thing

**Principle P2: Fail Fast With Context**

- Don't let bad state propagate
- Log the exact state when failure occurs
- Provide meaningful error messages
- Include stack trace AND context variables

**Principle P3: Multiple Fallbacks**

- Level 1: Graceful degradation (GPU → CPU)
- Level 2: Cached fallback (use last known good)
- Level 3: Simplified fallback (lower quality)
- Level 4: Human intervention (admin console)

**Principle P4: Prove It Works**

- "It works on my machine" = worthless
- Test on actual hardware
- Test with real data (not mocked)
- Test at scale (production load)
- Test failure modes (what breaks?)

---

## MULTI-AGENT ARGUMENTATION FRAMEWORK

### The Problem With Single Perspectives

One person (or one AI) looking at a problem sees:

- ✗ Their own biases
- ✗ Their preferred solutions
- ✗ Their blind spots
- ✗ What they EXPECT to see

**Solution:** Simulate multiple expert perspectives arguing the case.

### The 5-Agent Argumentation System (Expert Level - 20+ Years Experience)

When facing a complex problem, consult 5 expert-level agents with 20+ years of professional experience across Python, Web Development, C/C++, SQL, and Windows environments:

#### Agent 1: THE SENIOR PYTHON/DATA ARCHITECT 🏛️

**Experience:** 22 years Python development | 18 years system architecture | 15 years ML/GPU systems
**Expertise:** Production Python systems, async patterns, memory management, decorators, metaclasses, performance optimization
**Platforms:** Windows 10/11, Linux, cloud deployment, Docker orchestration
**Capabilities:**

- Can open Python IDEs, debugging tools, system profilers outside VS Code
- Listens to browser console for API calls, WebSocket events, performance metrics
- Can launch DevTools, monitoring dashboards, logging applications
- Monitors: Chrome DevTools, Edge DevTools, Firefox Console for real-time error tracking

**Role:** "What could go wrong from a memory & resource perspective?"

**Deep-Level Questions:**

- What's the garbage collection behavior under this scenario?
- Are we creating circular references or memory leaks?
- How will this perform under 10,000 concurrent requests?
- What's the actual memory footprint including Python overhead?
- Could this deadlock with other services?
- Are we properly using context managers and with-statements?

**Expert Output Example:**

```
ARCHITECT: GPU memory management needs atomic operations!
  Problem: Thread race conditions between VRAM check and allocation
  Root Cause: VRAM can be consumed between check and torch.cuda.malloc()
  Expert Solution:
    1. Use torch.cuda.memory_reserved() not memory_allocated()
    2. Pre-allocate fixed memory pool on startup (thread-safe)
    3. Implement proper exception handling with context managers
    4. Use multiprocessing.Manager for inter-process VRAM tracking
  Production Pattern:
    try:
        gpu_mgr.reserve_vram(required_mb)  # Atomic operation
        result = model.generate(input_data)
    finally:
        gpu_mgr.release_vram()  # Always cleanup
        torch.cuda.empty_cache()
  Validation: Tested with 10K concurrent requests, zero deadlocks
```

#### Agent 2: THE SENIOR FULL-STACK WEB ARCHITECT 🌐

**Experience:** 24 years web development | 20 years TypeScript/JavaScript | 16 years Flask/FastAPI | REST API design
**Expertise:** WebSocket optimization, real-time systems, database scaling, caching strategies, API security
**Platforms:** Windows IIS/Apache, Next.js, modern frontend frameworks, database optimization
**Capabilities:**

- Can open browser DevTools (Chrome, Edge, Firefox) outside VS Code
- Listens to browser console for network requests, errors, WebSocket messages, performance warnings
- Can launch debuggers, profilers, network monitors (Postman, Insomnia, Wireshark)
- Monitors: Network tab, Console tab, Application tab, Performance profiler, Sources debugger
- Can analyze: XHR/Fetch calls, WebSocket frames, localStorage/sessionStorage, cookies, cache

**Role:** "How do we build scalable, real-time systems?"

**Deep-Level Questions:**

- What's our database query optimization strategy?
- Are we using connection pooling correctly?
- How does WebSocket backpressure work in this scenario?
- What's the optimal batch size for this workload?
- Have we profiled the critical path?
- What's our caching invalidation strategy?

**Expert Output Example:**

```
WEB_ARCHITECT: WebSocket architecture for 10K concurrent clients
  Current Issue: Progress events flooding network, 40% packet loss
  Root Analysis:
    - Backend emitting every 100ms (100 events/sec × 10K clients = 1M/sec)
    - Frontend receiving events faster than rendering (UI thread bottleneck)
    - No backpressure mechanism (memory buildup)
  Expert Solution:
    1. Implement adaptive event throttling (50-200ms based on lag)
    2. Add client-side event batching (max 5 events/batch)
    3. Use binary frames (MessagePack) instead of JSON (40% less bandwidth)
    4. Implement server-side backpressure queue with max size
  Metrics Expected:
    - Packet loss: 40% → 0.1%
    - Latency: 800ms → 120ms
    - Network bandwidth: 280Mbps → 45Mbps
  Tested: Load tested with Locust, validated with 15K concurrent
```

#### Agent 3: THE SENIOR WINDOWS SYSTEMS ENGINEER 💻

**Experience:** 25 years Windows development | 20 years C/C++ | 18 years registry/DLL/COM | system-level optimization
**Expertise:** Windows 10/11 internals, DLL hell resolution, COM objects, process management, performance monitoring
**Platforms:** Windows only expertise, registry manipulation, Windows services, batch automation
**Capabilities:**

- Can open Windows tools outside VS Code: Task Manager, Resource Monitor, Performance Monitor, Event Viewer, Registry Editor
- Can launch system applications: Process Explorer, DebugView, WinDbg, Dependency Walker, DLL Export Viewer
- Listens to Windows Event Log for system errors, warnings, and application crashes
- Can monitor: Task Scheduler, System processes, DLL loading, memory allocation, registry changes
- Can capture: ETW traces, Performance counters, Event logs, debug output, system metrics

**Role:** "How do we leverage Windows capabilities and avoid pitfalls?"

**Deep-Level Questions:**

- What Windows APIs are most efficient for this task?
- Are we handling DLL versioning correctly (avoiding DLL Hell)?
- What's the process priority and affinity for optimal performance?
- Are we using Windows event logging properly?
- How does this interact with Windows Defender/security software?
- Are we managing registry settings appropriately?

**Expert Output Example:**

```
WINDOWS_ENGINEER: Docker Desktop on Windows 11 - Performance Optimization
  Issue: Docker container builds 3x slower on Windows than Linux
  Root Cause Analysis (Windows-specific):
    1. File system translation layer (WSL2 → Windows NTFS)
    2. Hyper-V VM overhead (3-5 second context switches)
    3. Antivirus scanning (Windows Defender) on container files
    4. Named pipe communication bottleneck
  Expert Solutions (Windows 10/11 specific):
    1. Disable Windows Defender scanning for Docker folder:
       Add-MpPreference -ExclusionPath "C:\ProgramData\Docker"
    2. Optimize WSL2 resources in .wslconfig:
       [interop]
       enabled=true
       appendWindowsPath=true
    3. Use buildkit for parallel layers (50% faster):
       $env:DOCKER_BUILDKIT=1
    4. Cache Docker images locally to C: drive (faster NTFS)
  Performance Improvement:
    - Build time: 5min 30sec → 1min 45sec (68% faster)
    - WSL2 memory: 4GB max → 2GB (better resource usage)
  Tested: 20+ builds with various Dockerfile sizes
```

#### Agent 4: THE SENIOR DATABASE ARCHITECT �️

**Experience:** 23 years SQL optimization | 20 years performance tuning | 18 years Windows SQL Server | backup strategies
**Expertise:** Query optimization, indexing strategies, transaction isolation, backup/recovery, data integrity
**Platforms:** SQL Server, PostgreSQL, optimization for Windows environments, GitHub-like version control concepts
**Capabilities:**

- Can open SQL Server Management Studio (SSMS), Azure Data Studio, DBeaver outside VS Code
- Can launch database profilers, query analyzers, and monitoring dashboards
- Listens to SQL Server error logs for query failures, locking issues, performance warnings
- Can monitor: Query execution plans, transaction logs, deadlock graphs, performance counters
- Can analyze: Query duration, index fragmentation, table statistics, connection pools, replication status

**Role:** "How do we manage data integrity and performance at scale?"

**Deep-Level Questions:**

- What's the optimal indexing strategy for this query pattern?
- Are we using proper transaction isolation levels?
- What's our backup and disaster recovery strategy?
- How does query execution plan change under load?
- Are we handling connection pooling efficiently?
- What's the data growth projection and retention policy?

**Expert Output Example:**

```
DATABASE_ARCHITECT: Local Backup System (Git-like for databases)
  Requirement: Local backup on C: drive with version control
  Expert Architecture:
    1. Snapshot-based backups (differential daily, full weekly)
    2. Backup versioning system (similar to Git commits)
    3. Point-in-time recovery capability
    4. Compression (50% space savings)
    5. Integrity verification (checksums)

  Implementation (Windows-specific):
    ```powershell
    # Daily incremental backup with version tracking
    $BackupPath = "C:\Backups\orfeas-studio"
    $Timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
    $BackupFile = "$BackupPath\backup-$Timestamp.zip"

    # Create backup with compression and checksum
    Compress-Archive -Path $DataPath -DestinationPath $BackupFile
    (Get-FileHash $BackupFile).Hash | Set-Content "$BackupFile.sha256"
    ```

  Backup Retention Strategy:
    - Daily backups: 7 days (7 versions)
    - Weekly full: 4 weeks (4 versions)
    - Monthly snapshots: 12 months (12 versions)
    - Total storage needed: ~200GB (with compression)

  Recovery Testing: Monthly full restore validation
```

#### Agent 5: THE SENIOR C/C++ SYSTEMS PROGRAMMER �

**Experience:** 26 years C/C++ | 22 years low-level optimization | 20 years Windows native APIs | performance profiling
**Expertise:** Memory management, pointer arithmetic, performance tuning, native Windows APIs, interop with Python
**Platforms:** Windows native development, DLL creation, FFI/ctypes, performance-critical code
**Capabilities:**

- Can open Visual Studio Debugger, WinDbg, Ghidra, IDA Pro outside VS Code
- Can launch performance profilers, memory analyzers, and disassemblers
- Listens to debugger output for breakpoint hits, memory access violations, thread state changes
- Can monitor: CPU registers, memory dumps, call stacks, assembly instruction traces
- Can analyze: SIMD utilization, branch prediction, cache efficiency, pointer dereferencing, DLL loading events

**Role:** "How do we optimize performance at the lowest level?"

**Deep-Level Questions:**

- What's the CPU cache efficiency of this algorithm?
- Are we doing unnecessary memory allocations in hot paths?
- Could we use SIMD instructions for this computation?
- What's the branch prediction impact?
- How does this interact with Windows API limitations?
- Are we properly profiling with Windows Performance Analyzer?

**Expert Output Example:**

```
SYSTEMS_PROGRAMMER: Python ↔ C/C++ Performance Bridge
  Goal: 3D model generation 10x faster via native acceleration
  Expert Approach (Windows-specific):
    1. Identify Python hot spots (99% of time in 1% of code)
    2. Write performance-critical path in C++ (STL algorithms)
    3. Create Windows DLL with ctypes interface
    4. Minimize data marshalling between Python/C++
    5. Use Windows Performance Analyzer for profiling

  Implementation Example:
    ```cpp
    // mesh_optimizer.cpp - High-performance mesh processing
    #include <algorithm>
    #include <vector>
    #include <omp.h>  // OpenMP for parallelization

    extern "C" {
        __declspec(dllexport) void optimize_mesh(
            float* vertices, int vertex_count,
            int* indices, int index_count) {
            // Parallel mesh optimization using all CPU cores
            #pragma omp parallel for
            for (int i = 0; i < vertex_count; ++i) {
                // SIMD-friendly vertex processing
                vertices[i*3 + 0] *= 0.95f;  // Auto-vectorized
            }
        }
    }
    ```

  Python Interface (ctypes):
    ```python
    import ctypes
    mesh_opt = ctypes.CDLL('mesh_optimizer.dll')
    mesh_opt.optimize_mesh(vertices.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
                          len(vertices), indices.ctypes.data_as(...))
    ```

  Performance Results (Windows 11 i9-12900K):
    - Pure Python: 45 seconds
    - Optimized C++: 4.2 seconds (10.7x speedup)
    - Profiling: 92% time in loop vectorized by SIMD
    - Scaling: Linear across all 12 cores

  Validation: Numerical equivalence tested, mesh integrity verified
```

#### Agent 6: THE SENIOR DEVOPS/PLATFORM ENGINEER �

**Experience:** 20 years systems administration | 18 years automation | 15 years Windows automation | infrastructure as code
**Expertise:** Backup strategies, local repository management, Windows automation scripts, disaster recovery, monitoring
**Platforms:** Windows batch/PowerShell scripting, scheduled tasks, backup orchestration, GitHub-like local systems
**Capabilities:**

- Can open Docker Desktop, Kubernetes tools (K9s), container registries outside VS Code
- Can launch monitoring dashboards: Prometheus, Grafana, ELK Stack, Datadog
- Listens to Docker logs for container health, deployment events, application output
- Can monitor: Container lifecycle, resource usage, network traffic, persistent volume status
- Can analyze: Application logs, deployment pipelines, backup verification, infrastructure state

**Role:** "How do we build reliable, reproducible systems?"

**Deep-Level Questions:**

- What's our disaster recovery time objective (RTO)?
- How do we automate the entire deployment stack?
- What's our monitoring and alerting strategy?
- Can we reproduce this environment from scratch?
- How do we manage configuration drift?
- What's our backup verification process?

**Expert Output Example:**

```
DEVOPS_ENGINEER: GitHub-Like Local Backup System (Windows)
  Requirement: Version-controlled backup on C: drive with rollback capability

  Architecture (Similar to Git):
    - Objects database: C:\Backups\.objects (content-addressable)
    - References: C:\Backups\.refs (branch pointers)
    - Commit log: C:\Backups\.commits (version history)
    - Working copy: C:\Backups\latest (current state)

  PowerShell Implementation:
    ```powershell
    function New-BackupCommit {
        param([string]$Message)

        # 1. Create snapshot hash (like Git blob)
        $snapshot = Get-DirectoryHash -Path $SourcePath
        $snapshotId = New-Object System.Security.Cryptography.SHA256Managed |
                      ForEach-Object {
                          $_.ComputeHash([System.Text.Encoding]::UTF8.GetBytes($snapshot))
                      } | ForEach-Object { $_.ToString('X2') } | Join-String

        # 2. Store backup with content deduplication
        $backupPath = "C:\Backups\.objects\$($snapshotId.Substring(0,2))\$($snapshotId.Substring(2))"
        Copy-Item -Path $SourcePath -Destination $backupPath -Recurse

        # 3. Create commit metadata
        $commit = @{
            id = (Get-Random -Minimum 0 -Maximum 999999999).ToString('X8')
            tree = $snapshotId
            parent = Get-Content "C:\Backups\.refs\HEAD"
            author = $env:USERNAME
            timestamp = Get-Date -Format 'o'
            message = $Message
        }

        # 4. Store commit log
        $commit | ConvertTo-Json | Add-Content "C:\Backups\.commits\$($commit.id)"
        Set-Content -Path "C:\Backups\.refs\HEAD" -Value $commit.id

        Write-Host "Backup committed: $($commit.id)"
    }

    # Scheduled backup (daily at 2 AM)
    Register-ScheduledTask -TaskName "DailyBackup" -Action {
        New-BackupCommit -Message "Daily backup $(Get-Date -Format 'yyyy-MM-dd')"
    }
    ```

  Rollback Capability:
    ```powershell
    function Restore-BackupCommit {
        param([string]$CommitId)

        $commit = Get-Content "C:\Backups\.commits\$CommitId" | ConvertFrom-Json
        $backupPath = "C:\Backups\.objects\$($commit.tree.Substring(0,2))\..."
        Copy-Item -Path $backupPath -Destination $RestorePath -Recurse -Force

        Write-Host "Restored to commit $CommitId from $(Get-Date -Date $commit.timestamp)"
    }
    ```

  Features:
    - Automatic deduplication (70% storage savings)
    - Point-in-time recovery (30-day history)
    - Integrity verification (SHA256 hashes)
    - Automated compression (NTFS compression on C:)
    - Email notifications on backup success/failure

  Tested: Full restore from 90-day-old backup successful
```

### Using Multi-Agent Argumentation

**When to use:**

- Making major architectural decisions
- Debugging mysterious failures
- Planning risky deployments
- Evaluating multiple solutions
- Before writing production code

**Process:**

1. **State the problem** clearly
2. **Ask each agent** their perspective
3. **Look for disagreement** - this reveals blind spots
4. **Identify consensus** - what do all agree on?
5. **Test hypothesis** - implement the solution that handles all concerns

**Example dialogue:**

```
PROBLEM: Should we use GPU or CPU for batch processing?

PESSIMIST: GPU will fail! Multiple concurrent jobs will fight for VRAM.
           OOM crashes will destroy data. Use CPU - it's slower but safe.

OPTIMIST: GPU is 40x faster! Most jobs don't need maximum VRAM. Worth
          the risk. 99% of users want speed over reliability.

ENGINEER: GPU needs: VRAM reservation, fallback logic, monitoring.
          CPU needs: Multi-threading, process pooling. GPU is harder.

RESEARCHER: Best practice: Use GPU for small jobs (<1GB), CPU for large.
            Hybrid approach shown in "GPU-CPU Orchestration" (2024).

DEVIL'S ADVOCATE: Why are we assuming CPU is a fallback? What if we just
                  reject jobs that need >6GB? Queue them or fail gracefully?

CONSENSUS: Use GPU with tiered fallback:
  1. Try GPU (fast)
  2. Fall back to CPU (slow)
  3. Queue job if both insufficient
  4. Reject with explanation if queued too long
```

---

## ONLINE RESEARCH & SOLUTION FINDING

### Built-in Research Queries

When you encounter a problem, ask:

**Query 1: Stack Overflow**

```
site:stackoverflow.com [error message] [language] [framework]
```

**Query 2: GitHub Issues**

```
site:github.com/[project] [error] "500 error" OR "crash"
```

**Query 3: Documentation**

```
site:[project].org OR site:[project].readthedocs.io [error] troubleshooting
```

**Query 4: Academic Research**

```
site:arxiv.org [technical topic] performance optimization
```

**Query 5: Blog Posts & Tutorials**

```
[error message] solution tutorial 2024
```

### Problem-Solving Research Pattern

**Step 1: Identify the error accurately**

```
What is the EXACT error message?
❌ "Something went wrong"
✅ "CUDA out of memory: tried to allocate 6.00GB, but only 2.50GB available"
```

**Step 2: Search for others who had same issue**

```
Search 1: [Exact error message]
Search 2: [Error + your framework] solution
Search 3: [Error + your hardware] fix
Search 4: [Error + version info] issue
```

**Step 3: Analyze solutions found**

```
- Count how many solutions exist (1 = rare, 10+ = common)
- Check dates (outdated solutions may not apply)
- Look at reputation (upvotes, GitHub stars)
- Check if solution applies to YOUR setup
```

**Step 4: Test hypothesis before production**

```
1. Reproduce error in isolated environment
2. Apply solution from research
3. Verify fix actually resolves root cause
4. Check for side effects
5. Document what worked
```

### Common Errors & Research Strategies

| Error | Research Strategy | Expected Solutions |
|-------|-------------------|-------------------|
| `CUDA out of memory` | Search: "[CUDA OOM pytorch](https://github.com/pytorch/pytorch/issues?q=CUDA+out+of+memory)" | GPU memory management, batch size reduction, gradient accumulation |
| `xformers DLL error` | Search: "[xformers 0xc0000139](https://github.com/search?q=xformers+0xc0000139)" | Env var ordering, Windows path issues, dependency conflicts |
| `WebSocket timeout` | Search: "[Socket.io timeout connection](https://socket.io/docs/)" | Heartbeat config, CORS settings, firewall rules |
| `Import error` | Search: "[Python import module not found](https://docs.python.org/3/)" | Missing dependency, wrong Python path, version mismatch |
| `3D model corruption` | Search: "[STL mesh repair Python](https://trimsh.org/)" | Mesh validation, auto-repair libraries, format conversion |

### Assembling Your Research

**Create a decision matrix:**

```
PROBLEM: Should we use GPU or CPU for processing?

Solution 1: GPU Only
  Research: NVIDIA docs (authoritative)
  Pros: 40x faster, production standard
  Cons: OOM risk, setup complexity
  Reliability: 95% (with fallback)
  Confidence: HIGH (industry standard)

Solution 2: CPU Only
  Research: Python threading docs
  Pros: Simple, always works
  Cons: 40x slower, won't meet SLA
  Reliability: 99.9%
  Confidence: MEDIUM (works but not optimal)

Solution 3: GPU + CPU Hybrid
  Research: "GPU-CPU Orchestration" paper
  Pros: Fast + reliable, flexible
  Cons: Complex, high maintenance
  Reliability: 98% (if implemented right)
  Confidence: MEDIUM (unproven in this project)

RECOMMENDATION: Solution 1 (GPU) with fallback to Solution 2 (CPU)
  Rationale: Matches industry practice, acceptable reliability, meets performance SLA
```

### Research Protocol

Before implementing ANY major change:

1. **Research phase** (30 min)
   - Search for existing solutions
   - Find 3+ credible sources
   - Read through GitHub issues
   - Check official documentation

2. **Analysis phase** (15 min)
   - Compare approaches found
   - Evaluate tradeoffs
   - Identify best practice
   - Note edge cases others found

3. **Hypothesis phase** (15 min)
   - State your solution clearly
   - Document why you chose it
   - List assumptions
   - Identify failure modes

4. **Test phase** (60 min)
   - Reproduce the original problem
   - Apply your solution
   - Verify it actually works
   - Test edge cases from research

5. **Documentation phase** (15 min)
   - Write what you learned
   - Document the solution
   - Link to research sources
   - Note limitations

---

## INTEGRATED PROBLEM-SOLVING WORKFLOW

### When You Encounter a Problem

```
🔴 PROBLEM APPEARS
        ↓
📚 RESEARCH IT
  - Search Stack Overflow
  - Check GitHub issues
  - Read official docs
  - Note common solutions
        ↓
🧠 CONSULT AGENTS (argue it out)
  - PESSIMIST: "What could go wrong?"
  - OPTIMIST: "Why this could work?"
  - ENGINEER: "How do we build it?"
  - RESEARCHER: "What do experts say?"
  - DEVIL: "Is our premise wrong?"
        ↓
⚖️ BUILD DECISION MATRIX
  - Compare 3+ solutions
  - Score on reliability/performance/complexity
  - Identify tradeoffs
  - Choose best approach
        ↓
✅ IMPLEMENT WITH PESSIMISM
  - Add validation
  - Add fallbacks
  - Add error handling
  - Add monitoring
  - Add tests
        ↓
🧪 TEST RIGOROUSLY
  - Normal case
  - Edge cases
  - Failure cases
  - Recovery cases
        ↓
📖 DOCUMENT & SHARE
  - What was the problem?
  - How did you research it?
  - Why did you choose this solution?
  - What were alternatives?
  - What did you learn?
```

---

## PESSIMISTIC CODE CHECKLIST

Before merging ANY code, ask pessimistically:

**Input & Validation**

- [ ] What if input is NULL?
- [ ] What if input is empty?
- [ ] What if input is wrong type?
- [ ] What if input is too large?
- [ ] What if input is malicious?

**State & Assumptions**

- [ ] What if previous operation failed?
- [ ] What if state is corrupted?
- [ ] What if system is in unknown state?
- [ ] What assumptions are we making?
- [ ] What if assumptions are wrong?

**Resources & Limits**

- [ ] What if we run out of memory?
- [ ] What if disk is full?
- [ ] What if network is down?
- [ ] What if timeout occurs?
- [ ] What if rate limiting kicks in?

**Error Handling**

- [ ] What errors can occur?
- [ ] Do we catch specific exceptions?
- [ ] Do we log with context?
- [ ] Do we have fallback?
- [ ] Do we cleanup resources?

**Testing**

- [ ] Does test cover happy path?
- [ ] Does test cover error paths?
- [ ] Do we test with real data?
- [ ] Do we test at scale?
- [ ] Do we test after deployment?

---

## DECISION-MAKING WITH EVIDENCE

### Evidence Collection Template

When making a decision:

```
DECISION: Should we cache expensive computations?

EVIDENCE FOR CACHING:
✓ Academic research: "Caching strategies in ML" (Google, 2023)
✓ Industry practice: 80% of ML services use caching
✓ Our data: Similar queries 70% of the time
✓ Performance: 40x faster with cache (measured)
✓ Cost: Saves $500/month in compute (calculated)
✗ ONE AGAINST: Cache invalidation is hard

EVIDENCE AGAINST CACHING:
✓ System complexity: +2000 LOC, harder to debug
✓ Memory cost: +4GB RAM required
✓ Staleness risk: Results may be outdated
✓ Maintenance: Need cache expiry logic
✗ ONE FOR: Queries change frequently anyway

CONFIDENCE SCORING:
  1. Is evidence from credible source? (YES: academic + industry)
  2. Is evidence recent? (YES: 2023/2024)
  3. Do multiple sources agree? (YES: Google + Stack Overflow + our data)
  4. Have we tested locally? (NEED TO DO)
  5. Is fallback available? (YES: can disable cache)

CONFIDENCE LEVEL: 85% (proceed with pilot)

IMPLEMENTATION PLAN:
1. Implement basic cache (Redis)
2. Monitor hit/miss rates (target 70%)
3. Measure performance improvement
4. Set TTL based on data freshness requirements
5. Have disable switch if issues occur
```

**Final Recommendation:**
Implement caching with:

- Daily TTL (adjust based on data update frequency)
- Monitoring dashboard (cache hit rate)
- Easy disable switch in config
- Tests covering cache misses and expiry
- Gradual rollout (10% → 50% → 100%)

---

## PROJECT-SPECIFIC CONVENTIONS & PATTERNS

### 1. Code Organization Conventions

**Module Naming**: Use descriptive names with `_` prefix for private/internal modules:

- `gpu_manager.py` - Public API, use `from gpu_manager import get_gpu_manager()`
- `stl_processor.py` - Public mesh operations, import classes directly
- `llm_integration.py` - LLM orchestration, use factory functions

**Testing Patterns**:

- Unit tests: `backend/tests/unit/test_*.py` - No GPU required, fast
- Integration tests: `backend/tests/integration/test_*.py` - Full workflow, uses real models
- Mark tests with `@pytest.mark.unit` or `@pytest.mark.integration`

**Logging Standards**:

```python
logger = logging.getLogger(__name__)
logger.info("[ORFEAS] Human-readable status message")  # [ORFEAS] prefix for traceability
logger.warning("[WARN] Non-critical issue detected")
logger.error("[ERROR] Operation failed", exc_info=True)  # Always include exc_info
```

### 2. Backend-Specific Patterns

**Factory Functions Over Direct Imports**:

- Use `get_gpu_manager()` instead of `GPUManager()` - enables singleton/mocking
- Use `get_3d_processor()` instead of `Hunyuan3DProcessor()` - centralizes initialization
- Located in main module files for discoverability

**Thread Safety in Cache Classes**:

```python
class CachedProcessor:
    _cache = {}
    _lock = threading.Lock()

    @classmethod
    def process(cls, data):
        if not cls._cache.get("initialized"):
            with cls._lock:
                if not cls._cache.get("initialized"):  # Double-check pattern
                    cls._initialize()
        return cls._execute(data)
```

**Error Recovery Pattern** (try-finally for GPU cleanup):

```python
try:
    result = processor.generate(image)
finally:
    torch.cuda.empty_cache()  # ALWAYS cleanup, even if error occurred
    logger.info(f"GPU cleanup complete. VRAM: {gpu_mgr.get_current_vram()}MB")
```

**WebSocket Room-Based Messaging**:

- Clients subscribe: `socket.emit('subscribe_to_job', {'job_id': '123abc'})`
- Backend emits to room: `socketio.emit('event_name', data, room='123abc')`
- Only subscribers in that room receive (not broadcast to all)

### 3. Frontend-Specific Patterns

**Socket.IO Connection Management** (Next.js hook):

```typescript
export function useSocket(url: string): UseSocketReturn {
  // Returns {socket, connected, connectionError}
  // Auto-reconnect with exponential backoff
  // Transports: polling → websocket upgrade
  // Max 10 reconnection attempts
}
```

**Section Navigation** (HTML frontend):

```html
<!-- Use showSection('sectionId') to switch between sections -->
<section id="3Dstudio" style="display: none">...</section>
<section id="image" style="display: none">...</section>
<button onclick="showSection('3Dstudio')">3D Studio</button>
```

**Three.js Model Loading**:

- Use `THREE.STLLoader` for static .stl imports
- Use `babylon.js` for WebGPU-accelerated rendering
- Support fallback to Three.js WebGL on older browsers

### 4. GPU Memory Management Conventions

**VRAM Budget for RTX 3090 (24GB)**:

- Shape generation: ~6GB (largest component)
- Texture synthesis: ~2GB
- Reserved overhead: ~2GB
- Available for concurrent jobs: ~14GB

**Pre-Check Pattern**:

```python
# BEFORE starting job
if not gpu_mgr.can_process_job(estimated_vram=6000):  # 6GB in MB
    return jsonify({"error": "Insufficient VRAM"}), 503

# Process job
result = generate_3d(...)

# AFTER (always)
torch.cuda.empty_cache()
```

**Device Selection**:

- Primary: CUDA if available (`DEVICE=cuda` env var)
- Fallback: CPU if GPU OOM
- Override: `DEVICE=cpu` to force CPU mode for testing

### 5. API Endpoint Patterns

**Synchronous Endpoints** (returns result immediately):

```
GET  /health          → {status, gpu_info, uptime}
GET  /metrics         → Prometheus text format
GET  /api/download/:id → Binary STL/OBJ file
```

**Asynchronous Endpoints** (returns job_id, use WebSocket for progress):

```
POST /api/generate-3d → {job_id, status, websocket_url}
POST /api/upload-image → {file_path, image_id, dimensions}
```

**Polling Fallback**:

```
GET /api/job-status/:id → {progress, status, stage, eta_seconds}
```

Use only if WebSocket unavailable (firewall, old client).

### 6. Environment Variable Initialization (CRITICAL)

**Order Matters** - Set variables BEFORE imports:

1. `ORT_TENSORRT_UNAVAILABLE=1` (ONNX Runtime crash prevention)
2. `XFORMERS_DISABLED=1` (Windows DLL crash prevention)
3. `HOME=$USERPROFILE` (Windows path resolution)
4. `CUDA_MODULE_LOADING=LAZY` (Gradual CUDA initialization)
5. THEN: `from dotenv import load_dotenv; load_dotenv()`
6. THEN: Import torch, model libraries

**Why**: Modules read environment variables at import time. Wrong order causes cryptic crashes.

### 7. Quality Assurance Conventions

**Validation Layers**:

1. **Image Upload**: Max 16MB, validates EXIF/encoding, checks dimensions
2. **Model Compatibility**: Checks GPU availability, VRAM
3. **Mesh Generation**: Auto-repairs invalid meshes, validates STL format
4. **Export**: Checks output format (STL/OBJ/GLB/PLY), validates binary encoding

**Prometheus Metrics** (auto-tracked):

- `generation_duration_seconds` - Wall-clock time per generation
- `generation_success_total` / `generation_failure_total` - Success rate
- `gpu_memory_used_mb` - Current VRAM usage
- `websocket_connections_active` - Connected clients
- `quality_printable_rate` - Mesh printability percentage

Enable with: `ENABLE_MONITORING=true`

### 8. Incremental Startup Pattern

**Phase 1 - Fast** (3-5 seconds):

- Flask/SocketIO init
- Route registration
- WebSocket handlers ready

**Phase 2 - On-Demand** (30+ seconds on first request):

- Lazy-load Hunyuan3D models (shape generation pipeline)
- Lazy-load texture synthesis pipeline
- Cache for subsequent requests (~5-10 seconds per job)

**Why**: Developers get instant feedback. Production doesn't waste VRAM on unused models.

---

**Last Updated:** October 28, 2025
**Reference:** Full extended docs in `.github/copilot-instructions-full.md`
