# Phase 1 Quick Start - 30 Minute Setup

**Objective:** Get GPU optimization running in your dev environment
**Time:** 30 minutes
**Requirements:** Python 3.10+, CUDA 12.0, RTX 3090

---

## Step 1: Verify GPU Setup (2 minutes)

```powershell
cd backend
python -c "import torch; print(f'CUDA Available: {torch.cuda.is_available()}'); print(f'Device: {torch.cuda.get_device_name(0)}'); print(f'Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB')"

```text

### Expected Output

```text
CUDA Available: True
Device: NVIDIA RTX 3090
Memory: 24.0 GB

```text

---

## Step 2: Test GPU Manager Standalone (3 minutes)

```powershell
cd backend
python gpu_optimization_advanced.py

```text

### Expected Output

```text
DynamicVRAMManager(
  Total: 24.0 GB
  Available: 22.5 GB
  Usage: 6.2%
  Precision: fp32
)

Memory Stats:
{'total_vram_gb': 24.0, 'allocated_gb': 0.8, 'reserved_gb': 0.4, 'available_gb': 22.5, 'usage_percent': 6.2, 'precision_mode': 'fp32', ...}

Recommended Precision: fp32
Optimal Batch Size: 12

```text

---

## Step 3: Run Unit Tests (5 minutes)

```powershell
cd backend
pytest tests/test_gpu_optimization.py -v --tb=short 2>&1 | head -50

```text

### Expected Output

```text
test_gpu_optimization.py::TestVRAMBudget::test_vram_budget_creation PASSED
test_gpu_optimization.py::TestVRAMBudget::test_vram_budget_custom_reserves PASSED
test_gpu_optimization.py::TestDynamicVRAMManager::test_manager_initialization PASSED
test_gpu_optimization.py::TestDynamicVRAMManager::test_get_available_vram PASSED
test_gpu_optimization.py::TestDynamicVRAMManager::test_get_vram_usage_percent PASSED
test_gpu_optimization.py::TestDynamicVRAMManager::test_recommend_precision_fp32 PASSED
...
===================== 20 passed in 2.34s =====================

```text

---

## Step 4: Start Backend with GPU Optimization (5 minutes)

```powershell
cd backend
python main.py

```text

### Expected Output

```text
[GPU Manager initialized: DynamicVRAMManager(Total: 24.0 GB, Available: 22.5 GB, Usage: 6.2%, Precision: fp32)]
[GPU VRAM monitoring started (5s interval)]

* Running on http://127.0.0.1:5000 (Press CTRL+C to quit)

```text

---

## Step 5: Test GPU Stats Endpoint (3 minutes)

### In another terminal

```powershell

## Test GPU stats endpoint

curl http://localhost:5000/api/v1/gpu/stats | python -m json.tool

```text

### Expected Response

```json
{
  "gpu": {
    "total_vram_gb": 24.0,
    "allocated_gb": 1.2,
    "reserved_gb": 0.8,
    "available_gb": 21.5,
    "usage_percent": 7.3,
    "precision_mode": "fp32",
    "mixed_precision_enabled": false,
    "gradient_checkpointing": false,
    "quantization_enabled": false
  },
  "queue_depth": 0,
  "recommended_precision": "fp32",
  "optimal_batch_size": 12,
  "timestamp": "2025-10-19T15:30:45.123456"
}

```text

---

## Step 6: Test Cache Endpoint (2 minutes)

```powershell

## Test cache stats

curl http://localhost:5000/api/v1/cache/stats | python -m json.tool

```text

### Expected Response

```json
{
  "entries": 0,
  "total_hits": 0,
  "ttl_seconds": 3600,
  "avg_hits_per_entry": 0
}

```text

---

## Step 7: Test Generation with Monitoring (5 minutes)

### In another terminal

```powershell

## Upload test image and monitor GPU

$imageFile = "backend/test_images/sample.jpg"
$response = curl -X POST -F "image=@$imageFile" -F "quality=7" http://localhost:5000/api/v1/generate
$response | python -m json.tool

## Check GPU stats after generation

curl http://localhost:5000/api/v1/gpu/stats | python -m json.tool

```text

### Expected in Logs

```text
[INFO] Before generation - GPU usage: 7.3%
[INFO] GPU memory available: 21.5 GB
[INFO] After generation - GPU usage: 45.2%
[INFO] GPU cache cleared

```text

---

## Verification Checklist

- [ ] CUDA detected and GPU available
- [ ] GPU manager initializes without errors
- [ ] 20+ unit tests pass
- [ ] Backend starts with GPU monitoring
- [ ] GPU stats endpoint returns JSON
- [ ] Cache stats endpoint working
- [ ] Generation still works
- [ ] Logs show GPU optimization messages
- [ ] Memory usage stays under 18GB

---

## Troubleshooting

### "CUDA not available"

```powershell

## Check CUDA installation

nvidia-smi
nvcc --version

## Verify PyTorch CUDA support

python -c "import torch; print(torch.__version__); print(torch.cuda.is_available())"

## Install CUDA-enabled PyTorch

pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu120

```text

### "GPU out of memory"

```powershell

## Manually clear GPU cache

python -c "import torch; torch.cuda.empty_cache(); print('GPU cache cleared')"

## Check memory usage

python -c "import torch; print(torch.cuda.memory_allocated() / 1e9, 'GB allocated')"

```text

### Tests fail

```powershell

## Run with verbose output

pytest tests/test_gpu_optimization.py -v --tb=long

## Check GPU memory before tests

curl http://localhost:5000/api/v1/gpu/stats | python -m json.tool

```text

---

## Next Steps

After verification:

1. **Tuesday:** Write and run additional unit tests (from PHASE_1_INTEGRATION_CHECKLIST.md)

2. **Wednesday:** Implement progressive rendering endpoint

3. **Thursday:** Integrate request deduplication cache

4. **Friday:** Deploy to staging and validate metrics

See `PHASE_1_INTEGRATION_CHECKLIST.md` for detailed steps.

---

## Performance Baseline

After this quick start, you should see:

| Metric | Value |
|--------|-------|
| VRAM Available | ~21.5 GB |
| GPU Usage | 6-10% idle |
| Precision Mode | FP32 (recommended) |
| Optimal Batch Size | 10-15 |
| Cache Entries | 0 (will grow with usage) |
| Response Time | ~60s (before optimization) |

**Goal for Friday:** VRAM 14GB, Response 30s, First Result 0.5s
