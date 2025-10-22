"""
ORFEAS AI 2D→3D Studio - GPU Optimizer
=======================================
ORFEAS AI Project

Dynamic GPU resource optimization and batch sizing

Features:
- Dynamic batch size calculation based on available VRAM
- GPU memory profiling and analysis
- Intelligent cache management
- Model optimization utilities
"""

import logging
import os
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import json

# Optional torch import with TESTING-safe stub
try:
    import torch  # type: ignore
except Exception as _torch_e:
    if os.getenv('TESTING','0')=='1' or os.getenv('FLASK_ENV')=='testing':
        class _CudaStub:
            @staticmethod
            def is_available(): return False
            @staticmethod
            def empty_cache(): return None
            @staticmethod
            def synchronize(): return None
            @staticmethod
            def get_device_properties(*_args, **_kwargs):
                class _Props: total_memory = 0
                return _Props()
            @staticmethod
            def memory_allocated(*_a, **_k): return 0
            @staticmethod
            def memory_reserved(*_a, **_k): return 0
        class _Backends:
            class cuda:
                matmul = type('matmul', (), {'allow_tf32': False})
            class cudnn:
                benchmark = False
                deterministic = False
        class _TorchStub:
            cuda = _CudaStub()
            backends = _Backends()
            @staticmethod
            def device(name: str): return name
        torch = _TorchStub()  # type: ignore
    else:
        raise
# psutil is not used here; remove import to avoid extra deps

logger = logging.getLogger(__name__)


@dataclass
class GPUMemoryProfile:
    """GPU memory usage profile"""
    total_mb: float
    used_mb: float
    free_mb: float
    cached_mb: float
    utilization_percent: float

    @property
    def available_for_processing(self) -> float:
        """Calculate memory available for new processing"""
        return self.free_mb + (self.cached_mb * 0.5)  # 50% of cache can be evicted


@dataclass
class BatchSizeRecommendation:
    """Batch size recommendation with reasoning"""
    recommended_size: int
    max_safe_size: int
    estimated_vram_per_image: float
    confidence: str  # "high", "medium", "low"
    reasoning: str


