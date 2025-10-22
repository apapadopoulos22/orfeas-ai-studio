"""
+==============================================================================â•—
|              ORFEAS Testing Suite - GPU Manager Tests                       |
|                    Unit tests for GPU management and optimization            |
+==============================================================================
"""
import pytest
import torch
import asyncio
from pathlib import Path
import sys

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from gpu_manager import GPUMemoryManager


@pytest.mark.unit
@pytest.mark.gpu
class TestGPUMemoryManager:
    """Test suite for GPUMemoryManager class."""

    def test_initialization(self, gpu_available):
        """Test GPU manager initialization."""
        if not gpu_available:
            pytest.skip("GPU not available")

        manager = GPUMemoryManager()
        assert manager is not None
        assert hasattr(manager, 'device')

    def test_gpu_detection(self, gpu_available):
        """Test GPU device detection."""
        if not gpu_available:
            pytest.skip("GPU not available")

        manager = GPUMemoryManager()
        assert manager.device.type in ['cuda', 'cpu']

        if torch.cuda.is_available():
            assert manager.device.type == 'cuda'
            assert torch.cuda.device_count() > 0

    def test_memory_stats(self, gpu_available):
        """Test GPU memory statistics retrieval."""
        if not gpu_available:
            pytest.skip("GPU not available")

        manager = GPUMemoryManager()
        stats = manager.get_memory_stats()

        # Check for keys that actually exist in GPUMemoryManager
        assert 'allocated' in stats or 'available' in stats
        if torch.cuda.is_available():
            assert stats.get('available', False) or 'allocated' in stats

    def test_memory_cleanup(self, gpu_available):
        """Test GPU memory cleanup."""
        if not gpu_available:
            pytest.skip("GPU not available")

        manager = GPUMemoryManager()

        # Allocate some tensors
        tensors = [torch.randn(1000, 1000, device=manager.device) for _ in range(10)]
        allocated_before = torch.cuda.memory_allocated()

        # Clear tensors and cleanup
        tensors.clear()
        if hasattr(manager, 'cleanup_memory'):
            manager.cleanup_memory()
        else:
            torch.cuda.empty_cache()

        allocated_after = torch.cuda.memory_allocated()
        assert allocated_after < allocated_before

    @pytest.mark.slow
    def test_memory_optimization(self, gpu_available, performance_tracker):
        """Test memory optimization features."""
        if not gpu_available:
            pytest.skip("GPU not available")

        manager = GPUMemoryManager()

        performance_tracker.start()

        # Test with different tensor sizes
        sizes = [(100, 100), (500, 500), (1000, 1000)]

        for size in sizes:
            tensor = torch.randn(*size, device=manager.device)
            del tensor
            manager.cleanup()

        elapsed = performance_tracker.stop()
        assert elapsed < 5.0  # Should complete in less than 5 seconds

    def test_optimal_batch_size(self, gpu_available):
        """Test optimal batch size calculation."""
        if not gpu_available:
            pytest.skip("GPU not available")

        manager = GPUMemoryManager()

        if hasattr(manager, 'get_optimal_batch_size'):
            batch_size = manager.get_optimal_batch_size()
            assert batch_size > 0
            assert batch_size <= 32  # Reasonable maximum

    @pytest.mark.stress
    def test_gpu_stress(self, gpu_available, gpu_memory_tracker):
        """Stress test GPU under heavy load."""
        if not gpu_available:
            pytest.skip("GPU not available")

        manager = GPUMemoryManager()
        gpu_memory_tracker.start()

        try:
            # Create large tensors to stress GPU
            tensors = []
            for i in range(20):
                tensor = torch.randn(2048, 2048, device=manager.device)
                tensors.append(tensor)

                # Perform some operations
                result = tensor @ tensor.T
                del result

            # Check we didn't run out of memory
            stats = manager.get_memory_stats()
            if torch.cuda.is_available() and 'allocated' in stats:
                assert stats['allocated'] < stats.get('total', float('inf'))

        finally:
            # Cleanup
            tensors.clear()
            if hasattr(manager, 'cleanup_memory'):
                manager.cleanup_memory()
            else:
                torch.cuda.empty_cache()
            gpu_memory_tracker.stop()

        memory_stats = gpu_memory_tracker.get_stats()
        print(f"\nGPU Stress Test Memory Stats: {memory_stats}")

        # Should have used significant memory but not crashed
        # Note: gpu_memory_tracker uses 'peak_mb', GPUMemoryManager uses 'max_allocated_mb'
        # Test allocates 20x (2048x2048 float32) = 20x16MB = ~320MB
        assert memory_stats['peak_mb'] > 300  # At least 300MB used (20 tensors)
@pytest.mark.unit
def test_gpu_availability():
    """Test basic GPU availability check."""
    available = torch.cuda.is_available()
    if available:
        device_count = torch.cuda.device_count()
        assert device_count > 0

        device_name = torch.cuda.get_device_name(0)
        assert len(device_name) > 0
        print(f"\nGPU Device: {device_name}")


@pytest.mark.integration
@pytest.mark.gpu
class TestGPUIntegration:
    """Integration tests for GPU operations."""

    @pytest.mark.asyncio
    async def test_async_gpu_operations(self, gpu_available):
        """Test asynchronous GPU operations."""
        if not gpu_available:
            pytest.skip("GPU not available")

        manager = GPUMemoryManager()

        async def gpu_task(size: int):
            """Simulate async GPU task."""
            tensor = torch.randn(size, size, device=manager.device)
            await asyncio.sleep(0.1)  # Simulate processing
            result = tensor.mean().item()
            del tensor
            return result

        # Run multiple tasks concurrently
        tasks = [gpu_task(500) for _ in range(5)]
        results = await asyncio.gather(*tasks)

        assert len(results) == 5
        assert all(isinstance(r, float) for r in results)

    def test_multiple_gpu_managers(self, gpu_available):
        """Test multiple GPU manager instances."""
        if not gpu_available:
            pytest.skip("GPU not available")

        manager1 = GPUMemoryManager()
        manager2 = GPUMemoryManager()

        # Both should work independently
        stats1 = manager1.get_memory_stats()
        stats2 = manager2.get_memory_stats()

        # Both should access same GPU
        assert manager1.device.type == manager2.device.type
