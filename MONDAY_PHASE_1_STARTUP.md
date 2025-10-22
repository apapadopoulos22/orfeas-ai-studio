# 🚀 MONDAY PHASE 1 IMPLEMENTATION - STARTUP GUIDE

**Status:** ✅ READY TO BEGIN
**Date:** Monday, October 21, 2025
**Tasks:** GPU Module Integration (6 hours)
**Expected Completion:** GPU stats endpoint operational

---

## ⚡ Quick Pre-Implementation Checklist (5 minutes)

### ✅ Verify Prerequisites

```powershell

## Step 1: Check CUDA availability

nvidia-smi

## Expected output

## NVIDIA RTX 3090 with 24GB VRAM

## CUDA Version: 12.0

## Step 2: Check Python

python --version

## Expected: Python 3.10+

## Step 3: Check PyTorch

python -c "import torch; print(f'PyTorch version: {torch.__version__}'); print(f'CUDA available: {torch.cuda.is_available()}')"

## Expected

## PyTorch version: 2.x.x

## CUDA available: True

## Step 4: Verify project structure

cd c:\Users\johng\Documents\oscar
dir backend\gpu_optimization_advanced.py
dir backend\progressive_renderer.py
dir backend\request_deduplication.py

## All should exist and be ready

```text

### If any check fails

- ❌ CUDA not available → Run `nvidia-smi` to diagnose
- ❌ Python wrong version → Update Python to 3.10+
- ❌ PyTorch missing CUDA → Reinstall with `pip install torch --index-url https://download.pytorch.org/whl/cu120`
- ❌ Files missing → Check files exist in backend directory

---

## 📋 Monday Task Breakdown (6 hours total)

### Task 1.1: Import GPU Module (10 minutes)

**File to modify:** `backend/main.py`

**Location:** After existing imports, around line 75

### Current state

Look for this section in main.py:

```python
from flask import Flask, request, jsonify, send_file, send_from_directory, Response
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from werkzeug.utils import secure_filename

```text

### Add after these imports

```python

## [ORFEAS PHASE 1] GPU Optimization Module - Dynamic VRAM Management

from gpu_optimization_advanced import (
    get_vram_manager,
    PrecisionMode,
    DynamicVRAMManager
)

```text

### Verification

```powershell
cd backend
python -c "from gpu_optimization_advanced import get_vram_manager; print('✓ GPU module imports successfully')"

```text

### Expected output

```text
✓ GPU module imports successfully

```text

### Status after completion

- [ ] Import added
- [ ] No import errors
- [ ] Verification successful

---

### Task 1.2: Initialize VRAM Manager on Startup (15 minutes)

**File to modify:** `backend/main.py`

**Location:** After Flask app creation (around line 150-200, look for app initialization)

### Find this section

```python
app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

```text

### Add this initialization function AFTER the app creation

```python
@app.before_serving
def initialize_gpu_optimization():
    """Initialize GPU optimization on startup"""
    try:
        vram_mgr = get_vram_manager()
        logger.info(f"GPU Manager initialized: {vram_mgr}")

        # Log initial memory state

        stats = vram_mgr.get_memory_stats()
        logger.info(f"Initial GPU stats: {stats}")

        # Start monitoring thread

        vram_mgr.monitor_vram_usage(interval_seconds=5.0)
        logger.info("GPU VRAM monitoring started (5s interval)")

    except Exception as e:
        logger.error(f"Failed to initialize GPU optimization: {e}")
        traceback.print_exc()

```text

### Verification

```powershell
cd backend
python main.py

## You should see in logs

## GPU Manager initialized: DynamicVRAMManager(Total: 24.0 GB, ...)

## Initial GPU stats: {...}

## GPU VRAM monitoring started (5s interval)

## Press Ctrl+C to stop

```text

### Status after completion

- [ ] Initialization code added
- [ ] Backend starts without errors
- [ ] Logs show GPU initialization messages
- [ ] No CUDA errors

---

### Task 1.3: Integrate VRAM Management in Generation Endpoint (30 minutes)

**File to modify:** `backend/main.py`

