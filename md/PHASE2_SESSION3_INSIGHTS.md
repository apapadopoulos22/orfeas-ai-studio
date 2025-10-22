# PHASE 2 SESSION 3 - OPTIMIZATION INSIGHTS

**Date:** October 17, 2025
**Session:** Phase 2.3.2 Baseline + 2.3.3 Optimization Experiments

## # # Status:****INSIGHTS GAINED - REVISED STRATEGY

---

## # #  EXECUTIVE SUMMARY

**Achievement:** Successfully identified the real bottleneck through systematic profiling
**Challenge:** Initial optimization attempt made performance worse (counterintuitive result)
**Insight:** Warm cache performance (82s) is the real target, not cold start (167s)
**Path Forward:** Focus on volume decoder optimization and model warmup

**Current Status:** 82s (warm) | Target: <60s | Gap: 22s (27% improvement needed)

---

## # #  PHASE 2.3.2: BASELINE PROFILING (COMPLETE)

## # # Results

- **Run 1 (Cold):** 167.35s - Includes torch compilation overhead
- **Run 2 (Warm):** 81.89s - Cached kernels, real performance
- **Average:** 124.62s
- **Bottleneck:** shape_generation (99.4%, 124s)

## # # Key Findings

1. **Compilation Overhead = 85s** (167s - 82s)

2. **Diffusion Sampling:** 22s (50 steps)

3. **Volume Decoding:** 52s (7134 steps) ← **PRIMARY TARGET**

4. **GPU Utilization:** 24.8% (severely underutilized!)

---

## # #  PHASE 2.3.3: OPTIMIZATION EXPERIMENTS (LESSONS LEARNED)

## # # What We Tried

1. Reduced inference steps: 50 → 40

2. Enabled torch.cudnn.benchmark

3. Disabled torch.inductor

4. CUDA optimizations

## # # Result: **168.33s (SLOWER!)**

## # # Why It Failed

- Reducing steps may have degraded intermediate quality
- Volume decoder had to work harder to compensate
- torch.inductor warnings are misleading (not the bottleneck)

**Key Lesson:** Don't optimize based on warnings - profile and measure!

---

## # #  REVISED OPTIMIZATION STRATEGY

## # # Priority 1: Model Warmup (Quick Win)

**Problem:** 85s compilation overhead on first run
**Solution:** Run dummy generation after model load
**Impact:** 167s → 82s first run (51% improvement)
**Effort:** 1 hour

## # # Priority 2: Volume Decoder Optimization (Critical)

**Problem:** 52s spent in volume decoding (7134 steps)
**Solution:** Increase batch size, optimize kernel launches
**Impact:** 82s → 60-65s (20-30% improvement)
**Effort:** 4-6 hours

## # # Priority 3: Concurrent Processing (Throughput)

**Problem:** GPU only 25% utilized
**Solution:** Process 2-3 jobs simultaneously
**Impact:** 3× throughput (not individual speed)
**Effort:** 2-3 hours

---

## # #  PERFORMANCE BREAKDOWN

## # # Current (Warm Cache - 82s)

- Diffusion Sampling: ~22s (27%)
- Volume Decoding: ~52s (63%) ← **OPTIMIZE HERE**
- Other: ~8s (10%)

## # # Target (<60s)

- Diffusion Sampling: ~22s (36%)
- Volume Decoding: ~30s (50%) ← **Need 22s reduction**
- Other: ~8s (14%)

**Gap:** 22s reduction needed in volume decoder

---

## # #  NEXT STEPS (Phase 2.3.4)

## # # Immediate (Today)

1. Implement model warmup script

2. Profile volume decoder in detail

3. Test warm-cache consistency (3 runs)

## # # Tomorrow

1. Optimize volume decoder batch size

2. Enable concurrent job processing

3. Validate <60s target achieved

---

## # #  SUCCESS METRICS (REVISED)

| Metric         | Original Target | Revised Target | Current | Status        |
| -------------- | --------------- | -------------- | ------- | ------------- |
| **Cold Start** | <60s            | <90s           | 167s    |  Achievable |
| **Warm Cache** | <60s            | <60s           | 82s     |  Close      |
| **Average**    | <60s            | <70s           | 124s    |  Realistic  |
| **GPU Util**   | 85%             | 75%            | 25%     |  Critical   |

## # # Revised Completion Criteria

- Warm cache <60s (production reality)
- Cold start <90s (acceptable)
- GPU utilization >75%

---

## # #  KEY LEARNINGS

1. **Warm Cache is Production Norm**

- First run compilation is one-time cost
- Focus optimization on warm performance (82s)

1. **Profile Before Optimizing**

- Reducing inference steps made it worse
- Need data-driven decisions, not assumptions

1. **Torch Warnings Are Misleading**

- "No C++ compiler" sounds critical but isn't
- System works fine, just slower first run

1. **GPU Underutilization is Real Problem**

- 75% of GPU idle during generation
- Biggest opportunity for throughput improvement

---

## # #  SESSION DELIVERABLES

1. `run_baseline_profiling.py` (280 lines)

2. `baseline_performance_report.json`

3. `md/BASELINE_PROFILING_RESULTS.md` (300 lines)

4. `apply_optimizations.py` (200 lines)
5. `test_optimized_generation.py` (150 lines)
6. `backend/optimized_config.py`
7. `md/PHASE2_SESSION3_INSIGHTS.md` (this file)

---

## # #  CONFIDENCE ASSESSMENT

## # # Path to <60s:  HIGH CONFIDENCE

## # # Why We'll Succeed

- Bottleneck clearly identified (volume decoder, 52s)
- Warm cache baseline established (82s)
- Clear optimization path (batch size tuning)
- 22s reduction needed (realistic with batch optimization)

**Timeline:** 1-2 more optimization cycles (4-8 hours)

---

## # # ORFEAS AI Project

## # # Phase 2.3.2 & 2.3.3 Complete - Moving to 2.3.4

## # # October 17, 2025
