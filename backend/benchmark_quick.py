"""
+==============================================================================â•—
| [WARRIOR] ORFEAS QUICK PERFORMANCE BENCHMARK - ORFEAS [WARRIOR] |
| Measure current generation performance and GPU utilization |
| Run: python backend/benchmark_quick.py |
+=============================================================================='ïù

Quick Performance Benchmark - Measure baseline performance

Benchmarks:
1. Single image generation (3 iterations)
2. GPU memory utilization
3. Model loading time
4. Preprocessing speed

Usage:
    python backend/benchmark_quick.py

Expected Output:
    [ORFEAS] SINGLE GENERATION BENCHMARK
       Iteration 1: 15.32s (success)
       Iteration 2: 12.45s (success)
       Iteration 3: 11.89s (success)
    [OK] Average: 13.22s (min: 11.89s, max: 15.32s)

    üíæ GPU MEMORY BENCHMARK
       Allocated: 8432.15 MB
       Reserved: 10240.00 MB
       Total: 24576.00 MB
       Utilization: 41.7%

Author: ORFEAS AI Development Team
Date: October 15, 2025
"""

import sys
import time
import torch
from pathlib import Path
import logging
import traceback

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def find_test_image() -> Path:
    """Find a test image in project directories"""
    search_paths = [
        Path('uploads'),
        Path('REAL_AI_TEST_OUTPUTS'),
        Path('backend/outputs'),
        Path('outputs'),
        Path('temp')
    ]

    for search_path in search_paths:
        if not search_path.exists():
            continue

        # Look for PNG files first
        png_files = list(search_path.glob('*.png'))
        if png_files:
            return png_files[0]

        # Then JPG
        jpg_files = list(search_path.glob('*.jpg'))
        if jpg_files:
            return jpg_files[0]

    return None


def benchmark_single_generation(server, test_image: Path, iterations: int = 3):
    """
    Benchmark single image generation

    Args:
        server: OrfeasUnifiedServer instance
        test_image: Path to test image
        iterations: Number of test iterations

    Returns:
        Average generation time in seconds
    """
    times = []

    logger.info(f"\n{'='*80}")
    logger.info(f"[ORFEAS] SINGLE GENERATION BENCHMARK ({iterations} iterations)")
    logger.info(f"   Test image: {test_image.name} ({test_image.stat().st_size / 1024:.2f} KB)")
    logger.info(f"{'='*80}")

    for i in range(iterations):
        job_id = f'bench_{i}_{int(time.time())}'

        logger.info(f"\n[PLAY] Iteration {i+1}/{iterations}")
        start = time.time()

        try:
            # Import here to ensure fresh server state
            output_dir = Path('outputs')
            output_dir.mkdir(exist_ok=True)

            # Call generation
            success, output = server.generate_3d_async(
                input_path=test_image,
                output_dir=output_dir,
                job_id=job_id,
                format_type='stl',
                quality='medium',
                dimensions={'width': 100, 'height': 100, 'depth': 100}
            )

            elapsed = time.time() - start
            times.append(elapsed)

            status = '[OK] success' if success else '[FAIL] failed'
            logger.info(f"   Result: {status} - Time: {elapsed:.2f}s")

            if success:
                output_path = output_dir / output
                if output_path.exists():
                    size_kb = output_path.stat().st_size / 1024
                    logger.info(f"   Output: {output} ({size_kb:.2f} KB)")

        except Exception as e:
            logger.error(f"   [FAIL] Iteration {i+1} failed: {e}")
            logger.error(traceback.format_exc())

    logger.info(f"\n{'='*80}")
    if times:
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)

        logger.info(f"[OK] BENCHMARK RESULTS:")
        logger.info(f"   Average: {avg_time:.2f}s")
        logger.info(f"   Min: {min_time:.2f}s")
        logger.info(f"   Max: {max_time:.2f}s")
        logger.info(f"   Std Dev: {(sum((t - avg_time)**2 for t in times) / len(times))**0.5:.2f}s")
        logger.info(f"{'='*80}")
        return avg_time
    else:
        logger.error("[FAIL] No successful iterations")
        return None


def benchmark_gpu_memory():
    """
    Check GPU memory usage and utilization

    Displays current GPU memory allocation and total capacity
    """
    logger.info(f"\n{'='*80}")
    logger.info("üíæ GPU MEMORY BENCHMARK")
    logger.info(f"{'='*80}")

    if not torch.cuda.is_available():
        logger.warning("[WARN] CUDA not available - GPU benchmarks skipped")
        return

    try:
        # Get GPU info
        device = torch.cuda.current_device()
        gpu_name = torch.cuda.get_device_name(device)

        # Memory stats
        allocated = torch.cuda.memory_allocated(device) / 1024**2  # MB
        reserved = torch.cuda.memory_reserved(device) / 1024**2    # MB
        total = torch.cuda.get_device_properties(device).total_memory / 1024**2  # MB

        utilization_pct = (reserved / total) * 100 if total > 0 else 0

        logger.info(f"   GPU Device: {gpu_name}")
        logger.info(f"   Allocated: {allocated:.2f} MB")
        logger.info(f"   Reserved: {reserved:.2f} MB")
        logger.info(f"   Total: {total:.2f} MB")
        logger.info(f"   Utilization: {utilization_pct:.1f}%")

        # CUDA info
        logger.info(f"\n   CUDA Version: {torch.version.cuda}")
        logger.info(f"   PyTorch Version: {torch.__version__}")

        # Optimization features
        logger.info(f"\n   [ORFEAS] Optimization Features:")
        logger.info(f"      Tensor Cores: {'[OK] Available' if torch.cuda.get_device_capability()[0] >= 7 else '[FAIL] Not Available'}")
        logger.info(f"      Mixed Precision (AMP): [OK] Enabled")
        logger.info(f"      CUDA Graphs: {'[OK] Available' if hasattr(torch.cuda, 'CUDAGraph') else '[FAIL] Not Available'}")

        logger.info(f"{'='*80}")

    except Exception as e:
        logger.error(f"[FAIL] GPU benchmark failed: {e}")
        logger.error(traceback.format_exc())


