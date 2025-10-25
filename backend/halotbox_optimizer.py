"""
HALOTBOX X1 SLA PRINTER STL OPTIMIZATION
==========================================

Specialized module for optimizing STL files for HalotBox X1 resin printer.
Implements best practices for:
- Print orientation and support placement
- Wall thickness optimization
- Detail preservation
- Support structure generation
- Material-specific parameters
- Export format optimization

HalotBox X1 Specifications:
- Build Platform: 192mm x 120mm x 200mm (XYZ)
- Layer Height: 25µm (0.025mm) standard, 50µm optional
- Pixel Size: 50µm
- Max Model Size: ~190 x 118 x 200mm
- File Formats: STL, OBJ (ASCII or binary)
- Slice Software: HalotBox Program
- Min Wall Thickness: 0.5mm (recommended: 1.0mm)
- Max Overhang: 45° (steeper needs support)
- Material: Standard resin, surgical guide, jewel, model, castable, flexible
"""

import numpy as np
import trimesh
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict, field
import logging
import json
from enum import Enum
from pathlib import Path

logger = logging.getLogger(__name__)


class HalotMaterial(Enum):
    """HalotBox X1 Compatible Materials"""
    STANDARD = "standard"          # General purpose
    SURGICAL_GUIDE = "surgical"    # Medical/dental
    JEWEL = "jewel"                # Jewelry precision
    MODEL = "model"                # Prototyping
    CASTABLE = "castable"          # Investment casting
    FLEXIBLE = "flexible"          # Flexible parts


class HalotQualityPreset(Enum):
    """Print Quality/Speed Presets"""
    FAST = "fast"                  # 100µm layers, quick
    STANDARD = "standard"          # 50µm layers, balanced
    HIGH = "high"                  # 25µm layers, finest detail
    ULTRA = "ultra"                # 25µm layers + aggressive support optimization


@dataclass
class HalotPrinterConfig:
    """HalotBox X1 Printer Configuration"""
    # Build volume (mm)
    build_volume_x: float = 192.0
    build_volume_y: float = 120.0
    build_volume_z: float = 200.0

    # Resolution
    pixel_size_mm: float = 0.050      # 50µm pixels
    min_layer_height_mm: float = 0.025  # 25µm
    standard_layer_height_mm: float = 0.050  # 50µm
    max_layer_height_mm: float = 0.100  # 100µm (FAST mode)

    # Geometry constraints
    min_wall_thickness_mm: float = 0.5
    recommended_wall_thickness_mm: float = 1.0
    max_overhang_angle_deg: float = 45.0
    support_angle_threshold_deg: float = 50.0

    # Support material parameters
    support_point_diameter_mm: float = 0.5
    support_line_width_mm: float = 0.3
    support_density: float = 0.05  # 5% density for support grid

    # File optimization
    max_file_size_mb: float = 100.0
    triangle_optimization: bool = True
    mesh_smoothing: bool = False

    # Material-specific settings
    material: HalotMaterial = HalotMaterial.STANDARD
    quality_preset: HalotQualityPreset = HalotQualityPreset.STANDARD

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        d = asdict(self)
        d['material'] = self.material.value
        d['quality_preset'] = self.quality_preset.value
        return d


@dataclass
class HalotOptimizationReport:
    """STL Optimization Result Report"""
    success: bool
    original_filename: str
    optimized_filename: str
    original_vertex_count: int
    optimized_vertex_count: int
    original_face_count: int
    optimized_face_count: int
    original_size_mb: float
    optimized_size_mb: float
    compression_ratio: float
    recommended_supports: bool
    estimated_print_time_hours: float
    estimated_resin_ml: float
    model_bounding_box: Dict[str, List[float]]
    fit_in_build_volume: bool
    wall_thickness_issues: List[str]
    orientation_recommendation: str
    warnings: List[str]
    errors: List[str]
    processing_time_sec: float
    json_report: Dict[str, Any] = field(default_factory=dict)


