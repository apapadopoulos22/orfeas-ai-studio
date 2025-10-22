"""
ORFEAS Test Suite - Shared pytest fixtures and configuration
Consolidates common test patterns from multiple legacy test files
"""
import pytest
import requests
from pathlib import Path
from PIL import Image
import io
import time
import sys
import os
from typing import Any, Dict, List

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# ============================================================================
# Cache Management Fixtures
# ============================================================================

@pytest.fixture(autouse=True)
def reset_cache_singleton():
    """Reset cache singleton before each test to ensure clean state."""
    # Import here to avoid import errors if cache_manager doesn't exist
    try:
        from cache_manager import clear_cache, _cache_instance
        import cache_manager

        # Clear any existing cache instance
        clear_cache()
        cache_manager._cache_instance = None

        yield

        # Cleanup after test
        clear_cache()
        cache_manager._cache_instance = None
    except ImportError:
        # Cache manager not available in this environment
        yield

# ============================================================================
# Configuration Fixtures
# ============================================================================

@pytest.fixture(scope="session")
def server_url() -> str:
    """Base URL for ORFEAS API server"""
    return "http://127.0.0.1:5000"

@pytest.fixture(scope="session")
def test_data_dir() -> None:
    """Directory for test data files"""
    test_dir = Path(__file__).parent / "test_data"
    test_dir.mkdir(exist_ok=True)
    return test_dir

@pytest.fixture(scope="session")
def timeout_config() -> Dict:
    """
    Timeout configuration for different operations

    [ORFEAS] MILESTONE 2: Enhanced timeouts for GPU-intensive operations
    - Health checks: 5s (fast, non-GPU)
    - Uploads: 60s (file I/O)
    - Text-to-image: 120s (GPU generation)
    - 3D generation: 300s (5 minutes - Hunyuan3D-2.1 can take 30-60s)
    - Downloads: 60s (file I/O)
    """
    return {
        "health_check": 5,
        "upload": 60,          # Increased from 30s
        "text_to_image": 120,
        "generate_3d": 300,    # Increased from 180s to 300s (5 minutes)
        "download": 60,        # New: explicit download timeout
        "default": 30
    }

# ============================================================================
# Server Health Fixtures
# ============================================================================

@pytest.fixture(scope="session")
def ensure_server_running(server_url: Any, request: Any) -> int:
    """Ensure server is running before tests start

    NOTE: This fixture is now OPTIONAL. Integration and E2E tests use
    integration_server and e2e_server fixtures which auto-start servers.
    This fixture only checks if a server is already running (for manual testing).
    """
    # Check if we're running integration/e2e tests with auto-server
    if hasattr(request, 'node') and hasattr(request.node, 'get_closest_marker'):
        if request.node.get_closest_marker('integration') or request.node.get_closest_marker('e2e'):
            # Skip check - integration_server/e2e_server will handle it
            return True

    max_retries = 5  # Reduced from 30 since we now auto-start
    retry_delay = 1

    print(f"\n Checking if server is running at {server_url}...")

    for attempt in range(max_retries):
        try:
            response = requests.get(
                f"{server_url}/health",
                timeout=5
            )
            if response.status_code == 200:
                print(f" Server is online at {server_url}")
                return True
        except requests.exceptions.ConnectionError:
            if attempt < max_retries - 1:
                print(f" Attempt {attempt + 1}/{max_retries} - waiting...")
                time.sleep(retry_delay)
            else:
                print(f" Server not running at {server_url}")
                print(f"   For integration tests, use integration_server fixture (auto-starts)")
                print(f"   For E2E tests, use e2e_server fixture (auto-starts)")
                pytest.skip(f"Server not running at {server_url} - use integration_server or e2e_server fixture")
        except Exception as e:
            pytest.fail(f" Unexpected error checking server: {e}")

    return False

# ============================================================================
# Image Generation Fixtures
# ============================================================================

@pytest.fixture
def test_image_512() -> None:
    """Generate a 512x512 test image (PNG bytes)"""
    img = Image.new('RGB', (512, 512), color=(255, 0, 0))  # Red

    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)

    return img_bytes

@pytest.fixture
def test_image_1024() -> None:
    """Generate a 1024x1024 test image (PNG bytes)"""
    img = Image.new('RGB', (1024, 1024), color=(0, 0, 255))  # Blue

    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)

    return img_bytes

