# ORFEAS AI - Advanced Patterns & Optimization Guide

**Document:** Advanced development patterns, performance optimization, and architectural best practices for ORFEAS AI 2D3D Studio
**Version:** 2.1 (Enterprise Edition)
**Last Updated:** October 2025

## Overview

This guide covers advanced development patterns for ORFEAS AI systems.

---

## Advanced Model Caching

### Thread-Safe Singleton Pattern

```python

## backend/hunyuan_integration.py - Production-grade caching

import threading
from functools import lru_cache
import logging

logger = logging.getLogger(__name__)

class Hunyuan3DProcessor:
    """Thread-safe model cache with automatic lifecycle management."""

    _model_cache = {
        'shapegen_pipeline': None,
        'texgen_pipeline': None,
        'rembg_model': None,
        'initialized': False,
        'version': None
    }
    _cache_lock = threading.RLock()  # Reentrant lock
    _initialization_event = threading.Event()

    def __init__(self):
        """Initialize with fast-path for cached models."""
        with self._cache_lock:
            if self._model_cache['initialized']:
                logger.info("[CACHE] Using pre-loaded models (<1s)")
                self._use_cached_models()
                return

            logger.info("[CACHE] First initialization - loading models (30s)")
            self._initialize_models()
            self._model_cache['initialized'] = True
            self._initialization_event.set()

    def _use_cached_models(self):
        """Fast path: reuse existing models from cache."""
        self.shapegen_pipeline = self._model_cache['shapegen_pipeline']
        self.texgen_pipeline = self._model_cache['texgen_pipeline']
        self.rembg = self._model_cache['rembg_model']

    def _initialize_models(self):
        """Load all models into GPU memory."""

        # Load shapegen (3.3GB)

        self.shapegen_pipeline = self._load_shapegen_model()
        self._model_cache['shapegen_pipeline'] = self.shapegen_pipeline

        # Load texgen (2GB)

        self.texgen_pipeline = self._load_texgen_model()
        self._model_cache['texgen_pipeline'] = self.texgen_pipeline

        # Load rembg (50MB)

        self.rembg = self._load_rembg_model()
        self._model_cache['rembg_model'] = self.rembg

    def generate_3d(self, image, steps=50, quality=7):
        """Generate 3D model with guaranteed cleanup."""
        try:

            # Ensure cache is ready

            self._initialization_event.wait(timeout=60)

            # Background removal

            processed_image = self.rembg.remove(image)

            # Shape generation

            mesh = self.shapegen_pipeline(
                image=processed_image,
                num_inference_steps=steps
            )

            # Texture synthesis

            textured_mesh = self.texgen_pipeline(
                mesh=mesh,
                image=processed_image
            )

            return textured_mesh

        except Exception as e:
            logger.error(f"[CACHE] Generation failed: {e}")
            raise
        finally:

            # CRITICAL: Always cleanup

            import torch
            torch.cuda.empty_cache()
            torch.cuda.synchronize()

```text

### Cache Invalidation & Version Management

```python
class CacheVersionManager:
    """Intelligent cache invalidation based on model versions."""

    @staticmethod
    def check_model_update():
        """Check if models need reloading."""
        current_version = Hunyuan3DProcessor._model_cache['version']
        latest_version = CacheVersionManager._get_latest_model_version()

        if current_version != latest_version:
            logger.warning(f"[CACHE] Model update available: {current_version} → {latest_version}")
            Hunyuan3DProcessor._model_cache['initialized'] = False
            return True
        return False

    @staticmethod
    def _get_latest_model_version():
        """Fetch latest model version from registry."""

        # Check local model directory timestamps

        import os
        model_dir = os.getenv('HUNYUAN3D_PATH')
        if os.path.exists(model_dir):
            return max(os.path.getmtime(model_dir), 0)
        return None

```text

---

## GPU Memory Optimization

### Dynamic Memory Allocation