class GPUOptimizer:
    """
    GPU optimization and resource management

    Provides dynamic batch sizing, memory profiling, and optimization utilities.
    """

    def __init__(self, target_utilization: float = 0.85):
        """
        Initialize GPU optimizer

        Args:
            target_utilization: Target GPU memory utilization (0.0-1.0)
        """
        self.target_utilization = target_utilization
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # Memory tracking
        self.memory_profiles: List[GPUMemoryProfile] = []
        self.batch_performance_history: Dict[int, List[float]] = {}

        # Configuration
        self.min_batch_size = 1
        self.max_batch_size = 10
        self.safety_margin_mb = 1024  # 1GB safety margin

        logger.info(f"[ORFEAS] GPU Optimizer initialized")
        logger.info(f"[ORFEAS] Target utilization: {target_utilization*100:.0f}%")

    def get_current_memory_profile(self) -> GPUMemoryProfile:
        """
        Get current GPU memory profile

        Returns:
            GPUMemoryProfile with current memory statistics
        """
        if not torch.cuda.is_available():
            return GPUMemoryProfile(
                total_mb=0,
                used_mb=0,
                free_mb=0,
                cached_mb=0,
                utilization_percent=0
            )

        # Get GPU memory info
        total = torch.cuda.get_device_properties(0).total_memory / (1024**2)  # MB
        allocated = torch.cuda.memory_allocated(0) / (1024**2)  # MB
        reserved = torch.cuda.memory_reserved(0) / (1024**2)  # MB
        free = total - reserved
        cached = reserved - allocated

        utilization = (reserved / total) * 100

        profile = GPUMemoryProfile(
            total_mb=total,
            used_mb=allocated,
            free_mb=free,
            cached_mb=cached,
            utilization_percent=utilization
        )

        # Store profile for trend analysis
        self.memory_profiles.append(profile)
        if len(self.memory_profiles) > 100:
            self.memory_profiles.pop(0)

        return profile

    def calculate_optimal_batch_size(
        self,
        image_size: Tuple[int, int] = (512, 512),
        inference_steps: int = 50,
        current_queue_size: int = 0
    ) -> BatchSizeRecommendation:
        """
        Calculate optimal batch size based on available GPU memory

        Args:
            image_size: Input image dimensions (width, height)
            inference_steps: Number of inference steps
            current_queue_size: Current number of jobs in queue

        Returns:
            BatchSizeRecommendation with optimal batch size and reasoning
        """
        profile = self.get_current_memory_profile()

        if not torch.cuda.is_available():
            return BatchSizeRecommendation(
                recommended_size=1,
                max_safe_size=1,
                estimated_vram_per_image=0,
                confidence="low",
                reasoning="No GPU available - using CPU fallback"
            )

        # Estimate VRAM per image (empirical formula)
        # Base: 2GB per image
        # Scale with image size and steps
        size_factor = (image_size[0] * image_size[1]) / (512 * 512)
        step_factor = inference_steps / 50
        estimated_vram_per_image = 2000 * size_factor * step_factor  # MB

        # Calculate available memory for batch processing
        available_memory = profile.available_for_processing - self.safety_margin_mb

        # Calculate max safe batch size
        max_safe_size = max(1, int(available_memory / estimated_vram_per_image))
        max_safe_size = min(max_safe_size, self.max_batch_size)

        # Calculate recommended size based on utilization target
        target_memory = profile.total_mb * self.target_utilization
        current_used = profile.used_mb
        memory_budget = target_memory - current_used - self.safety_margin_mb

        recommended_size = max(1, int(memory_budget / estimated_vram_per_image))
        recommended_size = min(recommended_size, max_safe_size)
        recommended_size = min(recommended_size, current_queue_size) if current_queue_size > 0 else recommended_size

        # Determine confidence based on historical data
        confidence = "high" if len(self.batch_performance_history) > 10 else "medium"
        if profile.utilization_percent > 90:
            confidence = "low"

        # Generate reasoning
        reasoning_parts = []
        reasoning_parts.append(f"Available: {available_memory:.0f}MB")
        reasoning_parts.append(f"Est. per image: {estimated_vram_per_image:.0f}MB")
        reasoning_parts.append(f"GPU utilization: {profile.utilization_percent:.1f}%")
        if current_queue_size > 0:
            reasoning_parts.append(f"Queue size: {current_queue_size}")

        reasoning = ", ".join(reasoning_parts)

        logger.info(f"[ORFEAS] Batch size recommendation: {recommended_size} ({reasoning})")

        return BatchSizeRecommendation(
            recommended_size=recommended_size,
            max_safe_size=max_safe_size,
            estimated_vram_per_image=estimated_vram_per_image,
            confidence=confidence,
            reasoning=reasoning
        )

    def record_batch_performance(self, batch_size: int, duration_seconds: float):
        """
        Record batch processing performance for learning

        Args:
            batch_size: Size of the batch
            duration_seconds: Time taken to process batch
        """
        if batch_size not in self.batch_performance_history:
            self.batch_performance_history[batch_size] = []

        self.batch_performance_history[batch_size].append(duration_seconds)

        # Keep only last 50 entries per batch size
        if len(self.batch_performance_history[batch_size]) > 50:
            self.batch_performance_history[batch_size].pop(0)

        # Calculate average
        avg_duration = sum(self.batch_performance_history[batch_size]) / len(self.batch_performance_history[batch_size])
        logger.info(f"[ORFEAS] Batch {batch_size}: {duration_seconds:.2f}s (avg: {avg_duration:.2f}s)")

    def optimize_cache(self):
        """
        Optimize GPU cache to free up memory

        This aggressively clears cached memory that can be freed.
        """
        if not torch.cuda.is_available():
            return

        profile_before = self.get_current_memory_profile()

        # Clear PyTorch cache
        torch.cuda.empty_cache()

        # Force garbage collection
        import gc
        gc.collect()

        # Synchronize to ensure cleanup is complete
        torch.cuda.synchronize()

        profile_after = self.get_current_memory_profile()

        freed_mb = profile_after.free_mb - profile_before.free_mb
        logger.info(f"[ORFEAS] Cache optimization: freed {freed_mb:.0f}MB")

    def get_memory_trends(self, window_size: int = 20) -> Dict[str, float]:
        """
        Analyze memory usage trends

        Args:
            window_size: Number of recent profiles to analyze

        Returns:
            Dict with trend statistics
        """
        if len(self.memory_profiles) < 2:
            return {
                "trend": "unknown",
                "avg_utilization": 0,
                "peak_utilization": 0,
                "stable": True
            }

        recent_profiles = self.memory_profiles[-window_size:]

        utilizations = [p.utilization_percent for p in recent_profiles]
        avg_utilization = sum(utilizations) / len(utilizations)
        peak_utilization = max(utilizations)
        min_utilization = min(utilizations)

        # Check stability (variance < 10%)
        variance = max(utilizations) - min(utilizations)
        stable = variance < 10

        # Determine trend
        if len(recent_profiles) >= 5:
            first_half_avg = sum(utilizations[:len(utilizations)//2]) / (len(utilizations)//2)
            second_half_avg = sum(utilizations[len(utilizations)//2:]) / (len(utilizations) - len(utilizations)//2)

            if second_half_avg > first_half_avg + 5:
                trend = "increasing"
            elif second_half_avg < first_half_avg - 5:
                trend = "decreasing"
            else:
                trend = "stable"
        else:
            trend = "unknown"

        return {
            "trend": trend,
            "avg_utilization": avg_utilization,
            "peak_utilization": peak_utilization,
            "min_utilization": min_utilization,
            "stable": stable,
            "variance": variance
        }

    def should_reduce_batch_size(self) -> bool:
        """
        Determine if batch size should be reduced based on memory pressure

        Returns:
            True if batch size should be reduced
        """
        profile = self.get_current_memory_profile()

        # Reduce if utilization > 95%
        if profile.utilization_percent > 95:
            logger.warning("[ORFEAS] High memory pressure - recommend reducing batch size")
            return True

        # Check trend - if rapidly increasing, reduce proactively
        trends = self.get_memory_trends()
        if trends["trend"] == "increasing" and trends["avg_utilization"] > 85:
            logger.warning("[ORFEAS] Memory trend increasing - recommend reducing batch size")
            return True

        return False

    def export_performance_report(self, output_path: str = "gpu_performance_report.json"):
        """
        Export performance report to JSON

        Args:
            output_path: Path to save report
        """
        report = {
            "device": str(self.device),
            "cuda_available": torch.cuda.is_available(),
            "current_profile": {
                "total_mb": self.memory_profiles[-1].total_mb if self.memory_profiles else 0,
                "used_mb": self.memory_profiles[-1].used_mb if self.memory_profiles else 0,
                "free_mb": self.memory_profiles[-1].free_mb if self.memory_profiles else 0,
                "utilization_percent": self.memory_profiles[-1].utilization_percent if self.memory_profiles else 0
            },
            "memory_trends": self.get_memory_trends(),
            "batch_performance": {
                str(batch_size): {
                    "count": len(durations),
                    "avg_duration": sum(durations) / len(durations),
                    "min_duration": min(durations),
                    "max_duration": max(durations)
                }
                for batch_size, durations in self.batch_performance_history.items()
            },
            "recommendations": {
                "target_utilization": self.target_utilization,
                "reduce_batch_size": self.should_reduce_batch_size()
            }
        }

        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)

        logger.info(f"[ORFEAS] Performance report exported to {output_path}")

        return report

    def get_optimization_recommendations(self) -> List[str]:
        """
        Get actionable optimization recommendations

        Returns:
            List of recommendation strings
        """
        recommendations = []

        profile = self.get_current_memory_profile()
        trends = self.get_memory_trends()

        # Memory-based recommendations
        if profile.utilization_percent < 60:
            recommendations.append("âš¡ GPU underutilized - increase batch size or concurrent jobs")
        elif profile.utilization_percent > 90:
            recommendations.append(" GPU near capacity - reduce batch size or concurrent jobs")

        # Cache recommendations
        if profile.cached_mb > 2000:  # > 2GB cached
            recommendations.append(" Large cache detected - run optimize_cache() to free memory")

        # Trend recommendations
        if trends["trend"] == "increasing" and not trends["stable"]:
            recommendations.append(" Memory usage increasing - monitor for potential leaks")

        # Batch size recommendations
        if self.batch_performance_history:
            # Find most efficient batch size
            avg_time_per_image = {}
            for batch_size, durations in self.batch_performance_history.items():
                avg_duration = sum(durations) / len(durations)
                avg_time_per_image[batch_size] = avg_duration / batch_size

            if avg_time_per_image:
                optimal_batch = min(avg_time_per_image, key=avg_time_per_image.get)
                recommendations.append(f" Optimal batch size appears to be {optimal_batch} based on performance history")

        return recommendations


# Singleton instance
_gpu_optimizer = None


def get_gpu_optimizer(target_utilization: float = 0.85) -> GPUOptimizer:
    """
    Get singleton GPU optimizer instance

    Args:
        target_utilization: Target GPU memory utilization (0.0-1.0)

    Returns:
        GPUOptimizer instance
    """
    global _gpu_optimizer
    if _gpu_optimizer is None:
        _gpu_optimizer = GPUOptimizer(target_utilization)
    return _gpu_optimizer


if __name__ == "__main__":
    # Standalone test
    print("=" * 80)
    print("ORFEAS GPU Optimizer - Standalone Test")
    print("=" * 80)

    optimizer = get_gpu_optimizer(target_utilization=0.85)

    # Test memory profiling
    print("\n1. Current Memory Profile:")
    profile = optimizer.get_current_memory_profile()
    print(f"   Total: {profile.total_mb:.0f}MB")
    print(f"   Used: {profile.used_mb:.0f}MB")
    print(f"   Free: {profile.free_mb:.0f}MB")
    print(f"   Utilization: {profile.utilization_percent:.1f}%")

    # Test batch size calculation
    print("\n2. Batch Size Recommendation:")
    recommendation = optimizer.calculate_optimal_batch_size(
        image_size=(512, 512),
        inference_steps=50,
        current_queue_size=8
    )
    print(f"   Recommended: {recommendation.recommended_size}")
    print(f"   Max Safe: {recommendation.max_safe_size}")
    print(f"   Est. VRAM/image: {recommendation.estimated_vram_per_image:.0f}MB")
    print(f"   Confidence: {recommendation.confidence}")
    print(f"   Reasoning: {recommendation.reasoning}")

    # Test recommendations
    print("\n3. Optimization Recommendations:")
    recommendations = optimizer.get_optimization_recommendations()
    for i, rec in enumerate(recommendations, 1):
        print(f"   {i}. {rec}")

    # Export report
    print("\n4. Exporting Performance Report...")
    report_path = "gpu_performance_report.json"
    optimizer.export_performance_report(report_path)
    print(f"   Report saved to: {report_path}")

    print("\n" + "=" * 80)
    print(" GPU Optimizer test complete!")
    print("=" * 80)
