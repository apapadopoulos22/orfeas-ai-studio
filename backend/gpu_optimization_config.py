# backend/gpu_optimization_config.py
# RTX 3090 GPU Memory Optimization Configuration
# Implements VRAM efficiency and inference acceleration

import os
import torch
import logging

logger = logging.getLogger(__name__)

def configure_rtx_3090_optimization():
    """Configure RTX 3090 for maximum performance and memory efficiency"""

    # 1. Disable XFORMERS to prevent DLL crashes (0xc0000139)
    os.environ['XFORMERS_DISABLED'] = '1'
    logger.info("[GPU] XFORMERS disabled to prevent DLL crashes")

    # 2. Set CUDA memory fraction to 95% (22.8GB of 24GB)
    torch.cuda.set_per_process_memory_fraction(0.95)
    logger.info("[GPU] CUDA memory fraction set to 95% (22.8GB)")

    # 3. Enable TensorFloat-32 for matrix operations (2x speedup)
    torch.backends.cuda.matmul.allow_tf32 = True
    torch.backends.cudnn.allow_tf32 = True
    logger.info("[GPU] TensorFloat-32 enabled for matrix operations")

    # 4. Enable cuDNN auto-tuning for optimal kernel selection
    torch.backends.cudnn.benchmark = True
    torch.backends.cudnn.deterministic = False
    logger.info("[GPU] cuDNN benchmark enabled for kernel optimization")

    # 5. Configure CUDA memory allocation strategy
    os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'max_split_size_mb:512'
    logger.info("[GPU] CUDA memory allocation optimized (512MB split limit)")

    # 6. Enable async GPU operations
    os.environ['CUDA_LAUNCH_BLOCKING'] = '0'
    logger.info("[GPU] Async GPU operations enabled")

    # 7. Configure CUBLAS workspace
    os.environ['CUBLAS_WORKSPACE_CONFIG'] = ':16:8'
    logger.info("[GPU] CUBLAS workspace configured")

    # 8. Verify GPU configuration
    if torch.cuda.is_available():
        gpu_props = torch.cuda.get_device_properties(0)
        total_memory_gb = gpu_props.total_memory / 1e9
        usable_memory_gb = (gpu_props.total_memory * 0.95) / 1e9

        logger.info(f"[GPU] Device: {gpu_props.name}")
        logger.info(f"[GPU] Compute Capability: {gpu_props.major}.{gpu_props.minor}")
        logger.info(f"[GPU] Total Memory: {total_memory_gb:.1f}GB")
        logger.info(f"[GPU] Usable Memory (95%): {usable_memory_gb:.1f}GB")
        logger.info(f"[GPU] Max Threads Per Block: {gpu_props.max_threads_per_block}")

        return True
    else:
        logger.error("[GPU] CUDA not available")
        return False


def cleanup_gpu_memory():
    """Emergency GPU memory cleanup"""
    try:
        torch.cuda.empty_cache()
        torch.cuda.synchronize()
        logger.info("[GPU] GPU cache cleared and synchronized")
        return True
    except Exception as e:
        logger.error(f"[GPU] Failed to cleanup GPU memory: {e}")
        return False


def get_gpu_memory_stats():
    """Get current GPU memory statistics"""
    if not torch.cuda.is_available():
        return None

    allocated_gb = torch.cuda.memory_allocated(0) / 1e9
    reserved_gb = torch.cuda.memory_reserved(0) / 1e9
    total_gb = torch.cuda.get_device_properties(0).total_memory / 1e9
    usage_percent = (allocated_gb / total_gb) * 100

    return {
        'allocated_gb': round(allocated_gb, 2),
        'reserved_gb': round(reserved_gb, 2),
        'total_gb': round(total_gb, 2),
        'usage_percent': round(usage_percent, 1),
        'available_gb': round(total_gb - allocated_gb, 2)
    }


def monitor_gpu_health():
    """Monitor GPU health and trigger cleanup if needed"""
    stats = get_gpu_memory_stats()

    if stats is None:
        return False

    logger.info(f"[GPU] Memory Status: {stats['allocated_gb']}GB / {stats['total_gb']}GB ({stats['usage_percent']}%)")

    # Trigger cleanup if usage exceeds 90%
    if stats['usage_percent'] > 90:
        logger.warning("[GPU] GPU memory usage critical (>90%), triggering cleanup")
        cleanup_gpu_memory()
        return True

    return False


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    print("[GPU] Configuring RTX 3090 optimization...")
    configure_rtx_3090_optimization()

    stats = get_gpu_memory_stats()
    print(f"\n[GPU] Configuration Complete!")
    print(f"[GPU] Memory Available: {stats['available_gb']}GB / {stats['total_gb']}GB")