```python

## backend/gpu_manager.py - RTX 3090 optimized

import torch
import logging
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class GPUMemoryManager:
    """Intelligent GPU memory management for RTX 3090."""

    VRAM_TOTAL = 24576  # MB (24GB)
    SAFETY_MARGIN = 0.8  # Use only 80% (19.2GB)
    AVAILABLE_VRAM = int(VRAM_TOTAL * SAFETY_MARGIN)

    def __init__(self):
        self.allocated_jobs = {}
        self.peak_usage = 0

    def get_available_memory(self):
        """Get currently available GPU memory."""
        torch.cuda.synchronize()
        torch.cuda.reset_peak_memory_stats()

        free, total = torch.cuda.mem_get_info()
        free_mb = free / 1024 / 1024

        logger.info(f"[GPU] Available: {free_mb:.0f}MB / {self.AVAILABLE_VRAM:.0f}MB")
        return free_mb

    def can_process_job(self, estimated_vram=6000):
        """Check if job can be processed."""
        available = self.get_available_memory()
        can_process = available > estimated_vram

        status = "✓ OK" if can_process else "✗ INSUFFICIENT"
        logger.info(f"[GPU] Job requires {estimated_vram}MB {status}")

        return can_process

    @contextmanager
    def allocate_job(self, job_id, estimated_vram=6000):
        """Context manager for safe GPU memory allocation."""
        logger.info(f"[GPU] Allocating job {job_id} ({estimated_vram}MB)")
        self.allocated_jobs[job_id] = estimated_vram

        try:
            yield
        finally:
            self.cleanup_job(job_id)

    def cleanup_job(self, job_id):
        """Clean up job resources."""
        logger.info(f"[GPU] Cleaning up job {job_id}")

        # Clear GPU cache

        torch.cuda.empty_cache()
        torch.cuda.synchronize()

        # Track peak usage

        peak = torch.cuda.max_memory_allocated() / 1024 / 1024
        if peak > self.peak_usage:
            self.peak_usage = peak
            logger.info(f"[GPU] Peak usage: {peak:.0f}MB")

        if job_id in self.allocated_jobs:
            del self.allocated_jobs[job_id]

## Usage pattern

gpu_mgr = GPUMemoryManager()

@app.route('/api/generate-3d', methods=['POST'])
def generate_3d():
    if not gpu_mgr.can_process_job(estimated_vram=6000):
        return jsonify({'error': 'GPU memory insufficient'}), 503

    job_id = str(uuid.uuid4())
    with gpu_mgr.allocate_job(job_id, estimated_vram=6000):
        processor = Hunyuan3DProcessor()
        mesh = processor.generate_3d(image)
        return jsonify({'result': mesh})

```text

### Memory Monitoring Dashboard

```python
@app.route('/api/gpu-metrics', methods=['GET'])
def get_gpu_metrics():
    """Real-time GPU metrics endpoint."""
    free, total = torch.cuda.mem_get_info()
    allocated = torch.cuda.memory_allocated() / 1024 / 1024
    reserved = torch.cuda.memory_reserved() / 1024 / 1024

    return jsonify({
        'total_vram_mb': total / 1024 / 1024,
        'free_vram_mb': free / 1024 / 1024,
        'allocated_mb': allocated,
        'reserved_mb': reserved,
        'utilization_percent': (allocated / (total / 1024 / 1024)) * 100,
        'peak_memory_mb': torch.cuda.max_memory_allocated() / 1024 / 1024,
        'jobs_queued': len(gpu_mgr.allocated_jobs)
    })

```text

---

## Async Job Orchestration

### Advanced Job Queue Management

