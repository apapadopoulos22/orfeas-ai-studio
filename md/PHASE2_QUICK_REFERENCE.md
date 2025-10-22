# Phase 2 Quick Reference - Session 1

## # # What We Built Today

## # # 1. GPU Optimizer (`backend/gpu_optimizer.py`)

**Purpose:** Maximize GPU utilization and prevent OOM crashes

## # # Key Functions

```python
from gpu_optimizer import get_gpu_optimizer

optimizer = get_gpu_optimizer(target_utilization=0.85)

## Get current GPU status

profile = optimizer.get_current_memory_profile()

## Returns: total_mb, used_mb, free_mb, cached_mb, utilization_percent

## Calculate optimal batch size

recommendation = optimizer.calculate_optimal_batch_size(
    image_size=(512, 512),
    inference_steps=50,
    current_queue_size=8
)

## Returns: recommended_size, max_safe_size, estimated_vram_per_image, confidence

## Get optimization tips

tips = optimizer.get_optimization_recommendations()

## Returns: ["Ã¢Å¡Â¡ GPU underutilized - increase batch size", ...]

## Free up memory

optimizer.optimize_cache()  # Clears PyTorch cache + garbage collection

```text

## # # Integration Example

```python

## In batch_processor.py

optimizer = get_gpu_optimizer()
recommendation = optimizer.calculate_optimal_batch_size(
    current_queue_size=len(job_queue)
)
batch_size = recommendation.recommended_size

```text

---

## # # 2. Performance Profiler (`backend/performance_profiler.py`)

**Purpose:** Identify bottlenecks and track performance trends

## # # Key Functions (2)

```python
from performance_profiler import get_performance_profiler

profiler = get_performance_profiler()

## Start profiling a pipeline

profiler.start_pipeline('generation_001', {'image_size': (512, 512)})

## Profile individual stages

with profiler.profile_stage('image_preprocessing'):
    preprocessed = preprocess_image(image)

with profiler.profile_stage('shape_generation'):
    mesh = generate_shape(preprocessed)

with profiler.profile_stage('texture_synthesis'):
    textured_mesh = apply_texture(mesh, image)

## End profiling

profile = profiler.end_pipeline()

## Returns: PipelineProfile with stage breakdown

## Identify bottlenecks

bottlenecks = profiler.identify_bottlenecks(threshold_percent=20.0)

## Returns: [{'stage': 'shape_generation', 'avg_percent': 45, 'severity': 'critical'}, ...]

## Get recommendations

recommendations = profiler.get_optimization_recommendations()

## Returns: ["ðŸ”´ CRITICAL: 'shape_generation' takes 45% - optimize this first", ...]

## Export report

profiler.export_report('performance_report.json')

```text

## # # Integration Example (2)

```python

## In hunyuan_integration.py

profiler = get_performance_profiler()

def generate_3d_model(image):
    profiler.start_pipeline(f'gen_{job_id}')

    with profiler.profile_stage('preprocessing'):
        preprocessed = preprocess(image)

    with profiler.profile_stage('shape_generation'):
        mesh = generate_shape(preprocessed)

    profile = profiler.end_pipeline()
    return mesh, profile

```text

---

## # # Next Steps (Session 2)

## # # 1. Integration

```python

## backend/batch_processor.py

from gpu_optimizer import get_gpu_optimizer

optimizer = get_gpu_optimizer()
recommendation = optimizer.calculate_optimal_batch_size(
    current_queue_size=len(self.pending_jobs)
)
batch_size = recommendation.recommended_size

```text

```python

## backend/hunyuan_integration.py

from performance_profiler import get_performance_profiler

profiler = get_performance_profiler()

## Add profiling around each major step

```text

## # # 2. API Endpoints

```python

## backend/main.py

@app.route('/api/performance/summary')
def performance_summary():
    profiler = get_performance_profiler()
    return jsonify(profiler.get_performance_summary())

@app.route('/api/performance/recommendations')
def performance_recommendations():
    profiler = get_performance_profiler()
    return jsonify({'recommendations': profiler.get_optimization_recommendations()})

@app.route('/api/gpu/status')
def gpu_status():
    optimizer = get_gpu_optimizer()
    profile = optimizer.get_current_memory_profile()
    return jsonify({
        'total_mb': profile.total_mb,
        'used_mb': profile.used_mb,
        'utilization': profile.utilization_percent
    })

```text

## # # 3. Baseline Profiling

Run actual 3D generation and analyze results:

```bash
cd backend
python test_batch_real.py  # With profiling enabled

```text

Expected output:

- Current generation time: 107s per image
- Bottleneck stages identified
- Optimization recommendations

## # # 4. Optimization Plan

Based on profiling results, implement:

- **FP16 Mixed Precision:** 20-30% speedup
- **Reduce Inference Steps:** 50 â†’ 40 (10-15% speedup)
- **Optimize Preprocessing:** Image caching (5-10% speedup)

Target: 107s â†’ <60s (45% improvement)

---

## # # Testing

## # # GPU Optimizer Test

```bash
cd backend
python gpu_optimizer.py

```text

Expected output:

```text

1. Current Memory Profile:

   Total: 24576MB
   Used: 8192MB
   Free: 16384MB
   Utilization: 33.3%

2. Batch Size Recommendation:

   Recommended: 6
   Max Safe: 8
   Est. VRAM/image: 2000MB
   Confidence: high

```text

## # # Performance Profiler Test

```bash
cd backend
python performance_profiler.py

```text

Expected output:

```text

1. Simulating Pipeline Execution...

   Total Duration: 0.950s
   Slowest Stage: shape_generation

4. Identified Bottlenecks:
   1. shape_generation: 52.6% (0.500s) - CRITICAL
   2. texture_synthesis: 31.6% (0.300s) - HIGH

5. Optimization Recommendations:
   1. ðŸ”´ CRITICAL: 'shape_generation' takes 52.6% - optimize this first
   2. â†’ Enable mixed precision (FP16) for faster inference

```text

---

## # # Phase 2 Progress

**Completed:** 2/8 tasks (25%)

- âœ… GPU Optimizer
- âœ… Performance Profiler

**Next:** Integration + Optimization (Task 2.3)

- ðŸ”² Integrate GPU Optimizer
- ðŸ”² Integrate Performance Profiler
- ðŸ”² Run baseline profiling
- ðŸ”² Optimize pipeline to <60s

## # # Timeline

- Day 1: âœ… Complete
- Day 2: Integration + profiling
- Day 3: Pipeline optimization
- Day 4: WebSocket progress
- Day 5: Week 1 testing

---

## # # Files Created

1. `backend/gpu_optimizer.py` (400+ lines)

2. `backend/performance_profiler.py` (450+ lines)

3. `md/PHASE2_SESSION1_PROGRESS.md` (comprehensive report)

4. `txt/PHASE2_SESSION1_VISUAL_SUMMARY.txt` (visual summary)
5. `md/PHASE2_QUICK_REFERENCE.md` (this file)

---

## # # Key Metrics

## # # Current Performance

- Generation time: 107s per image
- GPU utilization: 60-70%
- Batch throughput: 1Ã— baseline

## # # Target Performance

- Generation time: <60s per image (45% improvement)
- GPU utilization: 85%
- Batch throughput: 2-3Ã—

## # # Progress

- Overall: 25% (2/8 tasks)
- Week 1: 40% (2/5 tasks)
- Status: âœ… AHEAD OF SCHEDULE

---

_Last Updated: October 17, 2025_
_ORFEAS AI_
