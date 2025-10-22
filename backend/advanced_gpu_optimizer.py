"""
Advanced GPU Memory Optimization - Phase 4 Tier 1
Implements dynamic memory allocation, fragmentation handling, and predictive cleanup
Enhanced with performance profiling and intelligent batch sizing
"""

import torch
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
import threading
import psutil

logger = logging.getLogger(__name__)


@dataclass
class MemoryProfile:
    """GPU memory profile snapshot"""
    total_mb: float
    allocated_mb: float
    reserved_mb: float
    free_mb: float
    fragmentation_ratio: float
    timestamp: datetime
    pressure_level: str  # "low", "medium", "high", "critical"
    cpu_percent: float = 0.0
    system_memory_mb: float = 0.0


class AdvancedGPUOptimizer:
    """Advanced GPU memory optimizer with predictive cleanup and batch optimization"""

    def __init__(self, device: str = 'cuda', warning_threshold: float = 0.8):
        """Initialize GPU optimizer"""
        self.device = device
        self.warning_threshold = warning_threshold
        self.memory_history: List[MemoryProfile] = []
        self.cleanup_events: List[Dict] = []
        self.fragmentation_stats = {'max': 0.0, 'avg': 0.0, 'samples': 0}
        self._lock = threading.Lock()
        self.optimization_config = {
            'max_history_samples': 500,
            'fragmentation_warning_threshold': 0.30,
            'memory_pressure_threshold': 0.85,
            'critical_threshold': 0.95
        }

    def get_detailed_memory_profile(self) -> MemoryProfile:
        """Get comprehensive memory profile with fragmentation analysis"""
        if not torch.cuda.is_available():
            return MemoryProfile(
                total_mb=0, allocated_mb=0, reserved_mb=0,
                free_mb=0, fragmentation_ratio=0.0,
                timestamp=datetime.now(), pressure_level='none'
            )

        with self._lock:
            try:
                # GPU Memory stats
                props = torch.cuda.get_device_properties(0)
                total_memory = props.total_memory / 1e6  # Convert to MB

                # Get detailed memory stats
                reserved = torch.cuda.memory_reserved() / 1e6
                allocated = torch.cuda.memory_allocated() / 1e6
                free_in_reserved = reserved - allocated
                free_total = total_memory - reserved

                # Calculate fragmentation ratio
                if reserved > 0:
                    fragmentation_ratio = (reserved - allocated) / reserved
                else:
                    fragmentation_ratio = 0.0

                # Update fragmentation statistics
                self.fragmentation_stats['max'] = max(
                    self.fragmentation_stats['max'], fragmentation_ratio
                )
                self.fragmentation_stats['samples'] += 1

                if self.fragmentation_stats['samples'] > 0:
                    self.fragmentation_stats['avg'] = (
                        (self.fragmentation_stats['avg'] * (self.fragmentation_stats['samples'] - 1) +
                         fragmentation_ratio) / self.fragmentation_stats['samples']
                    )

                # System metrics
                cpu_percent = psutil.cpu_percent(interval=0.1)
                system_memory = psutil.virtual_memory()
                system_memory_mb = system_memory.used / 1024 / 1024

                # Determine pressure level
                utilization = allocated / total_memory if total_memory > 0 else 0

                if utilization >= self.optimization_config['critical_threshold']:
                    pressure_level = 'critical'
                elif utilization >= self.optimization_config['memory_pressure_threshold']:
                    pressure_level = 'high'
                elif utilization >= 0.70:
                    pressure_level = 'medium'
                else:
                    pressure_level = 'low'

                profile = MemoryProfile(
                    total_mb=total_memory,
                    allocated_mb=allocated,
                    reserved_mb=reserved,
                    free_mb=free_total,
                    fragmentation_ratio=fragmentation_ratio,
                    timestamp=datetime.now(),
                    pressure_level=pressure_level,
                    cpu_percent=cpu_percent,
                    system_memory_mb=system_memory_mb
                )

                # Maintain history with max size
                self.memory_history.append(profile)
                if len(self.memory_history) > self.optimization_config['max_history_samples']:
                    self.memory_history.pop(0)

                logger.debug(
                    f"[GPU-OPT] Profile: {allocated:.0f}MB/{total_memory:.0f}MB ({utilization*100:.1f}%), "
                    f"Frag: {fragmentation_ratio:.2f}, Level: {pressure_level}"
                )

                return profile

            except Exception as e:
                logger.error(f"[GPU-OPT] Failed to get memory profile: {e}")
                return MemoryProfile(
                    total_mb=0, allocated_mb=0, reserved_mb=0,
                    free_mb=0, fragmentation_ratio=0.0,
                    timestamp=datetime.now(), pressure_level='error'
                )

    def predict_cleanup_need(self) -> Tuple[bool, str]:
        """Predict if cleanup will be needed in next operation"""
        if len(self.memory_history) < 3:
            return False, "insufficient_history"

        with self._lock:
            recent = self.memory_history[-3:]
            allocations = [p.allocated_mb for p in recent]

            # Check if allocation is increasing
            is_increasing = all(
                allocations[i] <= allocations[i+1]
                for i in range(len(allocations)-1)
            )

            latest = recent[-1]
            utilization_ratio = latest.allocated_mb / latest.total_mb if latest.total_mb > 0 else 0

            # Decision criteria
            should_cleanup = (
                is_increasing and
                utilization_ratio > 0.70 and
                latest.fragmentation_ratio > self.optimization_config['fragmentation_warning_threshold']
            )

            reason = ""
            if is_increasing:
                reason += "allocation_increasing,"
            if utilization_ratio > 0.70:
                reason += "high_utilization,"
            if latest.fragmentation_ratio > self.optimization_config['fragmentation_warning_threshold']:
                reason += "high_fragmentation"

            return should_cleanup, reason.rstrip(',')

    def aggressive_cleanup(self) -> Dict:
        """Perform aggressive multi-stage memory cleanup"""
        start_allocated = torch.cuda.memory_allocated() / 1e6 if torch.cuda.is_available() else 0

        try:
            with self._lock:
                # Stage 1: Clear GPU cache
                torch.cuda.empty_cache()
                logger.debug("[GPU-OPT] Stage 1: Cleared CUDA cache")

                # Stage 2: Synchronize GPU
                if torch.cuda.is_available():
                    torch.cuda.synchronize()
                logger.debug("[GPU-OPT] Stage 2: GPU synchronized")

                # Stage 3: Force Python garbage collection
                import gc
                gc.collect()
                logger.debug("[GPU-OPT] Stage 3: Garbage collection complete")

                # Stage 4: Additional GPU sync
                if torch.cuda.is_available():
                    torch.cuda.synchronize()

            end_allocated = torch.cuda.memory_allocated() / 1e6 if torch.cuda.is_available() else 0
            freed_mb = start_allocated - end_allocated

            event = {
                'timestamp': datetime.now(),
                'freed_mb': freed_mb,
                'before_mb': start_allocated,
                'after_mb': end_allocated,
                'efficiency': (freed_mb / start_allocated * 100) if start_allocated > 0 else 0
            }

            self.cleanup_events.append(event)

            logger.info(
                f"[GPU-OPT] Aggressive cleanup: freed {freed_mb:.1f}MB "
                f"({start_allocated:.0f}MB → {end_allocated:.0f}MB, "
                f"efficiency: {event['efficiency']:.1f}%)"
            )

            return {
                'success': True,
                'freed_mb': freed_mb,
                'before_mb': start_allocated,
                'after_mb': end_allocated,
                'efficiency_percent': event['efficiency']
            }

        except Exception as e:
            logger.error(f"[GPU-OPT] Cleanup failed: {e}")
            return {'success': False, 'error': str(e)}

    def optimize_batch_size(self, base_batch_size: int = 1, safety_margin: float = 0.15) -> int:
        """Dynamically optimize batch size based on available memory and pressure"""
        profile = self.get_detailed_memory_profile()

        if profile.pressure_level == 'critical':
            optimized_size = max(1, base_batch_size // 4)
        elif profile.pressure_level == 'high':
            optimized_size = max(1, base_batch_size // 2)
        elif profile.pressure_level == 'medium':
            optimized_size = base_batch_size
        else:  # low pressure
            # Safe increase with margin
            available_ratio = 1.0 - profile.fragmentation_ratio - safety_margin
            if available_ratio > 0.3:
                optimized_size = min(base_batch_size * 2, 64)
            else:
                optimized_size = base_batch_size

        logger.debug(
            f"[GPU-OPT] Batch size optimization: {base_batch_size} → {optimized_size} "
            f"(pressure: {profile.pressure_level})"
        )

        return optimized_size

    def get_optimization_report(self) -> Dict:
        """Generate comprehensive optimization report"""
        if not self.memory_history:
            return {
                'status': 'no_history',
                'message': 'Insufficient data for optimization report'
            }

        with self._lock:
            profiles = self.memory_history
            latest = profiles[-1]

            # Calculate trends
            if len(profiles) >= 2:
                utilizations = [
                    (p.allocated_mb / p.total_mb if p.total_mb > 0 else 0)
                    for p in profiles[-10:]
                ]
                if len(utilizations) > 1:
                    trend = 'increasing' if utilizations[-1] > utilizations[0] else 'stable'
                else:
                    trend = 'unknown'
            else:
                trend = 'unknown'

            # Calculate statistics
            allocations = [p.allocated_mb for p in profiles[-60:]]  # Last 60 samples
            if allocations:
                avg_allocation = sum(allocations) / len(allocations)
                max_allocation = max(allocations)
                min_allocation = min(allocations)
            else:
                avg_allocation = max_allocation = min_allocation = 0

            return {
                'timestamp': datetime.now().isoformat(),
                'current_profile': {
                    'total_mb': round(latest.total_mb, 2),
                    'allocated_mb': round(latest.allocated_mb, 2),
                    'reserved_mb': round(latest.reserved_mb, 2),
                    'free_mb': round(latest.free_mb, 2),
                    'utilization_percent': round((latest.allocated_mb / latest.total_mb * 100) if latest.total_mb > 0 else 0, 2),
                    'fragmentation_ratio': round(latest.fragmentation_ratio, 3),
                    'pressure_level': latest.pressure_level,
                    'cpu_percent': latest.cpu_percent,
                    'system_memory_mb': round(latest.system_memory_mb, 2)
                },
                'statistics': {
                    'avg_allocation_mb': round(avg_allocation, 2),
                    'max_allocation_mb': round(max_allocation, 2),
                    'min_allocation_mb': round(min_allocation, 2),
                    'fragmentation_stats': {
                        'max': round(self.fragmentation_stats['max'], 3),
                        'avg': round(self.fragmentation_stats['avg'], 3),
                        'samples': self.fragmentation_stats['samples']
                    }
                },
                'trend': trend,
                'cleanup_events': {
                    'total_count': len(self.cleanup_events),
                    'total_freed_mb': round(sum(e['freed_mb'] for e in self.cleanup_events), 2),
                    'avg_freed_mb': round(
                        sum(e['freed_mb'] for e in self.cleanup_events) / len(self.cleanup_events)
                        if self.cleanup_events else 0, 2
                    ),
                    'recent_events': [
                        {
                            'timestamp': e['timestamp'].isoformat(),
                            'freed_mb': round(e['freed_mb'], 2),
                            'efficiency_percent': round(e.get('efficiency', 0), 1)
                        }
                        for e in self.cleanup_events[-5:]
                    ]
                },
                'recommendations': self._get_recommendations(latest)
            }

    def _get_recommendations(self, profile: MemoryProfile) -> List[str]:
        """Generate optimization recommendations"""
        recommendations = []

        if profile.pressure_level == 'critical':
            recommendations.append("🔴 CRITICAL: Immediate cleanup required - memory exhaustion risk")
            recommendations.append("⚠️  Reduce batch size significantly (divide by 4)")
            recommendations.append("🔍 Check for memory leaks or unexpected allocations")

        elif profile.pressure_level == 'high':
            recommendations.append("🟠 HIGH: Consider proactive cleanup before next operation")
            recommendations.append("💡 Reduce batch size by 50% or enable memory pooling")

        elif profile.pressure_level == 'medium':
            recommendations.append("🟡 MEDIUM: Monitor closely - consider optimization if trend increases")

        if profile.fragmentation_ratio > 0.5:
            recommendations.append("⚠️  High fragmentation detected - implement memory pooling strategy")

        if profile.fragmentation_ratio > self.optimization_config['fragmentation_warning_threshold']:
            recommendations.append("💡 Fragmentation present - proactive cleanup recommended")

        if len(self.cleanup_events) > 20:
            recommendations.append("📊 Frequent cleanups detected - optimize allocation patterns")

        if profile.cpu_percent > 80:
            recommendations.append("🔥 CPU utilization high - may impact GPU operations")

        if not recommendations:
            recommendations.append("✅ Memory optimization running smoothly - no action needed")

        return recommendations

    def get_config(self) -> Dict:
        """Get current optimization configuration"""
        return self.optimization_config.copy()

    def set_config(self, config: Dict) -> None:
        """Update optimization configuration"""
        with self._lock:
            self.optimization_config.update(config)
            logger.info(f"[GPU-OPT] Configuration updated: {self.optimization_config}")


# Singleton access
_optimizer_instance: Optional[AdvancedGPUOptimizer] = None
_optimizer_lock = threading.Lock()


def get_advanced_gpu_optimizer() -> AdvancedGPUOptimizer:
    """Get or create singleton instance of GPU optimizer"""
    global _optimizer_instance
    if _optimizer_instance is None:
        with _optimizer_lock:
            if _optimizer_instance is None:
                _optimizer_instance = AdvancedGPUOptimizer()
                logger.info("[GPU-OPT] Advanced GPU Optimizer initialized")
    return _optimizer_instance


def reset_optimizer() -> None:
    """Reset optimizer instance (for testing)"""
    global _optimizer_instance
    with _optimizer_lock:
        _optimizer_instance = None
