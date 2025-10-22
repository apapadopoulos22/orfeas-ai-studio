"""
ORFEAS AI 2D'Üí3D Studio - Phase 1 Batch Inference Performance Benchmark
========================================================================
ORFEAS AI Project

Performance Target: <25s for 4 jobs (currently 60s)
Expected Speedup: 2.7√ó faster via parallel GPU batching

Usage:
    python test_batch_performance.py
"""

import sys
import time
import logging
from pathlib import Path
from PIL import Image
import numpy as np
from typing import Any, List, Tuple

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from hunyuan_integration import get_3d_processor
from gpu_manager import get_gpu_manager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s'
)
logger = logging.getLogger(__name__)


def create_test_images(count: int = 4, size: Any = (512, 512)) -> None:
    """Create test images for benchmarking"""
    logger.info(f"Creating {count} test images ({size[0]}√ó{size[1]})")

    images = []
    for i in range(count):
        # Create colored gradient image
        img_array = np.zeros((size[1], size[0], 3), dtype=np.uint8)

        # Gradient based on index
        for y in range(size[1]):
            for x in range(size[0]):
                img_array[y, x] = [
                    int(255 * (i + 1) / count),  # R
                    int(255 * x / size[0]),       # G
                    int(255 * y / size[1])        # B
                ]

        img = Image.fromarray(img_array)
        images.append(img)

    logger.info(f"'úÖ Created {count} test images")
    return images


def benchmark_sequential(processor: Any, images: List) -> Tuple:
    """Benchmark sequential processing (original method)"""
    logger.info("=" * 80)
    logger.info("BENCHMARK 1: SEQUENTIAL PROCESSING (Original)")
    logger.info("=" * 80)

    start_time = time.time()
    meshes = []

    for idx, img in enumerate(images):
        logger.info(f"Processing image {idx + 1}/{len(images)}...")
        try:
            # Check if processor has generate_shape method (single image)
            if hasattr(processor, 'generate_shape'):
                mesh = processor.generate_shape(img, num_inference_steps=50)
                meshes.append(mesh)
            else:
                logger.warning("Processor missing generate_shape method, skipping")
                meshes.append(None)
        except Exception as e:
            logger.error(f"Failed: {e}")
            meshes.append(None)

    elapsed = time.time() - start_time

    logger.info("" * 80)
    logger.info(f"SEQUENTIAL RESULTS:")
    logger.info(f"  Total Time: {elapsed:.2f} seconds")
    logger.info(f"  Per Image: {elapsed / len(images):.2f} seconds")
    logger.info(f"  Success Rate: {len([m for m in meshes if m is not None])}/{len(meshes)}")
    logger.info("=" * 80)

    return elapsed, meshes


def benchmark_batch(processor: Any, images: List) -> Tuple:
    """Benchmark batch processing (Phase 1 optimization)"""
    logger.info("=" * 80)
    logger.info("BENCHMARK 2: BATCH PROCESSING (Phase 1 Optimization)")
    logger.info("=" * 80)

    # Check if batch inference is available
    if not hasattr(processor, 'generate_shape_batch'):
        logger.error("'ùå Batch inference not available!")
        logger.error("   Make sure batch_inference_extension.py is integrated")
        return None, []

    logger.info("'úÖ Batch inference available")
    logger.info(f"Processing {len(images)} images in parallel...")

    start_time = time.time()

    try:
        meshes = processor.generate_shape_batch(
            images=images,
            num_inference_steps=50
        )
    except Exception as e:
        logger.error(f"Batch processing failed: {e}")
        import traceback
        traceback.print_exc()
        return None, []

    elapsed = time.time() - start_time

    logger.info("" * 80)
    logger.info(f"BATCH RESULTS:")
    logger.info(f"  Total Time: {elapsed:.2f} seconds")
    logger.info(f"  Per Image: {elapsed / len(images):.2f} seconds")
    logger.info(f"  Success Rate: {len([m for m in meshes if m is not None])}/{len(meshes)}")
    logger.info("=" * 80)

    return elapsed, meshes


