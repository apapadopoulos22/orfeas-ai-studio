# ORFEAS Load Testing - Execution Guide

## # # Phase 2.6: Load Testing Suite

**Status**: '√∫√ñ COMPLETE - Ready to Execute
**Total Tests**: 5 scenarios
**Total Duration**: ~87 minutes (~1.5 hours)

---

## # # üìÅ Test Suite Files

All files located in: `backend/tests/load/`

| File                     | Lines | Description                                   |
| ------------------------ | ----- | --------------------------------------------- |
| `load_test_utils.py`     | 370   | Shared utilities (client, metrics, helpers)   |
| `test_load_baseline.py`  | 180   | Scenario 1: Single user baseline validation   |
| `test_load_normal.py`    | 250   | Scenario 2: 3 concurrent users, 10 min        |
| `test_load_peak.py`      | 240   | Scenario 3: 10 concurrent users, 5 min        |
| `test_load_spike.py`     | 380   | Scenario 4: Traffic spike test (2'√ú√≠20'√ú√≠2 users) |
| `test_load_sustained.py` | 440   | Scenario 5: 1-hour endurance with monitoring  |
| **TOTAL**                | 2400+ | Complete load testing framework               |

---

## # # Ô£ø√º√∂√Ñ Quick Start - Execute Tests

## # # Prerequisites

1. **Backend must be running and stable**

   ```powershell
   cd c:\Users\johng\Documents\Erevus\orfeas\backend
   python main.py

   # Wait for "[OK] Models loaded" message (~30-40 seconds)

   ```text

1. **Verify backend health**

   ```powershell
   curl http://localhost:5000/health

   # Should return: {"status": "healthy"}

   ```text

1. **Test image must exist**

   ```powershell

   # If missing, create it:

   python create_test_image.py temp/test_images/quality_test_unique2.png

   ```text

---

## # # Ô£ø√º√¨√π Execution Options

## # # Option A: Run Baseline Test Only (7 minutes)

**Best for**: Quick validation of system before full suite

```powershell
cd c:\Users\johng\Documents\Erevus\orfeas
python backend\tests\load\test_load_baseline.py

```text

**Expected Results**:

- Duration: ~7 minutes (5 generations ‚àö√≥ 82s)
- Output: `results_baseline.json`
- Validation: '√∫√ñ PASS if avg time 75-90s, 0 errors

---

## # # Option B: Run Full Test Suite Sequentially (~87 minutes)

**Best for**: Complete system validation

```powershell
cd c:\Users\johng\Documents\Erevus\orfeas

## Test 1: Baseline (7 min)

python backend\tests\load\test_load_baseline.py

## Test 2: Normal Load (10 min)

python backend\tests\load\test_load_normal.py

## Test 3: Peak Load (5 min)

python backend\tests\load\test_load_peak.py

## Test 4: Spike Test (5 min)

python backend\tests\load\test_load_spike.py

## Test 5: Sustained Load (60 min) - LONGEST

python backend\tests\load\test_load_sustained.py

```text

**Total Duration**: ~87 minutes (~1.5 hours)

---

## # # Option C: Run Selective Tests

**Best for**: Targeted validation of specific concerns

```powershell

## Check baseline performance

python backend\tests\load\test_load_baseline.py

## Check concurrent user handling

python backend\tests\load\test_load_normal.py

## Check peak capacity

python backend\tests\load\test_load_peak.py

## Skip sustained test if time-constrained

```text

---

## # # Ô£ø√º√¨√§ Test Scenarios - Detailed

## # # 1. Baseline Test (test_load_baseline.py)

- **Users**: 1
- **Duration**: ~7 minutes
- **Purpose**: Validate 82s warm baseline from Phase 2.3
- **Success Criteria**:

  - Average time: 75-90s (¬±10% of 82s)
  - Error rate: 0%
  - Success rate: 100%
  - All 5 generations complete

