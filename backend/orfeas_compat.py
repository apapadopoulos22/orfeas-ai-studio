from typing import Any

"""
ORFEAS Compatibility Wrapper
Handles package conflicts and provides safe imports
"""

import sys
import warnings
import logging
from pathlib import Path

# Suppress specific warnings
warnings.filterwarnings("ignore", category=UserWarning, module="torch")
warnings.filterwarnings("ignore", category=FutureWarning, module="transformers")

class CompatibilityWrapper:
    def __init__(self) -> None:
        self.fallback_imports = {}
        self.setup_fallbacks()
    
    def setup_fallbacks(self) -> None:
        """Setup fallback imports for problematic packages"""
        self.fallback_imports = {
            "open3d": self.safe_open3d_import,
            "cv2": self.safe_opencv_import,
            "trimesh": self.safe_trimesh_import
        }
    
    def safe_open3d_import(self) -> None:
        """Safe Open3D import with fallbacks"""
        try:
            import open3d as o3d
            return o3d
        except ImportError as e:
            print(f"[WARN] Open3D not available: {e}")
            return self.create_open3d_mock()
    
    def safe_opencv_import(self) -> None:
        """Safe OpenCV import with fallbacks"""
        opencv_variants = ["cv2", "opencv-python", "opencv-contrib-python"]
        
        for variant in opencv_variants:
            try:
                import cv2
                return cv2
            except ImportError:
                continue
        
        print("[WARN] OpenCV not available, using PIL fallback")
        return self.create_opencv_mock()
    
    def safe_trimesh_import(self) -> None:
        """Safe Trimesh import"""
        try:
            import trimesh
            return trimesh
        except ImportError as e:
            print(f"[WARN] Trimesh not available: {e}")
            return self.create_trimesh_mock()
    
    def create_open3d_mock(self) -> None:
        """Create Open3D mock for basic functionality"""
        class Open3DMock:
            def __init__(self) -> None:
                pass
            
            def read_point_cloud(self, *args, **kwargs) -> None:
                raise NotImplementedError("Open3D not available - install with: pip install open3d")
            
            def write_point_cloud(self, *args, **kwargs) -> None:
                raise NotImplementedError("Open3D not available")
        
        return Open3DMock()
    
    def create_opencv_mock(self) -> int:
        """Create OpenCV mock using PIL"""
        class OpenCVMock:
            def imread(self, path: str) -> None:
                from PIL import Image
                import numpy as np
                img = Image.open(path)
                return np.array(img)
            
            def imwrite(self, path: str, img: Any) -> int:
                from PIL import Image
                Image.fromarray(img).save(path)
                return True
        
        return OpenCVMock()
    
    def create_trimesh_mock(self) -> None:
        """Create basic Trimesh mock"""
        class TrimeshMock:
            def load(self, *args, **kwargs) -> None:
                raise NotImplementedError("Trimesh not available - install with: pip install trimesh")
        
        return TrimeshMock()
    
    def safe_import(self, package_name: Any) -> None:
        """Safely import a package with fallbacks"""
        if package_name in self.fallback_imports:
            return self.fallback_imports[package_name]()
        
        try:
            return __import__(package_name)
        except ImportError as e:
            print(f"[WARN] {package_name} import failed: {e}")
            return None

# Global compatibility instance
compat = CompatibilityWrapper()

# Provide safe import functions
def safe_import_open3d() -> None:
    return compat.safe_open3d_import()

def safe_import_opencv() -> None:
    return compat.safe_opencv_import()

def safe_import_trimesh() -> None:
    return compat.safe_trimesh_import()