@pytest.fixture
def test_image_file(tmp_path: str) -> None:
    """Generate a test image file on disk"""
    img = Image.new('RGB', (512, 512), color=(0, 255, 0))  # Green
    img_path = tmp_path / "test_image.png"
    img.save(img_path)

    return img_path

@pytest.fixture
def test_image_grayscale() -> None:
    """Generate a grayscale test image"""
    img = Image.new('L', (512, 512), color=128)

    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)

    return img_bytes

@pytest.fixture
def simple_stl_file() -> None:
    """Generate a simple STL file (binary format) for testing"""
    # Binary STL format: 80-byte header + 4-byte triangle count + triangles
    # Each triangle: 12 floats (normal + 3 vertices) + 2-byte attribute = 50 bytes

    import struct

    # Create a simple cube with 12 triangles (2 per face)
    stl_data = io.BytesIO()

    # 80-byte header
    header = b"ORFEAS Test STL File" + b"\x00" * 60
    stl_data.write(header)

    # Triangle count (12 triangles for a simple cube)
    stl_data.write(struct.pack('<I', 12))

    # Define 12 triangles (simplified cube)
    triangles = [
        # Front face (2 triangles)
        ((0.0, 0.0, 1.0), (0.0, 0.0, 10.0), (10.0, 0.0, 10.0), (10.0, 10.0, 10.0)),
        ((0.0, 0.0, 1.0), (0.0, 0.0, 10.0), (10.0, 10.0, 10.0), (0.0, 10.0, 10.0)),
        # Back face (2 triangles)
        ((0.0, 0.0, -1.0), (10.0, 0.0, 0.0), (0.0, 0.0, 0.0), (0.0, 10.0, 0.0)),
        ((0.0, 0.0, -1.0), (10.0, 0.0, 0.0), (0.0, 10.0, 0.0), (10.0, 10.0, 0.0)),
        # Top face (2 triangles)
        ((0.0, 1.0, 0.0), (0.0, 10.0, 10.0), (10.0, 10.0, 10.0), (10.0, 10.0, 0.0)),
        ((0.0, 1.0, 0.0), (0.0, 10.0, 10.0), (10.0, 10.0, 0.0), (0.0, 10.0, 0.0)),
        # Bottom face (2 triangles)
        ((0.0, -1.0, 0.0), (0.0, 0.0, 0.0), (10.0, 0.0, 0.0), (10.0, 0.0, 10.0)),
        ((0.0, -1.0, 0.0), (0.0, 0.0, 0.0), (10.0, 0.0, 10.0), (0.0, 0.0, 10.0)),
        # Right face (2 triangles)
        ((1.0, 0.0, 0.0), (10.0, 0.0, 10.0), (10.0, 0.0, 0.0), (10.0, 10.0, 0.0)),
        ((1.0, 0.0, 0.0), (10.0, 0.0, 10.0), (10.0, 10.0, 0.0), (10.0, 10.0, 10.0)),
        # Left face (2 triangles)
        ((-1.0, 0.0, 0.0), (0.0, 0.0, 0.0), (0.0, 0.0, 10.0), (0.0, 10.0, 10.0)),
        ((-1.0, 0.0, 0.0), (0.0, 0.0, 0.0), (0.0, 10.0, 10.0), (0.0, 10.0, 0.0)),
    ]

    # Write triangles
    for normal, v1, v2, v3 in triangles:
        # Normal vector
        stl_data.write(struct.pack('<fff', *normal))
        # Vertex 1
        stl_data.write(struct.pack('<fff', *v1))
        # Vertex 2
        stl_data.write(struct.pack('<fff', *v2))
        # Vertex 3
        stl_data.write(struct.pack('<fff', *v3))
        # Attribute byte count (always 0)
        stl_data.write(struct.pack('<H', 0))

    stl_data.seek(0)
    return stl_data


# ============================================================================
# API Client Helper
# ============================================================================

