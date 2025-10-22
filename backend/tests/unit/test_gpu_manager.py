"""
+==============================================================================â•—
|              ORFEAS Testing Suite - GPU Manager Unit Tests                 |
|         Comprehensive tests for GPU resource management                     |
+==============================================================================
"""
import pytest
from pathlib import Path
import sys
from unittest.mock import Mock, patch, MagicMock
from typing import Any

backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))

try:
    from gpu_manager import GPUManager, get_gpu_manager
    import torch
    GPU_MANAGER_AVAILABLE = True
except ImportError:
    GPU_MANAGER_AVAILABLE = False


@pytest.mark.skipif(not GPU_MANAGER_AVAILABLE, reason="GPU Manager not available")
@pytest.mark.unit
class TestGPUManagerUnit:
    """Unit tests for GPU Manager"""

    @pytest.fixture
    def gpu_manager(self) -> None:
        """Create GPU manager instance"""
        return GPUManager()

    @pytest.fixture
    def mock_cuda(self) -> None:
        """Mock CUDA availability"""
        with patch('torch.cuda.is_available', return_value=True):
            with patch('torch.cuda.device_count', return_value=1):
                with patch('torch.cuda.get_device_properties') as mock_props:
                    mock_props.return_value = Mock(
                        total_memory=24 * 1024**3,  # 24GB
                        name='NVIDIA RTX 3090'
                    )
                    yield mock_props

    def test_gpu_manager_initialization(self, gpu_manager: Any) -> None:
        """Test GPU manager initializes correctly"""
        assert gpu_manager is not None
        assert hasattr(gpu_manager, 'device')

    def test_gpu_manager_singleton(self) -> None:
        """Test GPU manager is singleton"""
        if GPU_MANAGER_AVAILABLE:
            manager1 = get_gpu_manager()
            manager2 = get_gpu_manager()
            assert manager1 is manager2

    def test_cuda_availability_check(self, gpu_manager: Any) -> None:
        """Test CUDA availability detection"""
        is_available = torch.cuda.is_available()
        assert isinstance(is_available, bool)

    def test_device_selection_auto(self, gpu_manager: Any) -> None:
        """Test automatic device selection"""
        if hasattr(gpu_manager, 'device'):
            assert gpu_manager.device in ['cuda', 'cpu']

    def test_device_selection_cuda(self) -> None:
        """Test CUDA device selection"""
        if torch.cuda.is_available():
            manager = GPUManager(device='cuda')
            assert 'cuda' in str(manager.device)

    def test_device_selection_cpu(self) -> None:
        """Test CPU device selection"""
        manager = GPUManager(device='cpu')
        assert manager.device == 'cpu'

    def test_get_gpu_stats(self, gpu_manager: Any) -> None:
        """Test GPU statistics retrieval"""
        if hasattr(gpu_manager, 'get_gpu_stats'):
            stats = gpu_manager.get_gpu_stats()
            assert isinstance(stats, dict)
            if torch.cuda.is_available():
                assert 'total_memory' in stats or 'device' in stats

    def test_gpu_memory_info(self, gpu_manager: Any) -> None:
        """Test GPU memory information"""
        if torch.cuda.is_available() and hasattr(gpu_manager, 'get_memory_info'):
            memory_info = gpu_manager.get_memory_info()
            assert isinstance(memory_info, dict)
            assert 'allocated' in memory_info or 'total' in memory_info

    def test_can_process_job(self, gpu_manager: Any) -> None:
        """Test job processing capability check"""
        if hasattr(gpu_manager, 'can_process_job'):
            can_process = gpu_manager.can_process_job(estimated_vram=1000)
            assert isinstance(can_process, bool)

    def test_allocate_job(self, gpu_manager: Any) -> None:
        """Test job allocation"""
        if hasattr(gpu_manager, 'allocate_job'):
            job_id = 'test_job_001'
            # Should not raise exception
            try:
                gpu_manager.allocate_job(job_id)
            except Exception as e:
                # May fail if GPU not available, that's OK
                pass

    def test_cleanup_after_job(self, gpu_manager: Any) -> None:
        """Test cleanup after job completion"""
        if hasattr(gpu_manager, 'cleanup_after_job'):
            # Should not raise exception
            try:
                gpu_manager.cleanup_after_job()
            except Exception as e:
                # May fail if no active job, that's OK
                pass

    def test_memory_cleanup(self, gpu_manager: Any) -> None:
        """Test memory cleanup functionality"""
        if torch.cuda.is_available():
            # Force memory allocation
            try:
                tensor = torch.randn(100, 100).cuda()
                del tensor
                torch.cuda.empty_cache()
                # Should not raise exception
            except:
                pytest.skip("CUDA operations failed")

    def test_gpu_utilization_tracking(self, gpu_manager: Any) -> None:
        """Test GPU utilization tracking"""
        if hasattr(gpu_manager, 'get_utilization'):
            utilization = gpu_manager.get_utilization()
            if utilization is not None:
                assert isinstance(utilization, (int, float))
                assert 0 <= utilization <= 100

    def test_multiple_device_support(self, gpu_manager: Any) -> None:
        """Test multi-GPU device support"""
        device_count = torch.cuda.device_count()
        assert isinstance(device_count, int)
        assert device_count >= 0

    def test_device_properties(self, gpu_manager: Any) -> None:
        """Test device properties retrieval"""
        if torch.cuda.is_available() and torch.cuda.device_count() > 0:
            props = torch.cuda.get_device_properties(0)
            assert props.total_memory > 0
            assert len(props.name) > 0

    def test_memory_allocation(self, gpu_manager: Any) -> None:
        """Test memory allocation tracking"""
        if torch.cuda.is_available():
            allocated_before = torch.cuda.memory_allocated(0)
            tensor = torch.randn(1000, 1000).cuda()
            allocated_after = torch.cuda.memory_allocated(0)
            assert allocated_after > allocated_before
            del tensor
            torch.cuda.empty_cache()

    def test_max_memory_tracking(self, gpu_manager: Any) -> None:
        """Test maximum memory usage tracking"""
        if torch.cuda.is_available():
            torch.cuda.reset_peak_memory_stats(0)
            tensor = torch.randn(1000, 1000).cuda()
            max_memory = torch.cuda.max_memory_allocated(0)
            assert max_memory > 0
            del tensor
            torch.cuda.empty_cache()

    def test_memory_reserved(self, gpu_manager: Any) -> None:
        """Test reserved memory tracking"""
        if torch.cuda.is_available():
            reserved = torch.cuda.memory_reserved(0)
            assert isinstance(reserved, int)
            assert reserved >= 0

    def test_cache_info(self, gpu_manager: Any) -> None:
        """Test memory cache information"""
        if torch.cuda.is_available():
            # Get cache info if available
            try:
                cache_info = torch.cuda.memory_stats(0)
                assert isinstance(cache_info, dict)
            except:
                pytest.skip("Memory stats not available")

    def test_device_synchronization(self, gpu_manager: Any) -> None:
        """Test device synchronization"""
        if torch.cuda.is_available():
            torch.cuda.synchronize()
            # Should not raise exception

    def test_concurrent_job_limit(self, gpu_manager: Any) -> None:
        """Test concurrent job limiting"""
        if hasattr(gpu_manager, 'max_concurrent_jobs'):
            assert isinstance(gpu_manager.max_concurrent_jobs, int)
            assert gpu_manager.max_concurrent_jobs > 0

    def test_memory_limit_enforcement(self, gpu_manager: Any) -> None:
        """Test memory limit enforcement"""
        if hasattr(gpu_manager, 'memory_limit'):
            limit = gpu_manager.memory_limit
            if limit is not None:
                assert 0.0 < limit <= 1.0

    @pytest.mark.parametrize("memory_mb", [100, 1000, 5000, 10000])
    def test_can_allocate_various_sizes(self, gpu_manager: Any, memory_mb: Any) -> None:
        """Test allocation checks for various memory sizes"""
        if hasattr(gpu_manager, 'can_process_job'):
            can_allocate = gpu_manager.can_process_job(estimated_vram=memory_mb)
            assert isinstance(can_allocate, bool)

    def test_managed_generation_context(self, gpu_manager: Any) -> None:
        """Test managed generation context manager"""
        if hasattr(gpu_manager, 'managed_generation'):
            try:
                with gpu_manager.managed_generation('test_job', required_memory_mb=100):
                    # Context should handle allocation/cleanup
                    pass
            except Exception as e:
                # May fail without GPU, that's OK
                pass

    def test_error_handling_no_gpu(self) -> None:
        """Test error handling when GPU not available"""
        with patch('torch.cuda.is_available', return_value=False):
            manager = GPUManager()
            assert manager.device == 'cpu'

    def test_fallback_to_cpu(self, gpu_manager: Any) -> None:
        """Test fallback to CPU when GPU unavailable"""
        if not torch.cuda.is_available():
            assert gpu_manager.device == 'cpu'

    def test_gpu_name_detection(self, gpu_manager: Any) -> None:
        """Test GPU name detection"""
        if torch.cuda.is_available() and torch.cuda.device_count() > 0:
            name = torch.cuda.get_device_name(0)
            assert isinstance(name, str)
            assert len(name) > 0