## # # 2. Normal Load Test (test_load_normal.py)

- **Users**: 3 concurrent
- **Duration**: 10 minutes
- **Purpose**: Simulate typical production traffic
- **Success Criteria**:

  - Server uptime: 100%
  - Error rate: <1%
  - Average response: <90s
  - P95 response: <120s
  - Success rate: >99%

## # # 3. Peak Load Test (test_load_peak.py)

- **Users**: 10 concurrent
- **Duration**: 5 minutes
- **Purpose**: Test system limits and capacity
- **Success Criteria**:

  - Minimum 50 requests attempted
  - Error rate: <5% (peak tolerance)
  - Average response: <150s
  - P95 response: <180s
  - At least 50 successful completions

## # # 4. Spike Test (test_load_spike.py)

- **Users**: 2 '√ú√≠ 20 '√ú√≠ 2 (spike pattern)
- **Duration**: 5 minutes (2 min baseline, 1 min spike, 2 min recovery)
- **Purpose**: Validate resilience and auto-recovery
- **Success Criteria**:

  - System survives spike without crashing
  - Spike error rate: <10%
  - Recovery error rate: <2%
  - Performance returns to baseline ¬±20%

## # # 5. Sustained Load Test (test_load_sustained.py)

- **Users**: 5 concurrent
- **Duration**: 60 minutes
- **Purpose**: Detect memory leaks and long-term stability
- **Success Criteria**:

  - Server uptime: 99.9% (<1 error per 1000 requests)
  - Performance degradation: <10% over time
  - Memory growth: <5%
  - GPU memory stable: <10% growth
  - Minimum 150 requests completed

---

## # # üìÅ Results Output

Each test saves results to JSON in `backend/tests/load/`:

| Test File                | Output File              | Contains                                                         |
| ------------------------ | ------------------------ | ---------------------------------------------------------------- |
| `test_load_baseline.py`  | `results_baseline.json`  | Duration, success rate, percentiles, validation                  |
| `test_load_normal.py`    | `results_normal.json`    | Concurrent user metrics, error analysis                          |
| `test_load_peak.py`      | `results_peak.json`      | Peak load handling, system limits                                |
| `test_load_spike.py`     | `results_spike.json`     | Phase-by-phase analysis (baseline/spike/recovery)                |
| `test_load_sustained.py` | `results_sustained.json` | Performance over time, resource monitoring, degradation analysis |

## # # Example JSON Structure

```json
{
  "scenario": "baseline",
  "duration_seconds": 410.5,
  "total_requests": 5,
  "successful_requests": 5,
  "failed_requests": 0,
  "success_rate": 100.0,
  "error_rate": 0.0,
  "avg_duration": 82.1,
  "min_duration": 79.5,
  "max_duration": 85.3,
  "p50_duration": 82.0,
  "p95_duration": 84.8,
  "p99_duration": 85.2,
  "throughput_per_minute": 0.73,
  "errors": {},
  "validation": {
    "avg_time_ok": true,
    "zero_errors": true,
    "full_success": true,
    "all_completed": true,
    "overall": true
  }
}

```text

---

## # # Ô£ø√º√¨√† Monitoring During Tests

## # # Prometheus Metrics to Watch

Access metrics at: `http://localhost:5000/metrics`

**Key Metrics** (from Phase 2.5 - 48+ total):

1. **HTTP Performance**:

- `http_request_duration_seconds` (response times)
- `http_requests_total` (request counts)
- `http_request_errors_total` (error tracking)

1. **GPU Usage**:

- `gpu_usage_percent` (GPU utilization)
- `gpu_memory_allocated_mb` (VRAM usage)
- `gpu_memory_cached_mb` (cache usage)

1. **3D Generation**:

- `model_3d_generations_total` (generation counts)
- `model_generation_duration_seconds` (generation times)
- `model_generation_failures_total` (failure tracking)

1. **WebSocket** (Phase 2.5):

