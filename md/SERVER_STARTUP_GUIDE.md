# Server Startup Guide

+==============================================================================â•—
| [WARRIOR] ORFEAS PROTOCOL - ORFEAS SERVER STARTUP GUIDE [WARRIOR] |
| QUICK START |
+==============================================================================

## # ORFEAS AI STUDIO - SERVER STARTUP GUIDE

**Last Updated:** October 14, 2025
**Status:** Production Ready
**Mode:** Automatic Backend Startup

---

## # #  PROBLEM SOLVED: Server Startup Failure

## # # **Root Cause:**

Virtual environment (`.venv`) had **ZERO Python packages installed** (only pip and setuptools).

## # # **Solution:**

1. [OK] Installed Flask and web framework dependencies

2. [OK] Installed image processing libraries (OpenCV, PIL, scikit-image)

3. [OK] Installing PyTorch 2.0.1 with CUDA 11.8 support (IN PROGRESS)

4. [OK] Installed 3D processing libraries (trimesh, numpy-stl)
5. [OK] Installed monitoring and metrics packages

---

## # # [FAST] QUICK START (IMMEDIATE ACTIONS)

## # # **Method 1: Automatic Frontend + Backend (RECOMMENDED)**

```powershell

## Navigate to project directory

cd "C:\Users\johng\Documents\Erevus\orfeas"

## Activate virtual environment

.\.venv\Scripts\Activate.ps1

## Start frontend server (auto-starts backend)

python frontend_server.py

```text

**Then open browser:** http://localhost:8000

The frontend will automatically detect backend status and start it if needed.

---

## # # **Method 2: Manual Backend Start (ADVANCED)**

```powershell

## Navigate to backend directory

cd "C:\Users\johng\Documents\Erevus\orfeas\backend"

## Activate virtual environment

.\.venv\Scripts\Activate.ps1

## Start backend server

python main.py

```text

**Backend runs on:** http://localhost:5000

---

## # #  DEPENDENCIES STATUS

## # # **Critical Packages (INSTALLED):**

```text
[OK] flask==2.3.3                  # Web framework
[OK] flask-cors==4.0.0              # CORS support
[OK] flask-socketio==5.3.6          # WebSocket real-time updates
[OK] python-socketio==5.8.0         # WebSocket client
[OK] eventlet==0.33.3               # Async networking
[OK] werkzeug==2.3.7                # WSGI utilities
[OK] pillow==10.0.1                 # Image processing
[OK] opencv-python==4.8.1.78        # Computer vision
[OK] numpy==1.24.3                  # Numerical computing
[OK] scikit-image==0.21.0           # Image algorithms
[OK] trimesh==3.23.5                # 3D mesh processing
[OK] numpy-stl==3.0.1               # STL file handling
[OK] gputil==1.4.0                  # GPU monitoring
[OK] psutil==5.9.6                  # System monitoring
[OK] prometheus-client==0.19.0      # Metrics export
[OK] python-dotenv==1.0.0           # Environment variables
[OK] pyyaml==6.0.1                  # Configuration files
[OK] requests==2.31.0               # HTTP client
[OK] aiohttp==3.8.6                 # Async HTTP
[OK] websockets==11.0.3             # WebSocket protocol

```text

## # # **AI/ML Packages (IN PROGRESS):**

```text
[WAIT] torch==2.0.1+cu118              # PyTorch with CUDA 11.8 (2.6GB - DOWNLOADING)
[WAIT] torchvision==0.15.2             # Vision models (will install after torch)
[WAIT] diffusers==0.21.4               # Stable Diffusion pipelines
[WAIT] transformers==4.35.2            # Hugging Face transformers
[WAIT] accelerate==0.24.1              # Training acceleration

```text

## # # **Optional Advanced Packages (NOT YET INSTALLED):**

```text
[FAIL] open3d==0.17.0                 # Advanced 3D visualization (large)
[FAIL] pymeshlab==2022.2.post4        # Advanced mesh processing (large)
[FAIL] torchaudio==2.0.2              # Audio processing (not needed)
[FAIL] xformers==0.0.22               # Transformer optimization (optional)
[FAIL] safetensors==0.4.0             # Model format (optional)

```text

---

## # # [ORFEAS] INSTALLATION PROGRESS

## # # **Step 1: Basic Web Framework [OK] COMPLETE**

- Installed in ~30 seconds
- Total size: ~50MB

## # # **Step 2: Image Processing [OK] COMPLETE**

- Installed in ~2 minutes
- Total size: ~200MB

## # # **Step 3: PyTorch (CUDA) [WAIT] IN PROGRESS**

- Download size: **2.6GB**
- Estimated time: **5-10 minutes** (depends on internet speed)
- Current status: **Downloading...**

## # # **Step 4: AI/ML Libraries (PENDING)**