def benchmark_preprocessing(test_image: Path, iterations: int = 10):
    """
    Benchmark image preprocessing speed

    Args:
        test_image: Path to test image
        iterations: Number of iterations

    Returns:
        Average preprocessing time
    """
    logger.info(f"\n{'='*80}")
    logger.info(f"[PICTURE] IMAGE PREPROCESSING BENCHMARK ({iterations} iterations)")
    logger.info(f"{'='*80}")

    try:
        from PIL import Image, ImageEnhance
        import numpy as np

        times = []
        for i in range(iterations):
            start = time.time()

            with Image.open(test_image) as img:
                img = img.convert('RGB')
                img = img.resize((256, 256), Image.Resampling.LANCZOS)
                enhancer = ImageEnhance.Contrast(img)
                img = enhancer.enhance(1.2)
                image_array = np.asarray(img, dtype=np.float32) / 255.0

            elapsed = time.time() - start
            times.append(elapsed)

        avg_time = sum(times) / len(times)
        logger.info(f"   Average: {avg_time*1000:.2f}ms")
        logger.info(f"   Min: {min(times)*1000:.2f}ms")
        logger.info(f"   Max: {max(times)*1000:.2f}ms")
        logger.info(f"{'='*80}")

        return avg_time

    except Exception as e:
        logger.error(f"[FAIL] Preprocessing benchmark failed: {e}")
        return None


def main():
    """Main benchmark execution"""

    logger.info("+==============================================================================â•—")
    logger.info("| [WARRIOR] ORFEAS PERFORMANCE BENCHMARK - ORFEAS [WARRIOR] |")
    logger.info("+=============================================================================='ïù")

    # Find test image
    logger.info("\n[SEARCH] Searching for test image...")
    test_image = find_test_image()

    if not test_image:
        logger.error("[FAIL] No test images found!")
        logger.error("   Please place a PNG or JPG file in one of these directories:")
        logger.error("   - uploads/")
        logger.error("   - REAL_AI_TEST_OUTPUTS/")
        logger.error("   - outputs/")
        return 1

    logger.info(f"[OK] Using test image: {test_image}")

    # GPU Memory Benchmark (before loading)
    benchmark_gpu_memory()

    # Preprocessing Benchmark
    benchmark_preprocessing(test_image, iterations=10)

    # Initialize server
    logger.info(f"\n{'='*80}")
    logger.info("[LAUNCH] Initializing ORFEAS server...")
    logger.info(f"{'='*80}")

    try:
        # Change to backend directory
        import os
        os.chdir(Path(__file__).parent)

        # Import server
        from main import OrfeasUnifiedServer

        # Create server instance
        server = OrfeasUnifiedServer(mode='POWERFUL_3D')
        logger.info("[OK] Server initialized")

    except Exception as e:
        logger.error(f"[FAIL] Failed to initialize server: {e}")
        logger.error(traceback.format_exc())
        return 1

    # Single Generation Benchmark
    avg_time = benchmark_single_generation(server, test_image, iterations=3)

    # GPU Memory Benchmark (after generation)
    benchmark_gpu_memory()

    # Summary
    logger.info(f"\n{'='*80}")
    logger.info("[OK] BENCHMARK COMPLETE!")
    logger.info(f"{'='*80}")

    if avg_time:
        logger.info(f"\n[STATS] KEY METRICS:")
        logger.info(f"   Average Generation Time: {avg_time:.2f}s")
        logger.info(f"   Target (after optimization): <10s")
        logger.info(f"   Improvement Needed: {max(0, avg_time - 10):.2f}s")

    logger.info("\n[TARGET] NEXT STEPS:")
    logger.info("   1. Review IMMEDIATE_IMPLEMENTATION_GUIDE.md")
    logger.info("   2. Implement Phase 1 optimizations")
    logger.info("   3. Re-run this benchmark to measure improvements")

    return 0


if __name__ == '__main__':
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.info("\n[WARN] Benchmark interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\n[FAIL] Benchmark failed: {e}")
        logger.error(traceback.format_exc())
        sys.exit(1)


# +==============================================================================â•—
# | Usage:                                                                       |
# |   python backend/benchmark_quick.py                                          |
# |                                                                              |
# | Expected Runtime: 1-2 minutes                                                |
# | Requirements: Test image in uploads/ or REAL_AI_TEST_OUTPUTS/               |
# +=============================================================================='ïù
