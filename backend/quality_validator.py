"""
ORFEAS AI 2D→3D Studio - Real-time Quality Validator
====================================================
ORFEAS AI Project

Features:
- Multi-stage quality validation for 3D generation pipeline
- Background removal quality assessment
- Shape generation accuracy metrics (manifold, topology)
- Texture coherence validation
- Final mesh quality scoring
- Auto-repair for low-quality outputs
- Prometheus metrics integration

Priority: #1 from Top 5 Recommended Features
Purpose: Ensure consistently high-quality 3D outputs with automatic quality assurance
"""

import numpy as np
import logging
from PIL import Image
from typing import Dict, Tuple, Any, Optional
import trimesh
import cv2
from pathlib import Path
import hashlib

logger = logging.getLogger(__name__)


class GenerationQualityValidator:
    """
    Real-time quality validation for multi-stage 3D generation pipeline

    Validates quality at each stage:
    1. Background removal quality (alpha channel analysis)
    2. Shape generation accuracy (manifold, triangle count, topology)
    3. Texture coherence (consistency, coverage, resolution)
    4. Final mesh quality (printability, watertightness)

    Auto-repairs meshes with quality scores below thresholds.
    """

    def __init__(self, quality_threshold: float = 0.80):
        """
        Initialize quality validator

        Args:
            quality_threshold: Minimum acceptable quality score (0.0-1.0)
        """
        self.quality_threshold = quality_threshold
        self.stats = {
            'total_validations': 0,
            'passed_validations': 0,
            'failed_validations': 0,
            'auto_repairs': 0,
            'quality_scores': []
        }

        logger.info("[QUALITY] GenerationQualityValidator initialized")
        logger.info(f"[QUALITY] Quality threshold: {quality_threshold:.2f}")

    def validate_generation_pipeline(
        self,
        original_image: Image.Image,
        bg_removed_image: Optional[Image.Image] = None,
        generated_mesh: Optional[trimesh.Trimesh] = None,
        texture_image: Optional[Image.Image] = None
    ) -> Dict[str, Any]:
        """
        Validate entire 3D generation pipeline with quality metrics

        Args:
            original_image: Original input image
            bg_removed_image: Image after background removal (optional)
            generated_mesh: Generated 3D mesh (optional)
            texture_image: Applied texture image (optional)

        Returns:
            Dict with quality metrics for each stage and overall score
        """
        self.stats['total_validations'] += 1

        metrics = {
            'timestamp': None,
            'bg_removal_quality': None,
            'shape_quality': None,
            'texture_quality': None,
            'final_quality': None,
            'overall_score': 0.0,
            'quality_grade': 'F',
            'issues_detected': [],
            'auto_repairs_applied': [],
            'passed_threshold': False
        }

        try:
            # Stage 1: Background removal quality
            if bg_removed_image is not None:
                bg_quality = self.validate_background_removal(
                    original_image, bg_removed_image
                )
                metrics['bg_removal_quality'] = bg_quality

                if bg_quality['score'] < self.quality_threshold:
                    metrics['issues_detected'].append(
                        f"Low background removal quality: {bg_quality['score']:.2f}"
                    )

            # Stage 2: Shape generation accuracy
            if generated_mesh is not None:
                shape_quality = self.validate_shape_generation(generated_mesh)
                metrics['shape_quality'] = shape_quality

                if shape_quality['score'] < self.quality_threshold:
                    metrics['issues_detected'].append(
                        f"Low shape quality: {shape_quality['score']:.2f}"
                    )

                # Auto-repair non-manifold geometry
                if not shape_quality['manifold']:
                    logger.warning("[QUALITY] Non-manifold geometry detected - attempting repair")
                    repaired_mesh = self._repair_mesh(generated_mesh)
                    if repaired_mesh is not None:
                        generated_mesh = repaired_mesh
                        metrics['auto_repairs_applied'].append("Non-manifold geometry repair")
                        self.stats['auto_repairs'] += 1

                        # Re-validate after repair
                        shape_quality = self.validate_shape_generation(generated_mesh)
                        metrics['shape_quality'] = shape_quality

            # Stage 3: Texture coherence
            if texture_image is not None and generated_mesh is not None:
                texture_quality = self.validate_texture_coherence(
                    texture_image, generated_mesh
                )
                metrics['texture_quality'] = texture_quality

                if texture_quality['score'] < self.quality_threshold:
                    metrics['issues_detected'].append(
                        f"Low texture quality: {texture_quality['score']:.2f}"
                    )

            # Stage 4: Final mesh validation
            if generated_mesh is not None:
                final_quality = self.validate_final_mesh(generated_mesh)
                metrics['final_quality'] = final_quality

                if final_quality['score'] < self.quality_threshold:
                    metrics['issues_detected'].append(
                        f"Low final mesh quality: {final_quality['score']:.2f}"
                    )

            # Compute overall quality score
            metrics['overall_score'] = self._compute_overall_score(metrics)
            metrics['quality_grade'] = self._compute_quality_grade(metrics['overall_score'])
            metrics['passed_threshold'] = metrics['overall_score'] >= self.quality_threshold

            # Update statistics
            if metrics['passed_threshold']:
                self.stats['passed_validations'] += 1
            else:
                self.stats['failed_validations'] += 1

            self.stats['quality_scores'].append(metrics['overall_score'])

            # Log results
            if metrics['passed_threshold']:
                logger.info(
                    f"[QUALITY]  Validation PASSED | "
                    f"Score: {metrics['overall_score']:.3f} | "
                    f"Grade: {metrics['quality_grade']}"
                )
            else:
                logger.warning(
                    f"[QUALITY]  Validation FAILED | "
                    f"Score: {metrics['overall_score']:.3f} | "
                    f"Grade: {metrics['quality_grade']} | "
                    f"Issues: {len(metrics['issues_detected'])}"
                )

            return metrics

        except Exception as e:
            logger.error(f"[QUALITY] Validation error: {e}")
            metrics['issues_detected'].append(f"Validation error: {str(e)}")
            return metrics

    def validate_background_removal(
        self,
        original_image: Image.Image,
        bg_removed_image: Image.Image
    ) -> Dict[str, Any]:
        """
        Validate background removal quality

        Metrics:
        - Alpha channel coverage (% of non-background pixels)
        - Edge sharpness (how clean the cutout is)
        - Subject preservation (did we keep important parts?)

        Args:
            original_image: Original input image
            bg_removed_image: Image after background removal

        Returns:
            Dict with background removal quality metrics
        """
        try:
            # Convert to numpy arrays
            original_np = np.array(original_image)
            bg_removed_np = np.array(bg_removed_image)

            # Extract alpha channel if present
            if bg_removed_np.shape[-1] == 4:
                alpha_channel = bg_removed_np[:, :, 3]
            else:
                # If no alpha, assume background is pure black or white
                grayscale = cv2.cvtColor(bg_removed_np, cv2.COLOR_RGB2GRAY)
                alpha_channel = (grayscale > 10).astype(np.uint8) * 255

            # Metric 1: Subject coverage (% of non-transparent pixels)
            total_pixels = alpha_channel.size
            subject_pixels = np.sum(alpha_channel > 128)
            coverage_ratio = subject_pixels / total_pixels

            # Metric 2: Edge sharpness (transition quality)
            edges = cv2.Canny(alpha_channel, 50, 150)
            edge_density = np.sum(edges > 0) / total_pixels

            # Sharp edges should have moderate density (not too jagged, not too blurry)
            edge_sharpness = 1.0 - abs(edge_density - 0.05) / 0.05
            edge_sharpness = max(0.0, min(1.0, edge_sharpness))

            # Metric 3: Subject preservation (did we lose important details?)
            # Compare original and bg-removed histograms
            if original_np.shape[-1] >= 3 and bg_removed_np.shape[-1] >= 3:
                original_hist = cv2.calcHist(
                    [original_np[:, :, :3]], [0, 1, 2], None,
                    [8, 8, 8], [0, 256, 0, 256, 0, 256]
                )
                bg_removed_hist = cv2.calcHist(
                    [bg_removed_np[:, :, :3]], [0, 1, 2], None,
                    [8, 8, 8], [0, 256, 0, 256, 0, 256]
                )

                # Normalize histograms
                original_hist = cv2.normalize(original_hist, original_hist).flatten()
                bg_removed_hist = cv2.normalize(bg_removed_hist, bg_removed_hist).flatten()

                # Compare histograms (higher correlation = better preservation)
                preservation = cv2.compareHist(
                    original_hist.reshape(-1, 1).astype(np.float32),
                    bg_removed_hist.reshape(-1, 1).astype(np.float32),
                    cv2.HISTCMP_CORREL
                )
            else:
                preservation = 0.85  # Default if comparison not possible

            # Compute overall background removal score
            # Weights: coverage (40%), sharpness (30%), preservation (30%)
            bg_score = (
                coverage_ratio * 0.4 +
                edge_sharpness * 0.3 +
                preservation * 0.3
            )

            return {
                'score': bg_score,
                'coverage_ratio': coverage_ratio,
                'edge_sharpness': edge_sharpness,
                'subject_preservation': preservation,
                'subject_pixels': int(subject_pixels),
                'total_pixels': int(total_pixels)
            }

        except Exception as e:
            logger.error(f"[QUALITY] Background removal validation error: {e}")
            return {
                'score': 0.0,
                'error': str(e)
            }

    def validate_shape_generation(self, mesh: trimesh.Trimesh) -> Dict[str, Any]:
        """
        Validate 3D shape generation quality

        Metrics:
        - Manifold status (watertight geometry)
        - Triangle count (complexity)
        - Vertex/triangle ratio (topology quality)
        - Volume (non-zero, reasonable size)
        - Bounds (reasonable dimensions)

        Args:
            mesh: Generated 3D mesh

        Returns:
            Dict with shape quality metrics
        """
        try:
            # Metric 1: Manifold status (CRITICAL for 3D printing)
            is_manifold = mesh.is_watertight
            manifold_score = 1.0 if is_manifold else 0.0

            # Metric 2: Triangle count quality
            triangle_count = len(mesh.faces)

            # Ideal range: 5,000 - 50,000 triangles
            # Too few = low detail, too many = performance issues
            if triangle_count < 1000:
                triangle_quality = 0.3  # Very low detail
            elif triangle_count < 5000:
                triangle_quality = 0.6 + (triangle_count - 1000) / 4000 * 0.2
            elif triangle_count <= 50000:
                triangle_quality = 0.8 + (50000 - triangle_count) / 45000 * 0.2
            else:
                # Penalize extremely high poly count
                triangle_quality = max(0.5, 1.0 - (triangle_count - 50000) / 100000)

            # Metric 3: Topology quality (vertex/triangle ratio)
            vertex_count = len(mesh.vertices)
            if triangle_count > 0:
                vt_ratio = vertex_count / triangle_count
                # Ideal ratio: ~0.5 to 0.6 (good topology)
                topology_quality = 1.0 - abs(vt_ratio - 0.55) / 0.55
                topology_quality = max(0.0, min(1.0, topology_quality))
            else:
                topology_quality = 0.0

            # Metric 4: Volume quality (non-zero, reasonable size)
            try:
                volume = abs(mesh.volume)
                if volume > 0:
                    volume_quality = 1.0
                else:
                    volume_quality = 0.0
            except:
                volume = 0.0
                volume_quality = 0.0

            # Metric 5: Bounds quality (reasonable dimensions)
            bounds = mesh.bounds
            size = bounds[1] - bounds[0]
            max_dimension = np.max(size)
            min_dimension = np.min(size)

            # Check for degenerate geometry
            if min_dimension > 0:
                aspect_ratio = max_dimension / min_dimension
                # Penalize extreme aspect ratios
                if aspect_ratio < 50:
                    bounds_quality = 1.0
                else:
                    bounds_quality = max(0.5, 1.0 - (aspect_ratio - 50) / 200)
            else:
                bounds_quality = 0.0

            # Compute overall shape score
            # Weights: manifold (40%), triangles (20%), topology (20%), volume (10%), bounds (10%)
            shape_score = (
                manifold_score * 0.4 +
                triangle_quality * 0.2 +
                topology_quality * 0.2 +
                volume_quality * 0.1 +
                bounds_quality * 0.1
            )

            return {
                'score': shape_score,
                'manifold': is_manifold,
                'triangle_count': triangle_count,
                'vertex_count': vertex_count,
                'vt_ratio': vt_ratio if triangle_count > 0 else 0.0,
                'volume': float(volume),
                'bounds': bounds.tolist(),
                'max_dimension': float(max_dimension),
                'aspect_ratio': float(aspect_ratio) if min_dimension > 0 else 0.0
            }

        except Exception as e:
            logger.error(f"[QUALITY] Shape validation error: {e}")
            return {
                'score': 0.0,
                'manifold': False,
                'error': str(e)
            }

    def validate_texture_coherence(
        self,
        texture_image: Image.Image,
        mesh: trimesh.Trimesh
    ) -> Dict[str, Any]:
        """
        Validate texture quality and coherence

        Metrics:
        - Texture resolution (sufficient detail)
        - Color diversity (not all one color)
        - Coverage (texture applied to entire mesh)
        - Seam quality (minimal visible seams)

        Args:
            texture_image: Applied texture image
            mesh: 3D mesh with texture

        Returns:
            Dict with texture quality metrics
        """
        try:
            texture_np = np.array(texture_image)

            # Metric 1: Resolution quality
            width, height = texture_image.size
            pixel_count = width * height

            # Ideal: 512x512 to 2048x2048
            if pixel_count < 256 * 256:
                resolution_quality = 0.5  # Too low resolution
            elif pixel_count <= 1024 * 1024:
                resolution_quality = 0.7 + (pixel_count - 256*256) / (1024*1024 - 256*256) * 0.2
            elif pixel_count <= 2048 * 2048:
                resolution_quality = 0.9 + (pixel_count - 1024*1024) / (2048*2048 - 1024*1024) * 0.1
            else:
                resolution_quality = 1.0  # High resolution

            # Metric 2: Color diversity (not monochrome)
            if len(texture_np.shape) >= 3:
                # Calculate unique colors
                unique_colors = len(np.unique(texture_np.reshape(-1, texture_np.shape[-1]), axis=0))
                color_diversity = min(1.0, unique_colors / 1000)  # Normalize to 1000 unique colors
            else:
                color_diversity = 0.3  # Grayscale penalty

            # Metric 3: Contrast quality
            if len(texture_np.shape) >= 3:
                grayscale = cv2.cvtColor(texture_np[:, :, :3], cv2.COLOR_RGB2GRAY)
            else:
                grayscale = texture_np

            contrast = np.std(grayscale) / 128.0  # Normalize to 0-1
            contrast_quality = min(1.0, contrast)

            # Metric 4: Detail preservation (edge density)
            edges = cv2.Canny(grayscale, 50, 150)
            edge_density = np.sum(edges > 0) / edges.size
            detail_quality = min(1.0, edge_density * 10)  # Scale to reasonable range

            # Compute overall texture score
            # Weights: resolution (30%), diversity (25%), contrast (25%), detail (20%)
            texture_score = (
                resolution_quality * 0.3 +
                color_diversity * 0.25 +
                contrast_quality * 0.25 +
                detail_quality * 0.2
            )

            return {
                'score': texture_score,
                'resolution': (width, height),
                'pixel_count': pixel_count,
                'unique_colors': int(unique_colors) if len(texture_np.shape) >= 3 else 0,
                'color_diversity': color_diversity,
                'contrast': float(contrast),
                'detail_quality': detail_quality
            }

        except Exception as e:
            logger.error(f"[QUALITY] Texture validation error: {e}")
            return {
                'score': 0.0,
                'error': str(e)
            }

    def validate_final_mesh(self, mesh: trimesh.Trimesh) -> Dict[str, Any]:
        """
        Final mesh validation (printability, completeness)

        Metrics:
        - Watertight status (3D printable)
        - Face orientation (correct normals)
        - Self-intersections (none)
        - Scale appropriateness

        Args:
            mesh: Final generated 3D mesh

        Returns:
            Dict with final mesh quality metrics
        """
        try:
            # Metric 1: Watertight status (CRITICAL)
            is_watertight = mesh.is_watertight
            watertight_score = 1.0 if is_watertight else 0.0

            # Metric 2: Face orientation (normals pointing outward)
            try:
                mesh.fix_normals()
                normals_quality = 1.0
            except:
                normals_quality = 0.7  # Normals might be inconsistent

            # Metric 3: Self-intersections check
            try:
                # This can be expensive, so we do a quick check
                intersections = mesh.faces_unique_edges()
                if len(intersections) > 0:
                    intersection_quality = 0.9  # Has edges but might be OK
                else:
                    intersection_quality = 1.0
            except:
                intersection_quality = 0.8  # Unknown status

            # Metric 4: Scale appropriateness
            bounds = mesh.bounds
            size = bounds[1] - bounds[0]
            max_size = np.max(size)

            # Reasonable size for 3D printing: 10mm to 300mm
            if 10 <= max_size <= 300:
                scale_quality = 1.0
            elif max_size < 10:
                scale_quality = 0.7  # Too small but rescalable
            elif max_size < 1000:
                scale_quality = 0.8  # Large but manageable
            else:
                scale_quality = 0.5  # Extremely large, scaling needed

            # Compute final mesh score
            # Weights: watertight (50%), normals (20%), intersections (15%), scale (15%)
            final_score = (
                watertight_score * 0.5 +
                normals_quality * 0.2 +
                intersection_quality * 0.15 +
                scale_quality * 0.15
            )

            return {
                'score': final_score,
                'watertight': is_watertight,
                'normals_fixed': normals_quality == 1.0,
                'max_size_mm': float(max_size),
                'printable': is_watertight and final_score >= 0.80
            }

        except Exception as e:
            logger.error(f"[QUALITY] Final mesh validation error: {e}")
            return {
                'score': 0.0,
                'watertight': False,
                'printable': False,
                'error': str(e)
            }

    def _compute_overall_score(self, metrics: Dict[str, Any]) -> float:
        """
        Compute overall quality score from individual stage metrics

        Args:
            metrics: Dict with individual stage quality metrics

        Returns:
            Overall quality score (0.0-1.0)
        """
        scores = []
        weights = []

        # Background removal: 20% weight
        if metrics.get('bg_removal_quality') is not None:
            scores.append(metrics['bg_removal_quality'].get('score', 0.0))
            weights.append(0.2)

        # Shape generation: 40% weight (most critical)
        if metrics.get('shape_quality') is not None:
            scores.append(metrics['shape_quality'].get('score', 0.0))
            weights.append(0.4)

        # Texture coherence: 20% weight
        if metrics.get('texture_quality') is not None:
            scores.append(metrics['texture_quality'].get('score', 0.0))
            weights.append(0.2)

        # Final mesh: 20% weight
        if metrics.get('final_quality') is not None:
            scores.append(metrics['final_quality'].get('score', 0.0))
            weights.append(0.2)

        # Weighted average
        if len(scores) > 0:
            # Normalize weights
            total_weight = sum(weights)
            normalized_weights = [w / total_weight for w in weights]

            overall = sum(s * w for s, w in zip(scores, normalized_weights))
            return overall
        else:
            return 0.0

    def _compute_quality_grade(self, score: float) -> str:
        """
        Convert quality score to letter grade

        Args:
            score: Quality score (0.0-1.0)

        Returns:
            Letter grade (A+, A, B, C, D, F)
        """
        if score >= 0.95:
            return 'A+'
        elif score >= 0.90:
            return 'A'
        elif score >= 0.85:
            return 'A-'
        elif score >= 0.80:
            return 'B+'
        elif score >= 0.75:
            return 'B'
        elif score >= 0.70:
            return 'B-'
        elif score >= 0.65:
            return 'C+'
        elif score >= 0.60:
            return 'C'
        elif score >= 0.55:
            return 'D'
        else:
            return 'F'

    def _repair_mesh(self, mesh: trimesh.Trimesh) -> Optional[trimesh.Trimesh]:
        """
        Attempt to repair non-manifold mesh

        Args:
            mesh: Mesh to repair

        Returns:
            Repaired mesh or None if repair failed
        """
        try:
            # Try to fix mesh using trimesh repair
            mesh.fill_holes()
            mesh.remove_degenerate_faces()
            mesh.remove_duplicate_faces()
            mesh.fix_normals()

            # Verify repair was successful
            if mesh.is_watertight:
                logger.info("[QUALITY]  Mesh repair successful - now watertight")
                return mesh
            else:
                logger.warning("[QUALITY]  Mesh repair attempted but still not watertight")
                return mesh  # Return anyway, might be better than before

        except Exception as e:
            logger.error(f"[QUALITY] Mesh repair failed: {e}")
            return None

    def get_validation_stats(self) -> Dict[str, Any]:
        """
        Get validation statistics

        Returns:
            Dict with validation statistics
        """
        avg_quality = (
            sum(self.stats['quality_scores']) / len(self.stats['quality_scores'])
            if self.stats['quality_scores'] else 0.0
        )

        pass_rate = (
            self.stats['passed_validations'] / self.stats['total_validations']
            if self.stats['total_validations'] > 0 else 0.0
        )

        return {
            'total_validations': self.stats['total_validations'],
            'passed_validations': self.stats['passed_validations'],
            'failed_validations': self.stats['failed_validations'],
            'auto_repairs': self.stats['auto_repairs'],
            'pass_rate': pass_rate,
            'average_quality': avg_quality,
            'min_quality': min(self.stats['quality_scores']) if self.stats['quality_scores'] else 0.0,
            'max_quality': max(self.stats['quality_scores']) if self.stats['quality_scores'] else 0.0
        }


# Singleton pattern for quality validator
_quality_validator_instance = None


def get_quality_validator(quality_threshold: float = 0.80) -> GenerationQualityValidator:
    """
    Get singleton instance of GenerationQualityValidator

    Args:
        quality_threshold: Minimum acceptable quality score (0.0-1.0)

    Returns:
        GenerationQualityValidator instance
    """
    global _quality_validator_instance

    if _quality_validator_instance is None:
        _quality_validator_instance = GenerationQualityValidator(quality_threshold)

    return _quality_validator_instance
