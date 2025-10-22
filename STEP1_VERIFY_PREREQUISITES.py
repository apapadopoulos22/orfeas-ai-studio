#!/usr/bin/env python3
"""
STEP 1 - VERIFY PREREQUISITES
Monday Phase 1 GPU Integration - Startup Verification
"""

import sys
import subprocess
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

print("=" * 70)
print("STEP 1 - VERIFY PREREQUISITES FOR MONDAY PHASE 1")
print("=" * 70)

# Track results
checks_passed = 0
checks_failed = 0

# ============================================================================
# CHECK 1: Python Version
# ============================================================================
print("\n[Check 1] Python Version")
try:
    version_info = sys.version_info
    version_str = f"{version_info.major}.{version_info.minor}.{version_info.micro}"
    if version_info.major >= 3 and version_info.minor >= 10:
        print(f"✓ Python {version_str} (PASS - meets requirement 3.10+)")
        checks_passed += 1
    else:
        print(f"✗ Python {version_str} (FAIL - need 3.10+)")
        checks_failed += 1
except Exception as e:
    print(f"✗ Error checking Python version: {e}")
    checks_failed += 1

# ============================================================================
# CHECK 2: PyTorch and CUDA
# ============================================================================
print("\n[Check 2] PyTorch and CUDA")
try:
    import torch
    print(f"✓ PyTorch {torch.__version__}")
    cuda_available = torch.cuda.is_available()
    if cuda_available:
        print(f"✓ CUDA Available: True")
        device_count = torch.cuda.device_count()
        print(f"✓ GPU Devices: {device_count}")
        if device_count > 0:
            device_name = torch.cuda.get_device_name(0)
            print(f"✓ GPU Device 0: {device_name}")
            total_memory = torch.cuda.get_device_properties(0).total_memory / 1e9
            print(f"✓ Total GPU Memory: {total_memory:.1f} GB")
        checks_passed += 1
    else:
        print("✗ CUDA Not Available")
        checks_failed += 1
except ImportError:
    print("✗ PyTorch not installed")
    checks_failed += 1
except Exception as e:
    print(f"✗ Error checking PyTorch: {e}")
    checks_failed += 1

# ============================================================================
# CHECK 3: GPU Optimization Module
# ============================================================================
print("\n[Check 3] GPU Optimization Module")
try:
    from gpu_optimization_advanced import (
        get_vram_manager,
        PrecisionMode,
        DynamicVRAMManager
    )
    print(f"✓ gpu_optimization_advanced imports successfully")

    # Try to initialize manager
    mgr = get_vram_manager()
    print(f"✓ VRAM Manager initialized: {type(mgr).__name__}")

    # Get memory stats
    stats = mgr.get_memory_stats()
    print(f"✓ Memory stats retrieved:")
    print(f"  - Total VRAM: {stats.get('total_vram_gb', 'N/A'):.1f} GB")
    print(f"  - Available: {stats.get('available_gb', 'N/A'):.1f} GB")
    print(f"  - Usage: {stats.get('usage_percent', 'N/A'):.1f}%")

    checks_passed += 1
except ImportError as e:
    print(f"✗ Cannot import gpu_optimization_advanced: {e}")
    checks_failed += 1
except Exception as e:
    print(f"✗ Error with GPU module: {e}")
    checks_failed += 1

# ============================================================================
# CHECK 4: Project Files
# ============================================================================
print("\n[Check 4] Project Files")
project_root = Path(__file__).parent
backend_dir = project_root / "backend"
files_to_check = [
    ("main.py", "Flask application entry point"),
    ("gpu_optimization_advanced.py", "GPU optimization module"),
]

files_ok = True
for filename, description in files_to_check:
    filepath = backend_dir / filename
    if filepath.exists():
        size_kb = filepath.stat().st_size / 1024
        print(f"✓ {filename} ({size_kb:.1f} KB) - {description}")
    else:
        print(f"✗ {filename} NOT FOUND - {description}")
        files_ok = False

if files_ok:
    checks_passed += 1
else:
    checks_failed += 1

# ============================================================================
# CHECK 5: Flask and Dependencies
# ============================================================================
print("\n[Check 5] Flask and Core Dependencies")
required_packages = [
    'flask',
    'flask_cors',
    'flask_socketio',
    'torch',
    'numpy',
]

deps_ok = True
for pkg in required_packages:
    try:
        __import__(pkg)
        print(f"✓ {pkg} installed")
    except ImportError:
        print(f"✗ {pkg} NOT installed")
        deps_ok = False

if deps_ok:
    checks_passed += 1
else:
    checks_failed += 1

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "=" * 70)
print("PREREQUISITE VERIFICATION SUMMARY")
print("=" * 70)
print(f"\nTotal Checks: {checks_passed + checks_failed}")
print(f"Passed: {checks_passed}")
print(f"Failed: {checks_failed}")

if checks_failed == 0:
    print("\n✓ ALL CHECKS PASSED - READY FOR MONDAY PHASE 1")
    print("\n📋 NEXT STEPS:")
    print("  1. Review MONDAY_MORNING_BRIEF.md")
    print("  2. Open backend/main.py in editor")
    print("  3. Start TASK 1.1 - Import GPU Module (10 min)")
    print("  4. Follow MONDAY_PHASE_1_STARTUP.md step-by-step")
    sys.exit(0)
else:
    print(f"\n✗ {checks_failed} CHECK(S) FAILED - CANNOT PROCEED")
    print("\nPlease fix the issues above before starting Monday Phase 1")
    sys.exit(1)
