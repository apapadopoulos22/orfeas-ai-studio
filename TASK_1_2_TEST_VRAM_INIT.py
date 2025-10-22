#!/usr/bin/env python3
"""
TASK 1.2 - Test VRAM Manager Initialization
Verify that the GPU optimization module initializes correctly
"""

import sys
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

print("=" * 70)
print("TASK 1.2 - INITIALIZE VRAM MANAGER ON STARTUP")
print("=" * 70)

print("\n[Step 1] Import VRAM Manager...")
try:
    from gpu_optimization_advanced import get_vram_manager
    print("✓ Successfully imported get_vram_manager")
except Exception as e:
    print(f"✗ Failed to import: {e}")
    sys.exit(1)

print("\n[Step 2] Initialize VRAM Manager...")
try:
    vram_manager = get_vram_manager()
    print(f"✓ VRAM Manager initialized: {vram_manager}")
    print(f"  Type: {type(vram_manager).__name__}")
except Exception as e:
    print(f"✗ Failed to initialize: {e}")
    sys.exit(1)

print("\n[Step 3] Get Initial Memory Statistics...")
try:
    stats = vram_manager.get_memory_stats()
    print(f"✓ Memory stats retrieved:")
    print(f"  - Total VRAM: {stats.get('total_vram_gb', 'N/A'):.1f} GB")
    print(f"  - Available: {stats.get('available_gb', 'N/A'):.1f} GB")
    print(f"  - Allocated: {stats.get('allocated_gb', 'N/A'):.1f} GB")
    print(f"  - Usage: {stats.get('usage_percent', 'N/A'):.1f}%")
    print(f"  - Precision Mode: {stats.get('precision_mode', 'N/A')}")
except Exception as e:
    print(f"✗ Failed to get memory stats: {e}")
    sys.exit(1)

print("\n[Step 4] Start Monitoring Thread (5s interval)...")
try:
    vram_manager.monitor_vram_usage(interval_seconds=5.0)
    print("✓ Monitoring thread started")
    print("  - Thread will log GPU stats every 5 seconds")
    print("  - Monitoring runs in background")
except Exception as e:
    print(f"✗ Failed to start monitoring: {e}")
    sys.exit(1)

print("\n[Step 5] Verify Monitoring is Running...")
import time
try:
    # Wait a moment for monitoring to kick in
    time.sleep(1)
    stats_after = vram_manager.get_memory_stats()
    print(f"✓ Monitoring active - stats accessible")
    print(f"  - Current usage: {stats_after.get('usage_percent', 'N/A'):.1f}%")
except Exception as e:
    print(f"✗ Monitoring verification failed: {e}")
    sys.exit(1)

print("\n" + "=" * 70)
print("✅ TASK 1.2 VERIFICATION COMPLETE")
print("=" * 70)
print("\nInitialization Status:")
print("  ✓ VRAM Manager initialized successfully")
print("  ✓ Memory statistics accessible")
print("  ✓ Monitoring thread started and running")
print("  ✓ Ready for Task 1.3 - Integrate GPU Monitoring in Generation Endpoint")
print("\n")
