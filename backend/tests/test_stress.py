"""
+==============================================================================â•—
|              ORFEAS Testing Suite - GPU Stress Testing                      |
|                    Comprehensive GPU load and stress tests                   |
+==============================================================================
"""
import pytest
import torch
import asyncio
from pathlib import Path
import sys
import time

backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from gpu_manager import GPUMemoryManager


@pytest.mark.stress
@pytest.mark.gpu
class TestGPUStressTests:
    """Comprehensive GPU stress testing suite."""

    def test_maximum_memory_allocation(self, gpu_available, gpu_memory_tracker):
        """Test GPU behavior at maximum memory allocation."""
        if not gpu_available:
            pytest.skip("GPU not available")

        manager = GPUMemoryManager()
        gpu_memory_tracker.start()

        tensors = []
        try:
            # Allocate memory until we reach ~80% capacity
            total_memory = torch.cuda.get_device_properties(0).total_memory / 1024**2
            target_memory = total_memory * 0.8

            chunk_size = 512
            while True:
                allocated = torch.cuda.memory_allocated() / 1024**2
                if allocated >= target_memory:
                    break

                tensor = torch.randn(chunk_size, chunk_size, device=manager.device)
                tensors.append(tensor)

                # Prevent infinite loop
                if len(tensors) > 1000:
                    break

            gpu_memory_tracker.stop()
            memory_stats = gpu_memory_tracker.get_stats()

            print(f"\nMaximum Memory Allocation Test:")
            print(f"  Tensors allocated: {len(tensors)}")
            print(f"  Peak memory: {memory_stats['peak_mb']:.2f} MB")
            print(f"  Total GPU memory: {total_memory:.2f} MB")
            print(f"  Utilization: {(memory_stats['peak_mb'] / total_memory * 100):.1f}%")

            assert memory_stats['peak_mb'] > 0

        finally:
            tensors.clear()
            manager.cleanup()

    @pytest.mark.slow
    def test_sustained_load(self, gpu_available):
        """Test GPU under sustained computational load."""
        if not gpu_available:
            pytest.skip("GPU not available")

        manager = GPUMemoryManager()
        duration_seconds = 10

        start_time = time.time()
        operations_completed = 0

        try:
            while time.time() - start_time < duration_seconds:
                # Perform intensive operations
                a = torch.randn(2048, 2048, device=manager.device)
                b = torch.randn(2048, 2048, device=manager.device)
                c = torch.matmul(a, b)

                del a, b, c
                operations_completed += 1

                if operations_completed % 10 == 0:
                    manager.cleanup()

            elapsed = time.time() - start_time
            ops_per_second = operations_completed / elapsed

            print(f"\nSustained Load Test:")
            print(f"  Duration: {elapsed:.2f}s")
            print(f"  Operations: {operations_completed}")
            print(f"  Ops/second: {ops_per_second:.2f}")

            assert operations_completed > 0
            assert ops_per_second > 0.1  # At least some operations completed

        finally:
            manager.cleanup()

    def test_rapid_allocation_deallocation(self, gpu_available, gpu_memory_tracker):
        """Test rapid memory allocation and deallocation cycles."""
        if not gpu_available:
            pytest.skip("GPU not available")

        manager = GPUMemoryManager()
        gpu_memory_tracker.start()

        num_cycles = 100

        for i in range(num_cycles):
            # Allocate
            tensor = torch.randn(1024, 1024, device=manager.device)

            # Use it
            result = tensor.mean()

            # Deallocate
            del tensor, result

            if i % 10 == 0:
                manager.cleanup()

        gpu_memory_tracker.stop()
        memory_stats = gpu_memory_tracker.get_stats()

        print(f"\nRapid Allocation/Deallocation Test:")
        print(f"  Cycles completed: {num_cycles}")
        print(f"  Memory growth: {memory_stats['delta_mb']:.2f} MB")

        # Memory shouldn't grow excessively (check for leaks)
        assert memory_stats['delta_mb'] < 1000  # Less than 1GB growth

    @pytest.mark.asyncio
    async def test_concurrent_gpu_tasks(self, gpu_available):
        """Test concurrent GPU task execution."""
        if not gpu_available:
            pytest.skip("GPU not available")

        manager = GPUMemoryManager()

        async def gpu_task(task_id: int, size: int):
            """Simulate concurrent GPU task."""
            tensor = torch.randn(size, size, device=manager.device)
            await asyncio.sleep(0.1)  # Simulate processing
            result = tensor.sum().item()
            del tensor
            return result

        # Run multiple concurrent tasks
        num_tasks = 10
        tasks = [gpu_task(i, 512) for i in range(num_tasks)]

        start_time = time.time()
        results = await asyncio.gather(*tasks)
        elapsed = time.time() - start_time

        print(f"\nConcurrent GPU Tasks:")
        print(f"  Tasks: {num_tasks}")
        print(f"  Total time: {elapsed:.2f}s")
        print(f"  Time per task: {elapsed/num_tasks:.2f}s")

        assert len(results) == num_tasks
        manager.cleanup()

    def test_mixed_precision_operations(self, gpu_available):
        """Test mixed precision (FP16/FP32) operations."""
        if not gpu_available:
            pytest.skip("GPU not available")

        manager = GPUMemoryManager()

        # FP32 operations
        fp32_tensor = torch.randn(1024, 1024, dtype=torch.float32, device=manager.device)
        fp32_result = fp32_tensor @ fp32_tensor.T

        # FP16 operations
        fp16_tensor = torch.randn(1024, 1024, dtype=torch.float16, device=manager.device)
        fp16_result = fp16_tensor @ fp16_tensor.T

        # Mixed precision
        mixed_result = fp32_tensor @ fp16_tensor.to(torch.float32).T

        assert fp32_result.shape == (1024, 1024)
        assert fp16_result.shape == (1024, 1024)
        assert mixed_result.shape == (1024, 1024)

        del fp32_tensor, fp16_tensor, fp32_result, fp16_result, mixed_result
        manager.cleanup()

    @pytest.mark.slow
    def test_memory_fragmentation(self, gpu_available, gpu_memory_tracker):
        """Test GPU memory fragmentation under varied allocations."""
        if not gpu_available:
            pytest.skip("GPU not available")

        manager = GPUMemoryManager()
        gpu_memory_tracker.start()

        tensors = []
        sizes = [256, 512, 1024, 2048, 512, 256, 1024]  # Varied sizes

        try:
            # Allocate varied sizes
            for size in sizes:
                tensor = torch.randn(size, size, device=manager.device)
                tensors.append(tensor)

            # Free every other tensor (create fragmentation)
            # Delete from end to avoid index shifting issues
            indices_to_delete = list(range(0, len(tensors), 2))
            for i in reversed(indices_to_delete):
                del tensors[i]

            manager.cleanup()

            # Allocate more after fragmentation
            for size in [1024, 1024, 512]:
                tensor = torch.randn(size, size, device=manager.device)
                tensors.append(tensor)

            gpu_memory_tracker.stop()
            memory_stats = gpu_memory_tracker.get_stats()

            print(f"\nMemory Fragmentation Test:")
            print(f"  Peak allocated: {memory_stats['peak_mb']:.2f} MB")
            print(f"  Peak reserved: {memory_stats.get('peak_reserved_mb', memory_stats['peak_mb']):.2f} MB")
            print(f"  Fragmentation overhead: {(memory_stats.get('peak_reserved_mb', memory_stats['peak_mb']) - memory_stats['peak_mb']):.2f} MB")

            # Should handle fragmentation without excessive overhead
            fragmentation_ratio = memory_stats.get('peak_reserved_mb', memory_stats['peak_mb']) / memory_stats['peak_mb']
            assert fragmentation_ratio < 2.0  # Less than 2x overhead

        finally:
            tensors.clear()
            manager.cleanup()


@pytest.mark.stress
class TestPerformanceRegression:
    """Performance regression testing."""

    def test_baseline_performance(self, gpu_available, performance_tracker):
        """Establish baseline performance metrics."""
        if not gpu_available:
            pytest.skip("GPU not available")

        manager = GPUMemoryManager()

        # Standard operation
        performance_tracker.start()

        tensor = torch.randn(2048, 2048, device=manager.device)
        result = tensor @ tensor.T
        final = result.mean().item()

        elapsed = performance_tracker.stop()

        print(f"\nBaseline Performance:")
        print(f"  Matrix multiplication (2048x2048): {elapsed:.4f}s")

        # Baseline is automatically stored by stop() in metrics dict
        # Access later with: performance_tracker.get_metric("default")

        # Should complete in reasonable time
        assert elapsed < 1.0  # Less than 1 second on RTX 3090

        del tensor, result
        manager.cleanup()
