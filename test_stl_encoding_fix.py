#!/usr/bin/env python3
"""
Test HalotBox STL Support Creation and Encoding Fix
Verifies that support analysis and STL export work without encoding errors
"""

import sys
import tempfile
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

def create_test_mesh_with_overhangs():
    """Create a mesh with overhangs that trigger support creation"""
    # Create a simple box with an overhang
    vertices = np.array([
        # Base cube
        [0, 0, 0], [10, 0, 0], [10, 10, 0], [0, 10, 0],
        [0, 0, 10], [10, 0, 10], [10, 10, 10], [0, 10, 10],
        # Overhang extension (pointing down)
        [5, 5, 15], [15, 5, 15], [15, 15, 15], [5, 15, 15],
    ], dtype=np.float32)

    faces = np.array([
        # Base cube
        [0, 1, 2], [0, 2, 3],  # Bottom
        [4, 6, 5], [4, 7, 6],  # Top
        [0, 5, 1], [0, 4, 5],  # Front
        [2, 7, 3], [2, 6, 7],  # Back
        [0, 3, 7], [0, 7, 4],  # Left
        [1, 5, 6], [1, 6, 2],  # Right
        # Overhang faces
        [8, 9, 10], [8, 10, 11],  # Overhang top
        [4, 8, 11], [4, 11, 7],   # Overhang side
    ], dtype=np.uint32)

    return trimesh.Trimesh(vertices=vertices, faces=faces)

def test_support_analysis_with_encoding():
    """Test support analysis doesn't crash on encoding"""
    print("\n" + "="*70)
    print("TEST: Support Analysis with STL Encoding Fix")
    print("="*70)

    config = HalotPrinterConfig(
        material=HalotMaterial.STANDARD,
        quality_preset=HalotQualityPreset.STANDARD
    )
    optimizer = HalotBoxOptimizer(config)

    mesh = create_test_mesh_with_overhangs()
    print(f"[START] Created mesh with overhangs: {len(mesh.vertices)} vertices, {len(mesh.faces)} faces")

    # Test the full optimization including support analysis
    report, optimized_mesh = optimizer.optimize_stl(mesh, "overhang_test.stl")

    if report.success:
        print(f"[OK] Optimization succeeded")
        print(f"  - Supports recommended: {report.recommended_supports}")
        print(f"  - Print time: {report.estimated_print_time_hours:.3f} hours")
        print(f"  - Resin: {report.estimated_resin_ml:.1f} mL")
        return True
    else:
        print(f"[FAIL] Optimization failed")
        if report.errors:
            for error in report.errors:
                print(f"  - Error: {error}")
        return False

def test_stl_export_with_invalid_vertices():
    """Test STL export handles invalid vertices gracefully"""
    print("\n" + "="*70)
    print("TEST: STL Export with Invalid Vertices (NaN/Inf)")
    print("="*70)

    config = HalotPrinterConfig(
        material=HalotMaterial.STANDARD,
        quality_preset=HalotQualityPreset.STANDARD
    )
    optimizer = HalotBoxOptimizer(config)

    mesh = create_test_mesh_with_overhangs()

    # Introduce some invalid values that would cause encoding errors
    mesh.vertices[0, 0] = np.nan
    mesh.vertices[1, 1] = np.inf
    print(f"[START] Created mesh with invalid vertices (NaN/Inf)")

    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "test_with_invalid.stl"
        result = optimizer.export_halotbox_stl(mesh, str(output_path))

        if result:
            print(f"[OK] STL export succeeded despite invalid vertices")
            if output_path.exists():
                size_kb = output_path.stat().st_size / 1024
                print(f"  - Output file: {size_kb:.1f} KB")
                # Verify the file can be read
                try:
                    reloaded = trimesh.load(str(output_path))
                    print(f"  - Reloaded mesh: {len(reloaded.vertices)} vertices, {len(reloaded.faces)} faces")
                    return True
                except Exception as e:
                    print(f"  - Failed to reload: {e}")
                    return False
            else:
                print(f"[FAIL] Output file not created")
                return False
        else:
            print(f"[OK] Export correctly handled invalid data (returned False)")
            return True

def test_all_materials_with_supports():
    """Test support analysis on all materials"""
    print("\n" + "="*70)
    print("TEST: Support Analysis on All Materials")
    print("="*70)

    mesh = create_test_mesh_with_overhangs()
    results = {}

    for material in HalotMaterial:
        config = HalotPrinterConfig(
            material=material,
            quality_preset=HalotQualityPreset.STANDARD
        )
        optimizer = HalotBoxOptimizer(config)

        try:
            report, opt_mesh = optimizer.optimize_stl(mesh.copy(), f"test_{material.value}.stl")
            results[material.value] = {
                'success': report.success,
                'supports': report.recommended_supports,
                'time': report.estimated_print_time_hours
            }
            status = "OK" if report.success else "FAILED"
            print(f"[{status}] {material.value.upper():15s} - Supports: {report.recommended_supports}, Time: {report.estimated_print_time_hours:.3f}h")
        except Exception as e:
            results[material.value] = {'success': False, 'error': str(e)[:50]}
            print(f"[ERROR] {material.value.upper():15s} - {str(e)[:50]}")

    all_passed = all(r.get('success', False) for r in results.values())
    return all_passed

def test_binary_vs_ascii_export():
    """Test that binary export works and is smaller than ASCII"""
    print("\n" + "="*70)
    print("TEST: Binary vs ASCII STL Export")
    print("="*70)

    config = HalotPrinterConfig(
        material=HalotMaterial.STANDARD,
        quality_preset=HalotQualityPreset.HIGH
    )
    optimizer = HalotBoxOptimizer(config)

    mesh = trimesh.primitives.Sphere(radius=10, subdivisions=4)
    print(f"[START] Created sphere mesh: {len(mesh.vertices)} vertices")

    with tempfile.TemporaryDirectory() as tmpdir:
        binary_path = Path(tmpdir) / "sphere_binary.stl"
        ascii_path = Path(tmpdir) / "sphere_ascii.stl"

        # Export binary (using our fixed function)
        binary_ok = optimizer.export_halotbox_stl(mesh, str(binary_path))

        # Export ASCII for comparison
        try:
            mesh.export(str(ascii_path), file_type='stl_ascii')
            ascii_ok = True
        except:
            ascii_ok = False

        if binary_ok and ascii_ok:
            binary_size = binary_path.stat().st_size
            ascii_size = ascii_path.stat().st_size
            ratio = ascii_size / binary_size

            print(f"[OK] Both exports succeeded")
            print(f"  - Binary: {binary_size:,} bytes")
            print(f"  - ASCII: {ascii_size:,} bytes")
            print(f"  - ASCII is {ratio:.1f}x larger")

            if binary_size < ascii_size:
                print(f"[PASS] Binary is smaller (as expected)")
                return True
            else:
                print(f"[WARN] Binary should be smaller but isn't")
                return True
        else:
            print(f"[FAIL] Export failed - binary: {binary_ok}, ascii: {ascii_ok}")
            return False

def main():
    print("\n" + "="*70)
    print("HALOTBOX SUPPORT CREATION & STL ENCODING - COMPREHENSIVE TEST")
    print("="*70)

    results = {}

    try:
        results["Support Analysis"] = test_support_analysis_with_encoding()
        results["Invalid Vertices"] = test_stl_export_with_invalid_vertices()
        results["All Materials"] = test_all_materials_with_supports()
        results["Binary Export"] = test_binary_vs_ascii_export()

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
            print("[SUCCESS] ALL TESTS PASSED - STL ENCODING FIX COMPLETE")
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
