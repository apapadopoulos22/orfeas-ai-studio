"""
ORFEAS Performance Tests - Memory Usage and Leak Detection
Tests to ensure no memory leaks and proper resource cleanup
"""
import pytest
import requests
import psutil
import gc
import time
import sys
from pathlib import Path
from typing import Any, List, Tuple

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


# ============================================================================
# Configuration
# ============================================================================

SERVER_URL = "http://127.0.0.1:5000"
MEMORY_THRESHOLD_MB = 100  # Maximum memory growth allowed (MB)
ITERATIONS = 50  # Number of iterations for leak detection


# ============================================================================
# Helper Functions
# ============================================================================

def get_process_memory_mb() -> None:
    """Get current process memory usage in MB"""
    process = psutil.Process()
    return process.memory_info().rss / 1024 / 1024


def measure_memory_growth(test_function: Any, iterations: List = ITERATIONS) -> Tuple:
    """
    Measure memory growth during repeated operations

    Args:
        test_function: Function to execute repeatedly
        iterations: Number of iterations

    Returns:
        Tuple of (initial_memory_mb, final_memory_mb, growth_mb)
    """
    # Force garbage collection before measurement
    gc.collect()
    time.sleep(0.1)

    initial_memory = get_process_memory_mb()

    # Execute test function multiple times
    for i in range(iterations):
        test_function()

        # Periodic garbage collection
        if i % 10 == 0:
            gc.collect()

    # Final garbage collection
    gc.collect()
    time.sleep(0.1)

    final_memory = get_process_memory_mb()
    growth = final_memory - initial_memory

    return initial_memory, final_memory, growth


# ============================================================================
# API Request Memory Leak Tests
# ============================================================================

@pytest.mark.performance
@pytest.mark.slow
class TestAPIMemoryLeaks:
    """Test for memory leaks in API requests"""

    def test_health_check_memory_leak(self) -> None:
        """Test that repeated health checks don't leak memory"""
        def health_check() -> None:
            try:
                response = requests.get(f"{SERVER_URL}/api/health", timeout=5)
                _ = response.json()  # Parse response
            except:
                pass

        initial, final, growth = measure_memory_growth(health_check, iterations=100)

        print(f"\nHealth Check Memory Test:")
        print(f"  Initial: {initial:.2f} MB")
        print(f"  Final: {final:.2f} MB")
        print(f"  Growth: {growth:.2f} MB")

        assert growth < MEMORY_THRESHOLD_MB, \
            f"Memory leak detected: {growth:.2f} MB growth (threshold: {MEMORY_THRESHOLD_MB} MB)"

    def test_models_info_memory_leak(self) -> None:
        """Test that repeated models-info requests don't leak memory"""
        def models_info() -> None:
            try:
                response = requests.get(f"{SERVER_URL}/api/models-info", timeout=5)
                _ = response.json()
            except:
                pass

        initial, final, growth = measure_memory_growth(models_info, iterations=100)

        print(f"\nModels Info Memory Test:")
        print(f"  Initial: {initial:.2f} MB")
        print(f"  Final: {final:.2f} MB")
        print(f"  Growth: {growth:.2f} MB")

        assert growth < MEMORY_THRESHOLD_MB, \
            f"Memory leak detected: {growth:.2f} MB growth"


# ============================================================================
# Large Response Memory Tests
# ============================================================================

@pytest.mark.performance
@pytest.mark.slow
class TestLargeResponseMemory:
    """Test memory handling with large responses"""

    def test_large_json_response_cleanup(self) -> None:
        """Test that large JSON responses are properly cleaned up"""
        initial_memory = get_process_memory_mb()

        # Make multiple requests that return potentially large responses
        for _ in range(20):
            try:
                response = requests.get(f"{SERVER_URL}/api/health", timeout=5)
                data = response.json()
                # Use the data
                _ = str(data)
            except:
                pass

        gc.collect()
        time.sleep(0.1)

        final_memory = get_process_memory_mb()
        growth = final_memory - initial_memory

        print(f"\nLarge Response Memory Test:")
        print(f"  Initial: {initial_memory:.2f} MB")
        print(f"  Final: {final_memory:.2f} MB")
        print(f"  Growth: {growth:.2f} MB")

        assert growth < 50, \
            f"Excessive memory growth: {growth:.2f} MB"


# ============================================================================
# Resource Cleanup Tests
# ============================================================================

