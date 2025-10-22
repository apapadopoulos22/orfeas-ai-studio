"""
Profile Hunyuan3D Initialization - Memory and Time Analysis
"""
import cProfile
import pstats
import sys
import os
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

def profile_hunyuan_init() -> None:
    """Profile Hunyuan3D initialization"""
    print("=" * 80)
    print("PROFILING HUNYUAN3D INITIALIZATION")
    print("=" * 80)

    # Profile the initialization
    profiler = cProfile.Profile()

    profiler.enable()

    try:
        from hunyuan_integration import Hunyuan3DProcessor
        processor = Hunyuan3DProcessor()
        print(f"\n[OK] Initialization complete")
    except Exception as e:
        print(f"\n[ERROR] Initialization failed: {e}")
        import traceback
        traceback.print_exc()

    profiler.disable()

    # Save stats
    profiler.dump_stats('profile_stats.prof')

    # Print top 30 functions by cumulative time
    print("\n" + "=" * 80)
    print("TOP 30 FUNCTIONS BY CUMULATIVE TIME")
    print("=" * 80)

    stats = pstats.Stats('profile_stats.prof')
    stats.sort_stats('cumulative')
    stats.print_stats(30)

    print("\n" + "=" * 80)
    print("TOP 30 FUNCTIONS BY TOTAL TIME")
    print("=" * 80)

    stats.sort_stats('tottime')
    stats.print_stats(30)

if __name__ == "__main__":
    profile_hunyuan_init()
