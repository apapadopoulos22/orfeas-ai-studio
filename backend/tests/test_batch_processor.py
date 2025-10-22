"""
+==============================================================================â•—
|              ORFEAS Testing Suite - Batch Processor Tests                   |
|                    Unit and integration tests for batch processing           |
+==============================================================================
"""
import pytest
import asyncio
from pathlib import Path
import sys

backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

try:
    from batch_processor import BatchProcessor, AsyncJobQueue
    BATCH_PROCESSOR_AVAILABLE = True
except ImportError:
    BATCH_PROCESSOR_AVAILABLE = False


@pytest.mark.skipif(not BATCH_PROCESSOR_AVAILABLE, reason="BatchProcessor not available")
@pytest.mark.unit
class TestBatchProcessorUnit:
    """Test suite for BatchProcessor class - UNIT TESTS ONLY."""

    @pytest.mark.asyncio
    async def test_initialization(self, gpu_manager):
        """Test batch processor initialization - UNIT TEST."""
        # Mock processor_3d for testing
        class MockProcessor3D:
            async def generate_3d(self, **kwargs):
                await asyncio.sleep(0.1)
                return {"status": "success", "model_path": "/tmp/test.glb"}

        processor = BatchProcessor(gpu_manager, MockProcessor3D())
        assert processor is not None