@pytest.fixture
def api_client(server_url: Any, timeout_config: Any) -> None:
    """Create an API client with common methods and error handling"""

    class APIClient:
        def __init__(self, base_url: Any, timeouts: List) -> None:
            self.base_url = base_url
            self.session = requests.Session()
            self.timeouts = timeouts

        def get(self, endpoint: Any, timeout: float = None, **kwargs) -> None:
            """GET request with automatic timeout"""
            timeout = timeout or self.timeouts.get("default", 30)
            url = f"{self.base_url}{endpoint}"

            try:
                response = self.session.get(url, timeout=timeout, **kwargs)
                return response
            except requests.exceptions.Timeout:
                pytest.fail(f"Request timeout after {timeout}s: GET {endpoint}")
            except requests.exceptions.ConnectionError as e:
                pytest.fail(f"Connection error: GET {endpoint} - {e}")

        def post(self, endpoint: Any, timeout: float = None, **kwargs) -> None:
            """POST request with automatic timeout"""
            timeout = timeout or self.timeouts.get("default", 30)
            url = f"{self.base_url}{endpoint}"

            try:
                response = self.session.post(url, timeout=timeout, **kwargs)
                return response
            except requests.exceptions.Timeout:
                pytest.fail(f"Request timeout after {timeout}s: POST {endpoint}")
            except requests.exceptions.ConnectionError as e:
                pytest.fail(f"Connection error: POST {endpoint} - {e}")

        def health_check(self) -> None:
            """Perform health check"""
            return self.get("/api/health", timeout=self.timeouts["health_check"])

        def upload_image(self, image_bytes: List, filename: Any = "test.png") -> None:
            """Upload image file"""
            files = {'image': (filename, image_bytes, 'image/png')}  # [FIX] Changed 'file' to 'image'
            return self.post(
                "/api/upload-image",  # [FIX] Add /api/ prefix
                files=files,
                timeout=self.timeouts["upload"]
            )

        def text_to_image(self, prompt: Any, art_style: Any = "realistic") -> None:
            """Generate image from text"""
            payload = {
                "prompt": prompt,
                "art_style": art_style
            }
            return self.post(
                "/api/text-to-image",  # [FIX] Add /api/ prefix
                json=payload,
                timeout=self.timeouts["text_to_image"]
            )

        def generate_3d(self, job_id: str, format: Any = "stl", quality: Any = 7) -> None:
            """Generate 3D model"""
            payload = {
                "job_id": job_id,
                "format": format,
                "quality": quality
            }
            return self.post(
                "/api/generate-3d",  # [FIX] Add /api/ prefix
                json=payload,
                timeout=self.timeouts["generate_3d"]
            )

        def get_job_status(self, job_id: str) -> None:
            """Get job status"""
            return self.get(f"/api/job-status/{job_id}")  # [FIX] Correct endpoint path

        def download_file(self, job_id: str, format: Any = "stl") -> None:
            """
            Download generated file

            [ORFEAS] MILESTONE 2: Added explicit timeout for downloads
            """
            return self.get(
                f"/api/download/{job_id}/model.{format}",
                timeout=self.timeouts.get("download", 60)
            )

    return APIClient(server_url, timeout_config)

# ============================================================================
# Job Management Fixtures
# ============================================================================

@pytest.fixture
def uploaded_job_id(api_client: Any, integration_server: Any, test_image_512: Any) -> None:
    """Upload image and return job_id for downstream tests

    Requires integration_server to ensure server is running before upload attempt.
    """
    response = api_client.upload_image(test_image_512)

    assert response.status_code == 200, f"Upload failed: {response.text}"

    data = response.json()
    assert "job_id" in data, "Response missing job_id"

    return data["job_id"]

# ============================================================================
# Cleanup Fixtures
# ============================================================================

@pytest.fixture(autouse=True)
def cleanup_test_files(test_data_dir: Any) -> None:
    """Clean up test files after each test"""
    yield

    # Optional: Clean up generated test files
    # for file in test_data_dir.glob("test_*"):
    #     file.unlink(missing_ok=True)

# ============================================================================
# GPU Testing Fixtures
# ============================================================================

@pytest.fixture(scope="session")
def gpu_available() -> int:
    """Check if GPU is available for testing"""
    try:
        import torch
        has_cuda = torch.cuda.is_available()

        if has_cuda:
            print(f"\n GPU Available: {torch.cuda.get_device_name(0)}")
            print(f"   CUDA Version: {torch.version.cuda}")
            print(f"   Total Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")
        else:
            print("\n No GPU detected - GPU tests will be skipped")

        return has_cuda
    except ImportError:
        print("\n PyTorch not available - GPU tests will be skipped")
        return False

