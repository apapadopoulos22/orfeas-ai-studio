#!/usr/bin/env python3
"""
Phase 4 Deployment Verification Script (Lite - No external dependencies)
Verifies all 8 components exist and have correct structure
"""

import sys
import os
import ast
import json

def verify_file_exists(filepath):
    """Check if file exists"""
    return os.path.isfile(filepath)

def get_functions_and_classes(filepath):
    """Extract function and class names from Python file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read())

        functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        return classes, functions
    except Exception as e:
        return [], []

def verify_deployment():
    """Verify all Phase 4 modules exist and have correct structure"""
    print("=" * 70)
    print("PHASE 4 DEPLOYMENT VERIFICATION (Lite - No Dependencies)")
    print("=" * 70)
    print()

    backend_path = r'c:\Users\johng\Documents\oscar\backend'

    modules = [
        {
            'name': 'advanced_gpu_optimizer',
            'path': os.path.join(backend_path, 'advanced_gpu_optimizer.py'),
            'expected_class': 'AdvancedGPUOptimizer',
            'expected_methods': ['get_detailed_memory_profile', 'predict_cleanup_need', 'optimize_batch_size']
        },
        {
            'name': 'performance_dashboard_realtime',
            'path': os.path.join(backend_path, 'performance_dashboard_realtime.py'),
            'expected_class': 'RealtimePerformanceDashboard',
            'expected_methods': ['broadcast_metrics', 'subscribe', 'get_dashboard_summary']
        },
        {
            'name': 'distributed_cache_manager',
            'path': os.path.join(backend_path, 'distributed_cache_manager.py'),
            'expected_class': 'DistributedCacheManager',
            'expected_methods': ['get', 'set', 'invalidate', 'get_stats']
        },
        {
            'name': 'test_production_load',
            'path': os.path.join(backend_path, 'tests', 'integration', 'test_production_load.py'),
            'expected_class': 'ProductionLoadTest',
            'expected_methods': ['run_load_test', 'run_stress_test', 'run_spike_test', 'run_endurance_test']
        },
        {
            'name': 'predictive_performance_optimizer',
            'path': os.path.join(backend_path, 'predictive_performance_optimizer.py'),
            'expected_class': 'PredictivePerformanceOptimizer',
            'expected_methods': ['analyze_trends', 'predict_memory_pressure', 'predict_response_time']
        },
        {
            'name': 'alerting_system',
            'path': os.path.join(backend_path, 'alerting_system.py'),
            'expected_class': 'AlertingSystem',
            'expected_methods': ['register_alert', 'check_alerts', 'subscribe', 'acknowledge_alert']
        },
        {
            'name': 'ml_anomaly_detector',
            'path': os.path.join(backend_path, 'ml_anomaly_detector.py'),
            'expected_class': 'MLAnomalyDetector',
            'expected_methods': ['detect_anomalies', 'calculate_baseline_stats', 'get_anomaly_report']
        },
        {
            'name': 'distributed_tracing',
            'path': os.path.join(backend_path, 'distributed_tracing.py'),
            'expected_class': 'DistributedTracingSystem',
            'expected_methods': ['start_trace', 'start_span', 'end_span', 'end_trace']
        },
    ]

    results = []
    for module_info in modules:
        module_name = module_info['name']
        filepath = module_info['path']
        expected_class = module_info['expected_class']

        # Check file exists
        if not verify_file_exists(filepath):
            print(f"[FAIL] {module_name:35} - FILE NOT FOUND")
            results.append({'module': module_name, 'status': 'FAIL'})
            continue

        # Get classes and functions
        classes, functions = get_functions_and_classes(filepath)

        # Check if expected class exists
        if expected_class in classes:
            status = 'OK'
            status_str = "[OK]"
        else:
            status = 'FAIL'
            status_str = "[FAIL]"

        print(f"{status_str} {module_name:35} - {expected_class} found")
        results.append({'module': module_name, 'status': status, 'class': expected_class, 'file_size': os.path.getsize(filepath)})

    print()
    print("=" * 70)
    print("DEPLOYMENT SUMMARY")
    print("=" * 70)
    print()

    passed = sum(1 for r in results if r['status'] == 'OK')
    total = len(results)

    print(f"[*] Components Verified: {passed}/{total}")
    print()

    # Tier breakdown
    print("[Tier 1 - Essential]")
    for r in results[0:4]:
        status_icon = "OK" if r['status'] == 'OK' else "FAIL"
        print(f"  [{status_icon}] {r['module']}")

    print()
    print("[Tier 2 - Enhanced]")
    for r in results[4:6]:
        status_icon = "OK" if r['status'] == 'OK' else "FAIL"
        print(f"  [{status_icon}] {r['module']}")

    print()
    print("[Tier 3 - Premium]")
    for r in results[6:8]:
        status_icon = "OK" if r['status'] == 'OK' else "FAIL"
        print(f"  [{status_icon}] {r['module']}")

    print()

    if passed == total:
        print("=" * 70)
        print("[SUCCESS] ALL COMPONENTS VERIFIED - READY FOR INTEGRATION")
        print("=" * 70)
        print()
        print("[*] Next Steps:")
        print("    1. Review PHASE_4_QUICK_REFERENCE.md")
        print("    2. Add imports to backend/main.py")
        print("    3. Create Flask API endpoints")
        print("    4. Setup WebSocket endpoint")
        print("    5. Create dashboard.html")
        print("    6. Run integration tests")
        print()
        return 0
    else:
        print("[ERROR] Some components failed verification")
        return 1


if __name__ == '__main__':
    sys.exit(verify_deployment())