**Location:** Find the generation endpoint (search for `@app.route('/api/v1/generate'`)

### Current endpoint structure

```python
@app.route('/api/v1/generate', methods=['POST'])
def generate_3d():
    """Generate 3D model from image"""

    # ... existing code ...

    try:

        # Generate logic here

        result = processor.generate_shape(image)
        return jsonify(result)
    finally:
        torch.cuda.empty_cache()

```text

### Add GPU monitoring

```python
@app.route('/api/v1/generate', methods=['POST'])
def generate_3d():
    """Generate 3D model from image (integrated with GPU optimization)"""
    vram_mgr = get_vram_manager()

    # Log current GPU state BEFORE generation

    current_stats = vram_mgr.get_memory_stats()
    logger.info(f"BEFORE generation - GPU usage: {current_stats['usage_percent']:.1f}%")
    logger.info(f"Available VRAM: {current_stats['available_gb']:.1f} GB")

    # Check if we have enough VRAM

    available_gb = vram_mgr.get_available_vram_gb()
    if available_gb < 4:
        logger.warning(f"Low GPU memory: {available_gb:.1f} GB available")

        # Recommend precision downgrade

        recommended = vram_mgr.recommend_precision_mode()
        logger.info(f"Recommended precision: {recommended.value}")

    try:

        # ... existing generation code ...

        result = processor.generate_shape(image)

        # Log GPU state AFTER generation

        final_stats = vram_mgr.get_memory_stats()
        logger.info(f"AFTER generation - GPU usage: {final_stats['usage_percent']:.1f}%")

        return jsonify(result)

    except torch.cuda.OutOfMemoryError as e:
        logger.error(f"GPU Out of Memory: {e}")

        # Trigger memory cleanup

        vram_mgr.clear_cache()
        torch.cuda.empty_cache()
        return jsonify({'error': 'GPU memory exceeded, try again'}), 507

    finally:

        # Always clear cache after generation

        vram_mgr.clear_cache()
        logger.info("GPU cache cleared after generation")

```text

### Verification

```powershell

## Test generation with monitoring

cd backend
python main.py &

## In another terminal

## First, prepare a test image or use existing one

## Then call the endpoint

$imageFile = "test_images/sample.jpg"
$response = curl -X POST -F "image=@$imageFile" -F "quality=7" http://localhost:5000/api/v1/generate

## Check logs

## docker-compose logs backend | tail -20

## or check backend/logs/app.log

```text

### Expected log output

```text
BEFORE generation - GPU usage: 7.3%
Available VRAM: 21.5 GB
[Generation happens]
AFTER generation - GPU usage: 45.2%
GPU cache cleared after generation

```text

### Status after completion

- [ ] GPU monitoring added to endpoint
- [ ] Generation still works normally
- [ ] Logs show GPU statistics
- [ ] OOM errors handled gracefully
- [ ] Cache cleanup on every request

---

### Task 1.4: Add GPU Stats Endpoint (20 minutes)

**File to modify:** `backend/main.py`

**Location:** Add new route after generation endpoint (around line 2000+)

### Add this new endpoint

```python
@app.route('/api/v1/gpu/stats', methods=['GET'])
@track_request_metrics
def get_gpu_stats():
    """Get real-time GPU memory statistics"""
    vram_mgr = get_vram_manager()
    stats = vram_mgr.get_memory_stats()

    return jsonify({
        'timestamp': datetime.now().isoformat(),
        'gpu': stats,
        'queue_depth': len(get_async_queue().jobs) if hasattr(get_async_queue(), 'jobs') else 0,
        'recommended_precision': vram_mgr.recommend_precision_mode().value,
        'optimal_batch_size': vram_mgr.calculate_optimal_batch_size(
            model_size_gb=6,
            queue_depth=len(get_async_queue().jobs) if hasattr(get_async_queue(), 'jobs') else 0,
            sample_size_mb=50
        )
    })

```text

### Verification

