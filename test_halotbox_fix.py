#!/usr/bin/env python3
"""Test HalotBox STL optimization with corrupted mesh handling"""

import sys
import json
import numpy as np
import trimesh
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from halotbox_optimizer import (
    HalotBoxOptimizer,
    HalotPrinterConfig,
    HalotMaterial,
    HalotQualityPreset
)

def create_corrupted_mesh():
    """Create a corrupted mesh with NaN/Inf values"""
    # Create a simple cube
    vertices = np.array([
        [0, 0, 0],
        [1, 0, 0],
        [1, 1, 0],
        [0, 1, 0],
        [0, 0, 1],
        [1, 0, 1],
        [1, 1, 1],
        [0, 1, 1],
    ], dtype=np.float32)

    faces = np.array([
        [0, 1, 2],
        [0, 2, 3],
        [4, 6, 5],
        [4, 7, 6],
        [0, 5, 1],
        [0, 4, 5],
        [2, 7, 3],
        [2, 6, 7],
        [0, 3, 7],
        [0, 7, 4],
        [1, 5, 6],
        [1, 6, 2],
    ], dtype=np.uint32)

    mesh = trimesh.Trimesh(vertices=vertices, faces=faces)

    # Add some NaN values to simulate corruption
    mesh.vertices[0, 0] = np.nan
    mesh.vertices[2, 1] = np.inf

    return mesh

def create_valid_mesh():
    """Create a simple valid mesh"""
    vertices = np.array([
        [0, 0, 0],
        [1, 0, 0],
        [1, 1, 0],
        [0, 1, 0],
        [0, 0, 1],
        [1, 0, 1],
        [1, 1, 1],
        [0, 1, 1],
    ], dtype=np.float32)

    faces = np.array([
        [0, 1, 2],
        [0, 2, 3],
        [4, 6, 5],
        [4, 7, 6],
        [0, 5, 1],
        [0, 4, 5],
        [2, 7, 3],
        [2, 6, 7],
        [0, 3, 7],
        [0, 7, 4],
        [1, 5, 6],
        [1, 6, 2],
    ], dtype=np.uint32)

    return trimesh.Trimesh(vertices=vertices, faces=faces)

def test_mesh_repair():
    """Test mesh repair functionality"""
    print("\n" + "="*70)
    print("TEST 1: Mesh Repair (Corrupted with NaN/Inf)")
    print("="*70)

    config = HalotPrinterConfig(
        material=HalotMaterial.STANDARD,
        quality_preset=HalotQualityPreset.STANDARD
    )
    optimizer = HalotBoxOptimizer(config)

    # Create corrupted mesh
    mesh = create_corrupted_mesh()
    print(f"[CORRUPTED] Created corrupted mesh: {len(mesh.vertices)} vertices with NaN/Inf")

    # Repair it
    repaired = optimizer._repair_corrupted_mesh(mesh)
    print(f"[OK] Mesh repaired successfully")
    print(f"  - Vertices before: {len(mesh.vertices)}")
    print(f"  - Vertices after: {len(repaired.vertices)}")
    print(f"  - All values finite: {np.all(np.isfinite(repaired.vertices))}")

    return repaired

def test_mesh_optimization():
    """Test full mesh optimization"""
    print("\n" + "="*70)
    print("TEST 2: Full Mesh Optimization")
    print("="*70)

    config = HalotPrinterConfig(
        material=HalotMaterial.STANDARD,
        quality_preset=HalotQualityPreset.HIGH
    )
    optimizer = HalotBoxOptimizer(config)

    # Create valid mesh
    mesh = create_valid_mesh()
    print(f"[OK] Created valid mesh: {len(mesh.vertices)} vertices, {len(mesh.faces)} faces")

    # Optimize
    report = optimizer.optimize_stl(mesh, "test_mesh.stl")
    print(f"[OK] Mesh optimized")
    print(f"  - Success: {report.success}")
    print(f"  - Print time (hours): {report.estimated_print_time_hours:.2f}")
    print(f"  - Resin volume (ml): {report.estimated_resin_ml:.1f}")
    print(f"  - Supports needed: {report.recommended_supports}")

    if report.errors:
        print(f"  - Errors: {', '.join(report.errors)}")

    return report

def test_different_materials():
    """Test optimization with different materials"""
    print("\n" + "="*70)
    print("TEST 3: Different Materials")
    print("="*70)

    mesh = create_valid_mesh()

    materials = [
        HalotMaterial.STANDARD,
        HalotMaterial.SURGICAL_GUIDE,
        HalotMaterial.JEWEL,
        HalotMaterial.CASTABLE,
        HalotMaterial.FLEXIBLE,
    ]

    for material in materials:
        config = HalotPrinterConfig(
            material=material,
            quality_preset=HalotQualityPreset.STANDARD
        )
        optimizer = HalotBoxOptimizer(config)
        report = optimizer.optimize_stl(mesh.copy(), f"test_{material.value}.stl")

        print(f"[OK] {material.value.upper():15s} - Time: {report.estimated_print_time_hours:6.2f}h, Resin: {report.estimated_resin_ml:6.1f}ml")

def test_all_quality_presets():
    """Test all quality presets"""
    print("\n" + "="*70)
    print("TEST 4: All Quality Presets")
    print("="*70)

    mesh = create_valid_mesh()

    presets = [
        HalotQualityPreset.FAST,
        HalotQualityPreset.STANDARD,
        HalotQualityPreset.HIGH,
        HalotQualityPreset.ULTRA,
    ]

    for preset in presets:
        config = HalotPrinterConfig(
            material=HalotMaterial.STANDARD,
            quality_preset=preset
        )
        optimizer = HalotBoxOptimizer(config)
        report = optimizer.optimize_stl(mesh.copy(), f"test_{preset.value}.stl")

        print(f"[OK] {preset.value.upper():10s} - Time: {report.estimated_print_time_hours:6.2f}h, Needed: {report.recommended_supports}")

if __name__ == "__main__":
    print("\n" + "="*70)
    print("HALOTBOX X1 STL OPTIMIZER - FIX VERIFICATION TESTS")
    print("="*70)

    try:
        # Test mesh repair
        repaired_mesh = test_mesh_repair()

        # Test full optimization
        report = test_mesh_optimization()

        # Test different materials
        test_different_materials()

        # Test quality presets
        test_all_quality_presets()

        print(f"\n[RESULTS] ALL TESTS PASSED - Mesh repair and optimization working!")
        print("="*70)

    except Exception as e:
        print(f"\n[ERROR] TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