```python

## backend/batch_processor.py - Enterprise-grade async processing

import asyncio
import uuid
from enum import Enum
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class JobStatus(Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class AsyncJob:
    """Represents an async job with full lifecycle tracking."""

    def __init__(self, job_type, params, priority=5):
        self.id = str(uuid.uuid4())
        self.job_type = job_type
        self.params = params
        self.priority = priority  # 1-10, higher = more important
        self.status = JobStatus.QUEUED
        self.created_at = datetime.utcnow()
        self.started_at = None
        self.completed_at = None
        self.result = None
        self.error = None
        self.progress = 0

    def to_dict(self):
        return {
            'id': self.id,
            'type': self.job_type,
            'status': self.status.value,
            'progress': self.progress,
            'created_at': self.created_at.isoformat(),
            'eta_seconds': self._estimate_eta()
        }

    def _estimate_eta(self):
        """Estimate time remaining."""
        if self.progress == 0:
            return None
        elapsed = (datetime.utcnow() - self.started_at).total_seconds()
        estimated_total = elapsed / (self.progress / 100)
        return max(0, int(estimated_total - elapsed))

class AsyncJobQueue:
    """Thread-safe job queue with priority support."""

    def __init__(self, max_concurrent=3):
        self.max_concurrent = max_concurrent
        self.queue = []
        self.active_jobs = {}
        self.completed_jobs = {}
        self.lock = asyncio.Lock()

    async def submit_job(self, job_type, params, priority=5):
        """Submit a new job."""
        job = AsyncJob(job_type, params, priority)

        async with self.lock:
            self.queue.append(job)
            self.queue.sort(key=lambda x: x.priority, reverse=True)

        logger.info(f"[QUEUE] Job {job.id} submitted ({job_type})")
        asyncio.create_task(self._process_queue())

        return job

    async def _process_queue(self):
        """Process jobs from queue."""
        while len(self.active_jobs) < self.max_concurrent and self.queue:
            async with self.lock:
                if not self.queue:
                    return
                job = self.queue.pop(0)

            job.status = JobStatus.PROCESSING
            job.started_at = datetime.utcnow()
            self.active_jobs[job.id] = job

            asyncio.create_task(self._execute_job(job))

    async def _execute_job(self, job):
        """Execute a single job."""
        try:
            logger.info(f"[QUEUE] Executing job {job.id}")

            if job.job_type == '3d_generation':
                job.result = await self._generate_3d(job)
            elif job.job_type == 'video_generation':
                job.result = await self._generate_video(job)

            job.status = JobStatus.COMPLETED
            logger.info(f"[QUEUE] Job {job.id} completed")

        except Exception as e:
            job.status = JobStatus.FAILED
            job.error = str(e)
            logger.error(f"[QUEUE] Job {job.id} failed: {e}")

        finally:
            job.completed_at = datetime.utcnow()
            async with self.lock:
                del self.active_jobs[job.id]
                self.completed_jobs[job.id] = job

            # Process next job

            await self._process_queue()

    async def _generate_3d(self, job):
        """Execute 3D generation job."""
        processor = Hunyuan3DProcessor()
        return processor.generate_3d(**job.params)

    async def _generate_video(self, job):
        """Execute video generation job."""

        # Implementation

        pass

    def get_job_status(self, job_id):
        """Get current job status."""
        if job_id in self.active_jobs:
            return self.active_jobs[job_id].to_dict()
        elif job_id in self.completed_jobs:
            return self.completed_jobs[job_id].to_dict()
        return None

## Global job queue

job_queue = AsyncJobQueue(max_concurrent=3)

## Flask endpoints

@app.route('/api/submit-job', methods=['POST'])
async def submit_job():
    """Submit async job."""
    data = request.get_json()
    job = await job_queue.submit_job(
        job_type=data['type'],
        params=data.get('params', {}),
        priority=data.get('priority', 5)
    )
    return jsonify(job.to_dict()), 202

@app.route('/api/job/<job_id>', methods=['GET'])
def get_job(job_id):
    """Get job status."""
    status = job_queue.get_job_status(job_id)
    return jsonify(status) if status else ('', 404)

```text

---

## Advanced Error Handling

### Context-Aware Error Recovery

```python

## backend/contextual_error_handler.py

import logging
from typing import Callable, Any, Optional

logger = logging.getLogger(__name__)

class ContextualErrorHandler:
    """Intelligent error handling with automatic recovery strategies."""

    RECOVERY_STRATEGIES = {
        'torch.cuda.OutOfMemoryError': 'reduce_batch_size',
        'FileNotFoundError': 'download_models',
        'ConnectionError': 'retry_with_backoff',
        'TimeoutError': 'reduce_quality',
    }

    @staticmethod
    def handle_with_recovery(operation: Callable, *args, max_retries=3, **kwargs):
        """Execute operation with automatic recovery."""
        for attempt in range(max_retries):
            try:
                return operation(*args, **kwargs)
            except Exception as e:
                error_type = type(e).__name__
                strategy = ContextualErrorHandler.RECOVERY_STRATEGIES.get(error_type)

                if strategy and attempt < max_retries - 1:
                    logger.warning(f"[ERROR] {error_type} - Attempting recovery: {strategy}")
                    ContextualErrorHandler._apply_recovery(strategy, kwargs)
                else:
                    logger.error(f"[ERROR] {error_type} - Max retries exceeded")
                    raise

    @staticmethod
    def _apply_recovery(strategy: str, kwargs: dict):
        """Apply recovery strategy."""
        if strategy == 'reduce_batch_size':
            kwargs['batch_size'] = kwargs.get('batch_size', 1) // 2
            import torch
            torch.cuda.empty_cache()

        elif strategy == 'download_models':
            import subprocess
            subprocess.run(['python', 'backend/download_models.py'])

        elif strategy == 'retry_with_backoff':
            import time
            time.sleep(2 ** kwargs.get('attempt', 0))

        elif strategy == 'reduce_quality':
            kwargs['quality'] = kwargs.get('quality', 7) - 1

```text

---

## Performance Profiling

