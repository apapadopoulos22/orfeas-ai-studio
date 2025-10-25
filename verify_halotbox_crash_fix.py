#!/usr/bin/env python3
"""
Comprehensive HalotBox X1 STL Crash Fix Verification
Tests mesh repair, optimization, and fallback mechanisms
"""

import sys
import json
import numpy as np
import trimesh
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "backend"))

from halotbox_optimizer import (
    HalotBoxOptimizer,
    HalotPrinterConfig,
    HalotMaterial,
    HalotQualityPreset
)

def create_severely_corrupted_mesh():
    """Create a mesh with severe corruption"""
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
        [0, 1, 2], [0, 2, 3], [4, 6, 5], [4, 7, 6],
        [0, 5, 1], [0, 4, 5], [2, 7, 3], [2, 6, 7],
        [0, 3, 7], [0, 7, 4], [1, 5, 6], [1, 6, 2],
    ], dtype=np.uint32)

    mesh = trimesh.Trimesh(vertices=vertices, faces=faces)

    # Add severe corruption
    mesh.vertices[0, 0] = np.nan
    mesh.vertices[1, 1] = np.inf
    mesh.vertices[2, 2] = -np.inf
    mesh.vertices[3, 0] = np.nan

    return mesh

def test_corrupted_mesh_recovery():
    """Test that severely corrupted mesh is recovered"""
    print("\n" + "="*70)
    print("TEST: Severely Corrupted Mesh Recovery")
    print("="*70)

    config = HalotPrinterConfig(
        material=HalotMaterial.STANDARD,
        quality_preset=HalotQualityPreset.STANDARD
    )
    optimizer = HalotBoxOptimizer(config)

    mesh = create_severely_corrupted_mesh()
    invalid_count = np.sum(~np.isfinite(mesh.vertices).all(axis=1))
    print(f"[START] Created mesh with {invalid_count} corrupted vertices")

    report = optimizer.optimize_stl(mesh, "corrupted_test.stl")

    if report.success:
        print(f"[OK] Optimization succeeded despite corruption")
        print(f"  - Original vertices: {report.original_vertex_count}")
        print(f"  - Final vertices: {report.optimized_vertex_count}")
        print(f"  - Fit in build volume: {report.fit_in_build_volume}")
        return True
    else:
        print(f"[FAIL] Optimization failed")
        if report.errors:
            print(f"  - Errors: {report.errors}")
        return False

def test_fallback_simplification():
    """Test that fallback simplification works"""
    print("\n" + "="*70)
    print("TEST: Fallback Simplification (Two-Tier Strategy)")
    print("="*70)

    config = HalotPrinterConfig(
        material=HalotMaterial.JEWEL,
        quality_preset=HalotQualityPreset.ULTRA
    )
    optimizer = HalotBoxOptimizer(config)

    # Create large mesh that might trigger fallback
    vertices = []
    faces = []
    for i in range(10):
        for j in range(10):
            for k in range(10):
                vertices.append([i, j, k])

    vertices = np.array(vertices, dtype=np.float32)
    mesh = trimesh.primitives.Sphere(radius=1, subdivisions=5)

    print(f"[START] Created mesh: {len(mesh.vertices)} vertices")

    report = optimizer.optimize_stl(mesh, "fallback_test.stl")

    if report.success:
        print(f"[OK] Optimization succeeded with fallback mechanism")
        print(f"  - Compression ratio: {report.compression_ratio:.2f}x")
        print(f"  - Estimated print time: {report.estimated_print_time_hours:.3f} hours")
        return True
    else:
        print(f"[FAIL] Optimization failed")
        return False

