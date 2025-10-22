#!/usr/bin/env python3
"""
Simple Performance Benchmark - Avoids Unicode Issues
"""

import time
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / 'backend'))

try:
    print("[BENCH] Loading cache module...")
    from cache_manager import LRUCache
    print("[OK] Cache loaded")

    print("[BENCH] Loading ultra-performance module...")
    from ultra_performance_integration import UltraPerformanceManager
    print("[OK] Ultra-performance loaded")

except ImportError as e:
    print(f"[ERROR] Failed to import: {e}")
    sys.exit(1)

def run_cache_benchmark():
    """Benchmark cache performance"""
    print("\n[BENCH] === CACHE PERFORMANCE BENCHMARK ===")

    cache = LRUCache(max_items=100, max_memory_mb=50.0)

    # Test 1: Get performance
    start = time.time()
    for i in range(10000):
        cache.get('test_key')
    get_time = time.time() - start
    get_latency_ms = (get_time / 10000) * 1000

    print(f"[CACHE] Get operations (10k): {get_time:.4f}s")
    print(f"[CACHE] Get latency: {get_latency_ms:.6f}ms per operation")

    # Test 2: Set performance
    start = time.time()
    for i in range(1000):
        cache.set(f'key_{i}', {'data': 'x' * 1000})
    set_time = time.time() - start
    set_latency_ms = (set_time / 1000) * 1000

    print(f"[CACHE] Set operations (1k): {set_time:.4f}s")
    print(f"[CACHE] Set latency: {set_latency_ms:.4f}ms per operation")

    return {
        'get_latency_ms': get_latency_ms,
        'set_latency_ms': set_latency_ms,
        'status': 'OK'
    }

def run_ultra_performance_benchmark():
    """Benchmark ultra-performance"""
    print("\n[BENCH] === ULTRA-PERFORMANCE BENCHMARK ===")

    try:
        manager = UltraPerformanceManager()

        # Test speed optimizer
        print("[PERF] Testing speed optimizer...")
        speed_result = manager.optimize_speed(
            input_data={'data': 'test'} * 100,
            target_speedup=100.0
        )
        print(f"[PERF] Speed improvement: {speed_result.get('improvement', 'N/A')}x")

        # Test accuracy enhancer
        print("[PERF] Testing accuracy enhancer...")
        accuracy_result = manager.enhance_accuracy(
            model_output={'prediction': 0.95},
            enhancement_level=100.0
        )
        print(f"[PERF] Accuracy enhancement: {accuracy_result.get('enhancement', 'N/A')}x")

        # Test security amplifier
        print("[PERF] Testing security amplifier...")
        security_result = manager.amplify_security(
            encryption_level=1.0,
            amplification_target=10.0
        )
        print(f"[PERF] Security amplification: {security_result.get('amplification', 'N/A')}x")

        return {
            'speed': speed_result,
            'accuracy': accuracy_result,
            'security': security_result,
            'status': 'OK'
        }
    except Exception as e:
        print(f"[ERROR] Ultra-performance test failed: {e}")
        return {'status': 'FAILED', 'error': str(e)}

def main():
    """Run all benchmarks"""
    print("=" * 60)
    print("[BENCH] ORFEAS SIMPLE PERFORMANCE BENCHMARK")
    print("=" * 60)

    results = {
        'timestamp': time.time(),
        'cache': None,
        'ultra_performance': None
    }

    # Run cache benchmark
    try:
        results['cache'] = run_cache_benchmark()
    except Exception as e:
        print(f"[ERROR] Cache benchmark failed: {e}")
        results['cache'] = {'status': 'FAILED', 'error': str(e)}

    # Run ultra-performance benchmark
    try:
        results['ultra_performance'] = run_ultra_performance_benchmark()
    except Exception as e:
        print(f"[ERROR] Ultra-performance benchmark failed: {e}")
        results['ultra_performance'] = {'status': 'FAILED', 'error': str(e)}

    # Summary
    print("\n" + "=" * 60)
    print("[SUMMARY] BENCHMARK RESULTS")
    print("=" * 60)
    print(f"[CACHE] Get latency: {results['cache'].get('get_latency_ms', 'N/A'):.6f}ms")
    print(f"[CACHE] Set latency: {results['cache'].get('set_latency_ms', 'N/A'):.4f}ms")
    print(f"[PERF] Speed optimization: {results['ultra_performance'].get('speed', {}).get('improvement', 'N/A')}x")
    print(f"[PERF] Accuracy enhancement: {results['ultra_performance'].get('accuracy', {}).get('enhancement', 'N/A')}x")
    print(f"[PERF] Security amplification: {results['ultra_performance'].get('security', {}).get('amplification', 'N/A')}x")
    print("[BENCH] Benchmark complete!")
    print("=" * 60)

if __name__ == '__main__':
    main()
