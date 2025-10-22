"""
ORFEAS AI 2Dâ†’3D Studio - Prometheus Metrics Exporter
=====================================================

Production-grade monitoring with Prometheus metrics export for:
- Request tracking and latency
- Error rates and types
- Resource usage (CPU, memory, GPU)
- Business metrics (generations, uploads)
- System health and availability

Author: ORFEAS Protocol - Monitoring Master
Date: October 14, 2025
"""

from prometheus_client import (
    Counter, Histogram, Gauge, Info, Summary,
    generate_latest, REGISTRY, CONTENT_TYPE_LATEST
)
from flask import Response
import psutil
import time
import functools
import os
from typing import Callable, Any
import logging

logger = logging.getLogger(__name__)

# ============================================================================
# Request Metrics
# ============================================================================

# Total HTTP requests
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

# Request duration
http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint'],
    buckets=(0.01, 0.05, 0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0)
)

# Request size
http_request_size_bytes = Summary(
    'http_request_size_bytes',
    'HTTP request size in bytes',
    ['method', 'endpoint']
)

# Response size
http_response_size_bytes = Summary(
    'http_response_size_bytes',
    'HTTP response size in bytes',
    ['method', 'endpoint']
)

# ============================================================================
# Error Metrics
# ============================================================================

# Total errors
errors_total = Counter(
    'errors_total',
    'Total errors',
    ['type', 'endpoint']
)

# Validation errors
validation_errors_total = Counter(
    'validation_errors_total',
    'Total validation errors',
    ['field', 'error_type']
)

# Rate limit rejections
rate_limit_rejections_total = Counter(
    'rate_limit_rejections_total',
    'Total rate limit rejections',
    ['endpoint']
)

# ============================================================================
# AI Generation Metrics
# ============================================================================

# Text-to-Image generations
text_to_image_generations_total = Counter(
    'text_to_image_generations_total',
    'Total text-to-image generations',
    ['art_style', 'status']
)

# Text-to-Image duration
text_to_image_duration_seconds = Histogram(
    'text_to_image_duration_seconds',
    'Text-to-image generation duration in seconds',
    ['art_style'],
    buckets=(5.0, 10.0, 20.0, 30.0, 60.0, 120.0, 300.0)
)

# 3D Model generations
model_3d_generations_total = Counter(
    'model_3d_generations_total',
    'Total 3D model generations',
    ['format', 'quality', 'status']
)

# 3D Model generation duration
model_3d_duration_seconds = Histogram(
    'model_3d_duration_seconds',
    '3D model generation duration in seconds',
    ['format', 'quality'],
    buckets=(10.0, 30.0, 60.0, 120.0, 300.0, 600.0, 1200.0)
)

# Image uploads
image_uploads_total = Counter(
    'image_uploads_total',
    'Total image uploads',
    ['format', 'status']
)

# ============================================================================
# System Resource Metrics
# ============================================================================

# CPU usage
cpu_usage_percent = Gauge(
    'cpu_usage_percent',
    'CPU usage percentage',
    ['core']
)

# Memory usage
memory_usage_bytes = Gauge(
    'memory_usage_bytes',
    'Memory usage in bytes',
    ['type']  # total, available, used, cached
)

# Disk usage
disk_usage_bytes = Gauge(
    'disk_usage_bytes',
    'Disk usage in bytes',
    ['path', 'type']  # total, used, free
)

# GPU usage (if available)
gpu_usage_percent = Gauge(
    'gpu_usage_percent',
    'GPU usage percentage',
    ['gpu_id']
)

# GPU memory
gpu_memory_bytes = Gauge(
    'gpu_memory_bytes',
    'GPU memory in bytes',
    ['gpu_id', 'type']  # total, used, free
)

# ============================================================================
# Application Metrics
# ============================================================================

# Active jobs
active_jobs = Gauge(
    'active_jobs',
    'Number of active jobs',
    ['type']  # upload, text_to_image, generate_3d
)

# Job queue size
job_queue_size = Gauge(
    'job_queue_size',
    'Number of jobs in queue',
    ['type']
)

# Concurrent requests
concurrent_requests = Gauge(
    'concurrent_requests',
    'Number of concurrent requests being processed',
    ['endpoint']
)

