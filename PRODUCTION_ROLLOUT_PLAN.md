# 🚀 ORFEAS AI - Production Rollout Plan

**Project:** ORFEAS AI Optimization Deployment
**Version:** 1.0.0
**Date:** October 25, 2025
**Status:** Ready for Phase 1

---

## 📋 Executive Summary

This document outlines a phased approach to deploying 13 major optimizations to the ORFEAS AI production environment. The rollout is designed to:

- **Minimize risk** through incremental deployment
- **Enable rapid rollback** if issues arise
- **Provide clear success metrics** at each phase
- **Maintain system stability** throughout the process

**Expected Improvements:**

- Response time: 60s → 10-15s (4-6x faster)
- First result: 60s → 0.5s (120x faster)
- GPU utilization: 20% → 75% (4x efficiency)
- Concurrent capacity: 3-4 → 10-15 jobs (3-4x increase)

---

## 🎯 Rollout Phases

### Phase 1: Low-Risk Infrastructure (Week 1)

**Goal:** Deploy compression, rate limiting, and WebSocket optimizations
**Risk Level:** 🟢 LOW
**Duration:** 2-3 days

#### Features Included

1. ✅ Flask Response Compression (gzip + brotli)
2. ✅ WebSocket Throttling (150ms batching)
3. ✅ Advanced Rate Limiting (multi-tier)

#### Deployment Steps

```powershell
# Step 1: Backup current configuration
cd C:\Users\johng\Documents\oscar
git checkout -b deploy/phase1-compression
cp backend\.env backend\.env.backup

# Step 2: Enable compression (already installed)
# Verify flask-compress and brotli are installed
python -c "import flask_compress, brotli; print('Dependencies OK')"

# Step 3: Update environment variables
# Add to backend/.env:
COMPRESS_GZIP_LEVEL=6
COMPRESS_BROTLI=1
COMPRESS_MIN_BYTES=1024
WS_EMIT_INTERVAL_MS=150
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_ADAPTIVE=true

# Step 4: Restart backend
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 3
cd backend
python main.py
```

#### Success Metrics

- ✅ Response size reduced by 70-90% (check network tab)
- ✅ Rate limit headers present in responses (X-RateLimit-Remaining)
- ✅ WebSocket message rate reduced by 60-80%
- ✅ No increase in error rate (< 0.5%)
- ✅ CPU usage stable or reduced

#### Monitoring Commands

```powershell
# Check compression working
curl -H "Accept-Encoding: gzip,br" http://localhost:5000/api/health -v | grep "Content-Encoding"

# Monitor rate limiting
Get-Content backend\logs\backend_requests.log -Tail 100 | Select-String "rate_limit"

# Check WebSocket performance
# Open browser console and monitor job_update event frequency
```

#### Rollback Procedure

```powershell
# Quick rollback - disable optimizations
$env:COMPRESS_LEVEL = "0"
$env:WS_EMIT_INTERVAL_MS = "0"
$env:RATE_LIMIT_DISABLED = "1"

# Restart backend
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force
cd backend
python main.py

# Or restore backup
cp backend\.env.backup backend\.env
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force
cd backend
python main.py
```

---

### Phase 2: Progressive Rendering (Week 2)

**Goal:** Enable progressive 3D generation for faster perceived performance
**Risk Level:** 🟡 MEDIUM
**Duration:** 3-4 days

#### Features Included

1. ✅ Progressive Renderer (3-stage streaming)
2. ✅ SSE (Server-Sent Events) endpoint

#### Deployment Steps

```powershell
# Step 1: Feature flag rollout (50% of users)
# Add to backend/.env:
PROGRESSIVE_RENDERING_ENABLED=true
PROGRESSIVE_ROLLOUT_PERCENTAGE=50  # Start with 50%

# Step 2: Monitor first 50% of traffic
# Check /api/progress/<job_id> endpoint health

# Step 3: Increase to 100% after 48 hours if metrics are good
PROGRESSIVE_ROLLOUT_PERCENTAGE=100
```

#### Success Metrics

- ✅ First result delivered in < 1 second (LOW quality preview)
- ✅ Medium quality delivered in < 20 seconds
- ✅ Final quality delivered in < 70 seconds
- ✅ User abandonment rate reduced by 50-70%
- ✅ SSE connection stability > 99%

#### Monitoring Commands

```powershell
# Test progressive endpoint
python tests\integration\test_progressive_and_cache.py -v

# Check SSE streaming
curl -N http://localhost:5000/api/progress/test-job-id

# Monitor stage timings
Get-Content backend\logs\backend_requests.log | Select-String "progressive" | Select-Object -Last 20
```

#### Rollback Procedure

