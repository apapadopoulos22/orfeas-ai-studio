"""
ORFEAS AI 2D→3D Studio - Performance Optimizer
==============================================
Advanced performance optimization for maximum speed and efficiency.

Features:
- Model-level optimizations with caching
- Memory optimization and GPU management
- Compilation optimization with torch.compile
- Request-level performance tuning
- Adaptive optimization based on metrics
- Real-time performance monitoring
"""

import os
import time
import torch
import threading
import psutil
import gc
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from contextlib import contextmanager
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """Performance metrics container"""
    processing_time: float
    memory_usage: Dict[str, float]
    gpu_utilization: float
    cache_hit_rate: float
    success_rate: float
    throughput: float
    quality_score: float

class PerformanceOptimizer:
    """
    Comprehensive performance optimization for maximum speed
    """

    def __init__(self):
        self.cache_layers = {
            'model_cache': {},      # Model instance caching
            'result_cache': {},     # Generation result caching
            'context_cache': {},    # Context analysis caching
            'precompute_cache': {}  # Pre-computed optimizations
        }
        self.optimization_config = self.load_optimization_config()
        self.performance_history = []
        self.optimization_lock = threading.Lock()
        self.auto_optimization_enabled = True

    def load_optimization_config(self) -> Dict[str, Any]:
        """Load optimization configuration"""

        return {
            'enable_torch_compile': os.getenv('ENABLE_MODEL_COMPILATION', 'true').lower() == 'true',
            'enable_cache_warming': os.getenv('ENABLE_CACHE_WARMING', 'true').lower() == 'true',
            'enable_mixed_precision': os.getenv('ENABLE_MIXED_PRECISION', 'true').lower() == 'true',
            'enable_quantization': os.getenv('ENABLE_MODEL_QUANTIZATION', 'false').lower() == 'true',
            'enable_pruning': os.getenv('ENABLE_MODEL_PRUNING', 'false').lower() == 'true',
            'batch_inference_size': int(os.getenv('BATCH_INFERENCE_SIZE', 4)),
            'performance_threshold': float(os.getenv('PERFORMANCE_THRESHOLD', 0.8)),
            'cache_size_limit': int(os.getenv('CACHE_SIZE_LIMIT_MB', 2048)),
            'auto_optimization_interval': int(os.getenv('AUTO_OPTIMIZATION_INTERVAL', 300)),
            'memory_cleanup_threshold': float(os.getenv('MEMORY_CLEANUP_THRESHOLD', 0.85))
        }

    def apply_speed_optimizations(self, model, processing_type: str):
        """Apply all speed optimizations for maximum performance"""

        logger.info(f"[ORFEAS] Applying speed optimizations for {processing_type}")

        try:
            # 1. Model-level optimizations
            optimized_model = self.optimize_model_inference(model)

            # 2. Memory optimization
            optimized_model = self.apply_memory_optimization(optimized_model)

            # 3. Compilation optimization
            if self.optimization_config.get('enable_torch_compile', False):
                optimized_model = self.apply_torch_compilation(optimized_model)

            # 4. GPU-specific optimizations
            optimized_model = self.apply_gpu_optimizations(optimized_model)

            # 5. Cache model for future use
            self.cache_optimized_model(processing_type, optimized_model)

            logger.info(f"[ORFEAS] Speed optimizations applied successfully for {processing_type}")
            return optimized_model

        except Exception as e:
            logger.error(f"[ORFEAS] Speed optimization failed: {e}")
            return model  # Return original model if optimization fails

    def optimize_model_inference(self, model):
        """Apply inference-specific optimizations"""

        try:
            # Enable inference mode
            model.eval()
            torch.set_grad_enabled(False)

            # Apply quantization if configured
            if self.optimization_config.get('enable_quantization', False):
                model = self.apply_quantization(model)

            # Apply pruning for faster inference
            if self.optimization_config.get('enable_pruning', False):
                model = self.apply_structured_pruning(model, sparsity=0.3)

            # Enable gradient checkpointing for memory efficiency
            if hasattr(model, 'gradient_checkpointing_enable'):
                model.gradient_checkpointing_enable()

            return model

        except Exception as e:
            logger.warning(f"[ORFEAS] Model inference optimization failed: {e}")
            return model

    def apply_quantization(self, model):
        """Apply model quantization for faster inference"""

        try:
            # Dynamic quantization for linear layers
            quantized_model = torch.quantization.quantize_dynamic(
                model,
                {torch.nn.Linear, torch.nn.Conv2d},
                dtype=torch.qint8
            )

            logger.info("[ORFEAS] Model quantization applied successfully")
            return quantized_model

        except Exception as e:
            logger.warning(f"[ORFEAS] Model quantization failed: {e}")
            return model

    def apply_structured_pruning(self, model, sparsity: float = 0.3):
        """Apply structured pruning to reduce model size"""

        try:
            import torch.nn.utils.prune as prune

            # Apply pruning to linear layers
            for name, module in model.named_modules():
                if isinstance(module, torch.nn.Linear):
                    prune.l1_unstructured(module, name='weight', amount=sparsity)
                    prune.remove(module, 'weight')

            logger.info(f"[ORFEAS] Model pruning applied with {sparsity} sparsity")
            return model

        except Exception as e:
            logger.warning(f"[ORFEAS] Model pruning failed: {e}")
            return model

    def apply_memory_optimization(self, model):
        """Optimize memory usage for better performance"""

        try:
            # Enable memory efficient attention if available
            try:
                model.use_memory_efficient_attention = True
                logger.info("[ORFEAS] Memory efficient attention enabled")
            except AttributeError:
                pass

            # Optimize CUDA memory allocation
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                torch.cuda.synchronize()

                # Set memory fraction if configured
                memory_fraction = float(os.getenv('GPU_MEMORY_LIMIT', 0.8))
                if memory_fraction < 1.0:
                    torch.cuda.set_per_process_memory_fraction(memory_fraction)

            return model

        except Exception as e:
            logger.warning(f"[ORFEAS] Memory optimization failed: {e}")
            return model

    def apply_torch_compilation(self, model):
        """Apply torch.compile optimization"""

        try:
            # Compile model for faster execution
            compiled_model = torch.compile(model, mode='max-autotune')
            logger.info("[ORFEAS] Model compiled with torch.compile")
            return compiled_model

        except Exception as e:
            logger.warning(f"[ORFEAS] Torch compilation failed: {e}")
            return model

    def apply_gpu_optimizations(self, model):
        """Apply GPU-specific performance optimizations"""

        if not torch.cuda.is_available():
            return model

        try:
            # Enable TensorFloat-32 for RTX GPUs
            torch.backends.cuda.matmul.allow_tf32 = True
            torch.backends.cudnn.allow_tf32 = True

            # Enable cuDNN benchmark mode
            torch.backends.cudnn.benchmark = True
            torch.backends.cudnn.deterministic = False

            # Enable mixed precision if configured
            if self.optimization_config.get('enable_mixed_precision', True):
                model = model.half()  # Convert to FP16
                logger.info("[ORFEAS] Mixed precision (FP16) enabled")

            # Move model to GPU with optimal settings
            if not next(model.parameters()).is_cuda:
                model = model.cuda()

            return model

        except Exception as e:
            logger.warning(f"[ORFEAS] GPU optimization failed: {e}")
            return model

    def cache_optimized_model(self, processing_type: str, model):
        """Cache optimized model for reuse"""

        try:
            with self.optimization_lock:
                self.cache_layers['model_cache'][processing_type] = {
                    'model': model,
                    'timestamp': time.time(),
                    'usage_count': 0
                }

            logger.info(f"[ORFEAS] Optimized model cached for {processing_type}")

        except Exception as e:
            logger.warning(f"[ORFEAS] Model caching failed: {e}")

    def get_cached_model(self, processing_type: str):
        """Retrieve cached optimized model"""

        try:
            with self.optimization_lock:
                cache_entry = self.cache_layers['model_cache'].get(processing_type)
                if cache_entry:
                    cache_entry['usage_count'] += 1
                    return cache_entry['model']

            return None

        except Exception as e:
            logger.warning(f"[ORFEAS] Model cache retrieval failed: {e}")
            return None

    def warm_model_caches(self):
        """Pre-warm model caches with dummy data"""

        if not self.optimization_config.get('enable_cache_warming', True):
            return

        try:
            logger.info("[ORFEAS] Warming model caches")

            # Create dummy inputs for cache warming
            dummy_inputs = self.create_dummy_inputs()

            # Warm each model type
            for model_type in ['shape_generation', 'texture_generation']:
                try:
                    model = self.get_cached_model(model_type)
                    if model:
                        with torch.no_grad():
                            _ = model(dummy_inputs[model_type])
                        logger.info(f"[ORFEAS] Cache warmed for {model_type}")
                except Exception as e:
                    logger.warning(f"[ORFEAS] Cache warming failed for {model_type}: {e}")

            logger.info("[ORFEAS] Model cache warming completed")

        except Exception as e:
            logger.error(f"[ORFEAS] Cache warming failed: {e}")

    def create_dummy_inputs(self) -> Dict[str, torch.Tensor]:
        """Create dummy inputs for cache warming"""

        return {
            'shape_generation': torch.randn(1, 3, 256, 256).cuda() if torch.cuda.is_available() else torch.randn(1, 3, 256, 256),
            'texture_generation': torch.randn(1, 4, 512, 512).cuda() if torch.cuda.is_available() else torch.randn(1, 4, 512, 512)
        }

    def optimize_request_processing(self, request_context: Dict) -> Dict[str, Any]:
        """Optimize processing for specific request"""

        try:
            optimization_strategy = self.select_optimization_strategy(request_context)

            optimizations = {
                'processing_mode': optimization_strategy['mode'],
                'batch_size': optimization_strategy['batch_size'],
                'quality_level': optimization_strategy['quality_level'],
                'use_cache': optimization_strategy['use_cache'],
                'memory_limit': optimization_strategy['memory_limit']
            }

            logger.info(f"[ORFEAS] Request optimization strategy: {optimizations}")
            return optimizations

        except Exception as e:
            logger.error(f"[ORFEAS] Request optimization failed: {e}")
            return self.get_default_optimization_settings()

    def select_optimization_strategy(self, request_context: Dict) -> Dict[str, Any]:
        """Select optimal strategy based on request context"""

        # Analyze request characteristics
        complexity_score = request_context.get('complexity_score', 0.5)
        priority_level = request_context.get('priority', 'normal')
        deadline = request_context.get('deadline')

        # Get current system load
        system_load = self.get_system_load()

        # Fast mode for simple requests or high load
        if complexity_score < 0.3 or system_load > 0.8:
            return {
                'mode': 'fast',
                'batch_size': 1,
                'quality_level': 5,
                'use_cache': True,
                'memory_limit': 4000  # 4GB
            }

        # High-quality mode for complex requests with low load
        elif complexity_score > 0.7 and system_load < 0.5:
            return {
                'mode': 'quality',
                'batch_size': 1,
                'quality_level': 9,
                'use_cache': True,
                'memory_limit': 12000  # 12GB
            }

        # Balanced mode (default)
        else:
            return {
                'mode': 'balanced',
                'batch_size': 1,
                'quality_level': 7,
                'use_cache': True,
                'memory_limit': 8000  # 8GB
            }

    def get_system_load(self) -> float:
        """Get current system load"""

        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)

            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent

            # GPU usage if available
            gpu_percent = 0
            if torch.cuda.is_available():
                gpu_memory = torch.cuda.memory_allocated() / torch.cuda.max_memory_allocated()
                gpu_percent = gpu_memory * 100

            # Combined load score
            load_score = max(cpu_percent, memory_percent, gpu_percent) / 100.0
            return min(load_score, 1.0)

        except Exception as e:
            logger.warning(f"[ORFEUS] System load detection failed: {e}")
            return 0.5  # Default moderate load

    def get_default_optimization_settings(self) -> Dict[str, Any]:
        """Get default optimization settings"""

        return {
            'processing_mode': 'balanced',
            'batch_size': 1,
            'quality_level': 7,
            'use_cache': True,
            'memory_limit': 8000
        }

    @contextmanager
    def performance_tracking(self, operation_name: str):
        """Context manager for performance tracking"""

        start_time = time.time()
        start_memory = self.get_memory_usage()

        try:
            yield
        finally:
            end_time = time.time()
            end_memory = self.get_memory_usage()

            metrics = PerformanceMetrics(
                processing_time=end_time - start_time,
                memory_usage={
                    'start': start_memory,
                    'end': end_memory,
                    'delta': end_memory - start_memory
                },
                gpu_utilization=self.get_gpu_utilization(),
                cache_hit_rate=self.calculate_cache_hit_rate(),
                success_rate=1.0,  # Success if we reach here
                throughput=1.0 / (end_time - start_time),
                quality_score=0.0  # To be filled by caller
            )

            self.record_performance_metrics(operation_name, metrics)

    def get_memory_usage(self) -> float:
        """Get current memory usage in MB"""

        try:
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024  # Convert to MB
        except Exception:
            return 0.0

    def get_gpu_utilization(self) -> float:
        """Get GPU utilization percentage"""

        try:
            if torch.cuda.is_available():
                return torch.cuda.utilization() / 100.0
            return 0.0
        except Exception:
            return 0.0

    def calculate_cache_hit_rate(self) -> float:
        """Calculate cache hit rate"""

        try:
            total_requests = 0
            cache_hits = 0

            for cache_name, cache in self.cache_layers.items():
                for entry in cache.values():
                    if isinstance(entry, dict) and 'usage_count' in entry:
                        total_requests += entry['usage_count']
                        if entry['usage_count'] > 1:
                            cache_hits += entry['usage_count'] - 1

            return cache_hits / total_requests if total_requests > 0 else 0.0

        except Exception:
            return 0.0

    def record_performance_metrics(self, operation_name: str, metrics: PerformanceMetrics):
        """Record performance metrics for analysis"""

        try:
            metric_entry = {
                'timestamp': time.time(),
                'operation': operation_name,
                'metrics': metrics
            }

            self.performance_history.append(metric_entry)

            # Keep only recent history
            cutoff_time = time.time() - 3600  # 1 hour
            self.performance_history = [
                entry for entry in self.performance_history
                if entry['timestamp'] > cutoff_time
            ]

        except Exception as e:
            logger.warning(f"[ORFEAS] Performance metrics recording failed: {e}")

    def should_auto_optimize(self, processing_time: float) -> bool:
        """Determine if auto-optimization should be triggered"""

        if not self.auto_optimization_enabled:
            return False

        try:
            # Check if performance is below threshold
            performance_threshold = self.optimization_config['performance_threshold']

            # Calculate recent average processing time
            recent_metrics = [
                entry for entry in self.performance_history
                if entry['timestamp'] > time.time() - 300  # 5 minutes
            ]

            if len(recent_metrics) < 5:
                return False

            avg_processing_time = sum(
                entry['metrics'].processing_time for entry in recent_metrics
            ) / len(recent_metrics)

            # Trigger optimization if current time significantly exceeds average
            return processing_time > avg_processing_time * 1.5

        except Exception as e:
            logger.warning(f"[ORFEAS] Auto-optimization check failed: {e}")
            return False

    def trigger_auto_optimization(self):
        """Trigger automatic optimization"""

        try:
            logger.info("[ORFEAS] Triggering automatic optimization")

            # Clear caches
            self.clear_old_caches()

            # Force garbage collection
            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()

            # Update optimization config based on performance
            self.update_optimization_config()

            logger.info("[ORFEAS] Automatic optimization completed")

        except Exception as e:
            logger.error(f"[ORFEAS] Auto-optimization failed: {e}")

    def clear_old_caches(self):
        """Clear old cache entries"""

        try:
            current_time = time.time()
            cache_ttl = 3600  # 1 hour

            for cache_name, cache in self.cache_layers.items():
                old_keys = []
                for key, entry in cache.items():
                    if isinstance(entry, dict) and 'timestamp' in entry:
                        if current_time - entry['timestamp'] > cache_ttl:
                            old_keys.append(key)

                for key in old_keys:
                    del cache[key]

                logger.info(f"[ORFEAS] Cleared {len(old_keys)} old entries from {cache_name}")

        except Exception as e:
            logger.warning(f"[ORFEAS] Cache cleanup failed: {e}")

    def update_optimization_config(self):
        """Update optimization configuration based on performance"""

        try:
            # Analyze recent performance
            recent_metrics = [
                entry for entry in self.performance_history
                if entry['timestamp'] > time.time() - 1800  # 30 minutes
            ]

            if len(recent_metrics) < 10:
                return

            avg_processing_time = sum(
                entry['metrics'].processing_time for entry in recent_metrics
            ) / len(recent_metrics)

            avg_memory_usage = sum(
                entry['metrics'].memory_usage.get('delta', 0) for entry in recent_metrics
            ) / len(recent_metrics)

            # Adjust settings based on performance
            if avg_processing_time > 30:  # Slow processing
                self.optimization_config['enable_mixed_precision'] = True
                self.optimization_config['batch_inference_size'] = 1
                logger.info("[ORFEAS] Enabled aggressive speed optimizations")

            if avg_memory_usage > 1000:  # High memory usage
                self.optimization_config['cache_size_limit'] -= 256
                self.optimization_config['memory_cleanup_threshold'] = 0.7
                logger.info("[ORFEAS] Reduced memory usage settings")

        except Exception as e:
            logger.warning(f"[ORFEAS] Configuration update failed: {e}")

    def get_performance_report(self) -> Dict[str, Any]:
        """Generate performance analysis report"""

        try:
            recent_metrics = [
                entry for entry in self.performance_history
                if entry['timestamp'] > time.time() - 3600  # 1 hour
            ]

            if not recent_metrics:
                return {'status': 'no_data'}

            # Calculate statistics
            processing_times = [entry['metrics'].processing_time for entry in recent_metrics]
            memory_deltas = [entry['metrics'].memory_usage.get('delta', 0) for entry in recent_metrics]

            report = {
                'total_operations': len(recent_metrics),
                'avg_processing_time': sum(processing_times) / len(processing_times),
                'max_processing_time': max(processing_times),
                'min_processing_time': min(processing_times),
                'avg_memory_delta': sum(memory_deltas) / len(memory_deltas),
                'cache_hit_rate': self.calculate_cache_hit_rate(),
                'gpu_utilization': self.get_gpu_utilization(),
                'system_load': self.get_system_load(),
                'optimization_config': self.optimization_config,
                'timestamp': datetime.utcnow().isoformat()
            }

            return report

        except Exception as e:
            logger.error(f"[ORFEAS] Performance report generation failed: {e}")
            return {'status': 'error', 'error': str(e)}