# Uptime
app_uptime_seconds = Gauge(
    'app_uptime_seconds',
    'Application uptime in seconds'
)

# Application info
app_info = Info(
    'app_info',
    'Application information'
)

# ============================================================================
# Business Metrics
# ============================================================================

# Total successful generations
successful_generations_total = Counter(
    'successful_generations_total',
    'Total successful generations',
    ['type']  # text_to_image, model_3d
)

# Failed generations
failed_generations_total = Counter(
    'failed_generations_total',
    'Total failed generations',
    ['type', 'reason']
)

# Average generation quality
generation_quality_score = Histogram(
    'generation_quality_score',
    'Generation quality score (1-10)',
    ['type'],
    buckets=(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
)

# File sizes
generated_file_size_bytes = Histogram(
    'generated_file_size_bytes',
    'Generated file size in bytes',
    ['type'],
    buckets=(1024, 10240, 102400, 1048576, 10485760, 104857600)  # 1KB to 100MB
)

# ============================================================================
# Quality Validation Metrics (Priority #1 Feature)
# ============================================================================

# Background removal quality
quality_bg_removal_score = Gauge(
    'quality_bg_removal_score',
    'Background removal quality score (0.0-1.0)'
)

# Shape generation quality
quality_shape_score = Gauge(
    'quality_shape_score',
    'Shape generation quality score (0.0-1.0)'
)

# Texture coherence quality
quality_texture_score = Gauge(
    'quality_texture_score',
    'Texture coherence quality score (0.0-1.0)'
)

# Final mesh quality
quality_final_score = Gauge(
    'quality_final_score',
    'Final mesh quality score (0.0-1.0)'
)

# Overall quality score
quality_overall_score = Gauge(
    'quality_overall_score',
    'Overall generation quality score (0.0-1.0)'
)

# Quality distribution histogram
quality_score_distribution = Histogram(
    'quality_score_distribution',
    'Distribution of quality scores',
    ['stage'],  # bg_removal, shape, texture, final, overall
    buckets=(0.5, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0)
)

# Quality grade distribution
quality_grade_total = Counter(
    'quality_grade_total',
    'Total count by quality grade',
    ['grade']  # A+, A, A-, B+, B, B-, C+, C, D, F
)

# Auto-repair operations
quality_auto_repairs_total = Counter(
    'quality_auto_repairs_total',
    'Total automatic mesh repairs performed',
    ['repair_type']  # non_manifold, degenerate_faces, duplicate_faces
)

# Quality validation failures
quality_validation_failures_total = Counter(
    'quality_validation_failures_total',
    'Total quality validation failures',
    ['stage', 'issue_type']  # stage: bg_removal/shape/texture/final, issue_type: specific failure
)

# Quality threshold passes
quality_threshold_passes_total = Counter(
    'quality_threshold_passes_total',
    'Total generations passing quality threshold',
    ['threshold']  # 0.80, 0.85, 0.90, etc.
)

# Manifold mesh rate
quality_manifold_rate = Gauge(
    'quality_manifold_rate',
    'Percentage of manifold (watertight) meshes generated'
)

# Printable mesh rate
quality_printable_rate = Gauge(
    'quality_printable_rate',
    'Percentage of 3D-printable meshes generated'
)

# ============================================================================
# Performance Metrics
# ============================================================================

# Database query duration (if applicable)
db_query_duration_seconds = Histogram(
    'db_query_duration_seconds',
    'Database query duration in seconds',
    ['query_type'],
    buckets=(0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0, 5.0)
)

# ============================================================================
# WebSocket Metrics (Phase 2.4 Integration)
# ============================================================================

# Active WebSocket connections
websocket_connections_active = Gauge(
    'websocket_connections_active',
    'Number of active WebSocket connections',
    ['client_type']  # browser, api, internal
)

# WebSocket messages sent
websocket_messages_sent_total = Counter(
    'websocket_messages_sent_total',
    'Total WebSocket messages sent to clients',
    ['event_type']  # progress, error, complete, status, heartbeat
)

# WebSocket errors
websocket_errors_total = Counter(
    'websocket_errors_total',
    'Total WebSocket connection/transmission errors',
    ['error_type']  # connection_failed, send_failed, timeout, disconnect
)

# WebSocket connection duration
websocket_connection_duration_seconds = Histogram(
    'websocket_connection_duration_seconds',
    'WebSocket connection duration in seconds',
    buckets=(10.0, 30.0, 60.0, 300.0, 600.0, 1800.0, 3600.0)  # 10s to 1hr
)

# ============================================================================
# Pipeline Stage Metrics (Phase 2.4 Progress Tracking)
# ============================================================================

# Pipeline stage duration tracking
pipeline_stage_duration_seconds = Histogram(
    'pipeline_stage_duration_seconds',
    'Duration of individual 3D generation pipeline stages',
    ['stage'],  # background_removal, shape_generation, texture_generation, mesh_export
    buckets=(1.0, 5.0, 10.0, 20.0, 30.0, 60.0, 120.0, 180.0)  # 1s to 3min
)

# Pipeline stage errors
pipeline_stage_errors_total = Counter(
    'pipeline_stage_errors_total',
    'Errors occurring in specific pipeline stages',
    ['stage', 'error_type']  # stage: which stage failed, error_type: specific error
)

# Cache hit rate
cache_hits_total = Counter(
    'cache_hits_total',
    'Total cache hits',
    ['cache_type']
)

cache_misses_total = Counter(
    'cache_misses_total',
    'Total cache misses',
    ['cache_type']
)

# ============================================================================
# Monitoring Functions
# ============================================================================

# Application start time
_app_start_time = time.time()

def set_app_info(version: str, environment: str):
    """
    Set application information metrics.

    Args:
        version: Application version
        environment: Deployment environment (dev/staging/production)
    """
    app_info.info({
        'version': version,
        'environment': environment,
        'python_version': '3.11',
        'framework': 'Flask + SocketIO'
    })


def update_system_metrics():
    """
    Update system resource metrics.
    Should be called periodically (e.g., every 5 seconds).
    """
    try:
        # CPU metrics
        cpu_percent = psutil.cpu_percent(interval=0.1, percpu=True)
        for i, usage in enumerate(cpu_percent):
            cpu_usage_percent.labels(core=str(i)).set(usage)

        # Memory metrics
        memory = psutil.virtual_memory()
        memory_usage_bytes.labels(type='total').set(memory.total)
        memory_usage_bytes.labels(type='available').set(memory.available)
        memory_usage_bytes.labels(type='used').set(memory.used)
        memory_usage_bytes.labels(type='cached').set(getattr(memory, 'cached', 0))

        # Disk metrics
        disk = psutil.disk_usage('/')
        disk_usage_bytes.labels(path='/', type='total').set(disk.total)
        disk_usage_bytes.labels(path='/', type='used').set(disk.used)
        disk_usage_bytes.labels(path='/', type='free').set(disk.free)

        # Uptime
        uptime = time.time() - _app_start_time
        app_uptime_seconds.set(uptime)

    except Exception as e:
        logger.error(f"Error updating system metrics: {e}")


def update_gpu_metrics():
    """
    Update GPU metrics if NVIDIA GPU is available.
    Requires pynvml library.
    """
    try:
        import pynvml

        pynvml.nvmlInit()
        device_count = pynvml.nvmlDeviceGetCount()

        for i in range(device_count):
            handle = pynvml.nvmlDeviceGetHandleByIndex(i)

            # GPU utilization
            utilization = pynvml.nvmlDeviceGetUtilizationRates(handle)
            gpu_usage_percent.labels(gpu_id=str(i)).set(utilization.gpu)

            # GPU memory
            memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
            gpu_memory_bytes.labels(gpu_id=str(i), type='total').set(memory_info.total)
            gpu_memory_bytes.labels(gpu_id=str(i), type='used').set(memory_info.used)
            gpu_memory_bytes.labels(gpu_id=str(i), type='free').set(memory_info.free)

        pynvml.nvmlShutdown()

    except ImportError:
        logger.debug("pynvml not available, skipping GPU metrics")
    except Exception as e:
        logger.error(f"Error updating GPU metrics: {e}")


# ============================================================================
# Decorator for Automatic Metrics
# ============================================================================

def track_request_metrics(endpoint: str):
    """
    Decorator to automatically track request metrics.

    Args:
        endpoint: Endpoint name for labeling

    Usage:
        @app.route('/api/endpoint')
        @track_request_metrics('api_endpoint')
        def my_endpoint():
            ...
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # [ORFEAS] ORFEAS FIX: Skip metrics in test mode to prevent blocking
            if os.getenv('TESTING') == '1' or os.getenv('FLASK_ENV') == 'testing':
                return func(*args, **kwargs)

            method = 'GET'  # Default, will be overridden by Flask
            start_time = time.time()

            # Track concurrent requests
            concurrent_requests.labels(endpoint=endpoint).inc()

            try:
                # Execute function
                result = func(*args, **kwargs)

                # Track success
                duration = time.time() - start_time
                http_request_duration_seconds.labels(
                    method=method,
                    endpoint=endpoint
                ).observe(duration)

                http_requests_total.labels(
                    method=method,
                    endpoint=endpoint,
                    status='200'
                ).inc()

                return result

            except Exception as e:
                # Track error
                duration = time.time() - start_time
                http_request_duration_seconds.labels(
                    method=method,
                    endpoint=endpoint
                ).observe(duration)

                http_requests_total.labels(
                    method=method,
                    endpoint=endpoint,
                    status='500'
                ).inc()

                errors_total.labels(
                    type=type(e).__name__,
                    endpoint=endpoint
                ).inc()

                raise

            finally:
                # Decrement concurrent requests
                concurrent_requests.labels(endpoint=endpoint).dec()

        return wrapper
    return decorator


# ============================================================================
# Metrics Endpoint
# ============================================================================

def metrics_endpoint() -> Response:
    """
    Flask endpoint to expose Prometheus metrics.

    Returns:
        Response with metrics in Prometheus format

    Usage:
        @app.route('/metrics')
        def metrics():
            return metrics_endpoint()
    """
    # Update system metrics before export
    update_system_metrics()
    update_gpu_metrics()

    # Generate metrics
    return Response(
        generate_latest(REGISTRY),
        mimetype=CONTENT_TYPE_LATEST
    )


# ============================================================================
# Helper Functions
# ============================================================================

def track_generation_start(job_type: str):
    """Track when a generation job starts."""
    active_jobs.labels(type=job_type).inc()


def track_generation_end(job_type: str, success: bool, duration: float, **labels):
    """Track when a generation job ends."""
    active_jobs.labels(type=job_type).dec()

    if success:
        successful_generations_total.labels(type=job_type).inc()
    else:
        reason = labels.get('reason', 'unknown')
        failed_generations_total.labels(type=job_type, reason=reason).inc()


def track_validation_error(field: str, error_type: str):
    """Track a validation error."""
    validation_errors_total.labels(field=field, error_type=error_type).inc()


def track_rate_limit_rejection(endpoint: str):
    """Track a rate limit rejection."""
    rate_limit_rejections_total.labels(endpoint=endpoint).inc()


# ============================================================================
# Quality Validation Metrics Tracking
# ============================================================================

def track_quality_metrics(
    bg_removal: float = None,
    shape: float = None,
    texture: float = None,
    final: float = None,
    overall: float = None,
    quality_grade: str = None,
    manifold: bool = None,
    printable: bool = None,
    auto_repairs: int = 0,
    repair_types: list = None
):
    """
    Track quality validation metrics for a 3D generation.

    Args:
        bg_removal: Background removal quality score (0.0-1.0)
        shape: Shape generation quality score (0.0-1.0)
        texture: Texture coherence quality score (0.0-1.0)
        final: Final mesh quality score (0.0-1.0)
        overall: Overall quality score (0.0-1.0)
        quality_grade: Quality grade (A+, A, B+, B, C, D, F)
        manifold: Whether mesh is manifold (watertight)
        printable: Whether mesh is 3D-printable
        auto_repairs: Number of auto-repairs performed
        repair_types: List of repair types applied

    Example:
        track_quality_metrics(
            bg_removal=0.92,
            shape=0.88,
            texture=0.85,
            final=0.90,
            overall=0.89,
            quality_grade='A',
            manifold=True,
            printable=True,
            auto_repairs=2,
            repair_types=['non_manifold', 'degenerate_faces']
        )
    """
    try:
        # Update individual stage scores
        if bg_removal is not None:
            quality_bg_removal_score.set(bg_removal)
            quality_score_distribution.labels(stage='bg_removal').observe(bg_removal)

        if shape is not None:
            quality_shape_score.set(shape)
            quality_score_distribution.labels(stage='shape').observe(shape)

        if texture is not None:
            quality_texture_score.set(texture)
            quality_score_distribution.labels(stage='texture').observe(texture)

        if final is not None:
            quality_final_score.set(final)
            quality_score_distribution.labels(stage='final').observe(final)

        # Update overall quality
        if overall is not None:
            quality_overall_score.set(overall)
            quality_score_distribution.labels(stage='overall').observe(overall)

            # Track threshold passes
            thresholds = [0.95, 0.90, 0.85, 0.80, 0.75, 0.70]
            for threshold in thresholds:
                if overall >= threshold:
                    quality_threshold_passes_total.labels(threshold=str(threshold)).inc()
                    break

        # Track quality grade
        if quality_grade is not None:
            quality_grade_total.labels(grade=quality_grade).inc()

        # Track auto-repairs
        if auto_repairs > 0 and repair_types:
            for repair_type in repair_types:
                quality_auto_repairs_total.labels(repair_type=repair_type).inc()

        # Track manifold/printable rates (update rolling average)
        # Note: These require session-level tracking, implemented separately
        if manifold is not None:
            logger.debug(f"[QUALITY_METRICS] Manifold: {manifold}")

        if printable is not None:
            logger.debug(f"[QUALITY_METRICS] Printable: {printable}")

    except Exception as e:
        logger.error(f"[QUALITY_METRICS] Error tracking quality metrics: {e}")


def track_quality_validation_failure(stage: str, issue_type: str):
    """
    Track a quality validation failure.

    Args:
        stage: Validation stage (bg_removal, shape, texture, final)
        issue_type: Specific issue detected (e.g., low_coverage, non_manifold, low_resolution)

    Example:
        track_quality_validation_failure('shape', 'non_manifold')
        track_quality_validation_failure('texture', 'low_resolution')
    """
    try:
        quality_validation_failures_total.labels(stage=stage, issue_type=issue_type).inc()
        logger.warning(f"[QUALITY_METRICS] Validation failure - Stage: {stage}, Issue: {issue_type}")
    except Exception as e:
        logger.error(f"[QUALITY_METRICS] Error tracking validation failure: {e}")


def update_quality_rates(manifold_count: int, total_count: int, printable_count: int):
    """
    Update manifold and printable mesh rate gauges.

    Args:
        manifold_count: Number of manifold meshes in session
        total_count: Total number of meshes generated in session
        printable_count: Number of printable meshes in session

    Example:
        # Update after every 10 generations
        update_quality_rates(manifold_count=8, total_count=10, printable_count=7)
    """
    try:
        if total_count > 0:
            manifold_rate = (manifold_count / total_count) * 100
            printable_rate = (printable_count / total_count) * 100

            quality_manifold_rate.set(manifold_rate)
            quality_printable_rate.set(printable_rate)

            logger.debug(f"[QUALITY_METRICS] Manifold rate: {manifold_rate:.1f}%, Printable rate: {printable_rate:.1f}%")
    except Exception as e:
        logger.error(f"[QUALITY_METRICS] Error updating quality rates: {e}")


# ============================================================================
# WebSocket Metrics Tracking (Phase 2.4)
# ============================================================================

def track_websocket_connection(client_type: str = 'browser', increment: bool = True):
    """
    Track WebSocket connection open/close events.

    Args:
        client_type: Type of client (browser, api, internal)
        increment: True for connect, False for disconnect

    Example:
        track_websocket_connection('browser', increment=True)   # Connection opened
        track_websocket_connection('browser', increment=False)  # Connection closed
    """
    try:
        if increment:
            websocket_connections_active.labels(client_type=client_type).inc()
            logger.debug(f"[WS_METRICS] WebSocket connected - Type: {client_type}")
        else:
            websocket_connections_active.labels(client_type=client_type).dec()
            logger.debug(f"[WS_METRICS] WebSocket disconnected - Type: {client_type}")
    except Exception as e:
        logger.error(f"[WS_METRICS] Error tracking WebSocket connection: {e}")


def track_websocket_message(event_type: str):
    """
    Track WebSocket message sent to client.

    Args:
        event_type: Type of event (progress, error, complete, status, heartbeat)

    Example:
        track_websocket_message('progress')
        track_websocket_message('complete')
        track_websocket_message('error')
    """
    try:
        websocket_messages_sent_total.labels(event_type=event_type).inc()
    except Exception as e:
        logger.error(f"[WS_METRICS] Error tracking WebSocket message: {e}")


def track_websocket_error(error_type: str):
    """
    Track WebSocket error.

    Args:
        error_type: Type of error (connection_failed, send_failed, timeout, disconnect)

    Example:
        track_websocket_error('connection_failed')
        track_websocket_error('send_failed')
    """
    try:
        websocket_errors_total.labels(error_type=error_type).inc()
        logger.warning(f"[WS_METRICS] WebSocket error - Type: {error_type}")
    except Exception as e:
        logger.error(f"[WS_METRICS] Error tracking WebSocket error: {e}")


def track_websocket_duration(duration_seconds: float):
    """
    Track WebSocket connection duration when connection closes.

    Args:
        duration_seconds: Connection duration in seconds

    Example:
        track_websocket_duration(125.3)  # Connection lasted 2 minutes 5 seconds
    """
    try:
        websocket_connection_duration_seconds.observe(duration_seconds)
        logger.debug(f"[WS_METRICS] WebSocket duration: {duration_seconds:.1f}s")
    except Exception as e:
        logger.error(f"[WS_METRICS] Error tracking WebSocket duration: {e}")


# ============================================================================
# Pipeline Stage Metrics Tracking (Phase 2.4)
# ============================================================================

def track_pipeline_stage(stage: str, duration_seconds: float):
    """
    Track completion of a pipeline stage with its duration.

    Args:
        stage: Pipeline stage name (background_removal, shape_generation, texture_generation, mesh_export)
        duration_seconds: Stage duration in seconds

    Example:
        track_pipeline_stage('background_removal', 3.2)
        track_pipeline_stage('shape_generation', 45.8)
        track_pipeline_stage('texture_generation', 52.1)
        track_pipeline_stage('mesh_export', 1.5)
    """
    try:
        pipeline_stage_duration_seconds.labels(stage=stage).observe(duration_seconds)
        logger.debug(f"[PIPELINE_METRICS] Stage '{stage}' completed in {duration_seconds:.2f}s")
    except Exception as e:
        logger.error(f"[PIPELINE_METRICS] Error tracking pipeline stage: {e}")


def track_pipeline_stage_error(stage: str, error_type: str):
    """
    Track error in a specific pipeline stage.

    Args:
        stage: Pipeline stage where error occurred
        error_type: Type of error (timeout, out_of_memory, invalid_input, processing_failed)

    Example:
        track_pipeline_stage_error('shape_generation', 'out_of_memory')
        track_pipeline_stage_error('texture_generation', 'timeout')
    """
    try:
        pipeline_stage_errors_total.labels(stage=stage, error_type=error_type).inc()
        logger.error(f"[PIPELINE_METRICS] Stage error - Stage: {stage}, Error: {error_type}")
    except Exception as e:
        logger.error(f"[PIPELINE_METRICS] Error tracking pipeline stage error: {e}")


# ============================================================================
# Export Public API
# ============================================================================

__all__ = [
    'metrics_endpoint',
    'set_app_info',
    'update_system_metrics',
    'update_gpu_metrics',
    'track_request_metrics',
    'track_generation_start',
    'track_generation_end',
    'track_validation_error',
    'track_rate_limit_rejection',

    # Quality validation tracking (Priority #1 Feature)
    'track_quality_metrics',
    'track_quality_validation_failure',
    'update_quality_rates',

    # WebSocket tracking (Phase 2.4)
    'track_websocket_connection',
    'track_websocket_message',
    'track_websocket_error',
    'track_websocket_duration',

    # Pipeline stage tracking (Phase 2.4)
    'track_pipeline_stage',
    'track_pipeline_stage_error',

    # Metrics (for manual use)
    'http_requests_total',
    'http_request_duration_seconds',
    'errors_total',
    'text_to_image_generations_total',
    'model_3d_generations_total',
    'active_jobs',
    'successful_generations_total',
]