@pytest.fixture
def performance_tracker() -> None:
    """Track performance metrics during tests"""
    import time

    class PerformanceTracker:
        def __init__(self) -> None:
            self.metrics = {}
            self.start_times = {}
            self.start_time = None

        def start(self, metric_name: Any = "default") -> None:
            """Start timing a metric"""
            self.start_time = time.time()
            self.start_times[metric_name] = time.time()

        def stop(self, metric_name: Any = "default") -> None:
            """Stop timing a metric and record duration"""
            if metric_name in self.start_times:
                duration = time.time() - self.start_times[metric_name]
                self.metrics[metric_name] = duration
                del self.start_times[metric_name]
                return duration
            elif self.start_time is not None:
                duration = time.time() - self.start_time
                self.start_time = None
                return duration
            return None

        def get_metric(self, metric_name: Any) -> None:
            """Get a recorded metric"""
            return self.metrics.get(metric_name)

        def get_all_metrics(self) -> None:
            """Get all recorded metrics"""
            return self.metrics.copy()

    return PerformanceTracker()

@pytest.fixture
def gpu_manager(gpu_available: Any) -> None:
    """Create GPU memory manager instance for testing"""
    if not gpu_available:
        pytest.skip("GPU not available - skipping GPU tests")

    from gpu_manager import GPUMemoryManager
    manager = GPUMemoryManager(memory_limit_gb=8)
    yield manager
    # Cleanup after test
    manager.cleanup()

@pytest.fixture
def gpu_memory_tracker(gpu_available: Any) -> Dict:
    """Track GPU memory usage during tests"""
    if not gpu_available:
        pytest.skip("GPU not available - skipping GPU tests")

    import torch

    class GPUMemoryTracker:
        def __init__(self) -> None:
            self.start_allocated = 0
            self.end_allocated = 0
            self.peak_allocated = 0

        def start(self) -> None:
            """Start tracking GPU memory"""
            torch.cuda.empty_cache()
            torch.cuda.reset_peak_memory_stats()
            self.start_allocated = torch.cuda.memory_allocated()

        def stop(self) -> None:
            """Stop tracking and record stats"""
            self.end_allocated = torch.cuda.memory_allocated()
            self.peak_allocated = torch.cuda.max_memory_allocated()

        def get_stats(self) -> Dict:
            """Get memory statistics"""
            return {
                "start_allocated_mb": self.start_allocated / 1024**2,
                "end_allocated_mb": self.end_allocated / 1024**2,
                "peak_allocated_mb": self.peak_allocated / 1024**2,
                "delta_mb": (self.end_allocated - self.start_allocated) / 1024**2,
                # Also include the underscore-less versions for backward compatibility
                "start_mb": self.start_allocated / 1024**2,
                "end_mb": self.end_allocated / 1024**2,
                "peak_mb": self.peak_allocated / 1024**2,
            }

    return GPUMemoryTracker()

@pytest.fixture
def test_image_path(test_image_file: Any) -> None:
    """Alias fixture for test_image_file (for batch_processor tests)"""
    return test_image_file

@pytest.fixture(scope="session")
def hunyuan_processor(gpu_available: Any) -> None:
    """Create Hunyuan3D processor instance for integration tests

    Requires:
    - GPU with CUDA support
    - Hunyuan3D-2.1 models downloaded and available
    - ~18-20GB VRAM for model loading

    Will skip tests if:
    - GPU not available
    - Models not found
    - Insufficient VRAM
    """
    if not gpu_available:
        pytest.skip("GPU not available - skipping Hunyuan3D integration tests")

    try:
        # Import Hunyuan3D integration
        from hunyuan_integration import get_3d_processor

        # Attempt to load processor
        print("\nðŸ”„ Loading Hunyuan3D-2.1 processor...")
        processor = get_3d_processor()

        if processor is None:
            pytest.skip("Hunyuan3D processor initialization failed - models may not be available")

        print(" Hunyuan3D processor loaded successfully")
        yield processor

        # Cleanup
        print("\n[CLEANUP] Hunyuan3D processor cleanup...")
        if hasattr(processor, 'cleanup'):
            processor.cleanup()

    except ImportError as e:
        pytest.skip(f"Hunyuan3D integration not available: {e}")
    except Exception as e:
        pytest.skip(f"Failed to load Hunyuan3D processor: {e}")