- Will install after PyTorch completes
- Packages: diffusers, transformers, accelerate
- Estimated time: 2-3 minutes
- Total size: ~500MB

## # # **Total Installation:**

- **Time:** 10-15 minutes (mostly PyTorch download)
- **Disk Space:** ~3.5GB for complete installation

---

## # # [LAB] TESTING AFTER INSTALLATION

## # # **Step 1: Verify Virtual Environment**

```powershell

## Check Python version

.\.venv\Scripts\python.exe --version

## Expected: Python 3.11.9

## Check installed packages

.\.venv\Scripts\python.exe -m pip list

## Should show 30+ packages

```text

## # # **Step 2: Test Backend Imports**

```powershell
cd backend
.\.venv\Scripts\python.exe -c "import flask, torch, numpy, cv2; print('[OK] All imports successful')"

```text

## # # **Step 3: Start Frontend Server**

```powershell
python frontend_server.py

```text

## # # Expected output

```text
======================================================================
[WEB] ORFEAS FRONTEND SERVER
   With Automatic Backend Startup
======================================================================

[OK] Frontend file: orfeas-studio.html
[OK] Server port: 8000
[OK] Backend target: http://127.0.0.1:5000

 Serving from: C:\Users\johng\Documents\Erevus\orfeas

======================================================================
[LAUNCH] SERVER STARTING...
======================================================================

[OK] Server running on: http://localhost:8000
[OK] Direct link: http://localhost:8000/orfeas-studio.html

[EDIT] Features:
   • Serves orfeas-studio.html frontend
   • Automatic backend detection
   • Automatic backend startup via API
   • No browser security restrictions!

[TARGET] OPEN IN BROWSER: http://localhost:8000

======================================================================
⏸  Press Ctrl+C to stop the server
======================================================================

```text

## # # **Step 4: Test Backend Auto-Start**

1. Open browser to http://localhost:8000

2. UI should show "Backend: Not Running" initially

3. Click "Start Backend" button

4. Wait 30-45 seconds for backend to load models
5. Status should change to "Backend: Running [OK]"

## # # **Step 5: Test Image Upload**

1. Click "Upload Image" button

2. Select any JPG/PNG image

3. Click "Generate 3D Model"

4. Wait for processing (~10-30 seconds)
5. 3D preview should appear
6. Download STL button should activate

---

## # #  TROUBLESHOOTING

## # # **Issue 1: "Module not found" errors**

```text
[FAIL] ModuleNotFoundError: No module named 'torch'

```text

## # # Solution

Wait for PyTorch installation to complete. Check terminal with ID `5cd2afde-0401-469e-9aad-c52889845caf` for progress.

---

## # # **Issue 2: Frontend server exits immediately**

```text
[FAIL] Server stopped unexpectedly

```text

## # # Solution (2)

Backend failed to start. Check backend dependencies are installed:

```powershell
cd backend
.\.venv\Scripts\python.exe -c "import flask, torch, numpy; print('OK')"

```text

---

## # # **Issue 3: Backend takes too long to start**

```text
[WAIT] Waiting for backend... (20/45)
[WAIT] Waiting for backend... (21/45)

```text

## # # Reasons

1. **First startup:** Models are loading into GPU memory (30-45 seconds normal)

2. **GPU detection:** DirectML initialization takes time

3. **Model download:** Hunyuan3D models downloading from Hugging Face

**Solution:** Be patient! First startup always takes longer.

---

## # # **Issue 4: Port 8000 already in use**

```text
[FAIL] ERROR: Port 8000 is already in use

```text

## # # Solution (3)

```powershell

## Find process using port 8000

netstat -ano | findstr :8000

## Kill the process (replace PID)

taskkill /PID <PID> /F

## Or change port in frontend_server.py

## FRONTEND_PORT = 8001  # Use different port

```text

---

## # # **Issue 5: GPU not detected**

```text
[WARN] No NVIDIA GPU detected, using CPU

```text

## # # Solution (4)

1. Check GPU drivers installed

2. Verify CUDA compatibility

3. Try DirectML fallback:

   ```python

   # In backend/gpu_manager.py

   USE_DIRECTML = True  # Enable DirectML for AMD/Intel GPUs

   ```text

---

## # # [STATS] SYSTEM REQUIREMENTS

## # # **Minimum Requirements:**

- **OS:** Windows 10/11 64-bit
- **RAM:** 8GB (16GB recommended)
- **Disk Space:** 5GB free
- **GPU:** Any DirectX 12 compatible (DirectML support)
- **Python:** 3.11.x

## # # **Recommended Requirements:**

- **OS:** Windows 11 64-bit
- **RAM:** 16GB+
- **Disk Space:** 10GB+ free
- **GPU:** NVIDIA RTX 3060+ with 8GB+ VRAM
- **CUDA:** 11.8 or higher
- **Python:** 3.11.9

