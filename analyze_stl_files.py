#!/usr/bin/env python3
"""Analyze the working vs non-working STL files to understand the differences"""
import trimesh
import numpy as np
import sys

def analyze_stl(file_path, label):
    """Comprehensive STL file analysis"""
    print(f"\n{'=' * 80}")
    print(f"ANALYZING: {label}")
    print(f"File: {file_path}")
    print(f"{'=' * 80}")

    try:
        # Load the mesh
        mesh = trimesh.load(file_path)

        print(f"\n[BASIC INFO]")
        print(f"  Vertices: {len(mesh.vertices)}")
        print(f"  Faces: {len(mesh.faces)}")
        print(f"  Is watertight: {mesh.is_watertight}")
        print(f"  Is winding consistent: {mesh.is_winding_consistent}")
        print(f"  Volume: {mesh.volume:.2f} mm³")
        print(f"  Surface area: {mesh.area:.2f} mm²")

        print(f"\n[BOUNDING BOX]")
        bounds = mesh.bounds
        print(f"  Min: [{bounds[0][0]:.2f}, {bounds[0][1]:.2f}, {bounds[0][2]:.2f}]")
        print(f"  Max: [{bounds[1][0]:.2f}, {bounds[1][1]:.2f}, {bounds[1][2]:.2f}]")
        size = bounds[1] - bounds[0]
        print(f"  Size: {size[0]:.2f} x {size[1]:.2f} x {size[2]:.2f} mm")

        print(f"\n[VERTEX VALIDATION]")
        # Check for NaN/Inf
        has_nan = np.isnan(mesh.vertices).any()
        has_inf = np.isinf(mesh.vertices).any()
        print(f"  Contains NaN: {has_nan}")
        print(f"  Contains Inf: {has_inf}")

        if has_nan or has_inf:
            nan_count = np.isnan(mesh.vertices).sum()
            inf_count = np.isinf(mesh.vertices).sum()
            print(f"  NaN count: {nan_count}")
            print(f"  Inf count: {inf_count}")

        # Vertex range
        v_min = mesh.vertices.min(axis=0)
        v_max = mesh.vertices.max(axis=0)
        print(f"  Vertex range X: [{v_min[0]:.4f}, {v_max[0]:.4f}]")
        print(f"  Vertex range Y: [{v_min[1]:.4f}, {v_max[1]:.4f}]")
        print(f"  Vertex range Z: [{v_min[2]:.4f}, {v_max[2]:.4f}]")

        print(f"\n[FACE VALIDATION]")
        # Check face indices
        max_face_index = mesh.faces.max()
        num_vertices = len(mesh.vertices)
        print(f"  Max face index: {max_face_index}")
        print(f"  Number of vertices: {num_vertices}")

        if max_face_index >= num_vertices:
            print(f"  ❌ ERROR: Face indices exceed vertex count!")
            invalid_faces = (mesh.faces >= num_vertices).any(axis=1).sum()
            print(f"  Invalid faces: {invalid_faces}")
        else:
            print(f"  ✅ All face indices valid")

        print(f"\n[MESH QUALITY]")
        # Check for degenerate faces
        try:
            face_areas = mesh.area_faces
            zero_area_faces = (face_areas < 1e-10).sum()
            print(f"  Zero-area faces: {zero_area_faces}")
            print(f"  Min face area: {face_areas.min():.6f}")
            print(f"  Max face area: {face_areas.max():.2f}")
            print(f"  Avg face area: {face_areas.mean():.4f}")
        except Exception as e:
            print(f"  ⚠️  Could not compute face areas: {e}")

        # Check for duplicate vertices
        try:
            unique_vertices = len(np.unique(mesh.vertices, axis=0))
            duplicates = len(mesh.vertices) - unique_vertices
            print(f"  Duplicate vertices: {duplicates}")
        except Exception as e:
            print(f"  ⚠️  Could not check duplicates: {e}")

        print(f"\n[TOPOLOGY]")
        # Check edges
        try:
            edges = mesh.edges
            print(f"  Total edges: {len(edges)}")
            print(f"  Unique edges: {len(mesh.edges_unique)}")
        except Exception as e:
            print(f"  ⚠️  Could not compute edges: {e}")

        # Check for non-manifold edges
        try:
            if hasattr(mesh, 'is_volume'):
                print(f"  Is volume: {mesh.is_volume}")
        except Exception as e:
            print(f"  ⚠️  Could not check volume: {e}")

        print(f"\n[FILE FORMAT]")
        # Check if binary or ASCII
        with open(file_path, 'rb') as f:
            header = f.read(80)
            is_binary = not header.startswith(b'solid')
            print(f"  Format: {'Binary' if is_binary else 'ASCII'}")
            if is_binary:
                f.seek(80)
                num_triangles = int.from_bytes(f.read(4), 'little')
                print(f"  Triangles (from header): {num_triangles}")
                print(f"  Triangles (actual): {len(mesh.faces)}")
                if num_triangles != len(mesh.faces):
                    print(f"  ⚠️  Triangle count mismatch!")

        print(f"\n[SUPPORT ANALYSIS]")
        # Estimate support requirements
        try:
            # Find faces that point downward (need supports)
            face_normals = mesh.face_normals
            downward_faces = face_normals[:, 2] < -0.5  # Z component < -0.5
            support_faces = downward_faces.sum()
            support_percentage = (support_faces / len(mesh.faces)) * 100
            print(f"  Faces needing supports: {support_faces} ({support_percentage:.1f}%)")

            # Find overhangs
            overhang_angle = 45  # degrees
            overhang_threshold = np.cos(np.radians(90 - overhang_angle))
            overhangs = face_normals[:, 2] < overhang_threshold
            overhang_count = overhangs.sum()
            overhang_percentage = (overhang_count / len(mesh.faces)) * 100
            print(f"  Overhang faces (>{overhang_angle}°): {overhang_count} ({overhang_percentage:.1f}%)")
        except Exception as e:
            print(f"  ⚠️  Could not analyze supports: {e}")

        print(f"\n[SUMMARY]")
        issues = []
        if has_nan:
            issues.append("❌ Contains NaN values")
        if has_inf:
            issues.append("❌ Contains Inf values")
        if max_face_index >= num_vertices:
            issues.append("❌ Invalid face indices")
        if not mesh.is_watertight:
            issues.append("⚠️  Not watertight")
        if not mesh.is_winding_consistent:
            issues.append("⚠️  Inconsistent winding")
        if zero_area_faces > 0:
            issues.append(f"⚠️  {zero_area_faces} degenerate faces")

        if issues:
            print(f"  Issues found:")
            for issue in issues:
                print(f"    {issue}")
        else:
            print(f"  ✅ No critical issues detected")

        return True

    except Exception as e:
        print(f"\n❌ ERROR loading file: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    working_file = r"C:\Users\johng\Downloads\model_4.STL"
    broken_file = r"C:\Users\johng\Downloads\houndeye_no tail.stl"

    print("\n" + "=" * 80)
    print("STL FILE COMPARISON ANALYSIS")
    print("=" * 80)

    # Analyze working file
    working_ok = analyze_stl(working_file, "WORKING EXAMPLE (model_4.STL)")

    # Analyze broken file
    broken_ok = analyze_stl(broken_file, "NON-WORKING EXAMPLE (houndeye_no tail.stl)")

    # Comparison summary
    print(f"\n{'=' * 80}")
    print("COMPARISON SUMMARY")
    print(f"{'=' * 80}")
    print(f"\nWorking file loaded: {'✅ YES' if working_ok else '❌ NO'}")
    print(f"Broken file loaded: {'✅ YES' if broken_ok else '❌ NO'}")

    if working_ok and broken_ok:
        print(f"\n📊 Both files loaded successfully - check detailed analysis above")
        print(f"   Look for differences in:")
        print(f"   - Vertex/face validation errors")
        print(f"   - Watertight/winding consistency")
        print(f"   - File format issues")
        print(f"   - Support analysis results")

    print(f"\n{'=' * 80}")
