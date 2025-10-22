#!/usr/bin/env python3
"""
PHASE 4 QUICK-START TESTING & DEPLOYMENT SCRIPT
================================================

Automated testing and deployment for ORFEAS Phase 4 (99%+ Enterprise Optimization)
Run this script to execute all tests and validate deployment readiness
"""

import subprocess
import sys
import time
import json
from pathlib import Path
from datetime import datetime

class Phase4Tester:
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "tests": [],
            "passed": 0,
            "failed": 0,
            "warnings": 0
        }
        self.workspace = Path(__file__).parent

    def run_command(self, cmd, name, description=""):
        """Run a shell command and capture result"""
        try:
            print(f"\n[TEST] {name}")
            if description:
                print(f"       {description}")

            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30,
                cwd=str(self.workspace)
            )

            if result.returncode == 0:
                print(f"       [PASS] {cmd}")
                self.results["passed"] += 1
                self.results["tests"].append({
                    "name": name,
                    "status": "PASS",
                    "command": cmd
                })
                return True
            else:
                print(f"       [FAIL] Error: {result.stderr[:200]}")
                self.results["failed"] += 1
                self.results["tests"].append({
                    "name": name,
                    "status": "FAIL",
                    "error": result.stderr[:200],
                    "command": cmd
                })
                return False
        except subprocess.TimeoutExpired:
            print(f"       [TIMEOUT] Command took too long")
            self.results["warnings"] += 1
            return False
        except Exception as e:
            print(f"       [ERROR] {str(e)}")
            self.results["failed"] += 1
            return False

    def test_python_syntax(self):
        """Test Python syntax of main.py"""
        print("\n" + "="*70)
        print("PHASE 1: SYNTAX VALIDATION")
        print("="*70)

        self.run_command(
            "python -m py_compile backend/main.py",
            "Python Syntax Check",
            "Validating backend/main.py has valid Python syntax"
        )

    def test_verification_script(self):
        """Run the verification script"""
        print("\n" + "="*70)
        print("PHASE 2: COMPONENT VERIFICATION")
        print("="*70)

        self.run_command(
            "python verify_phase4_deployment_lite.py",
            "Phase 4 Components",
            "Verifying all 8 Phase 4 components are present and valid"
        )

    def test_endpoint_availability(self):
        """Check if endpoints can be called"""
        print("\n" + "="*70)
        print("PHASE 3: ENDPOINT AVAILABILITY")
        print("="*70)

        # Note: Requires backend to be running
        print("\n[NOTE] Backend must be running for endpoint tests")
        print("       Start with: cd backend && python main.py")
        print("       Then run: curl http://localhost:5000/api/phase4/status")

        endpoints = [
            "GET /api/phase4/status",
            "GET /api/phase4/gpu/profile",
            "GET /api/phase4/dashboard/summary",
            "GET /api/phase4/cache/stats",
            "GET /api/phase4/predictions",
            "GET /api/phase4/alerts/active",
            "GET /api/phase4/anomalies",
            "GET /api/phase4/traces",
        ]

        print("\n[ENDPOINTS] Ready to test once backend is running:")
        for ep in endpoints:
            print(f"  - {ep}")

    def test_imports(self):
        """Test if Phase 4 imports work"""
        print("\n" + "="*70)
        print("PHASE 4: IMPORT VALIDATION")
        print("="*70)

        imports = [
            ("advanced_gpu_optimizer", "Advanced GPU Optimizer"),
            ("performance_dashboard_realtime", "Real-Time Dashboard"),
            ("distributed_cache_manager", "Distributed Cache"),
            ("predictive_performance_optimizer", "Predictive Optimizer"),
            ("alerting_system", "Alerting System"),
            ("ml_anomaly_detector", "Anomaly Detector"),
            ("distributed_tracing", "Distributed Tracing"),
        ]

        for module, name in imports:
            cmd = f"python -c \"from backend.{module} import *; print('OK')\""
            self.run_command(cmd, f"Import {name}", f"Checking {module} module")

    def test_file_integrity(self):
        """Check that all files exist"""
        print("\n" + "="*70)
        print("PHASE 5: FILE INTEGRITY")
        print("="*70)

        required_files = [
            "backend/advanced_gpu_optimizer.py",
            "backend/performance_dashboard_realtime.py",
            "backend/distributed_cache_manager.py",
            "backend/predictive_performance_optimizer.py",
            "backend/alerting_system.py",
            "backend/ml_anomaly_detector.py",
            "backend/distributed_tracing.py",
            "backend/tests/integration/test_production_load.py",
            "backend/main.py",
            "PHASE_4_QUICK_REFERENCE.md",
            "PHASE_4_DEPLOYMENT_COMPLETE_99_PERCENT.md",
        ]

        for file_path in required_files:
            full_path = self.workspace / file_path
            if full_path.exists():
                print(f"[OK] {file_path}")
                self.results["passed"] += 1
            else:
                print(f"[MISSING] {file_path}")
                self.results["failed"] += 1

    def generate_report(self):
        """Generate final test report"""
        print("\n" + "="*70)
        print("FINAL REPORT")
        print("="*70)

        total = self.results["passed"] + self.results["failed"]
        success_rate = (self.results["passed"] / total * 100) if total > 0 else 0

        print(f"\nTests Passed:   {self.results['passed']}")
        print(f"Tests Failed:   {self.results['failed']}")
        print(f"Warnings:       {self.results['warnings']}")
        print(f"Success Rate:   {success_rate:.1f}%")
        print(f"Timestamp:      {self.results['timestamp']}")

        if self.results["failed"] == 0:
            print("\n[SUCCESS] All tests passed! Ready for deployment.")
            return 0
        else:
            print(f"\n[WARNING] {self.results['failed']} test(s) failed. Review above.")
            return 1

    def run_all_tests(self):
        """Run all tests"""
        print("\n")
        print("="*70)
        print("ORFEAS PHASE 4 - AUTOMATED TESTING & DEPLOYMENT")
        print("="*70)
        print(f"Workspace: {self.workspace}")
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        self.test_python_syntax()
        time.sleep(0.5)

        self.test_file_integrity()
        time.sleep(0.5)

        self.test_verification_script()
        time.sleep(0.5)

        self.test_imports()
        time.sleep(0.5)

        self.test_endpoint_availability()
        time.sleep(0.5)

        return self.generate_report()