@pytest.fixture
def temp_output_dir(tmp_path: str) -> None:
    """Create temporary output directory for 3D model generation"""
    output_dir = tmp_path / "3d_outputs"
    output_dir.mkdir(exist_ok=True)
    return output_dir

# ============================================================================
# Integration Testing Fixtures
# ============================================================================

@pytest.fixture(scope="function")  # [ORFEAS FIX] Changed from "session" to "function" to prevent server state issues
def integration_server() -> None:
    """Start backend server on port 5000 for integration tests (API endpoints)"""
    import subprocess
    import time
    import socket

    # [ORFEAS FIX] Check if port is already in use and kill zombie processes
    def is_port_in_use(port: Any) -> None:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('127.0.0.1', port)) == 0

    def kill_process_on_port(port: Any) -> None:
        """Kill any process using the specified port"""
        try:
            if os.name == 'nt':  # Windows
                # Find and kill process on port
                result = subprocess.run(
                    f'netstat -ano | findstr :{port}',
                    shell=True,
                    capture_output=True,
                    text=True
                )
                for line in result.stdout.split('\n'):
                    if f':{port}' in line and 'LISTENING' in line:
                        parts = line.split()
                        if parts:
                            pid = parts[-1]
                            subprocess.run(f'taskkill /F /PID {pid}', shell=True, capture_output=True)
                            print(f" Killed zombie process on port {port} (PID: {pid})")
                            time.sleep(1)  # Wait for port to be released
        except Exception as e:
            print(f" Warning: Could not kill process on port {port}: {e}")

    # Clean up any zombie processes
    if is_port_in_use(5000):
        print("\n Port 5000 is in use, cleaning up...")
        kill_process_on_port(5000)
        time.sleep(2)  # Wait for port to be fully released

    print("\n Starting integration test server on port 5000...")

    # Start backend server on port 5000 (default)
    # [TIMING DEBUG] Allow server output to console for debugging
    server_process = subprocess.Popen(
        [
            sys.executable,
            str(Path(__file__).parent.parent / "main.py")
        ],
        env={
            **dict(os.environ),
            "ORFEAS_PORT": "5000",
            "FLASK_ENV": "testing",
            "LOG_LEVEL": "INFO",  # Changed from ERROR to INFO to see timing logs
            "SKIP_GPU_INIT": "1",  # Skip GPU initialization
            "SKIP_MODEL_LOAD": "1",  # Skip heavy model loading
            "TESTING": "1",  # Enable test mode
            "XFORMERS_DISABLED": "1"  # Prevent DLL issues
        },
        stdout=None,  # Changed from subprocess.PIPE to None (inherit console)
        stderr=None,  # Changed from subprocess.PIPE to None (inherit console)
        text=True,
        bufsize=1  # Line buffered for real-time output
    )

    # Wait for server to start (check health endpoint)
    max_attempts = 60  # Increased from 30 to 60 (60 seconds total)
    server_ready = False

    for attempt in range(max_attempts):
        try:
            response = requests.get("http://127.0.0.1:5000/api/health", timeout=2)
            if response.status_code == 200:
                server_ready = True
                print(f" Integration server ready on port 5000 (attempt {attempt + 1})")
                break
        except (requests.ConnectionError, requests.Timeout):
            if attempt < max_attempts - 1:
                # Print progress every 5 attempts
                if (attempt + 1) % 5 == 0:
                    print(f" Waiting for server... ({attempt + 1}/{max_attempts})")
                time.sleep(1)
            continue
        except Exception as e:
            print(f" Unexpected error during health check: {e}")
            time.sleep(1)
            continue

    if not server_ready:
        # Get server output for debugging
        print("\n[INTEGRATION] Server failed to start. Capturing output...")
        try:
            # Try to get output without blocking
            import select
            if hasattr(select, 'select'):  # Unix-like systems
                stdout, stderr = server_process.communicate(timeout=2)
            else:  # Windows
                # Non-blocking read on Windows
                stdout_lines = []
                stderr_lines = []
                try:
                    import msvcrt
                    import time as t

                    # Try to read with timeout
                    start = t.time()
                    while t.time() - start < 2:
                        if server_process.stdout:
                            line = server_process.stdout.readline()
                            if line:
                                stdout_lines.append(line)
                        if server_process.stderr:
                            line = server_process.stderr.readline()
                            if line:
                                stderr_lines.append(line)

                    stdout = ''.join(stdout_lines)
                    stderr = ''.join(stderr_lines)
                except:
                    stdout, stderr = server_process.communicate(timeout=1)

            if stdout:
                print(f"\n[INTEGRATION] Server stdout:\n{stdout[:1000]}")  # First 1000 chars
            if stderr:
                print(f"\n[INTEGRATION] Server stderr:\n{stderr[:1000]}")  # First 1000 chars
        except subprocess.TimeoutExpired:
            print("[INTEGRATION] Could not capture server output (timeout)")
        except Exception as e:
            print(f"[INTEGRATION] Error capturing output: {e}")

        server_process.kill()
        pytest.fail("[INTEGRATION] Integration test server failed to start on port 5000 after 60 seconds")

    yield "http://127.0.0.1:5000"

    # Cleanup: Stop server
    print("\n Stopping integration test server...")
    server_process.terminate()
    try:
        server_process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        server_process.kill()
    print(" Integration server stopped")

