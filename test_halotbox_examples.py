"""
HALOTBOX X1 OPTIMIZATION - QUICK TEST SCRIPT
=============================================

This script demonstrates how to use the HalotBox optimizer directly
from Python code.
"""

import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

import trimesh
import numpy as np
from halotbox_optimizer import (
    HalotBoxOptimizer,
    HalotPrinterConfig,
    HalotMaterial,
    HalotQualityPreset,
    optimize_for_halotbox
)


def create_test_mesh():
    """Create a simple test mesh (cube)"""
    vertices = np.array([
        [0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0],  # bottom
        [0, 0, 1], [1, 0, 1], [1, 1, 1], [0, 1, 1],  # top
    ]) * 10  # Scale to 10x10x10

    faces = np.array([
        # bottom
        [0, 1, 2], [0, 2, 3],
        # top
        [4, 6, 5], [4, 7, 6],
        # sides
        [0, 5, 1], [0, 4, 5],
        [1, 6, 2], [1, 5, 6],
        [2, 7, 3], [2, 6, 7],
        [3, 4, 0], [3, 7, 4],
    ])

    return trimesh.Trimesh(vertices=vertices, faces=faces)


def example_1_quick_optimization():
    """Example 1: Quick optimization with defaults"""
    print("\n" + "=" * 70)
    print("EXAMPLE 1: Quick Optimization (Defaults)")
    print("=" * 70)

    # Create test mesh
    mesh = create_test_mesh()
    print(f"Created test mesh: {len(mesh.vertices)} vertices, {len(mesh.faces)} faces")

    # Quick optimize
    report = optimize_for_halotbox(mesh, "test_cube.stl")

    print(f"\n✓ Optimization complete!")
    print(f"  Fit in build volume: {report.fit_in_build_volume}")
    print(f"  Needs supports: {report.recommended_supports}")
    print(f"  Est. print time: {report.estimated_print_time_hours:.1f} hours")
    print(f"  Est. resin: {report.estimated_resin_ml:.1f} mL")
    print(f"  Warnings: {len(report.warnings)}")
    print(f"  Processing time: {report.processing_time_sec:.3f}s")


def example_2_custom_material():
    """Example 2: Optimize for specific material"""
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Jewelry Material Optimization")
    print("=" * 70)

    mesh = create_test_mesh()

    # Custom config for jewelry
    config = HalotPrinterConfig(
        material=HalotMaterial.JEWEL,
        quality_preset=HalotQualityPreset.ULTRA
    )
    optimizer = HalotBoxOptimizer(config)

    report = optimizer.optimize_stl(mesh, "jewelry_ring.stl")

    print(f"\n✓ Jewelry optimization complete!")
    print(f"  Material: {config.material.value}")
    print(f"  Quality: {config.quality_preset.value}")

    # Get material profile
    profile = optimizer.get_material_profile()
    print(f"  Exposure time: {profile['exposure_time_ms']}ms")
    print(f"  Layer height: {profile['layer_height_mm']}mm")
    print(f"  Cure time: {profile['cure_time_sec']}s")


def example_3_surgical_guide():
    """Example 3: Medical/Surgical optimization"""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Surgical Guide Material")
    print("=" * 70)

    mesh = create_test_mesh()

    config = HalotPrinterConfig(
        material=HalotMaterial.SURGICAL_GUIDE,
        quality_preset=HalotQualityPreset.HIGH
    )
    optimizer = HalotBoxOptimizer(config)

    report = optimizer.optimize_stl(mesh, "surgical_guide.stl")

    print(f"\n✓ Surgical guide optimization complete!")
    print(f"  Material: {config.material.value}")
    print(f"  Min wall thickness required: {config.min_wall_thickness_mm}mm")
    print(f"  Fit in build volume: {report.fit_in_build_volume}")

    # Get profile
    profile = optimizer.get_material_profile()
    print(f"  Post-cure: {profile.get('notes', 'N/A')}")