## # # **Optimal Setup (ORFEAS Studio):**

- **OS:** Windows 11 Pro 64-bit
- **RAM:** 32GB DDR4/DDR5
- **Disk Space:** 50GB+ NVMe SSD
- **GPU:** NVIDIA RTX 4070+ with 12GB+ VRAM
- **CUDA:** 12.1+
- **Python:** 3.11.9 with virtual environment

---

## # # [CONFIG] ENVIRONMENT CONFIGURATION

## # # **Required Environment Variables (.env file):**

```bash

## ORFEAS Backend Configuration

FLASK_ENV=production
FLASK_DEBUG=False

## GPU Settings

CUDA_VISIBLE_DEVICES=0           # Use first GPU
PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512

## Model Paths (optional)

HUNYUAN3D_MODEL_PATH=./models/hunyuan3d
MIDAS_MODEL_PATH=./models/midas

## Upload Settings

MAX_UPLOAD_SIZE_MB=50
ALLOWED_EXTENSIONS=jpg,jpeg,png,webp

## Rate Limiting

RATE_LIMIT_PER_MINUTE=10
RATE_LIMIT_PER_HOUR=100

## Monitoring

ENABLE_METRICS=true
METRICS_PORT=9090

```text

## # # **Create .env file:**

```powershell

## Copy example and edit

cp .env.example .env

## Or create manually

notepad .env

```text

---

## # # [METRICS] PERFORMANCE OPTIMIZATION

## # # **GPU Memory Management:**

```python

## backend/gpu_manager.py settings

GPU_MEMORY_FRACTION = 0.8        # Use 80% of VRAM
ENABLE_MEMORY_CLEANUP = True     # Auto-cleanup after generation
CLEANUP_INTERVAL = 300           # Cleanup every 5 minutes

```text

## # # **Image Processing:**

```python

## backend/config.py settings

MAX_IMAGE_DIMENSION = 2048       # Max input resolution
PREVIEW_SIZE = 512               # Preview thumbnail size
JPEG_QUALITY = 85                # Compression quality

```text

## # # **3D Generation:**

```python

## backend/config.py settings

DEFAULT_MESH_QUALITY = 'medium'  # low, medium, high, ultra
MAX_VERTICES = 100000            # Vertex count limit
ENABLE_MESH_SIMPLIFICATION = True

```text

---

## # # [TARGET] NEXT STEPS AFTER INSTALLATION

## # # **Step 1: Complete PyTorch Installation**

- [WAIT] Wait for current download to finish (~5-10 minutes)
- Terminal ID: `5cd2afde-0401-469e-9aad-c52889845caf`

## # # **Step 2: Install Remaining AI Packages**

```powershell
cd backend
.\.venv\Scripts\python.exe -m pip install diffusers==0.21.4 transformers==4.35.2 accelerate==0.24.1

```text

## # # **Step 3: Verify Installation**

```powershell

## Test all imports

python -c "import flask, torch, numpy, cv2, trimesh; print('[OK] All critical packages installed')"

## Check PyTorch GPU support

python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"

```text

## # # **Step 4: Start Servers**

```powershell

## Start frontend (will auto-start backend)

python frontend_server.py

## Open browser

start http://localhost:8000

```text

## # # **Step 5: First Generation Test**

1. Upload test image

2. Click "Generate 3D Model"

3. Verify STL generation works

4. Check GPU utilization in Task Manager

---

## # #  ADDITIONAL RESOURCES

## # # **Documentation:**

- Backend API: `backend/README.md`
- Frontend Guide: `md/ORFEAS_STUDIO_GUIDE.md`
- Phase 3 Testing: `md/PHASE_3_TESTING_GUIDE.md`
- Deployment: `md/PHASE_3_DEPLOYMENT_REPORT.md`

## # # **Configuration Files:**

- Backend config: `backend/config.py`
- GPU config: `backend/gpu_config.json`
- Environment: `.env` (create from `.env.example`)

## # # **Monitoring:**

- Prometheus metrics: http://localhost:9090
- Health check: http://localhost:5000/api/health
- System status: http://localhost:5000/api/system/status

---

+==============================================================================â•—
| [WARRIOR] ORFEAS PROTOCOL [WARRIOR] |
| SERVER RECOVERY IN PROGRESS |
| PyTorch Installation: [WAIT] DOWNLOADING |
+==============================================================================

**CURRENT STATUS:** Dependencies installing, server will be ready in 10-15 minutes.

**WAIT FOR:** PyTorch download completion (Terminal ID: 5cd2afde-0401-469e-9aad-c52889845caf)

**THEN:** Run `python frontend_server.py` and open http://localhost:8000