@pytest.mark.performance
class TestResourceCleanup:
    """Test proper cleanup of resources"""

    def test_connection_pool_cleanup(self) -> None:
        """Test that connection pools are properly managed"""
        session = requests.Session()

        initial_memory = get_process_memory_mb()

        # Make many requests with the same session
        for _ in range(100):
            try:
                response = session.get(f"{SERVER_URL}/api/health", timeout=5)
                _ = response.json()
            except:
                pass

        # Close session
        session.close()
        gc.collect()
        time.sleep(0.1)

        final_memory = get_process_memory_mb()
        growth = final_memory - initial_memory

        print(f"\nConnection Pool Memory Test:")
        print(f"  Initial: {initial_memory:.2f} MB")
        print(f"  Final: {final_memory:.2f} MB")
        print(f"  Growth: {growth:.2f} MB")

        assert growth < MEMORY_THRESHOLD_MB, \
            f"Connection pool memory leak: {growth:.2f} MB growth"

    def test_garbage_collection_effectiveness(self) -> None:
        """Test that garbage collection is effective"""
        # Create temporary objects
        temp_data = []
        for i in range(1000):
            temp_data.append({"index": i, "data": "x" * 1000})

        memory_with_objects = get_process_memory_mb()

        # Clear references
        temp_data = None

        # Force garbage collection
        gc.collect()
        time.sleep(0.1)

        memory_after_gc = get_process_memory_mb()

        freed_memory = memory_with_objects - memory_after_gc

        print(f"\nGarbage Collection Test:")
        print(f"  Memory with objects: {memory_with_objects:.2f} MB")
        print(f"  Memory after GC: {memory_after_gc:.2f} MB")
        print(f"  Freed memory: {freed_memory:.2f} MB")

        # GC should free at least some memory
        assert freed_memory > 0, "Garbage collection not freeing memory"


# ============================================================================
# Continuous Operation Memory Tests
# ============================================================================

@pytest.mark.performance
@pytest.mark.slow
class TestContinuousOperationMemory:
    """Test memory stability during continuous operations"""

    def test_extended_operation_memory_stability(self) -> None:
        """Test memory stability during extended operation"""
        measurements = []

        # Measure memory every 10 iterations
        for iteration in range(5):
            for _ in range(10):
                try:
                    response = requests.get(f"{SERVER_URL}/api/health", timeout=5)
                    _ = response.json()
                except:
                    pass

            gc.collect()
            memory = get_process_memory_mb()
            measurements.append(memory)

        # Calculate memory trend
        initial = measurements[0]
        final = measurements[-1]
        growth = final - initial

        print(f"\nExtended Operation Memory Test:")
        print(f"  Measurements: {[f'{m:.2f}' for m in measurements]}")
        print(f"  Initial: {initial:.2f} MB")
        print(f"  Final: {final:.2f} MB")
        print(f"  Growth: {growth:.2f} MB")

        # Memory should not grow significantly
        assert growth < MEMORY_THRESHOLD_MB, \
            f"Memory growing over time: {growth:.2f} MB"

    def test_memory_returns_to_baseline(self) -> None:
        """Test that memory returns to baseline after load"""
        gc.collect()
        time.sleep(0.5)
        baseline_memory = get_process_memory_mb()

        # Generate load
        for _ in range(50):
            try:
                response = requests.get(f"{SERVER_URL}/api/health", timeout=5)
                _ = response.json()
            except:
                pass

        # Wait and collect garbage
        time.sleep(1)
        gc.collect()
        time.sleep(0.5)

        post_load_memory = get_process_memory_mb()
        difference = post_load_memory - baseline_memory

        print(f"\nMemory Baseline Recovery Test:")
        print(f"  Baseline: {baseline_memory:.2f} MB")
        print(f"  Post-load: {post_load_memory:.2f} MB")
        print(f"  Difference: {difference:.2f} MB")

        # Should return close to baseline (within 50MB)
        assert difference < 50, \
            f"Memory not returning to baseline: +{difference:.2f} MB"


# ============================================================================
# System Resource Tests
# ============================================================================

@pytest.mark.performance
class TestSystemResources:
    """Test overall system resource usage"""

    def test_cpu_usage_reasonable(self) -> None:
        """Test that CPU usage remains reasonable during requests"""
        process = psutil.Process()

        # Measure CPU over several requests
        cpu_percentages = []

        for _ in range(10):
            try:
                response = requests.get(f"{SERVER_URL}/api/health", timeout=5)
                cpu_percent = process.cpu_percent(interval=0.1)
                cpu_percentages.append(cpu_percent)
            except:
                pass

        avg_cpu = sum(cpu_percentages) / len(cpu_percentages) if cpu_percentages else 0

        print(f"\nCPU Usage Test:")
        print(f"  Average CPU: {avg_cpu:.2f}%")
        print(f"  Max CPU: {max(cpu_percentages):.2f}%")

        # CPU should not be constantly maxed
        assert avg_cpu < 80, f"CPU usage too high: {avg_cpu:.2f}%"

    def test_open_file_descriptors(self) -> None:
        """Test that file descriptors are properly closed"""
        process = psutil.Process()

        try:
            initial_fds = len(process.open_files())
        except:
            pytest.skip("Cannot access file descriptors on this platform")

        # Make many requests
        for _ in range(50):
            try:
                response = requests.get(f"{SERVER_URL}/api/health", timeout=5)
                _ = response.json()
            except:
                pass

        gc.collect()
        time.sleep(0.5)

        final_fds = len(process.open_files())
        growth = final_fds - initial_fds

        print(f"\nFile Descriptor Test:")
        print(f"  Initial FDs: {initial_fds}")
        print(f"  Final FDs: {final_fds}")
        print(f"  Growth: {growth}")

        # Should not leak file descriptors
        assert growth < 10, f"File descriptor leak: +{growth} FDs"


# ============================================================================
# Run Tests
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s", "--tb=short", "-m", "performance"])
