"""
ORFEAS Performance Monitoring and Metrics Collection
Integrates Prometheus metrics for production observability
"""
import os
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from functools import wraps
import time
import psutil
import logging
from typing import Any, Tuple

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

logger = logging.getLogger(__name__)

# ============================================================================
# Prometheus Metrics Definitions
# ============================================================================

# Request metrics
REQUEST_COUNT = Counter(
    'orfeas_requests_total',
    'Total number of HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_DURATION = Histogram(
    'orfeas_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint'],
    buckets=(0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0, 120.0, float('inf'))
)

REQUEST_IN_PROGRESS = Gauge(
    'orfeas_requests_in_progress',
    'Number of requests currently being processed',
    ['endpoint']
)

# Generation metrics
GENERATION_COUNT = Counter(
    'orfeas_generations_total',
    'Total number of AI generations',
    ['type', 'provider', 'status']
)

GENERATION_DURATION = Histogram(
    'orfeas_generation_duration_seconds',
    'Generation duration in seconds',
    ['type', 'provider'],
    buckets=(1.0, 5.0, 10.0, 30.0, 60.0, 120.0, 180.0, 300.0, float('inf'))
)

GENERATION_IN_PROGRESS = Gauge(
    'orfeas_generations_in_progress',
    'Number of generations currently in progress',
    ['type']
)

# System resource metrics
CPU_USAGE = Gauge(
    'orfeas_cpu_usage_percent',
    'CPU usage percentage'
)

MEMORY_USAGE = Gauge(
    'orfeas_memory_usage_bytes',
    'System memory usage in bytes'
)

MEMORY_PERCENT = Gauge(
    'orfeas_memory_usage_percent',
    'Memory usage percentage'
)

if TORCH_AVAILABLE:
    GPU_MEMORY_USAGE = Gauge(
        'orfeas_gpu_memory_bytes',
        'GPU memory usage in bytes',
        ['gpu_id']
    )

    GPU_MEMORY_ALLOCATED = Gauge(
        'orfeas_gpu_memory_allocated_bytes',
        'GPU memory allocated in bytes',
        ['gpu_id']
    )

# Job queue metrics
JOB_QUEUE_SIZE = Gauge(
    'orfeas_job_queue_size',
    'Number of jobs in queue'
)

JOB_PROCESSING_TIME = Histogram(
    'orfeas_job_processing_seconds',
    'Job processing time in seconds',
    ['job_type'],
    buckets=(1.0, 5.0, 10.0, 30.0, 60.0, 120.0, 180.0, 300.0, float('inf'))
)

# Error metrics
ERROR_COUNT = Counter(
    'orfeas_errors_total',
    'Total number of errors',
    ['error_type', 'endpoint']
)

# ============================================================================
# Decorator Functions
# ============================================================================

def track_request_metrics(endpoint_name: Any) -> None:
    """
    Decorator to track HTTP request metrics

    Usage:
        @track_request_metrics('/api/generate')
        def generate_endpoint():
            ...
    """
    def decorator(func: Any) -> None:
        @wraps(func)
        def wrapper(*args, **kwargs) -> None:
            # [TEST MODE FIX] Skip monitoring entirely in test mode to prevent hangs
            if os.getenv('TESTING', '0') == '1':
                return func(*args, **kwargs)

            start_time = time.time()
            method = 'POST'  # Can be detected from Flask request
            status = 500

            # Track in-progress requests
            REQUEST_IN_PROGRESS.labels(endpoint=endpoint_name).inc()

            try:
                response = func(*args, **kwargs)

                # Get status code from response
                if hasattr(response, 'status_code'):
                    status = response.status_code
                elif isinstance(response, tuple) and len(response) > 1:
                    status = response[1]
                else:
                    status = 200

                return response

            except Exception as e:
                logger.error(f"Error in {endpoint_name}: {e}")
                ERROR_COUNT.labels(
                    error_type=type(e).__name__,
                    endpoint=endpoint_name
                ).inc()
                raise

            finally:
                duration = time.time() - start_time

                # Record metrics
                REQUEST_COUNT.labels(
                    method=method,
                    endpoint=endpoint_name,
                    status=status
                ).inc()

                REQUEST_DURATION.labels(
                    method=method,
                    endpoint=endpoint_name
                ).observe(duration)

                REQUEST_IN_PROGRESS.labels(endpoint=endpoint_name).dec()

        return wrapper
    return decorator


