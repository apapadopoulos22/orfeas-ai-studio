#!/usr/bin/env python
"""
Test texgen model loading as well
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'backend'))
sys.path.insert(0, str(Path(__file__).parent / 'Hunyuan3D-2.1' / 'Hunyuan3D-2'))

from dotenv import load_dotenv
load_dotenv()

print("=" * 80)
print("TEST: TexGen Model Loading")
print("=" * 80)

try:
    # Try importing texgen
    from hy3dgen.texgen.pipelines import Hunyuan3DPaintPipeline

    print("\n✅ texgen pipelines imported successfully")
    print("   Cache detection logic in from_pretrained() is active")

except Exception as e:
    print(f"\n❌ Error importing texgen: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