### Comprehensive Performance Monitoring

```python

## backend/performance_profiler.py

import time
import functools
import logging
from prometheus_client import Histogram, Counter

logger = logging.getLogger(__name__)

## Prometheus metrics

request_duration = Histogram(
    'request_duration_seconds',
    'Request duration',
    ['endpoint', 'status']
)

request_count = Counter(
    'requests_total',
    'Total requests',
    ['endpoint', 'method']
)

def profile_performance(endpoint_name):
    """Decorator for performance profiling."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            status = 'success'

            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                status = 'error'
                raise
            finally:
                duration = time.time() - start_time
                request_duration.labels(
                    endpoint=endpoint_name,
                    status=status
                ).observe(duration)
                request_count.labels(
                    endpoint=endpoint_name,
                    method=func.__name__
                ).inc()

                logger.info(f"[PERF] {endpoint_name}: {duration:.2f}s ({status})")

        return wrapper
    return decorator

## Usage

@app.route('/api/generate-3d', methods=['POST'])
@profile_performance('generate_3d')
def generate_3d():

    # Implementation

    pass

```text

---

## Multi-Model Orchestration

### Intelligent Model Selection

```python

## backend/model_orchestrator.py

from enum import Enum

class ModelQuality(Enum):
    FAST = 5      # 5s generation, lower quality
    BALANCED = 7  # 15s generation, good quality
    QUALITY = 9   # 30s generation, high quality

class ModelOrchestrator:
    """Select optimal model configuration based on context."""

    @staticmethod
    def select_model_config(quality_level, available_vram):
        """Choose model configuration."""
        configs = {
            ModelQuality.FAST: {
                'steps': 30,
                'guidance_scale': 7.5,
                'batch_size': 2
            },
            ModelQuality.BALANCED: {
                'steps': 50,
                'guidance_scale': 9.0,
                'batch_size': 1
            },
            ModelQuality.QUALITY: {
                'steps': 100,
                'guidance_scale': 10.0,
                'batch_size': 1
            }
        }

        return configs[quality_level]

```text

---

## Context-Aware Processing

### Intelligent Context Management

```python

## backend/context_manager.py

class IntelligentContextManager:
    """Maintain and optimize request context."""

    def __init__(self):
        self.context_cache = {}
        self.performance_history = {}

    def analyze_request_context(self, request_data):
        """Extract meaningful context from request."""
        return {
            'user_id': request_data.get('user_id'),
            'priority': request_data.get('priority', 5),
            'quality_preference': request_data.get('quality', 7),
            'timestamp': datetime.utcnow()
        }

    def predict_optimal_config(self, context):
        """Predict optimal processing configuration."""

        # Use historical data to make predictions

        similar_requests = self._find_similar_requests(context)

        if similar_requests:
            avg_quality = sum(r['quality'] for r in similar_requests) / len(similar_requests)
            return {'predicted_quality': avg_quality}

        return {'predicted_quality': 7}

```text

---

## Security Hardening

### Input Validation & Sanitization

```python

## backend/security_hardening.py

from PIL import Image
import hashlib

class SecurityHardening:
    """Enterprise-grade security validation."""

    @staticmethod
    def validate_image_upload(file):
        """Validate image before processing."""

        # Check file type

        if not file.filename.lower().endswith(('.jpg', '.png', '.webp')):
            raise ValueError("Invalid image format")

        # Check file size (max 50MB)

        file.seek(0, 2)
        file_size = file.tell()
        if file_size > 50 * 1024 * 1024:
            raise ValueError("Image too large")

        # Verify image integrity

        try:
            file.seek(0)
            img = Image.open(file)
            img.verify()
        except Exception as e:
            raise ValueError(f"Invalid image: {e}")

        # Check for suspicious content

        file_hash = hashlib.md5(file.getvalue()).hexdigest()
        if SecurityHardening._is_suspicious_hash(file_hash):
            raise ValueError("File flagged as suspicious")

        return True

    @staticmethod
    def _is_suspicious_hash(file_hash):
        """Check against known malicious hashes."""

        # Implementation: check against database

        return False

```text

---

## Advanced Deployment Patterns

### Canary Deployments

```python

## backend/deployment_manager.py

class DeploymentManager:
    """Manage progressive deployments."""

    @staticmethod
    def route_canary_traffic(version_a, version_b, percentage=10):
        """Route 10% traffic to new version."""
        import random
        return version_b if random.random() < percentage / 100 else version_a

```text

---

This advanced patterns guide complements the slim core instructions and provides deep implementation details for enterprise features.
