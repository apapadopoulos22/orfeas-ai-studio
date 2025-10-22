
# ORFEAS Optimized Configuration - Phase 2.3.3
# Generated automatically by apply_optimizations.py

# CRITICAL OPTIMIZATION: Reduce inference steps for 10-15% speedup
DEFAULT_INFERENCE_STEPS = 40  # Reduced from 50 (baseline) to 40
MAX_INFERENCE_STEPS = 100
MIN_INFERENCE_STEPS = 20

# GPU Optimization Settings
GPU_MEMORY_LIMIT = 0.85  # Increased from 0.80 (use more VRAM)
MAX_CONCURRENT_JOBS = 3  # Enable concurrent processing
ENABLE_MIXED_PRECISION = True  # FP16 for faster inference

# CUDA Optimization Flags
TORCH_CUDNN_BENCHMARK = True
TORCH_INDUCTOR_DISABLE = True
CUDA_MODULE_LOADING = "LAZY"

# Pipeline Optimization
AGGRESSIVE_CACHING = True
PRELOAD_MODELS = True

# Quality vs Speed Tradeoff
QUALITY_PRESET = "balanced"  # balanced, high_quality, high_speed

print("[ORFEAS] Optimized configuration loaded")
print("[ORFEAS] Inference steps reduced: 50 → 40 (10-15% faster expected)")
print("[ORFEAS] GPU memory limit increased: 80% → 85%")
print("[ORFEAS] Concurrent jobs enabled: 3 simultaneous generations")