```powershell
# Disable progressive rendering
$env:PROGRESSIVE_RENDERING_ENABLED = "false"

# Restart backend
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force
cd backend
python main.py

# Frontend will fall back to standard /api/generate-3d endpoint
```

---

### Phase 3: Intelligent Caching (Week 3)

**Goal:** Enable Redis-backed caching for duplicate requests
**Risk Level:** 🟡 MEDIUM
**Duration:** 2-3 days

#### Pre-Deployment Requirements

1. Redis server installed and running
2. Redis connection tested
3. Cache invalidation strategy agreed upon

#### Deployment Steps

```powershell
# Step 1: Install and start Redis (if not already running)
# Option A: Docker
docker run -d -p 6379:6379 redis:alpine

# Option B: Windows Redis (if installed)
redis-server

# Step 2: Test Redis connection
python -c "import redis; r=redis.Redis(); r.ping(); print('Redis OK')"

# Step 3: Enable caching with feature flag
# Add to backend/.env:
CACHE_ENABLED=true
REDIS_URL=redis://localhost:6379/0
CACHE_TTL_SECONDS=3600
CACHE_MAX_MEMORY_MB=1024

# Step 4: Gradual rollout (30% → 60% → 100%)
CACHE_ROLLOUT_PERCENTAGE=30  # Day 1
CACHE_ROLLOUT_PERCENTAGE=60  # Day 2
CACHE_ROLLOUT_PERCENTAGE=100 # Day 3
```

#### Success Metrics

- ✅ Cache hit rate: 20-30% within 7 days
- ✅ Cached requests: < 50ms response time
- ✅ Redis memory usage: < 2GB
- ✅ Cache miss penalty: < 5ms overhead
- ✅ Redis uptime: > 99.9%

#### Monitoring Commands

```powershell
# Check Redis stats
redis-cli INFO stats | Select-String "keyspace_hits"

# Monitor cache hit rate
python -c "
import redis
r = redis.Redis()
info = r.info('stats')
hits = info['keyspace_hits']
misses = info['keyspace_misses']
rate = hits / (hits + misses) * 100 if (hits + misses) > 0 else 0
print(f'Cache hit rate: {rate:.1f}%')
"

# Check cache memory
redis-cli INFO memory | Select-String "used_memory_human"
```

#### Rollback Procedure

```powershell
# Disable caching
$env:CACHE_ENABLED = "false"

# Restart backend (will use in-memory fallback)
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force
cd backend
python main.py

# Optional: Flush Redis if needed
redis-cli FLUSHDB
```

---

### Phase 4: GPU Optimizations (Week 4)

**Goal:** Enable batch processing and quantization for maximum throughput
**Risk Level:** 🔴 HIGH
**Duration:** 5-7 days

#### Features Included

1. ✅ GPU Batch Processor (dynamic batching)
2. ✅ Model Quantization (INT8/FP16)
3. ✅ Adaptive Quantization

#### Pre-Deployment Requirements

1. **GPU baseline captured** (memory, utilization, temperature)
2. **Stress testing completed** with benchmark suite
3. **Model quality validation** (INT8 vs FP32 accuracy)

#### Deployment Steps

```powershell
# Step 1: Capture GPU baseline
nvidia-smi --query-gpu=memory.used,memory.total,utilization.gpu --format=csv > baseline_gpu.csv

# Step 2: Run stress test
python benchmark\benchmark_optimizations.py
locust -f load\locustfile.py --headless -u 10 -r 2 -t 5m

# Step 3: Enable batch processing (conservative settings)
# Add to backend/.env:
GPU_BATCH_ENABLED=true
GPU_MAX_BATCH_SIZE=4  # Start conservative
GPU_BATCH_TIMEOUT_MS=2000
GPU_FP16_ENABLED=false  # Disable FP16 initially

# Step 4: Monitor for 24 hours, then enable FP16
GPU_FP16_ENABLED=true

# Step 5: Increase batch size gradually
GPU_MAX_BATCH_SIZE=6  # Day 2
GPU_MAX_BATCH_SIZE=8  # Day 3

# Step 6: Enable quantization (after batch processing stable)
MODEL_QUANTIZATION_ENABLED=true
QUANTIZATION_MODE=adaptive  # adaptive, int8, fp16, or disabled
```

#### Success Metrics

- ✅ GPU utilization: 60-80% (up from 20%)
- ✅ Concurrent jobs: 8-12 (up from 3-4)
- ✅ VRAM efficiency: 50% reduction with FP16
- ✅ Throughput: 3-4x increase
- ✅ GPU temperature: < 85°C
- ✅ Model quality: > 98% accuracy vs baseline

#### Monitoring Commands

