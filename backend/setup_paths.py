"""
ORFEAS Python Path Setup
Configures Python paths for Hunyuan3D imports
"""

import sys
import os
from pathlib import Path

def setup_hunyuan_paths() -> int:
    """Setup Python paths for Hunyuan3D imports"""
    base_dir = Path(__file__).parent.parent
    hunyuan_path = base_dir / "Hunyuan3D-2.1" / "Hunyuan3D-2"

    if hunyuan_path.exists():
        hunyuan_str = str(hunyuan_path)
        if hunyuan_str not in sys.path:
            sys.path.insert(0, hunyuan_str)
            print(f"[OK] Added Hunyuan3D path: {hunyuan_str}")
        else:
            print(f"[OK] Hunyuan3D path already in sys.path")
        return True
    else:
        print(f"[FAIL] Hunyuan3D directory not found: {hunyuan_path}")
        return False

def test_imports() -> None:
    """Test the Hunyuan3D imports"""
    try:
        setup_hunyuan_paths()

        # Test hy3dgen imports
        try:
            import hy3dgen
            print("[OK] hy3dgen imported successfully")
        except ImportError as e:
            print(f"[FAIL] hy3dgen import failed: {e}")

        try:
            from hy3dgen.rembg import BackgroundRemover
            print("[OK] hy3dgen.rembg imported successfully")
        except ImportError as e:
            print(f"[FAIL] hy3dgen.rembg import failed: {e}")

        try:
            from hy3dgen.shapegen import Hunyuan3DDiTFlowMatchingPipeline
            print("[OK] hy3dgen.shapegen imported successfully")
        except ImportError as e:
            print(f"[FAIL] hy3dgen.shapegen import failed: {e}")

    except Exception as e:
        print(f"[FAIL] Path setup failed: {e}")

if __name__ == "__main__":
    test_imports()