- `websocket_connections_active` (active connections)
- `websocket_messages_sent_total` (message counts)
- `websocket_connection_duration_seconds` (connection lifetime)

1. **Pipeline Stages** (Phase 2.5):

- `pipeline_stage_duration_seconds` (stage performance)
- `pipeline_stage_errors_total` (stage failures)

## # # Grafana Dashboard

Access at: `http://localhost:3000` (admin/orfeas_admin_2025)

Real-time visualizations during tests:

- Request rate over time
- Response time percentiles
- GPU utilization graphs
- Error rate trends
- WebSocket connection counts

---

## # # Ô£ø√º√™√µ Troubleshooting

## # # Backend Not Responding

```powershell

## Check if backend is running

Get-Process python* -ErrorAction SilentlyContinue | Where-Object { $_.Path -like "*orfeas*" }

## Restart backend

cd c:\Users\johng\Documents\Erevus\orfeas\backend
python main.py

## Wait for "[OK] Models loaded"

```text

## # # Test Image Missing

```powershell

## Create test image

cd c:\Users\johng\Documents\Erevus\orfeas
python create_test_image.py temp/test_images/quality_test_unique2.png

```text

## # # Connection Refused Errors

```powershell

## Verify backend port

curl http://localhost:5000/health

## If fails, check backend logs

Get-Content backend\logs\backend_requests.log -Tail 50

```text

## # # Backend Crashes During Test

1. **Check GPU memory**: Backend may be OOM

   ```powershell
   nvidia-smi

   # If VRAM >20GB, reduce MAX_CONCURRENT_JOBS in .env

   ```text

1. **Reduce concurrency**: Edit test file's `NUM_USERS` variable

2. **Monitor resources**: Use Task Manager or `nvidia-smi -l 1`

## # # Slow Performance

- **Expected**: First generation is slow (model loading)
- **Warm cache**: Subsequent generations should be ~82s
- **If all slow**: Check GPU utilization with `nvidia-smi`

---

## # # '√∫√ñ Validation Criteria Summary

| Test      | Error Rate | Avg Time | P95 Time | Success Rate | Special             |
| --------- | ---------- | -------- | -------- | ------------ | ------------------- |
| Baseline  | 0%         | 75-90s   | -        | 100%         | Validates 82s       |
| Normal    | <1%        | <90s     | <120s    | >99%         | Typical usage       |
| Peak      | <5%        | <150s    | <180s    | -            | ‚â•50 successes       |
| Spike     | <10% spike | -        | -        | -            | Survives & recovers |
| Sustained | <0.1%      | -        | -        | -            | <5% memory growth   |

---

## # # Ô£ø√º√¨√π After Testing Checklist

- [ ] All test JSON results saved
- [ ] Prometheus metrics validated during tests
- [ ] No memory leaks detected (sustained test)
- [ ] No performance degradation over time
- [ ] Error rates within acceptable limits
- [ ] Generate comprehensive load test report
- [ ] Compare results against Phase 2.3 baseline (82s)
- [ ] Document any anomalies or concerns
- [ ] Update Phase 2.6 status to COMPLETE
- [ ] Move to Phase 2.7: Production Deployment

---

## # # üéØ Success Criteria for Phase 2.6 Completion

'√∫√ñ **Phase 2.6 is COMPLETE when**:

1. All 5 test scenarios executed successfully

2. Results JSON files generated for all tests

3. No critical failures (server crashes, >10% errors)

4. Performance validated against 82s baseline
5. Memory leaks ruled out (sustained test)
6. System handles spike traffic gracefully
7. 48+ Prometheus metrics validated during tests
8. Load test report generated

---

**Total Time Investment**: ~3 hours (stabilization + execution + analysis)

**Expected Outcome**: Validated production-ready system with comprehensive load test results proving stability, performance, and scalability.

---

**Next Phase**: Phase 2.7 - Production Deployment (Docker, HTTPS, health checks, backups)
