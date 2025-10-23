"""
ORFEAS AI 2D→3D Studio - RTX 3090 Optimization Module
==================================================
Lightweight, production-safe RTX optimization utilities.

Goals:
- Enable safe CUDA/cuDNN knobs (TF32, benchmarks) on Ampere (RTX 3090)
- Avoid hard dependency on torch when unavailable (TESTING/CPU-only)
- Optional TensorRT presence detection without import side effects
- Simple VRAM/performance stats for health/metrics endpoints

This module is intentionally minimal and defensive. It should import cleanly
in CI/TESTING environments without torch or CUDA present.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# Optional torch import (kept None if not installed); all accesses are guarded
try:  # pragma: no cover - torch may be missing in CI
    import torch  # type: ignore
except Exception:  # pragma: no cover
    torch = None  # type: ignore


class RTXOptimizer:
    """Safe RTX 3090 optimization facade.

    Exposes convenience toggles and stats with strict guards to work on
    CPU-only and TESTING environments.
    """

    def __init__(self, vram_limit: float = 0.8) -> None:
        self.vram_limit = max(0.1, min(0.99, vram_limit))
        self._trt_available: Optional[bool] = None

    # -------- Capability checks --------
    @property
    def cuda_available(self) -> bool:
        return bool(
            torch and getattr(torch, "cuda", None) and hasattr(torch.cuda, "is_available") and torch.cuda.is_available()  # type: ignore[attr-defined]
        )

    @property
    def device_name(self) -> str:
        if not self.cuda_available:
            return "cpu"
        try:
            return str(torch.cuda.get_device_name(0))  # type: ignore[attr-defined]
        except Exception:
            return "cuda"

    # -------- Core toggles --------
    def enable_mixed_precision(self) -> bool:
        """Enable TF32 for matmul/cuDNN on Ampere+ if CUDA is available."""
        if not self.cuda_available:
            logger.info("CUDA not available; skipping mixed precision toggles")
            return False
        try:
            torch.backends.cuda.matmul.allow_tf32 = True  # type: ignore[attr-defined]
            torch.backends.cudnn.allow_tf32 = True  # type: ignore[attr-defined]
            logger.info("TF32 enabled (matmul + cuDNN)")
            return True
        except Exception as e:  # pragma: no cover
            logger.warning(f"Failed enabling TF32: {e}")
            return False

    def enable_cudnn_benchmark(self) -> bool:
        if not self.cuda_available:
            return False
        try:
            torch.backends.cudnn.benchmark = True  # type: ignore[attr-defined]
            torch.backends.cudnn.deterministic = False  # type: ignore[attr-defined]
            logger.info("cuDNN benchmark enabled; deterministic off")
            return True
        except Exception as e:  # pragma: no cover
            logger.warning(f"Failed configuring cuDNN benchmark: {e}")
            return False

    def set_memory_fraction(self) -> bool:
        if not self.cuda_available:
            return False
        try:
            torch.cuda.set_per_process_memory_fraction(self.vram_limit)  # type: ignore[attr-defined]
            logger.info(f"Set CUDA per-process memory fraction to {self.vram_limit}")
            return True
        except Exception as e:  # pragma: no cover
            logger.warning(f"Could not set memory fraction: {e}")
            return False

    def empty_cache(self) -> None:
        if self.cuda_available:
            try:
                torch.cuda.empty_cache()  # type: ignore[attr-defined]
                torch.cuda.synchronize()  # type: ignore[attr-defined]
            except Exception:  # pragma: no cover
                pass

    # -------- Optional TensorRT presence --------
    @property
    def tensorrt_available(self) -> bool:
        if self._trt_available is not None:
            return self._trt_available
        try:  # pragma: no cover - optional
            import tensorrt as _trt  # noqa: F401

            self._trt_available = True
        except Exception:
            self._trt_available = False
        return self._trt_available

    # -------- Model helpers --------
    def optimize_model_for_inference(self, model: Any) -> Any:
        """Apply safe RTX-oriented toggles to a torch model if possible."""
        if not model:
            return model
        self.enable_mixed_precision()
        self.enable_cudnn_benchmark()
        self.set_memory_fraction()
        # We do not forcibly half() the model here; caller can choose.
        return model

    # -------- Stats --------
    def get_vram_stats(self) -> Dict[str, float]:
        if not self.cuda_available:
            return {"total_gb": 0.0, "allocated_gb": 0.0, "reserved_gb": 0.0, "free_gb": 0.0}
        try:
            total = float(torch.cuda.get_device_properties(0).total_memory) / 1024 ** 3  # type: ignore[attr-defined]
            allocated = float(torch.cuda.memory_allocated()) / 1024 ** 3  # type: ignore[attr-defined]
            reserved = float(torch.cuda.memory_reserved()) / 1024 ** 3  # type: ignore[attr-defined]
            free = max(0.0, total - allocated)
            return {
                "total_gb": round(total, 3),
                "allocated_gb": round(allocated, 3),
                "reserved_gb": round(reserved, 3),
                "free_gb": round(free, 3),
            }
        except Exception as e:  # pragma: no cover
            logger.warning(f"Failed to read VRAM stats: {e}")
            return {"total_gb": 0.0, "allocated_gb": 0.0, "reserved_gb": 0.0, "free_gb": 0.0}

    def get_performance_stats(self) -> Dict[str, Any]:
        return {
            "cuda": self.cuda_available,
            "device": self.device_name,
            "tensorrt": self.tensorrt_available,
            "vram": self.get_vram_stats(),
        }


# Global singleton compatible with project patterns
_rtx_opt_instance: Optional[RTXOptimizer] = None


def get_rtx_optimizer() -> RTXOptimizer:
    global _rtx_opt_instance
    if _rtx_opt_instance is None:
        _rtx_opt_instance = RTXOptimizer()
    return _rtx_opt_instance


def initialize_rtx_optimizations() -> Dict[str, bool]:
    """Initialize toggles early in app startup.

    Returns a dict for quick diagnostics/health endpoints.
    """
    opt = get_rtx_optimizer()
    return {
        "cuda": opt.cuda_available,
        "mixed_precision": opt.enable_mixed_precision(),
        "cudnn_benchmark": opt.enable_cudnn_benchmark(),
        "memory_fraction": opt.set_memory_fraction(),
        "tensorrt": False,  # Disabled: TensorRT import causes hang on Windows
    }


__all__ = ["RTXOptimizer", "get_rtx_optimizer", "initialize_rtx_optimizations"]