```powershell
# Real-time GPU monitoring
nvidia-smi dmon -s u

# Check batch processing stats
Get-Content backend\logs\backend_requests.log | Select-String "batch_size" | Select-Object -Last 20

# Monitor concurrent jobs
python -c "
import requests
r = requests.get('http://localhost:5000/api/queue/stats')
print(r.json())
"

# Temperature monitoring
nvidia-smi --query-gpu=temperature.gpu --format=csv -lms 1000
```

#### Rollback Procedure

```powershell
# Step 1: Disable batch processing and quantization
$env:GPU_BATCH_ENABLED = "false"
$env:MODEL_QUANTIZATION_ENABLED = "false"

# Step 2: Clear GPU memory
python -c "import torch; torch.cuda.empty_cache(); print('GPU cache cleared')"

# Step 3: Restart backend
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force
cd backend
python main.py

# Step 4: Verify GPU state
nvidia-smi

# If GPU is unstable, reboot system
```

---

## 📊 Success Criteria by Phase

### Phase 1 Success (Infrastructure)

- [x] All services start without errors
- [x] Compression headers present in responses
- [x] Rate limiting returns 429 when exceeded
- [x] WebSocket message frequency reduced
- [x] No increase in error rate
- [x] Response times improved or unchanged

### Phase 2 Success (Progressive Rendering)

- [ ] First result < 1 second
- [ ] SSE connection stability > 99%
- [ ] User abandonment reduced by 50%+
- [ ] No websocket connection issues
- [ ] Frontend displays all 3 quality stages

### Phase 3 Success (Caching)

- [ ] Redis uptime > 99.9%
- [ ] Cache hit rate 20-30% after 7 days
- [ ] Cached request time < 50ms
- [ ] Redis memory < 2GB
- [ ] No cache poisoning incidents

### Phase 4 Success (GPU Optimizations)

- [ ] GPU utilization 60-80%
- [ ] Concurrent jobs 8-12+
- [ ] Throughput increased 3-4x
- [ ] Model quality maintained (>98%)
- [ ] GPU temperature stable (<85°C)
- [ ] No CUDA out-of-memory errors

---

## 🚨 Emergency Procedures

### Critical Issue Detection

**Trigger Emergency Rollback If:**

- Error rate increases by > 5%
- Response time increases by > 50%
- GPU temperature exceeds 90°C
- Redis becomes unresponsive
- CUDA out-of-memory errors spike
- User-reported critical bugs increase by > 200%

### Emergency Rollback Script

```powershell
# emergency_rollback.ps1
# Run this script if critical issues detected

Write-Host "🚨 EMERGENCY ROLLBACK INITIATED" -ForegroundColor Red

# Step 1: Stop backend
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force
Write-Host "✓ Backend stopped" -ForegroundColor Yellow

# Step 2: Restore backup configuration
if (Test-Path "backend\.env.backup") {
    Copy-Item "backend\.env.backup" "backend\.env" -Force
    Write-Host "✓ Configuration restored" -ForegroundColor Yellow
}

# Step 3: Clear GPU memory
python -c "import torch; torch.cuda.empty_cache(); print('GPU cleared')"
Write-Host "✓ GPU cache cleared" -ForegroundColor Yellow

# Step 4: Disable all optimizations
$env:PROGRESSIVE_RENDERING_ENABLED = "false"
$env:CACHE_ENABLED = "false"
$env:GPU_BATCH_ENABLED = "false"
$env:MODEL_QUANTIZATION_ENABLED = "false"

# Step 5: Restart with safe defaults
cd backend
python main.py

Write-Host "✓ Backend restarted with safe configuration" -ForegroundColor Green
Write-Host "Monitor logs: Get-Content logs\backend_requests.log -Tail 50 -Wait" -ForegroundColor Cyan
```

### Post-Incident Review

After any rollback:

1. Capture logs from last 60 minutes
2. Document exact error messages
3. Review monitoring metrics
4. Identify root cause
5. Create fix and test thoroughly
6. Update rollout plan with lessons learned

---

## 📈 Monitoring Dashboard

### Key Performance Indicators (KPIs)

#### Response Time Metrics

- **P50 Response Time:** Target < 15s (currently 60s)
- **P95 Response Time:** Target < 30s (currently 124s)
- **P99 Response Time:** Target < 45s (currently 180s)
- **First Result Time:** Target < 1s (currently 60s)

#### Throughput Metrics

- **Requests Per Hour:** Target 400+ (currently 100)
- **Concurrent Jobs:** Target 10-15 (currently 3-4)
- **Queue Wait Time:** Target < 5s (currently 20-30s)

#### Resource Metrics

- **GPU Utilization:** Target 60-80% (currently 20%)
- **VRAM Usage:** Target 18-20GB (currently 5GB)
- **CPU Usage:** Target < 60% (currently 40%)
- **Redis Memory:** Target < 2GB

