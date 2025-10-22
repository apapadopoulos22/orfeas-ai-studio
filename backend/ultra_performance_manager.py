#!/usr/bin/env python3
"""
ORFEAS Ultra-Performance Manager - Module Alias
==============================================

This module provides backward compatibility for validation scripts
by aliasing ultra_performance_integration.py exports.

Usage:
    from backend.ultra_performance_manager import UltraPerformanceManager
"""

# Import and re-export from the main integration module
from .ultra_performance_integration import (
    UltraPerformanceManager,
    PerformanceTargets,
    SpeedOptimizationEngine,
    AccuracyEnhancementEngine,
    SecurityAmplificationEngine,
    ProblemSolvingEngine,
    PerformanceMonitor,
    UltraCacheManager,
    UltraSecurityManager
)

__all__ = [
    'UltraPerformanceManager',
    'PerformanceTargets',
    'SpeedOptimizationEngine',
    'AccuracyEnhancementEngine',
    'SecurityAmplificationEngine',
    'ProblemSolvingEngine',
    'PerformanceMonitor',
    'UltraCacheManager',
    'UltraSecurityManager'
]