def example_4_batch_optimization():
    """Example 4: Batch optimize multiple materials"""
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Batch Optimization (All Materials)")
    print("=" * 70)

    mesh = create_test_mesh()
    materials = [
        HalotMaterial.STANDARD,
        HalotMaterial.JEWEL,
        HalotMaterial.SURGICAL_GUIDE,
        HalotMaterial.CASTABLE,
    ]

    results = []
    for material in materials:
        config = HalotPrinterConfig(
            material=material,
            quality_preset=HalotQualityPreset.STANDARD
        )
        optimizer = HalotBoxOptimizer(config)
        report = optimizer.optimize_stl(mesh, f"test_{material.value}.stl")

        profile = optimizer.get_material_profile()
        results.append({
            'material': material.value,
            'exposure_ms': profile['exposure_time_ms'],
            'layer_mm': profile['layer_height_mm'],
            'print_time_h': report.estimated_print_time_hours,
            'resin_ml': report.estimated_resin_ml,
        })

    print("\nMaterial Comparison:")
    print(f"{'Material':<15} {'Exp(ms)':<10} {'Layer(mm)':<12} {'Time(h)':<10} {'Resin(mL)':<12}")
    print("-" * 60)
    for r in results:
        print(f"{r['material']:<15} {r['exposure_ms']:<10} {r['layer_mm']:<12} {r['print_time_h']:<10.1f} {r['resin_ml']:<12.1f}")


def example_5_quality_presets():
    """Example 5: Compare quality presets"""
    print("\n" + "=" * 70)
    print("EXAMPLE 5: Quality Preset Comparison")
    print("=" * 70)

    mesh = create_test_mesh()
    presets = [
        HalotQualityPreset.FAST,
        HalotQualityPreset.STANDARD,
        HalotQualityPreset.HIGH,
        HalotQualityPreset.ULTRA,
    ]

    results = []
    for preset in presets:
        config = HalotPrinterConfig(
            material=HalotMaterial.STANDARD,
            quality_preset=preset
        )
        optimizer = HalotBoxOptimizer(config)
        report = optimizer.optimize_stl(mesh, f"test_{preset.value}.stl")

        results.append({
            'preset': preset.value,
            'vertices': report.optimized_vertex_count,
            'faces': report.optimized_face_count,
            'print_time_h': report.estimated_print_time_hours,
        })

    print("\nQuality Preset Comparison:")
    print(f"{'Preset':<12} {'Vertices':<12} {'Faces':<12} {'Time(h)':<12}")
    print("-" * 50)
    for r in results:
        print(f"{r['preset']:<12} {r['vertices']:<12} {r['faces']:<12} {r['print_time_h']:<12.1f}")


def example_6_configuration_export():
    """Example 6: Export configuration as JSON"""
    print("\n" + "=" * 70)
    print("EXAMPLE 6: Configuration Export")
    print("=" * 70)

    config = HalotPrinterConfig(
        material=HalotMaterial.SURGICAL_GUIDE,
        quality_preset=HalotQualityPreset.HIGH
    )
    optimizer = HalotBoxOptimizer(config)

    json_config = optimizer.get_optimization_json()
    print("\nConfiguration (JSON):")
    print(json_config)

    # This can be saved to file and imported into HalotBox Program
    output_file = "halotbox_config.json"
    with open(output_file, 'w') as f:
        f.write(json_config)
    print(f"\n✓ Configuration saved to: {output_file}")


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("HALOTBOX X1 OPTIMIZER - TEST EXAMPLES")
    print("=" * 70)

    try:
        example_1_quick_optimization()
        example_2_custom_material()
        example_3_surgical_guide()
        example_4_batch_optimization()
        example_5_quality_presets()
        example_6_configuration_export()

        print("\n" + "=" * 70)
        print("✓ ALL EXAMPLES COMPLETED SUCCESSFULLY")
        print("=" * 70)

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