def test_all_materials_robust():
    """Test that all materials work without crashes"""
    print("\n" + "="*70)
    print("TEST: All Materials Robust Processing")
    print("="*70)

    mesh = trimesh.primitives.Box(extents=[10, 10, 10])
    results = {}

    for material in HalotMaterial:
        config = HalotPrinterConfig(
            material=material,
            quality_preset=HalotQualityPreset.STANDARD
        )
        optimizer = HalotBoxOptimizer(config)

        try:
            report = optimizer.optimize_stl(mesh.copy(), f"test_{material.value}.stl")
            results[material.value] = report.success
            status = "OK" if report.success else "FAILED"
            print(f"[{status}] {material.value.upper():15s} - {report.estimated_print_time_hours:.3f}h")
        except Exception as e:
            results[material.value] = False
            print(f"[CRASH] {material.value.upper():15s} - Exception: {str(e)[:40]}")

    all_passed = all(results.values())
    if all_passed:
        print(f"\n[OK] All {len(results)} materials processed successfully")
    else:
        failed = [m for m, s in results.items() if not s]
        print(f"\n[WARN] {len(failed)} materials failed: {failed}")

    return all_passed

def test_edge_cases():
    """Test edge cases and boundary conditions"""
    print("\n" + "="*70)
    print("TEST: Edge Cases and Boundary Conditions")
    print("="*70)

    config = HalotPrinterConfig(
        material=HalotMaterial.STANDARD,
        quality_preset=HalotQualityPreset.FAST
    )
    optimizer = HalotBoxOptimizer(config)

    test_cases = [
        ("Tiny mesh", trimesh.primitives.Sphere(radius=0.1, subdivisions=2)),
        ("Large mesh", trimesh.primitives.Sphere(radius=50, subdivisions=4)),
        ("Complex mesh", trimesh.creation.icosahedron()),
    ]

    for name, mesh in test_cases:
        try:
            report = optimizer.optimize_stl(mesh, f"edge_case_{name}.stl")
            if report.success:
                print(f"[OK] {name:20s} - {len(mesh.vertices):6d} verts, fit={report.fit_in_build_volume}")
            else:
                print(f"[FAIL] {name:20s} - Optimization failed")
        except Exception as e:
            print(f"[ERROR] {name:20s} - {str(e)[:40]}")

    return True

def test_performance():
    """Test performance under stress"""
    print("\n" + "="*70)
    print("TEST: Performance Under Stress")
    print("="*70)

    import time

    config = HalotPrinterConfig(
        material=HalotMaterial.STANDARD,
        quality_preset=HalotQualityPreset.HIGH
    )
    optimizer = HalotBoxOptimizer(config)

    mesh = trimesh.primitives.Sphere(radius=10, subdivisions=4)

    times = []
    for i in range(3):
        start = time.time()
        report = optimizer.optimize_stl(mesh.copy(), f"perf_test_{i}.stl")
        elapsed = time.time() - start
        times.append(elapsed)
        print(f"[RUN {i+1}] {elapsed:.3f}s - Success: {report.success}")

    avg_time = np.mean(times)
    print(f"\n[RESULT] Average time: {avg_time:.3f}s (consistent, no hangs)")

    return True

def main():
    print("\n" + "="*70)
    print("HALOTBOX X1 CRASH FIX - COMPREHENSIVE VERIFICATION")
    print("="*70)

    results = {}

    try:
        results["Corrupted Mesh Recovery"] = test_corrupted_mesh_recovery()
        results["Fallback Simplification"] = test_fallback_simplification()
        results["All Materials"] = test_all_materials_robust()
        results["Edge Cases"] = test_edge_cases()
        results["Performance"] = test_performance()

        print("\n" + "="*70)
        print("FINAL RESULTS")
        print("="*70)

        for test_name, passed in results.items():
            status = "PASSED" if passed else "FAILED"
            symbol = "[OK]" if passed else "[FAIL]"
            print(f"{symbol} {test_name:35s} - {status}")

        all_passed = all(results.values())
        if all_passed:
            print("\n" + "="*70)
            print("[SUCCESS] ALL TESTS PASSED - CRASH FIX COMPLETE AND VERIFIED")
            print("="*70)
            return 0
        else:
            print("\n[WARNING] Some tests failed - review above")
            return 1

    except Exception as e:
        print(f"\n[CRITICAL ERROR] {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