class HalotBoxOptimizer:
    """
    HalotBox X1 STL Optimizer

    Optimizes 3D models specifically for the HalotBox X1 SLA printer with
    automatic support generation, orientation, and material-specific settings.
    """

    def __init__(self, config: Optional[HalotPrinterConfig] = None):
        """
        Initialize HalotBox optimizer

        Args:
            config: Custom printer configuration or use defaults
        """
        self.config = config or HalotPrinterConfig()
        self._validate_config()
        logger.info("[HALOTBOX] Optimizer initialized")
        logger.info(f"   Printer: HalotBox X1")
        logger.info(f"   Build Volume: {self.config.build_volume_x}x{self.config.build_volume_y}x{self.config.build_volume_z}mm")
        logger.info(f"   Layer Height: {self.config.standard_layer_height_mm}mm (standard)")
        logger.info(f"   Material: {self.config.material.value}")
        logger.info(f"   Quality: {self.config.quality_preset.value}")

    def _validate_config(self):
        """Validate configuration parameters"""
        if self.config.min_wall_thickness_mm < 0.3:
            logger.warning(f"[HALOTBOX] Min wall thickness too small: {self.config.min_wall_thickness_mm}mm (minimum: 0.3mm)")
            self.config.min_wall_thickness_mm = 0.5

        if self.config.support_angle_threshold_deg > 90:
            logger.warning(f"[HALOTBOX] Support angle threshold > 90°, clamping to 85°")
            self.config.support_angle_threshold_deg = 85.0

    def _repair_corrupted_mesh(self, mesh: trimesh.Trimesh) -> trimesh.Trimesh:
        """
        Comprehensive mesh repair for corrupted or invalid STL files

        Args:
            mesh: Potentially corrupted trimesh object

        Returns:
            Repaired mesh or original if repair fails
        """
        import numpy as np

        try:
            logger.info("[HALOTBOX] Starting comprehensive mesh repair...")
            original_vertices = len(mesh.vertices) if mesh.vertices is not None else 0
            original_faces = len(mesh.faces) if mesh.faces is not None else 0

            # Step 1: Handle empty or None arrays
            if mesh.vertices is None or len(mesh.vertices) == 0:
                logger.error("[HALOTBOX] Mesh has no vertices - cannot repair")
                return mesh

            if mesh.faces is None or len(mesh.faces) == 0:
                logger.error("[HALOTBOX] Mesh has no faces - cannot repair")
                return mesh

            # Step 2: Remove NaN and Inf values
            if np.any(np.isnan(mesh.vertices)) or np.any(np.isinf(mesh.vertices)):
                logger.warning("[HALOTBOX] Found NaN/Inf vertices - cleaning...")
                valid_mask = np.all(np.isfinite(mesh.vertices), axis=1)
                if not np.any(valid_mask):
                    logger.error("[HALOTBOX] All vertices are invalid (NaN/Inf)")
                    return mesh

                # Keep only valid vertices and remap face indices
                valid_indices = np.where(valid_mask)[0]
                old_to_new = {old: new for new, old in enumerate(valid_indices)}

                try:
                    mesh.vertices = mesh.vertices[valid_mask]
                    # Remap faces to valid vertices only
                    new_faces = []
                    for face in mesh.faces:
                        if all(idx in old_to_new for idx in face):
                            new_faces.append([old_to_new[idx] for idx in face])
                    mesh.faces = np.array(new_faces)
                    logger.info(f"[HALOTBOX] Cleaned NaN/Inf: {original_vertices} → {len(mesh.vertices)} vertices")
                except Exception as e:
                    logger.warning(f"[HALOTBOX] Failed to clean NaN/Inf: {e}")

            # Step 3: Remove duplicate vertices
            try:
                initial_verts = len(mesh.vertices)
                mesh.merge_vertices()
                logger.info(f"[HALOTBOX] Merged duplicates: {initial_verts} → {len(mesh.vertices)} vertices")
            except Exception as e:
                logger.warning(f"[HALOTBOX] merge_vertices failed: {e}")

            # Step 4: Remove degenerate faces (zero area, flipped normals)
            try:
                initial_faces = len(mesh.faces)
                mesh.remove_degenerate_faces()
                logger.info(f"[HALOTBOX] Removed degenerate: {initial_faces} → {len(mesh.faces)} faces")
            except Exception as e:
                logger.warning(f"[HALOTBOX] remove_degenerate_faces failed: {e}")

            # Step 5: Fix mesh topology
            try:
                mesh.fix_normals()
                logger.info("[HALOTBOX] Fixed normals")
            except Exception as e:
                logger.warning(f"[HALOTBOX] fix_normals failed: {e}")

            # Step 6: Fill holes in mesh
            try:
                try:
                    is_watertight = mesh.is_watertight
                except:
                    is_watertight = False

                if not is_watertight:
                    logger.info("[HALOTBOX] Mesh is not watertight - attempting to fill holes...")
                    mesh.fill_holes()
                    logger.info("[HALOTBOX] Holes filled")
            except Exception as e:
                logger.warning(f"[HALOTBOX] fill_holes failed: {e}")

            # Step 7: Remove unreferenced vertices
            try:
                initial_verts = len(mesh.vertices)
                # Get all referenced vertex indices from faces
                referenced = set(mesh.faces.flatten())
                if len(referenced) < initial_verts:
                    logger.info(f"[HALOTBOX] Removing unreferenced vertices: {initial_verts} → {len(referenced)}")
                    mesh.remove_unreferenced_vertices()
            except Exception as e:
                logger.warning(f"[HALOTBOX] remove_unreferenced_vertices failed: {e}")

            # Step 8: Validate final mesh
            final_vertices = len(mesh.vertices) if mesh.vertices is not None else 0
            final_faces = len(mesh.faces) if mesh.faces is not None else 0

            if final_vertices < 4 or final_faces < 1:
                logger.error(f"[HALOTBOX] Mesh repair resulted in invalid mesh: {final_vertices} verts, {final_faces} faces")
                return mesh

            logger.info(f"[HALOTBOX] ✓ Mesh repair complete: {original_vertices}→{final_vertices} verts, {original_faces}→{final_faces} faces")
            try:
                is_watertight = mesh.is_watertight
            except:
                is_watertight = False
            logger.info(f"[HALOTBOX] Mesh watertight: {is_watertight}")

            return mesh

        except Exception as e:
            logger.error(f"[HALOTBOX] Critical mesh repair failure: {e}")
            return mesh

    def optimize_stl(self, mesh: trimesh.Trimesh, filename: str) -> Tuple[HalotOptimizationReport, trimesh.Trimesh]:
        """
        Optimize STL for HalotBox X1 printing

        Args:
            mesh: Input trimesh object
            filename: Original filename

        Returns:
            Optimization report with recommendations
        """
        import time
        start_time = time.time()

        report = HalotOptimizationReport(
            success=False,
            original_filename=filename,
            optimized_filename="",
            original_vertex_count=len(mesh.vertices),
            optimized_vertex_count=0,
            original_face_count=len(mesh.faces),
            optimized_face_count=0,
            original_size_mb=0.0,
            optimized_size_mb=0.0,
            compression_ratio=1.0,
            recommended_supports=False,
            estimated_print_time_hours=0.0,
            estimated_resin_ml=0.0,
            model_bounding_box={},
            fit_in_build_volume=False,
            wall_thickness_issues=[],
            orientation_recommendation="",
            warnings=[],
            errors=[],
            processing_time_sec=0.0
        )
        optimized_mesh = mesh  # Initialize with input mesh as fallback

        try:
            # Step 0: Pre-validation and repair - Check mesh integrity
            logger.info(f"[HALOTBOX] Pre-validation: Checking mesh integrity...")
            try:
                # Check basic mesh properties
                if len(mesh.vertices) == 0:
                    raise ValueError("Mesh has no vertices")
                if len(mesh.faces) == 0:
                    raise ValueError("Mesh has no faces")

                logger.info(f"[HALOTBOX] Initial mesh: {len(mesh.vertices)} vertices, {len(mesh.faces)} faces")

                # Run comprehensive repair on potentially corrupted mesh
                mesh = self._repair_corrupted_mesh(mesh)

                # Validate repair result
                if len(mesh.vertices) < 4 or len(mesh.faces) < 1:
                    raise ValueError(f"Mesh repair failed: {len(mesh.vertices)} vertices, {len(mesh.faces)} faces")

                logger.info(f"[HALOTBOX] ✓ Pre-validation and repair complete")

            except ValueError as e:
                logger.error(f"[HALOTBOX] Pre-validation failed: {e}")
                report.errors.append(f"Mesh validation failed: {e}")
                report.success = False
                return report, mesh

            # Step 1: Analyze original mesh
            logger.info(f"[HALOTBOX] Analyzing mesh: {filename}")
            original_bounds = mesh.bounds
            report.model_bounding_box = {
                'min': original_bounds[0].tolist(),
                'max': original_bounds[1].tolist(),
                'size': (original_bounds[1] - original_bounds[0]).tolist()
            }

            # Step 2: Check if model fits in build volume
            model_size = original_bounds[1] - original_bounds[0]
            build_volume = np.array([
                self.config.build_volume_x,
                self.config.build_volume_y,
                self.config.build_volume_z
            ])

            if np.all(model_size <= build_volume):
                report.fit_in_build_volume = True
                logger.info(f"[HALOTBOX] ✓ Model fits in build volume: {model_size.tolist()} ≤ {build_volume.tolist()}")
            else:
                report.fit_in_build_volume = False
                oversized_dims = np.where(model_size > build_volume)[0]
                for dim_idx in oversized_dims:
                    dim_name = ['X', 'Y', 'Z'][dim_idx]
                    report.warnings.append(
                        f"Model {dim_name} dimension exceeds build volume: "
                        f"{model_size[dim_idx]:.1f}mm > {build_volume[dim_idx]:.1f}mm. "
                        f"Scale down by {(model_size[dim_idx] / build_volume[dim_idx]):.2f}x"
                    )

            # Step 3: Check wall thickness
            logger.info(f"[HALOTBOX] Checking wall thickness...")
            wall_issues = self._check_wall_thickness(mesh)
            if wall_issues:
                report.wall_thickness_issues = wall_issues
                for issue in wall_issues:
                    report.warnings.append(f"Wall thickness: {issue}")

            # Step 4: Optimize mesh
            logger.info(f"[HALOTBOX] Optimizing mesh...")
            optimized_mesh = self._optimize_mesh(mesh)
            report.optimized_vertex_count = len(optimized_mesh.vertices)
            report.optimized_face_count = len(optimized_mesh.faces)

            # Step 5: Determine print orientation
            logger.info(f"[HALOTBOX] Calculating optimal orientation...")
            orientation_vec = self._calculate_optimal_orientation(optimized_mesh)
            report.orientation_recommendation = (
                f"Recommended orientation: rotate model so longest axis "
                f"is vertical (Z) for best support efficiency. "
                f"Optimal vector: {orientation_vec.tolist()}"
            )

            # Step 6: Final mesh validation before support analysis (prevents encoding errors)
            logger.info(f"[HALOTBOX] Final validation before support analysis...")
            try:
                # Check mesh integrity for export/support analysis
                if len(optimized_mesh.vertices) == 0 or len(optimized_mesh.faces) == 0:
                    raise ValueError("Mesh has no geometry after optimization")

                # Clean any remaining invalid values that could cause encoding issues
                if np.any(~np.isfinite(optimized_mesh.vertices)):
                    logger.warning("[HALOTBOX] Found invalid vertices before support analysis - cleaning...")
                    valid_mask = np.all(np.isfinite(optimized_mesh.vertices), axis=1)
                    if not np.any(valid_mask):
                        raise ValueError("All vertices are invalid")
                    optimized_mesh.vertices = optimized_mesh.vertices[valid_mask]
                    optimized_mesh.remove_unreferenced_vertices()
                    logger.info(f"[HALOTBOX] Cleaned mesh: {len(optimized_mesh.vertices)} vertices")

                # Verify mesh is still valid
                if len(optimized_mesh.vertices) < 4 or len(optimized_mesh.faces) < 1:
                    raise ValueError("Mesh too small after validation")

                logger.info(f"[HALOTBOX] ✓ Final validation passed")
            except Exception as e:
                logger.error(f"[HALOTBOX] Mesh validation before support failed: {e}")
                report.errors.append(f"Mesh validation error: {e}")
                report.success = False
                return report, mesh

            # Step 7: Check if supports needed
            logger.info(f"[HALOTBOX] Analyzing support requirements...")
            needs_supports = self._estimate_support_requirement(optimized_mesh)
            report.recommended_supports = needs_supports
            if needs_supports:
                report.warnings.append(
                    f"Model has overhangs > {self.config.max_overhang_angle_deg}°. "
                    f"Supports recommended. Use HalotBox Program's auto-support feature."
                )

            # Step 8: Estimate print metrics
            logger.info(f"[HALOTBOX] Estimating print metrics...")
            report.estimated_print_time_hours = self._estimate_print_time(optimized_mesh)
            report.estimated_resin_ml = self._estimate_resin_volume(optimized_mesh)

            logger.info(f"[HALOTBOX] Estimated print time: {report.estimated_print_time_hours:.1f} hours")
            logger.info(f"[HALOTBOX] Estimated resin: {report.estimated_resin_ml:.1f} mL")

            # Step 8: Prepare optimized filename
            name_without_ext = Path(filename).stem
            report.optimized_filename = f"{name_without_ext}_halotbox_optimized.stl"

            report.success = True
            logger.info(f"[HALOTBOX] ✓ Optimization complete")

        except Exception as e:
            logger.error(f"[HALOTBOX] Optimization failed: {e}")
            report.errors.append(str(e))
            report.success = False

        report.processing_time_sec = time.time() - start_time
        return report, optimized_mesh

    def _check_wall_thickness(self, mesh: trimesh.Trimesh) -> List[str]:
        """Check for walls thinner than recommended"""
        issues = []
        try:
            # Simplified check: look at edge lengths
            edge_lengths = np.linalg.norm(
                mesh.vertices[mesh.edges[:, 0]] - mesh.vertices[mesh.edges[:, 1]],
                axis=1
            )

            min_edge = edge_lengths.min()
            if min_edge < self.config.min_wall_thickness_mm:
                issues.append(
                    f"Very thin edges detected: {min_edge:.3f}mm "
                    f"(minimum: {self.config.min_wall_thickness_mm}mm)"
                )
        except Exception as e:
            logger.debug(f"Wall thickness check failed: {e}")

        return issues

    def _optimize_mesh(self, mesh: trimesh.Trimesh) -> trimesh.Trimesh:
        """Optimize mesh for HalotBox printing with robust error handling"""
        try:
            logger.info(f"[HALOTBOX] Starting mesh optimization...")

            # Step 1: Remove degenerate faces (zero area)
            try:
                initial_faces = len(mesh.faces)
                mesh.remove_degenerate_faces()
                removed = initial_faces - len(mesh.faces)
                if removed > 0:
                    logger.info(f"[HALOTBOX] Removed {removed} degenerate faces")
            except Exception as e:
                logger.warning(f"[HALOTBOX] Failed to remove degenerate faces: {e}")

            # Step 2: Fix normals (critical for mesh validity)
            try:
                mesh.fix_normals()
                logger.info(f"[HALOTBOX] Fixed face normals")
            except Exception as e:
                logger.warning(f"[HALOTBOX] Failed to fix normals: {e}")

            # Step 3: Check mesh validity before simplification
            try:
                # Check if mesh is watertight instead of is_valid (which doesn't exist)
                try:
                    is_watertight = mesh.is_watertight
                except:
                    is_watertight = False

                logger.info(f"[HALOTBOX] Mesh watertight: {is_watertight}")

                if not is_watertight:
                    logger.warning(f"[HALOTBOX] Mesh is not watertight - attempting repair...")
                    # Try to make watertight
                    try:
                        mesh.fill_holes()
                        logger.info(f"[HALOTBOX] Filled holes")
                    except Exception as e:
                        logger.warning(f"[HALOTBOX] fill_holes failed: {e}")

                    # Remove duplicate vertices
                    try:
                        mesh.merge_vertices()
                        logger.info(f"[HALOTBOX] Merged duplicate vertices")
                    except Exception as e:
                        logger.warning(f"[HALOTBOX] merge_vertices failed: {e}")

            except Exception as e:
                logger.warning(f"[HALOTBOX] Mesh validity check failed: {e}")

            # Step 4: Simplify mesh (with extra error handling)
            target_vertices = {
                HalotQualityPreset.FAST: 500000,
                HalotQualityPreset.STANDARD: 250000,
                HalotQualityPreset.HIGH: 100000,
                HalotQualityPreset.ULTRA: 50000,
            }[self.config.quality_preset]

            current_vertices = len(mesh.vertices)

            if current_vertices > target_vertices:
                ratio = target_vertices / current_vertices
                logger.info(f"[HALOTBOX] Mesh simplification needed: {current_vertices} → {target_vertices} vertices ({ratio:.2%})")

                try:
                    # Use quadric mesh simplification
                    logger.info(f"[HALOTBOX] Attempting quadric mesh simplification...")
                    simplified = mesh.simplify_mesh(target_count=target_vertices, agg_vert_count=7)

                    # Verify simplification worked
                    if simplified is not None and len(simplified.vertices) > 0:
                        logger.info(f"[HALOTBOX] ✓ Simplification successful: {len(mesh.vertices)} → {len(simplified.vertices)} vertices")
                        mesh = simplified
                    else:
                        logger.warning(f"[HALOTBOX] Simplification returned empty mesh, using original")

                except Exception as e:
                    logger.warning(f"[HALOTBOX] Quadric simplification failed: {e}, attempting fallback...")

                    # Fallback: Use voxel-based simplification
                    try:
                        logger.info(f"[HALOTBOX] Attempting voxel-based simplification...")
                        # Get current mesh bounds for voxel size calculation
                        bounds = mesh.bounds
                        size = bounds[1] - bounds[0]
                        max_dim = np.max(size)

                        # Calculate voxel size to achieve target vertex reduction
                        current_vert = len(mesh.vertices)
                        reduction_factor = target_vertices / current_vert if current_vert > 0 else 0.5
                        voxel_size = max_dim * (1.0 / np.cbrt(reduction_factor + 0.1))

                        logger.info(f"[HALOTBOX] Voxel size: {voxel_size:.4f}mm for reduction factor {reduction_factor:.2%}")

                        # Apply voxel-based simplification
                        simplified = mesh.voxelized(pitch=voxel_size).as_mesh()

                        if simplified is not None and len(simplified.vertices) > 0:
                            logger.info(f"[HALOTBOX] ✓ Voxel simplification successful: {len(mesh.vertices)} → {len(simplified.vertices)} vertices")
                            mesh = simplified
                        else:
                            logger.warning(f"[HALOTBOX] Voxel simplification returned empty mesh")

                    except Exception as e2:
                        logger.warning(f"[HALOTBOX] Voxel simplification also failed: {e2}, using original mesh")
                        # Return original mesh - no simplification possible

            logger.info(f"[HALOTBOX] ✓ Mesh optimization complete: {len(mesh.vertices)} vertices, {len(mesh.faces)} faces")
            return mesh

        except Exception as e:
            logger.error(f"[HALOTBOX] Mesh optimization critical failure: {e}")
            logger.error(f"[HALOTBOX] Returning original mesh unchanged")
            return mesh

    def _calculate_optimal_orientation(self, mesh: trimesh.Trimesh) -> np.ndarray:
        """Calculate optimal print orientation"""
        try:
            # Get principal axes (PCA-like)
            principal_axis = mesh.vertices - mesh.center_mass
            if len(principal_axis) > 0:
                principal_axis = principal_axis[np.argmax(
                    np.linalg.norm(principal_axis, axis=1)
                )]
                principal_axis = principal_axis / np.linalg.norm(principal_axis)
                return principal_axis
        except Exception as e:
            logger.debug(f"Orientation calculation failed: {e}")

        return np.array([0, 0, 1])  # Default: Z-up

    def _estimate_support_requirement(self, mesh: trimesh.Trimesh, angle_threshold: Optional[float] = None) -> bool:
        """Estimate if model needs supports"""
        if angle_threshold is None:
            angle_threshold = np.radians(self.config.support_angle_threshold_deg)

        try:
            # Validate mesh before analysis
            if len(mesh.vertices) == 0 or len(mesh.faces) == 0:
                logger.warning("[HALOTBOX] Support check: Mesh has no vertices or faces")
                return True

            # Check for invalid vertices which would cause encoding issues
            if np.any(~np.isfinite(mesh.vertices)):
                logger.warning("[HALOTBOX] Support check: Mesh contains NaN/Inf vertices")
                return True  # Conservative: assume supports needed

            # Check face normals for steep overhangs
            # Faces pointing nearly horizontal (to build platform) don't need supports
            # Faces pointing downward need supports
            normals = mesh.face_normals

            # Ensure normals are finite
            if not np.all(np.isfinite(normals)):
                logger.warning("[HALOTBOX] Support check: Face normals contain NaN/Inf")
                return True

            vertical_component = np.abs(normals[:, 2])  # Z component

            # Faces with low vertical component are nearly horizontal (overhangs)
            overhanging_faces = vertical_component < np.cos(angle_threshold)
            needs_supports = np.any(overhanging_faces)

            logger.info(f"[HALOTBOX] Support analysis: {np.sum(overhanging_faces)}/{len(mesh.faces)} faces need supports")
            return needs_supports

        except Exception as e:
            logger.debug(f"[HALOTBOX] Support requirement check failed: {e}")
            return True  # Conservative: assume supports needed

    def _estimate_print_time(self, mesh: trimesh.Trimesh) -> float:
        """Estimate print time in hours"""
        try:
            # Get model height
            height_mm = mesh.bounds[1][2] - mesh.bounds[0][2]

            # Estimate layer count
            layer_height_mm = self.config.standard_layer_height_mm
            layers = height_mm / layer_height_mm

            # Base time per layer (in seconds): includes exposure + movement
            # HalotBox X1: ~2-5 seconds per layer typically
            time_per_layer_sec = 3.0

            # Add support generation time (rough estimate)
            support_overhead = 1.2 if self._estimate_support_requirement(mesh) else 1.0

            total_seconds = layers * time_per_layer_sec * support_overhead
            return total_seconds / 3600.0  # Convert to hours

        except Exception as e:
            logger.debug(f"Print time estimation failed: {e}")
            return 0.0

    def _estimate_resin_volume(self, mesh: trimesh.Trimesh) -> float:
        """Estimate resin volume in mL"""
        try:
            # Get volume
            if mesh.is_watertight:
                volume_mm3 = mesh.volume
            else:
                # Rough estimate from bounds
                bounds = mesh.bounds
                size = bounds[1] - bounds[0]
                volume_mm3 = np.prod(size) * 0.5  # Rough estimate

            # Convert to mL (1 mL = 1000 mm³)
            volume_ml = volume_mm3 / 1000.0

            # Add support overhead (~20%)
            total_volume_ml = volume_ml * 1.2

            return total_volume_ml

        except Exception as e:
            logger.debug(f"Resin volume estimation failed: {e}")
            return 0.0

    def export_halotbox_stl(self, mesh: trimesh.Trimesh, output_path: str) -> bool:
        """
        Export STL optimized for HalotBox X1

        Args:
            mesh: Mesh to export
            output_path: Output file path

        Returns:
            True if successful
        """
        try:
            logger.info(f"[HALOTBOX] Preparing mesh for export...")

            # Ensure mesh is valid before export
            if len(mesh.vertices) == 0 or len(mesh.faces) == 0:
                logger.error(f"[HALOTBOX] Cannot export: mesh has no vertices or faces")
                return False

            # Check for NaN/Inf values which break STL encoding
            if np.any(~np.isfinite(mesh.vertices)):
                logger.warning("[HALOTBOX] Mesh contains invalid vertices (NaN/Inf) - cleaning...")
                valid_mask = np.all(np.isfinite(mesh.vertices), axis=1)

                # Create mapping from old indices to new indices
                index_map = np.full(len(valid_mask), -1, dtype=np.int32)
                index_map[valid_mask] = np.arange(np.sum(valid_mask), dtype=np.int32)

                # Keep only valid vertices
                mesh.vertices = mesh.vertices[valid_mask]

                # Remove faces that reference invalid vertices
                # A face is valid if ALL its vertices are valid
                valid_faces = []
                for face in mesh.faces:
                    if all(index_map[v] >= 0 for v in face):
                        # Remap face indices to new vertex positions
                        new_face = np.array([index_map[v] for v in face], dtype=np.uint32)
                        valid_faces.append(new_face)

                if len(valid_faces) == 0:
                    logger.error("[HALOTBOX] No valid faces after cleaning vertices")
                    return False

                mesh.faces = np.array(valid_faces, dtype=np.uint32)
                logger.info(f"[HALOTBOX] Cleaned mesh: {len(mesh.vertices)} vertices, {len(mesh.faces)} faces")

            logger.info(f"[HALOTBOX] Exporting binary STL: {len(mesh.vertices)} vertices, {len(mesh.faces)} faces")

            # HalotBox X1 prefers binary STL format (more reliable and smaller)
            # Using file_type='stl' exports as binary
            mesh.export(output_path, file_type='stl')

            # Verify file was created
            if not Path(output_path).exists():
                logger.error(f"[HALOTBOX] STL export failed - file not created")
                return False

            file_size_kb = Path(output_path).stat().st_size / 1024
            logger.info(f"[HALOTBOX] ✓ STL exported successfully: {file_size_kb:.1f} KB")
            return True

        except UnicodeEncodeError as e:
            logger.error(f"[HALOTBOX] STL encoding error: {e}")
            logger.error(f"[HALOTBOX] This usually indicates invalid vertex data (NaN/Inf)")
            return False
        except Exception as e:
            logger.error(f"[HALOTBOX] STL export failed: {e}")
            import traceback
            logger.error(f"[HALOTBOX] Traceback: {traceback.format_exc()}")
            return False

    def get_material_profile(self) -> Dict[str, Any]:
        """Get material-specific print parameters"""
        material_profiles = {
            HalotMaterial.STANDARD: {
                'exposure_time_ms': 8.0,
                'layer_height_mm': 0.050,
                'lift_speed_mm_min': 60,
                'cure_time_sec': 2.0,
                'bed_temp_celsius': 28,
                'viscosity_cps': 500
            },
            HalotMaterial.SURGICAL_GUIDE: {
                'exposure_time_ms': 10.0,
                'layer_height_mm': 0.025,
                'lift_speed_mm_min': 40,
                'cure_time_sec': 3.0,
                'bed_temp_celsius': 30,
                'viscosity_cps': 600,
                'min_wall_thickness_mm': 1.5,
                'notes': 'Medical grade - requires validation'
            },
            HalotMaterial.JEWEL: {
                'exposure_time_ms': 6.0,
                'layer_height_mm': 0.025,
                'lift_speed_mm_min': 80,
                'cure_time_sec': 1.5,
                'bed_temp_celsius': 25,
                'viscosity_cps': 400,
                'detail_level': 'ultra',
                'notes': 'For fine jewelry detail'
            },
            HalotMaterial.MODEL: {
                'exposure_time_ms': 8.5,
                'layer_height_mm': 0.050,
                'lift_speed_mm_min': 60,
                'cure_time_sec': 2.5,
                'bed_temp_celsius': 28,
                'viscosity_cps': 520
            },
            HalotMaterial.CASTABLE: {
                'exposure_time_ms': 9.0,
                'layer_height_mm': 0.050,
                'lift_speed_mm_min': 50,
                'cure_time_sec': 3.0,
                'bed_temp_celsius': 32,
                'viscosity_cps': 700,
                'min_wall_thickness_mm': 1.2,
                'notes': 'For investment casting - ash-free'
            },
            HalotMaterial.FLEXIBLE: {
                'exposure_time_ms': 12.0,
                'layer_height_mm': 0.050,
                'lift_speed_mm_min': 40,
                'cure_time_sec': 4.0,
                'bed_temp_celsius': 26,
                'viscosity_cps': 800
            }
        }

        return material_profiles.get(self.config.material, material_profiles[HalotMaterial.STANDARD])

    def get_optimization_json(self) -> str:
        """Export configuration as JSON for HalotBox Program"""
        profile = self.get_material_profile()
        config_json = {
            'printer': 'HalotBox X1',
            'material': self.config.material.value,
            'quality_preset': self.config.quality_preset.value,
            'print_parameters': profile,
            'build_volume_mm': {
                'x': self.config.build_volume_x,
                'y': self.config.build_volume_y,
                'z': self.config.build_volume_z
            },
            'layer_height_mm': self.config.standard_layer_height_mm,
            'min_wall_thickness_mm': self.config.min_wall_thickness_mm,
            'support_angle_threshold_deg': self.config.support_angle_threshold_deg,
            'optimization_features': [
                'Mesh auto-repair',
                'Triangle optimization',
                'Orientation recommendation',
                'Support requirement analysis',
                'Print time estimation',
                'Material profile selection'
            ]
        }
        return json.dumps(config_json, indent=2)


# Convenience functions
def optimize_for_halotbox(mesh: trimesh.Trimesh, filename: str,
                          material: HalotMaterial = HalotMaterial.STANDARD,
                          quality: HalotQualityPreset = HalotQualityPreset.STANDARD) -> HalotOptimizationReport:
    """
    Quick optimization with defaults

    Args:
        mesh: Input mesh
        filename: Original filename
        material: Material type
        quality: Quality preset

    Returns:
        Optimization report
    """
    config = HalotPrinterConfig(material=material, quality_preset=quality)
    optimizer = HalotBoxOptimizer(config)
    return optimizer.optimize_stl(mesh, filename)


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)

    # Create sample configuration
    config = HalotPrinterConfig(
        material=HalotMaterial.STANDARD,
        quality_preset=HalotQualityPreset.HIGH
    )

    optimizer = HalotBoxOptimizer(config)
    print(optimizer.get_optimization_json())
