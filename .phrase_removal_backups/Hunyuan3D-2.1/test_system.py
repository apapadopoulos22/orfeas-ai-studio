#!/usr/bin/env python3
"""
THERION AI 2D STUDIO - HUNYUAN3D 2.1 TEST SCRIPT
"""

import sys
import os
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "hy3dshape"))
sys.path.insert(0, str(project_root / "hy3dpaint"))

import torch
import requests
from PIL import Image
import time

def test_cuda():
    """Test CUDA availability"""
    print(" Testing CUDA...")
    if torch.cuda.is_available():
        gpu_count = torch.cuda.device_count()
        gpu_name = torch.cuda.get_device_name(0)
        vram_gb = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        print(f" CUDA Available: {gpu_count} GPU(s)")
        print(f" GPU: {gpu_name}")
        print(f" VRAM: {vram_gb:.1f}GB")
        return True
    else:
        print(" CUDA not available!")
        return False

def test_imports():
    """Test package imports"""
    print(" Testing imports...")
    
    try:
        from hy3dshape.pipelines import Hunyuan3DDiTFlowMatchingPipeline
        print(" Shape pipeline import successful")
    except ImportError as e:
        print(f" Shape pipeline import failed: {e}")
        return False
    
    try:
        from textureGenPipeline import Hunyuan3DPaintPipeline, Hunyuan3DPaintConfig
        print(" Paint pipeline import successful")
    except ImportError as e:
        print(f" Paint pipeline import failed: {e}")
        return False
    
    return True

def test_pipeline_loading():
    """Test pipeline loading"""
    print(" Testing pipeline loading...")
    
    try:
        from hy3dshape.pipelines import Hunyuan3DDiTFlowMatchingPipeline
        shape_pipeline = Hunyuan3DDiTFlowMatchingPipeline.from_pretrained(
            'tencent/Hunyuan3D-2.1',
            subfolder='hunyuan3d-dit-v2-1'
        )
        print(" Shape pipeline loaded successfully")
    except Exception as e:
        print(f" Shape pipeline loading failed: {e}")
        return False
    
    try:
        from textureGenPipeline import Hunyuan3DPaintPipeline, Hunyuan3DPaintConfig
        paint_config = Hunyuan3DPaintConfig(max_num_view=6, resolution=512)
        paint_pipeline = Hunyuan3DPaintPipeline(paint_config)
        print(" Paint pipeline loaded successfully")
    except Exception as e:
        print(f" Paint pipeline loading failed: {e}")
        return False
    
    return True

def test_api_server():
    """Test API server"""
    print(" Testing API server...")
    
    try:
        response = requests.get("http://localhost:8000/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f" API server responding: {data}")
            return True
        else:
            print(f" API server error: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f" API server not reachable: {e}")
    
    return False

if __name__ == "__main__":
    print(" THERION Hunyuan3D 2.1 Test Suite")
    print("=" * 50)
    
    success_count = 0
    total_tests = 4
    
    if test_cuda():
        success_count += 1
    
    if test_imports():
        success_count += 1
    
    if test_pipeline_loading():
        success_count += 1
    
    if test_api_server():
        success_count += 1
    
    print("=" * 50)
    print(f" Test Results: {success_count}/{total_tests} passed")
    
    if success_count == total_tests:
        print(" ALL TESTS PASSED!")
    else:
        print(" Some tests failed. Check the logs above.")