```powershell

## Test GPU stats endpoint

curl http://localhost:5000/api/v1/gpu/stats | python -m json.tool

## Expected response

## {

## "timestamp": "2025-10-21T09:30:45.123456",

## "gpu": {

## "total_vram_gb": 24.0,

## "allocated_gb": 1.2,

## "reserved_gb": 0.8,

## "available_gb": 21.5,

## "usage_percent": 7.3,

## "precision_mode": "fp32",

## "mixed_precision_enabled": false,

## "gradient_checkpointing": false,

## "quantization_enabled": false

## },

## "queue_depth": 0,

## "recommended_precision": "fp32",

## "optimal_batch_size": 12,

## }

```text

### Status after completion

- [ ] Endpoint created at `/api/v1/gpu/stats`
- [ ] Endpoint returns valid JSON
- [ ] All GPU stats fields present
- [ ] No errors in response
- [ ] Can be called repeatedly

---

### Task 1.5: Test and Verify Integration (45 minutes)

### Full integration test

```powershell
cd backend

## Step 1: Start backend

python main.py

## Step 2: In another terminal, run verification script

## Create a test script: test_monday_integration.py

$content = @'
"""Monday Phase 1 Integration Test"""
import requests
import json
import time

BASE_URL = "http://localhost:5000"

print("=" * 60)
print("MONDAY PHASE 1 INTEGRATION TEST")
print("=" * 60)

## Test 1: GPU Stats Endpoint

print("\n[Test 1] GPU Stats Endpoint")
try:
    response = requests.get(f"{BASE_URL}/api/v1/gpu/stats")
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Endpoint responds with 200 OK")
        print(f"✓ Total VRAM: {data['gpu']['total_vram_gb']:.1f} GB")
        print(f"✓ Available: {data['gpu']['available_gb']:.1f} GB")
        print(f"✓ Usage: {data['gpu']['usage_percent']:.1f}%")
        print(f"✓ Recommended Precision: {data['recommended_precision']}")
        print(f"✓ Optimal Batch Size: {data['optimal_batch_size']}")
    else:
        print(f"✗ Failed: {response.status_code}")
except Exception as e:
    print(f"✗ Error: {e}")

## Test 2: Multiple calls (should show consistent data)

print("\n[Test 2] Consistency Check (3 rapid calls)")
try:
    for i in range(3):
        response = requests.get(f"{BASE_URL}/api/v1/gpu/stats")
        if response.status_code == 200:
            usage = response.json()['gpu']['usage_percent']
            print(f"  Call {i+1}: {usage:.1f}% usage")
        time.sleep(0.5)
    print("✓ Endpoint stable and responsive")
except Exception as e:
    print(f"✗ Error: {e}")

## Test 3: Check response time

print("\n[Test 3] Performance Check")
try:
    start = time.time()
    response = requests.get(f"{BASE_URL}/api/v1/gpu/stats")
    elapsed = (time.time() - start) * 1000
    print(f"✓ Response time: {elapsed:.1f}ms (target: <100ms)")
    if elapsed > 100:
        print(f"  ⚠ Consider optimization if >200ms")
except Exception as e:
    print(f"✗ Error: {e}")

print("\n" + "=" * 60)
print("INTEGRATION TEST COMPLETE")
print("=" * 60)
'@

$content | Out-File backend/test_monday_integration.py -Encoding UTF8

## Run the test

python backend/test_monday_integration.py

```text

### Expected output

```text
============================================================
MONDAY PHASE 1 INTEGRATION TEST
============================================================

[Test 1] GPU Stats Endpoint
✓ Endpoint responds with 200 OK
✓ Total VRAM: 24.0 GB
✓ Available: 21.5 GB
✓ Usage: 7.3%
✓ Recommended Precision: fp32
✓ Optimal Batch Size: 12

[Test 2] Consistency Check (3 rapid calls)
  Call 1: 7.3% usage
  Call 2: 7.4% usage
  Call 3: 7.2% usage
✓ Endpoint stable and responsive

[Test 3] Performance Check
✓ Response time: 12.5ms (target: <100ms)

============================================================
INTEGRATION TEST COMPLETE
============================================================

```text

### Status after completion