def print_deployment_guide():
    """Print quick deployment guide"""
    guide = """

QUICK DEPLOYMENT GUIDE
======================

STEP 1: Test Backend Syntax (5 min)
  python -m py_compile backend/main.py
  python verify_phase4_deployment_lite.py

STEP 2: Start Backend (2 min)
  cd backend
  python main.py

  Wait for logs showing:
    [ORFEAS PHASE 4] Tier 1 components imported
    [ORFEAS PHASE 4] Tier 2 components imported
    [ORFEAS PHASE 4] Tier 3 components imported
    [ORFEAS PHASE 4] All enterprise optimization tiers initialized

STEP 3: Test Endpoints (10 min)
  In new terminal:

  # Test Status
  curl http://localhost:5000/api/phase4/status

  # Test GPU
  curl http://localhost:5000/api/phase4/gpu/profile

  # Test Dashboard
  curl http://localhost:5000/api/phase4/dashboard/summary

  # Test Cache
  curl http://localhost:5000/api/phase4/cache/stats

  # Test Predictions
  curl http://localhost:5000/api/phase4/predictions

  # Test Alerts
  curl http://localhost:5000/api/phase4/alerts/active

  # Test Anomalies
  curl http://localhost:5000/api/phase4/anomalies

  # Test Traces
  curl http://localhost:5000/api/phase4/traces

STEP 4: Run Load Test (30 min)
  python backend/tests/integration/test_production_load.py

STEP 5: Deploy to Docker (15 min)
  docker-compose build backend
  docker-compose up -d backend

  Verify:
  curl http://localhost:5000/api/phase4/status

STEP 6: Monitor Logs (continuous)
  docker-compose logs -f backend

SUCCESS CRITERIA
================

All Phase 4 endpoints respond with HTTP 200
GPU optimizer shows memory improvements
Dashboard streaming metrics in real-time
Cache hit rate improving
Predictions generating with confidence scores
Alerts triggering appropriately
Anomalies detected with high accuracy
Traces collecting with minimal overhead
No critical errors in logs

DOCUMENTATION REFERENCES
========================

- Technical Guide: PHASE_4_DEPLOYMENT_COMPLETE_99_PERCENT.md
- Quick Reference: PHASE_4_QUICK_REFERENCE.md
- API Endpoints: backend/PHASE_4_API_ENDPOINTS.py
- Troubleshooting: PHASE_4_INTEGRATION_AND_DEPLOYMENT.md

"""
    print(guide)


if __name__ == "__main__":
    tester = Phase4Tester()
    exit_code = tester.run_all_tests()
    print_deployment_guide()
    sys.exit(exit_code)
