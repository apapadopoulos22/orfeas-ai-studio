"""
ORFEAS Backend - Safe Start Script
===================================
ORFEAS DEBUGGING_TROUBLESHOOTING_SPECIALIST

This script starts the backend in SAFE_FALLBACK mode to avoid
loading issues with Hunyuan3D models.

Usage:
    python start_safe.py
"""

import os
import sys

# Set environment to SAFE_FALLBACK mode
os.environ['ORFEAS_MODE'] = 'safe_fallback'  # Correct environment variable name
os.environ['ORFEAS_PORT'] = '5000'  # Use port 5000 consistently

print("\n" + "="*80)
print("[SHIELD] ORFEAS BACKEND - SAFE START MODE")
print("="*80)
print("\n[CONFIG] Configuration:")
print("   • Mode: SAFE_FALLBACK (no Hunyuan3D loading)")
print("   • Port: 5000")
print("   • CORS: Enabled (*)")
print("\n" + "="*80 + "\n")

# Import and run main server
try:
    from main import main
    main()
except KeyboardInterrupt:
    print("\n\n[WARN]  Server stopped by user")
    sys.exit(0)
except Exception as e:
    print(f"\n\n[FAIL] Server failed to start: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