def compare_results(seq_time: float, batch_time: float, target_time: float = 25.0) -> None:
    """Compare sequential vs batch performance"""
    logger.info("=" * 80)
    logger.info("PERFORMANCE COMPARISON")
    logger.info("=" * 80)

    if seq_time and batch_time:
        speedup = seq_time / batch_time
        improvement = ((seq_time - batch_time) / seq_time) * 100

        logger.info(f"Sequential Time:  {seq_time:.2f}s")
        logger.info(f"Batch Time:       {batch_time:.2f}s")
        logger.info(f"Speedup:          {speedup:.2f}√ó faster")
        logger.info(f"Improvement:      {improvement:.1f}% reduction")
        logger.info("" * 80)

        # Check against target
        logger.info(f"Target Time:      <{target_time}s")
        if batch_time < target_time:
            logger.info(f"'úÖ SUCCESS: Batch time {batch_time:.2f}s < {target_time}s target!")
        else:
            logger.warning(f"  CLOSE: Batch time {batch_time:.2f}s, target is {target_time}s")

        # Check against expected speedup
        expected_speedup = 2.7
        if speedup >= expected_speedup:
            logger.info(f"'úÖ SUCCESS: Achieved {speedup:.2f}√ó speedup (target: {expected_speedup}√ó)")
        else:
            logger.warning(f"  Speedup {speedup:.2f}× less than target {expected_speedup}×")

    elif batch_time:
        logger.info(f"Batch Time: {batch_time:.2f}s")
        if batch_time < target_time:
            logger.info(f"'úÖ SUCCESS: Under {target_time}s target!")

    logger.info("=" * 80)


def main() -> None:
    """Main benchmark execution"""
    logger.info("")
    logger.info("â•'     ORFEAS PHASE 1 - BATCH INFERENCE PERFORMANCE BENCHMARK       â•'")
    logger.info("â•'                                                                   â•'")
    logger.info("'ïë  Target: <25s for 4 jobs (2.7√ó faster than sequential)          'ïë")
    logger.info("")
    print()

    # Initialize GPU manager
    logger.info("Initializing GPU manager...")
    gpu_mgr = get_gpu_manager()
    gpu_stats = gpu_mgr.get_gpu_stats()

    if gpu_stats.get('available'):
        logger.info(f"'úÖ GPU Available: {gpu_stats.get('device_name')}")
        logger.info(f"   Total VRAM: {gpu_stats.get('total_memory_mb', 0):.0f}MB")
        logger.info(f"   Free VRAM: {gpu_stats.get('free_memory_mb', 0):.0f}MB")
    else:
        logger.warning("  No GPU detected - benchmark will run on CPU (slow)")

    print()

    # Initialize processor
    logger.info("Initializing Hunyuan3D processor...")
    logger.info("(First load may take 30-36 seconds...)")

    try:
        processor = get_3d_processor()
        logger.info("'úÖ Processor initialized")
    except Exception as e:
        logger.error(f"'ùå Failed to initialize processor: {e}")
        import traceback
        traceback.print_exc()
        return

    print()

    # Create test images
    num_images = 4  # Standard benchmark size
    images = create_test_images(count=num_images)

    print()

    # Run benchmarks
    seq_time = None
    batch_time = None

    # Batch benchmark (primary test)
    batch_time, batch_meshes = benchmark_batch(processor, images)

    print()

    # Sequential benchmark (comparison - optional, can be slow)
    run_sequential = input("Run sequential benchmark for comparison? (y/N): ").lower() == 'y'
    if run_sequential:
        seq_time, seq_meshes = benchmark_sequential(processor, images)
        print()

    # Compare results
    compare_results(seq_time, batch_time, target_time=25.0)

    # Final verdict
    print()
    logger.info("")
    if batch_time and batch_time < 25.0:
        logger.info("'ïë                    'úÖ PHASE 1 TARGET ACHIEVED! 'úÖ                 'ïë")
        logger.info(f"â•'         Batch processing: {batch_time:.2f}s < 25s target                   â•'")
    elif batch_time:
        logger.info("'ïë                    üìä BENCHMARK COMPLETE üìä                       'ïë")
        logger.info(f"â•'         Batch processing: {batch_time:.2f}s (target: <25s)               â•'")
    else:
        logger.info("                      BENCHMARK INCOMPLETE                      ")
    logger.info("")

    # GPU cleanup
    if gpu_stats.get('available'):
        logger.info("Cleaning up GPU memory...")
        gpu_mgr.cleanup_after_job()
        logger.info("'úÖ GPU cleanup complete")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nBenchmark interrupted by user")
    except Exception as e:
        logger.error(f"Benchmark failed: {e}")
        import traceback
        traceback.print_exc()