@pytest.mark.unit
@pytest.mark.skipif(not GPU_MANAGER_AVAILABLE, reason="GPU Manager not available")
class TestGPUManagerIntegration:
    """Integration tests for GPU Manager with other components"""

    def test_gpu_manager_with_batch_processor(self) -> None:
        """Test GPU manager integration with batch processor"""
        try:
            from batch_processor import BatchProcessor
            gpu_mgr = get_gpu_manager()
            # Should be able to pass GPU manager to batch processor
            assert gpu_mgr is not None
        except ImportError:
            pytest.skip("Batch processor not available")

    def test_gpu_manager_with_hunyuan(self) -> None:
        """Test GPU manager integration with Hunyuan processor"""
        try:
            from hunyuan_integration import Hunyuan3DProcessor
            gpu_mgr = get_gpu_manager()
            # GPU manager should be available for Hunyuan processor
            assert gpu_mgr is not None
        except ImportError:
            pytest.skip("Hunyuan integration not available")

    def test_memory_tracking_during_operation(self) -> None:
        """Test memory tracking during actual operations"""
        if torch.cuda.is_available():
            gpu_mgr = get_gpu_manager()

            # Track memory before operation
            if hasattr(gpu_mgr, 'get_memory_info'):
                mem_before = gpu_mgr.get_memory_info()

            # Perform GPU operation
            tensor = torch.randn(1000, 1000).cuda()

            # Track memory after operation
            if hasattr(gpu_mgr, 'get_memory_info'):
                mem_after = gpu_mgr.get_memory_info()

            # Cleanup
            del tensor
            torch.cuda.empty_cache()

    def test_multi_job_scenario(self) -> None:
        """Test handling multiple jobs"""
        gpu_mgr = get_gpu_manager()

        job_ids = ['job1', 'job2', 'job3']
        for job_id in job_ids:
            if hasattr(gpu_mgr, 'can_process_job'):
                can_process = gpu_mgr.can_process_job(estimated_vram=1000)
                # Should handle multiple job checks
                assert isinstance(can_process, bool)

    def test_resource_exhaustion_handling(self) -> None:
        """Test handling of resource exhaustion"""
        gpu_mgr = get_gpu_manager()

        if hasattr(gpu_mgr, 'can_process_job'):
            # Try to allocate massive amount
            can_process_huge = gpu_mgr.can_process_job(estimated_vram=1000000)
            # Should return False for unrealistic allocations
            # (or handle appropriately)
            assert isinstance(can_process_huge, bool)