# ============================================================================
# E2E Testing Fixtures
# ============================================================================

@pytest.fixture(scope="function")  # [ORFEAS FIX] Each test gets fresh server
def e2e_server() -> None:
    """Start backend server on port 8000 for E2E tests (Playwright)"""
    import subprocess
    import time
    import sys

    print("\n[E2E] Starting test server on port 8000...")

    main_py_path = Path(__file__).parent.parent / "main.py"
    print(f"[E2E] Using main.py at: {main_py_path}")
    print(f"[E2E] Python executable: {sys.executable}")

    # Start backend server on port 8000
    server_process = subprocess.Popen(
        [
            sys.executable,
            str(main_py_path)
        ],
        env={
            **dict(os.environ),
            "ORFEAS_PORT": "8000",
            "FLASK_ENV": "testing",
            "TESTING": "1",  # [ORFEAS FIX] Enable test mode to skip AI/GPU
            "LOG_LEVEL": "WARNING"
        },
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    # Wait for server to start (check health endpoint)
    max_attempts = 30
    server_ready = False

    for attempt in range(max_attempts):
        try:
            print(f"[E2E] Attempt {attempt + 1}/{max_attempts}: Checking http://localhost:8000/api/health")
            response = requests.get("http://localhost:8000/api/health", timeout=2)
            if response.status_code == 200:
                server_ready = True
                print(f"[E2E] Server ready on port 8000")
                break
        except (requests.ConnectionError, requests.Timeout) as e:
            print(f"[E2E] Connection attempt {attempt + 1} failed: {e}")
            if attempt < max_attempts - 1:
                time.sleep(1)
            continue

    if not server_ready:
        # Get server output for debugging
        try:
            stdout, stderr = server_process.communicate(timeout=1)
            print(f"[E2E] Server stdout: {stdout.decode('utf-8', errors='ignore')}")
            print(f"[E2E] Server stderr: {stderr.decode('utf-8', errors='ignore')}")
        except:
            print("[E2E] Could not get server output")
        server_process.kill()
        pytest.fail("[E2E] E2E test server failed to start on port 8000")

    yield "http://localhost:8000"

    # Cleanup: Stop server
    print("\n[E2E] Stopping test server...")
    server_process.terminate()
    try:
        server_process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        server_process.kill()
    print("[E2E] Server stopped")

# ============================================================================
# Markers for Test Organization
# ============================================================================

def pytest_configure(config: Dict) -> None:
    """Register custom markers"""
    config.addinivalue_line(
        "markers", "unit: Unit tests (fast, isolated)"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests (API tests)"
    )
    config.addinivalue_line(
        "markers", "security: Security tests"
    )
    config.addinivalue_line(
        "markers", "performance: Performance tests"
    )
    config.addinivalue_line(
        "markers", "slow: Slow tests (skip with -m 'not slow')"
    )
    config.addinivalue_line(
        "markers", "gpu: GPU tests (require CUDA)"
    )
    config.addinivalue_line(
        "markers", "stress: Stress tests (heavy load)"
    )
    config.addinivalue_line(
        "markers", "e2e: End-to-end tests (require browser)"
    )

# ============================================================================
# Test Reporting Hooks
# ============================================================================

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item: Any, call: Any) -> None:
    """Make test result available to fixtures"""
    outcome = yield
    rep = outcome.get_result()

    setattr(item, f"rep_{rep.when}", rep)