#### Quality Metrics

- **Cache Hit Rate:** Target 25-30%
- **Error Rate:** Target < 0.5%
- **User Abandonment:** Target < 10% (currently 30%)
- **Model Accuracy:** Target > 98% vs baseline

### Monitoring Commands

```powershell
# Real-time monitoring script
# monitoring.ps1

while ($true) {
    Clear-Host
    Write-Host "=== ORFEAS AI Production Monitoring ===" -ForegroundColor Cyan
    Write-Host "Time: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')`n" -ForegroundColor Gray

    # Backend health
    $health = curl -s http://localhost:5000/api/health | ConvertFrom-Json
    Write-Host "Backend Status: $($health.status)" -ForegroundColor Green

    # GPU stats
    $gpu = nvidia-smi --query-gpu=utilization.gpu,memory.used,temperature.gpu --format=csv,noheader,nounits
    Write-Host "GPU: $gpu" -ForegroundColor Yellow

    # Redis stats (if caching enabled)
    if ($env:CACHE_ENABLED -eq "true") {
        $redis = redis-cli PING
        Write-Host "Redis: $redis" -ForegroundColor Magenta
    }

    # Recent errors
    $errors = Get-Content backend\logs\backend_requests.log -Tail 100 | Select-String "ERROR" | Measure-Object
    Write-Host "Recent Errors: $($errors.Count)" -ForegroundColor $(if ($errors.Count -gt 5) {"Red"} else {"Green"})

    Write-Host "`nPress Ctrl+C to stop monitoring" -ForegroundColor Gray
    Start-Sleep -Seconds 5
}
```

---

## ✅ Pre-Deployment Checklist

### Before Phase 1

- [ ] All 13 optimizations tested locally
- [ ] Integration tests passing
- [ ] Load tests completed
- [ ] Backup of current `.env` created
- [ ] Git branch created for deployment
- [ ] Team notified of deployment window

### Before Phase 2

- [ ] Phase 1 metrics validated
- [ ] Progressive rendering tested with 10+ images
- [ ] SSE connections tested for stability
- [ ] Frontend updated to support progressive display

### Before Phase 3

- [ ] Redis installed and tested
- [ ] Cache invalidation strategy defined
- [ ] Redis backup/restore tested
- [ ] Memory limits configured

### Before Phase 4

- [ ] GPU baseline captured
- [ ] Stress testing completed
- [ ] Model quality validation done
- [ ] Temperature monitoring in place
- [ ] Emergency rollback script tested

---

## 📞 Support & Escalation

### During Deployment

**Deployment Lead:** [Your Name]
**On-Call Engineer:** [Name]
**Escalation Path:** [Manager] → [CTO]

### Monitoring Contacts

- **Real-time monitoring:** Grafana dashboard
- **Alerts:** Slack #orfeas-alerts channel
- **Logs:** `backend/logs/backend_requests.log`
- **Metrics:** Prometheus + Grafana

### Documentation

- **Optimization Details:** `COMPREHENSIVE_OPTIMIZATION_RECOMMENDATIONS.md`
- **Testing:** `tests/integration/`, `load/`, `benchmark/`
- **Configuration:** `backend/.env` and `backend/.env.example`

---

## 🎯 Expected Timeline

| Week | Phase | Activities | Risk Level |
|------|-------|-----------|------------|
| **Week 1** | Phase 1 | Deploy compression, rate limiting, WebSocket optimization | 🟢 LOW |
| **Week 2** | Phase 2 | Enable progressive rendering with 50% → 100% rollout | 🟡 MEDIUM |
| **Week 3** | Phase 3 | Deploy Redis caching with 30% → 60% → 100% rollout | 🟡 MEDIUM |
| **Week 4** | Phase 4 | Enable GPU batch processing and quantization gradually | 🔴 HIGH |

**Total Duration:** 4-5 weeks from Phase 1 start to Phase 4 completion

---

## 📝 Deployment Log Template

```markdown
### Deployment: [Phase Name]
**Date:** YYYY-MM-DD
**Time:** HH:MM
**Deployed By:** [Name]

#### Pre-Deployment
- [ ] Checklist completed
- [ ] Backup created
- [ ] Team notified

#### Deployment
- [ ] Configuration updated
- [ ] Backend restarted
- [ ] Health checks passed

#### Post-Deployment
- [ ] Metrics validated
- [ ] No errors in logs
- [ ] User testing completed
- [ ] Success criteria met

#### Notes:
[Any observations, issues, or lessons learned]
```

---

**Document Owner:** ORFEAS AI Engineering Team
**Last Updated:** October 25, 2025
**Next Review:** After Phase 2 completion