- [ ] Backend starts without errors
- [ ] GPU module initializes on startup
- [ ] GPU stats endpoint returns valid JSON
- [ ] Generation endpoint still works with GPU logging
- [ ] All logs clean (no errors)
- [ ] Response times acceptable

---

## ✅ Monday Completion Checklist

### Before Leaving for Day

- [ ] GPU module imported in main.py
- [ ] VRAM manager initializes on startup (check logs)
- [ ] GPU monitoring integrated in generation endpoint
- [ ] GPU stats endpoint working at `/api/v1/gpu/stats`
- [ ] Test script successful (all 3 tests pass)
- [ ] No critical errors in `backend/logs/app.log`
- [ ] Performance baseline established

### Documentation

- [ ] Review what was accomplished
- [ ] Note any issues encountered and solutions
- [ ] Record actual VRAM usage during test
- [ ] Prepare for Tuesday (unit tests)

---

## 📊 Monday Success Metrics

**Target:** GPU module integrated and operational

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| GPU stats endpoint working | ✓ | ? | ⏳ |
| Backend starts cleanly | ✓ | ? | ⏳ |
| GPU monitoring active | ✓ | ? | ⏳ |
| Generation works with logging | ✓ | ? | ⏳ |
| No critical errors | ✓ | ? | ⏳ |

### Daily Standup Points

1. What was accomplished today?

2. What metrics were achieved?

3. Any blockers encountered?

4. Plans for Tuesday?

---

## 🔧 Troubleshooting

### Backend won't start

```powershell

## Check error

cd backend
python main.py

## Common fixes

## 1. Import error → Check gpu_optimization_advanced.py exists

## 2. CUDA error → Run nvidia-smi

## 3. Dependencies → pip install -r requirements.txt

## 4. Port conflict → Change port in main.py if 5000 taken

```text

### GPU stats endpoint 404

```powershell

## Verify endpoint is added

cd backend
python -c "
import main

## Check if route exists

for rule in main.app.url_map.iter_rules():
    if 'gpu' in rule.rule:
        print(f'Found: {rule.rule}')
"

## If not found, verify the route was added to main.py

```text

### High GPU usage immediately

```powershell

## This is expected if model is being loaded

## Monitor for a minute - should stabilize after initial load

## If stays >80%, check

## - Competing processes

## - Model not cached properly

## - Memory leak in monitoring thread

```text

### Endpoint slow (>200ms)

```powershell

## Expected ~10-20ms

## If slower

## 1. Check GPU load (nvidia-smi)

## 2. Check system load (Task Manager)

## 3. Profile with: python -m cProfile test_script.py

```text

---

## 📝 End-of-Day Report

### Template for end of Monday

```text
MONDAY, OCTOBER 21 - PHASE 1 GPU INTEGRATION

COMPLETED:
✓ GPU module imported
✓ VRAM manager initialized
✓ Generation endpoint monitoring active
✓ GPU stats endpoint operational
✓ Integration tests passing

METRICS ACHIEVED:

- Total VRAM: 24.0 GB
- Available at startup: [X] GB
- GPU usage idle: [X]%
- Endpoint response time: [X]ms
- Monitoring thread: Active

ISSUES ENCOUNTERED:
[List any issues and how they were resolved]

BLOCKERS (if any):
[List any remaining issues]

NEXT STEPS (TUESDAY):

- Run 20+ unit tests
- Benchmark performance
- Generate baseline report
- Tuesday completion target: Unit tests passing

STATUS: ✅ ON TRACK

```text

---

## 🎯 Next Phase (Tuesday Preview)

### Tuesday will focus on

1. Running comprehensive unit tests (20+)

2. Performance benchmarking

3. Generating performance baseline

4. Documentation of baseline metrics

### Files you'll need Tuesday

- `backend/tests/test_gpu_optimization.py`
- `backend/tests/test_phase1_performance.py`

See `PHASE_1_INTEGRATION_CHECKLIST.md § Tuesday` for details.

---

**Status:** ✅ READY TO START
**Time Estimate:** 6 hours
**Target Completion:** GPU stats endpoint working

**👉 Next Action:** Run Step 1 - Verify Prerequisites