def track_generation_metrics(gen_type: Any, provider: Any) -> None:
    """
    Decorator to track AI generation metrics

    Usage:
        @track_generation_metrics('text-to-image', 'openai')
        async def generate_image(prompt):
            ...
    """
    def decorator(func: Any) -> None:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            status = 'failed'

            GENERATION_IN_PROGRESS.labels(type=gen_type).inc()

            try:
                result = await func(*args, **kwargs)
                status = 'success'
                return result

            except Exception as e:
                logger.error(f"Generation failed ({gen_type}/{provider}): {e}")
                ERROR_COUNT.labels(
                    error_type=type(e).__name__,
                    endpoint=f"generation_{gen_type}"
                ).inc()
                raise

            finally:
                duration = time.time() - start_time

                GENERATION_COUNT.labels(
                    type=gen_type,
                    provider=provider,
                    status=status
                ).inc()

                GENERATION_DURATION.labels(
                    type=gen_type,
                    provider=provider
                ).observe(duration)

                GENERATION_IN_PROGRESS.labels(type=gen_type).dec()

        # Also support sync functions
        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> None:
            start_time = time.time()
            status = 'failed'

            GENERATION_IN_PROGRESS.labels(type=gen_type).inc()

            try:
                result = func(*args, **kwargs)
                status = 'success'
                return result

            finally:
                duration = time.time() - start_time

                GENERATION_COUNT.labels(
                    type=gen_type,
                    provider=provider,
                    status=status
                ).inc()

                GENERATION_DURATION.labels(
                    type=gen_type,
                    provider=provider
                ).observe(duration)

                GENERATION_IN_PROGRESS.labels(type=gen_type).dec()

        # Return appropriate wrapper
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


# ============================================================================
# System Metrics Collection
# ============================================================================

def update_system_metrics() -> None:
    """Update system resource metrics"""
    try:
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=0.1)
        CPU_USAGE.set(cpu_percent)

        # Memory usage
        memory = psutil.virtual_memory()
        MEMORY_USAGE.set(memory.used)
        MEMORY_PERCENT.set(memory.percent)

        # GPU metrics (if available)
        if TORCH_AVAILABLE and torch.cuda.is_available():
            for i in range(torch.cuda.device_count()):
                allocated = torch.cuda.memory_allocated(i)
                reserved = torch.cuda.memory_reserved(i)

                GPU_MEMORY_ALLOCATED.labels(gpu_id=i).set(allocated)
                GPU_MEMORY_USAGE.labels(gpu_id=i).set(reserved)

    except Exception as e:
        logger.error(f"Error updating system metrics: {e}")


# ============================================================================
# Flask Integration
# ============================================================================

def setup_monitoring(app: Any) -> Tuple:
    """
    Set up monitoring endpoints in Flask application

    Usage:
        from monitoring import setup_monitoring

        app = Flask(__name__)
        setup_monitoring(app)
    """

    @app.route('/metrics')
    def metrics() -> Tuple:
        """Prometheus metrics endpoint"""
        update_system_metrics()
        return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

    @app.route('/health-detailed')
    def health_detailed() -> Tuple:
        """Detailed health check with system metrics"""
        update_system_metrics()

        health_data = {
            "status": "healthy",
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent
        }

        if TORCH_AVAILABLE and torch.cuda.is_available():
            health_data["gpu_available"] = True
            health_data["gpu_count"] = torch.cuda.device_count()
            health_data["gpu_memory"] = [
                {
                    "gpu_id": i,
                    "allocated_mb": torch.cuda.memory_allocated(i) / 1024 / 1024,
                    "reserved_mb": torch.cuda.memory_reserved(i) / 1024 / 1024
                }
                for i in range(torch.cuda.device_count())
            ]
        else:
            health_data["gpu_available"] = False

        return health_data, 200

    logger.info("[OK] Monitoring endpoints configured: /metrics, /health-detailed")


# ============================================================================
# Job Queue Tracking
# ============================================================================

class JobQueueTracker:
    """Track job queue metrics"""

    @staticmethod
    def set_queue_size(size: Any) -> None:
        """Update job queue size"""
        JOB_QUEUE_SIZE.set(size)

    @staticmethod
    def track_job_processing(job_type: Any) -> None:
        """Context manager to track job processing time"""
        class JobTimer:
            def __enter__(self) -> None:
                self.start_time = time.time()
                return self

            def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
                duration = time.time() - self.start_time
                JOB_PROCESSING_TIME.labels(job_type=job_type).observe(duration)

        return JobTimer()


# ============================================================================
# Export Public API
# ============================================================================

__all__ = [
    'setup_monitoring',
    'track_request_metrics',
    'track_generation_metrics',
    'update_system_metrics',
    'JobQueueTracker'
]