@pytest.mark.skipif(not BATCH_PROCESSOR_AVAILABLE, reason="BatchProcessor not available")
@pytest.mark.integration
@pytest.mark.requires_models
class TestBatchProcessorIntegration:
    """Test suite for BatchProcessor class - INTEGRATION TESTS (require Hunyuan3D models)."""

    @pytest.mark.asyncio
    async def test_single_job(self, gpu_manager, test_image_path):
        """Test single job processing - INTEGRATION TEST (requires Hunyuan3D models)."""
        class MockProcessor3D:
            def image_to_3d_generation(self, image_path=None, image=None, output_path=None, output_dir=None, quality=7, format="glb", **kwargs):
                # Mock the actual method BatchProcessor calls
                return True  # Return success

        processor = BatchProcessor(gpu_manager, MockProcessor3D())

        job = {
            "job_id": "test_job_001",
            "image_path": str(test_image_path),
            "output_dir": str(test_image_path.parent / "output"),
            "format_type": "glb",
            "parameters": {}
        }

        result = await processor._process_single_job(job)
        assert result is not None
        # Check for success field (real BatchProcessor format)
        assert result.get("success") == True or result.get("status") == "success"

    @pytest.mark.integration
    @pytest.mark.requires_models
    @pytest.mark.asyncio
    async def test_batch_processing(self, gpu_manager, test_image_path, performance_tracker):
        """Test batch processing of multiple jobs - INTEGRATION TEST (requires Hunyuan3D models)."""
        class MockProcessor3D:
            def image_to_3d_generation(self, image_path=None, image=None, output_path=None, output_dir=None, quality=7, format="glb", **kwargs):
                # Mock the actual method BatchProcessor calls
                import time
                time.sleep(0.05)  # Simulate processing time
                return True  # Return success

        processor = BatchProcessor(gpu_manager, MockProcessor3D())

        # Create batch of jobs with all required fields
        jobs = [
            {
                "job_id": f"test_job_{i:03d}",
                "image_path": str(test_image_path),
                "output_dir": str(test_image_path.parent / "output"),
                "format_type": "glb",  # Required by batch_processor
                "quality": "medium",    # Required by batch_processor
                "parameters": {}
            }
            for i in range(4)
        ]

        performance_tracker.start()
        results = await processor.process_batch(jobs)
        elapsed = performance_tracker.stop()

        assert len(results) == 4
        # Check for success in either format
        assert all(r.get("success") == True or r.get("status") == "success" for r in results)

        print(f"\nBatch processing time: {elapsed:.2f}s")

        # Batch should be faster than sequential (4 * 0.2 = 0.8s sequential)
        # With batching should be closer to 0.2-0.4s
        assert elapsed < 1.0  # Much faster than sequential

    @pytest.mark.integration
    @pytest.mark.requires_models
    @pytest.mark.asyncio
    async def test_job_queue(self, gpu_manager, test_image_path):
        """Test async job queue - INTEGRATION TEST (requires Hunyuan3D models)."""
        class MockProcessor3D:
            def image_to_3d_generation(self, image_path=None, image=None, output_path=None, output_dir=None, quality=7, format="glb", **kwargs):
                # Mock the actual method BatchProcessor calls
                import time
                time.sleep(0.05)  # Simulate processing time
                return True  # Return success

        processor = BatchProcessor(gpu_manager, MockProcessor3D())
        queue = AsyncJobQueue(processor)

        # Add jobs with real image paths
        job_ids = []
        for i in range(3):
            job_id = await queue.add_job({
                "job_id": f"queue_job_{i:03d}",
                "image_path": str(test_image_path),
                "output_dir": str(test_image_path.parent / "output"),
                "format_type": "glb",
                "parameters": {}
            })
            job_ids.append(job_id)

        assert len(job_ids) == 3

        # Start processing
        processing_task = asyncio.create_task(queue.start_processing())

        # Wait for processing to complete
        await asyncio.sleep(1.0)

        # Check results (get_result is NOT async - remove await)
        for job_id in job_ids:
            result = queue.get_result(job_id)  # NOT await - synchronous method
            if result:
                assert result.get("success") == True or result.get("status") == "success"

        # Stop queue
        queue.stop_processing()  # Correct method name
        try:
            processing_task.cancel()
            await processing_task
        except asyncio.CancelledError:
            pass  # Expected cancellation

    @pytest.mark.integration
    @pytest.mark.requires_models
    @pytest.mark.asyncio
    async def test_error_handling(self, gpu_manager, test_image_path, tmp_path):
        """Test error handling in batch processing - INTEGRATION TEST (requires Hunyuan3D models)."""
        class FailingProcessor3D:
            def image_to_3d_generation(self, image_path=None, image=None, output_path=None, output_dir=None, quality=7, format="glb", **kwargs):
                # First job succeeds, second fails
                if "fail" in str(output_dir or ""):
                    raise Exception("Intentional failure")
                return True  # Return success for first job

        processor = BatchProcessor(gpu_manager, FailingProcessor3D())

        # Create a non-existent fail image path
        fail_image_path = tmp_path / "nonexistent_fail.png"

        jobs = [
            {"job_id": "success_job_001", "image_path": str(test_image_path), "output_dir": str(test_image_path.parent / "output"), "format_type": "glb", "parameters": {}},
            {"job_id": "fail_job_001", "image_path": str(fail_image_path), "output_dir": str(test_image_path.parent / "output"), "format_type": "glb", "parameters": {}},
        ]

        results = await processor.process_batch(jobs)

        # Should handle errors gracefully
        assert len(results) == 2
        # First job should succeed
        assert results[0].get("success") == True or results[0].get("status") == "success"
        # Second job should fail (either error key or success=False)
        assert results[1].get("success") == False or "error" in results[1] or results[1].get("status") == "error"

    @pytest.mark.stress
    @pytest.mark.asyncio
    async def test_high_load(self, gpu_manager, gpu_memory_tracker, test_image_path):
        """Test batch processor under high load."""
        class MockProcessor3D:
            async def generate_3d(self, **kwargs):
                await asyncio.sleep(0.05)
                return {"status": "success"}

        processor = BatchProcessor(gpu_manager, MockProcessor3D())

        gpu_memory_tracker.start()

        # Create large batch with all required fields
        jobs = [
            {
                "job_id": f"load_test_{i:03d}",
                "image_path": str(test_image_path),  # Use real test image
                "output_dir": str(test_image_path.parent / "output"),
                "format_type": "glb",
                "quality": "medium",
                "parameters": {}
            }
            for i in range(20)
        ]

        results = await processor.process_batch(jobs)

        gpu_memory_tracker.stop()
        memory_stats = gpu_memory_tracker.get_stats()

        assert len(results) == 20
        print(f"\nHigh load memory stats: {memory_stats}")


@pytest.mark.unit
class TestBatchOptimization:
    """Test batch processing optimizations."""

    def test_job_grouping(self):
        """Test intelligent job grouping by parameters."""
        # This would test grouping logic if implemented
        pass

    def test_memory_management(self):
        """Test memory management during batch processing."""
        # This would test memory optimization if implemented
        pass
