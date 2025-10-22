"""
ORFEAS AI 2Dâ†’3D Studio - Quality Validator Tests
================================================
ORFEAS AI Project

Purpose: Comprehensive test suite for GenerationQualityValidator
Coverage: All validation stages, quality scoring, auto-repair, integration
"""

import pytest
import numpy as np
from PIL import Image
import trimesh
import sys
from pathlib import Path
from typing import Any

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from quality_validator import GenerationQualityValidator, get_quality_validator


class TestGenerationQualityValidator:
    """Test GenerationQualityValidator class"""

    @pytest.fixture
    def validator(self) -> None:
        """Create validator instance for testing"""
        return GenerationQualityValidator(quality_threshold=0.80)

    @pytest.fixture
    def sample_image(self) -> None:
        """Create sample test image"""
        return Image.new('RGB', (512, 512), color=(128, 128, 128))

    @pytest.fixture
    def sample_bg_removed(self) -> None:
        """Create sample background-removed image with alpha"""
        img = Image.new('RGBA', (512, 512), color=(128, 128, 128, 255))
        # Make outer border transparent (simulating bg removal)
        pixels = img.load()
        for i in range(512):
            for j in range(512):
                if i < 50 or i > 462 or j < 50 or j > 462:
                    pixels[i, j] = (0, 0, 0, 0)  # Transparent
        return img

    @pytest.fixture
    def sample_mesh_good(self) -> None:
        """Create good quality sample mesh (manifold)"""
        # Create simple cube (watertight)
        return trimesh.creation.box(extents=[100, 100, 100])

    @pytest.fixture
    def sample_mesh_bad(self) -> None:
        """Create poor quality mesh (non-manifold)"""
        # Create mesh with duplicate vertices and degenerate faces
        vertices = np.array([
            [0, 0, 0],
            [1, 0, 0],
            [1, 1, 0],
            [0, 1, 0],
            [0, 0, 0],  # Duplicate vertex
        ])
        faces = np.array([
            [0, 1, 2],
            [0, 2, 3],
            [0, 0, 0],  # Degenerate face
        ])
        return trimesh.Trimesh(vertices=vertices, faces=faces)

    # ===== Background Removal Tests =====

    def test_background_removal_good_quality(self, validator: Any, sample_image: Any, sample_bg_removed: Any) -> None:
        """Test background removal validation with good quality"""
        result = validator.validate_background_removal(sample_image, sample_bg_removed)

        assert 'score' in result
        assert result['score'] > 0.5  # Should be reasonable quality
        assert 'coverage_ratio' in result
        assert 'edge_sharpness' in result
        assert 'subject_preservation' in result

        print(f"\n[TEST] Background removal quality: {result['score']:.3f}")

    def test_background_removal_low_coverage(self, validator: Any, sample_image: Any) -> None:
        """Test background removal with very low subject coverage"""
        # Create mostly transparent image
        bg_removed = Image.new('RGBA', (512, 512), color=(0, 0, 0, 0))
        # Only small subject in center
        pixels = bg_removed.load()
        for i in range(200, 300):
            for j in range(200, 300):
                pixels[i, j] = (128, 128, 128, 255)

        result = validator.validate_background_removal(sample_image, bg_removed)

        assert 'score' in result
        assert 'coverage_ratio' in result
        # Coverage should be low (only 100x100 out of 512x512)
        assert result['coverage_ratio'] < 0.1

        print(f"\n[TEST] Low coverage score: {result['score']:.3f}")

    def test_background_removal_no_alpha(self, validator: Any, sample_image: Any) -> None:
        """Test background removal without alpha channel"""
        bg_removed = Image.new('RGB', (512, 512), color=(128, 128, 128))

        result = validator.validate_background_removal(sample_image, bg_removed)

        assert 'score' in result
        assert result['score'] >= 0.0  # Should handle gracefully

    # ===== Shape Generation Tests =====

    def test_shape_validation_good_mesh(self, validator: Any, sample_mesh_good: Any) -> None:
        """Test shape validation with good quality manifold mesh"""
        result = validator.validate_shape_generation(sample_mesh_good)

        assert 'score' in result
        assert result['score'] > 0.7  # Good quality mesh
        assert result['manifold'] == True
        assert result['triangle_count'] > 0
        assert result['vertex_count'] > 0
        assert result['volume'] > 0

        print(f"\n[TEST] Good mesh quality: {result['score']:.3f}")
        print(f"[TEST] Manifold: {result['manifold']}")
        print(f"[TEST] Triangles: {result['triangle_count']}")

    def test_shape_validation_bad_mesh(self, validator: Any, sample_mesh_bad: Any) -> None:
        """Test shape validation with poor quality non-manifold mesh"""
        result = validator.validate_shape_generation(sample_mesh_bad)

        assert 'score' in result
        # Bad mesh should have lower score
        assert result['manifold'] == False

        print(f"\n[TEST] Bad mesh quality: {result['score']:.3f}")
        print(f"[TEST] Manifold: {result['manifold']}")

    def test_shape_validation_high_poly(self, validator: Any) -> None:
        """Test shape validation with very high polygon count"""
        # Create mesh with many triangles (100k+)
        mesh = trimesh.creation.icosphere(subdivisions=7)  # ~100k triangles

        result = validator.validate_shape_generation(mesh)

        assert 'score' in result
        assert result['triangle_count'] > 50000
        # High poly count should be penalized slightly

        print(f"\n[TEST] High poly mesh quality: {result['score']:.3f}")
        print(f"[TEST] Triangle count: {result['triangle_count']}")

    def test_shape_validation_low_poly(self, validator: Any) -> None:
        """Test shape validation with very low polygon count"""
        # Create simple tetrahedron (4 triangles)
        vertices = np.array([
            [0, 0, 0],
            [1, 0, 0],
            [0.5, 1, 0],
            [0.5, 0.5, 1]
        ])
        faces = np.array([
            [0, 1, 2],
            [0, 1, 3],
            [1, 2, 3],
            [0, 2, 3]
        ])
        mesh = trimesh.Trimesh(vertices=vertices, faces=faces)

        result = validator.validate_shape_generation(mesh)

        assert 'score' in result
        assert result['triangle_count'] < 100
        # Very low poly should be penalized

        print(f"\n[TEST] Low poly mesh quality: {result['score']:.3f}")
        print(f"[TEST] Triangle count: {result['triangle_count']}")

    # ===== Texture Validation Tests =====

    def test_texture_validation_good_quality(self, validator: Any, sample_mesh_good: Any) -> None:
        """Test texture validation with good quality texture"""
        # Create colorful, detailed texture
        texture = Image.new('RGB', (1024, 1024))
        pixels = texture.load()
        for i in range(1024):
            for j in range(1024):
                pixels[i, j] = (
                    (i * 255) // 1024,
                    (j * 255) // 1024,
                    ((i + j) * 128) // 1024
                )

        result = validator.validate_texture_coherence(texture, sample_mesh_good)

        assert 'score' in result
        assert result['score'] > 0.5
        assert result['resolution'] == (1024, 1024)
        assert result['unique_colors'] > 100

        print(f"\n[TEST] Good texture quality: {result['score']:.3f}")
        print(f"[TEST] Unique colors: {result['unique_colors']}")

    def test_texture_validation_low_resolution(self, validator: Any, sample_mesh_good: Any) -> None:
        """Test texture validation with low resolution"""
        texture = Image.new('RGB', (128, 128), color=(128, 128, 128))

        result = validator.validate_texture_coherence(texture, sample_mesh_good)

        assert 'score' in result
        assert result['resolution'] == (128, 128)
        # Low resolution should be penalized

        print(f"\n[TEST] Low resolution texture quality: {result['score']:.3f}")

    def test_texture_validation_monochrome(self, validator: Any, sample_mesh_good: Any) -> None:
        """Test texture validation with single color"""
        texture = Image.new('RGB', (512, 512), color=(100, 100, 100))

        result = validator.validate_texture_coherence(texture, sample_mesh_good)

        assert 'score' in result
        # Monochrome should have low color diversity
        assert result['color_diversity'] < 0.5

        print(f"\n[TEST] Monochrome texture quality: {result['score']:.3f}")
        print(f"[TEST] Color diversity: {result['color_diversity']:.3f}")

    # ===== Final Mesh Tests =====

    def test_final_mesh_validation_watertight(self, validator: Any, sample_mesh_good: Any) -> None:
        """Test final mesh validation with watertight mesh"""
        result = validator.validate_final_mesh(sample_mesh_good)

        assert 'score' in result
        assert result['watertight'] == True
        assert result['printable'] == True
        assert result['score'] > 0.8

        print(f"\n[TEST] Watertight mesh final quality: {result['score']:.3f}")
        print(f"[TEST] Printable: {result['printable']}")

    def test_final_mesh_validation_non_watertight(self, validator: Any, sample_mesh_bad: Any) -> None:
        """Test final mesh validation with non-watertight mesh"""
        result = validator.validate_final_mesh(sample_mesh_bad)

        assert 'score' in result
        assert result['watertight'] == False
        assert result['printable'] == False

        print(f"\n[TEST] Non-watertight mesh final quality: {result['score']:.3f}")
        print(f"[TEST] Printable: {result['printable']}")

    def test_final_mesh_validation_scale(self, validator: Any) -> None:
        """Test final mesh validation with different scales"""
        # Test tiny mesh (< 10mm)
        tiny_mesh = trimesh.creation.box(extents=[5, 5, 5])
        result_tiny = validator.validate_final_mesh(tiny_mesh)

        # Test normal mesh (10-300mm)
        normal_mesh = trimesh.creation.box(extents=[100, 100, 100])
        result_normal = validator.validate_final_mesh(normal_mesh)

        # Test huge mesh (> 1000mm)
        huge_mesh = trimesh.creation.box(extents=[2000, 2000, 2000])
        result_huge = validator.validate_final_mesh(huge_mesh)

        # Normal scale should have highest score
        assert result_normal['score'] >= result_tiny['score']
        assert result_normal['score'] >= result_huge['score']

        print(f"\n[TEST] Tiny mesh scale quality: {result_tiny['score']:.3f}")
        print(f"\n[TEST] Normal mesh scale quality: {result_normal['score']:.3f}")
        print(f"\n[TEST] Huge mesh scale quality: {result_huge['score']:.3f}")

    # ===== Full Pipeline Tests =====

    def test_full_pipeline_validation_success(self, validator: Any, sample_image: Any, sample_bg_removed: Any, sample_mesh_good: Any) -> None:
        """Test full pipeline validation with good quality at all stages"""
        texture = Image.new('RGB', (512, 512), color=(128, 128, 128))

        result = validator.validate_generation_pipeline(
            original_image=sample_image,
            bg_removed_image=sample_bg_removed,
            generated_mesh=sample_mesh_good,
            texture_image=texture
        )

        assert 'overall_score' in result
        assert 'quality_grade' in result
        assert 'issues_detected' in result
        assert 'passed_threshold' in result

        # Good quality should pass threshold
        assert result['overall_score'] > 0.5

        print(f"\n[TEST] Full pipeline quality: {result['overall_score']:.3f}")
        print(f"[TEST] Quality grade: {result['quality_grade']}")
        print(f"[TEST] Passed threshold: {result['passed_threshold']}")
        print(f"[TEST] Issues detected: {len(result['issues_detected'])}")

    def test_full_pipeline_validation_low_quality(self, validator: Any, sample_image: Any, sample_mesh_bad: Any) -> None:
        """Test full pipeline validation with poor quality"""
        result = validator.validate_generation_pipeline(
            original_image=sample_image,
            generated_mesh=sample_mesh_bad
        )

        assert 'overall_score' in result
        assert 'issues_detected' in result

        # Bad mesh should trigger issues
        assert len(result['issues_detected']) > 0

        print(f"\n[TEST] Low quality pipeline score: {result['overall_score']:.3f}")
        print(f"[TEST] Issues detected: {result['issues_detected']}")

    def test_full_pipeline_auto_repair(self, validator: Any, sample_image: Any, sample_mesh_bad: Any) -> None:
        """Test auto-repair functionality in full pipeline"""
        result = validator.validate_generation_pipeline(
            original_image=sample_image,
            generated_mesh=sample_mesh_bad
        )

        assert 'auto_repairs_applied' in result

        # Should attempt repair for non-manifold mesh
        if not sample_mesh_bad.is_watertight:
            # Repair might have been attempted
            print(f"\n[TEST] Auto-repairs applied: {result['auto_repairs_applied']}")

    # ===== Quality Grade Tests =====

    def test_quality_grade_computation(self, validator: Any) -> None:
        """Test quality grade letter assignment"""
        assert validator._compute_quality_grade(0.98) == 'A+'
        assert validator._compute_quality_grade(0.92) == 'A'
        assert validator._compute_quality_grade(0.87) == 'A-'
        assert validator._compute_quality_grade(0.82) == 'B+'
        assert validator._compute_quality_grade(0.77) == 'B'
        assert validator._compute_quality_grade(0.72) == 'B-'
        assert validator._compute_quality_grade(0.50) == 'F'

        print("\n[TEST] Quality grade computation: PASSED")

    # ===== Statistics Tests =====

    def test_validation_statistics(self, validator: Any, sample_image: Any, sample_mesh_good: Any) -> None:
        """Test validation statistics tracking"""
        # Run multiple validations
        for i in range(5):
            validator.validate_generation_pipeline(
                original_image=sample_image,
                generated_mesh=sample_mesh_good
            )

        stats = validator.get_validation_stats()

        assert stats['total_validations'] >= 5
        assert 'passed_validations' in stats
        assert 'failed_validations' in stats
        assert 'auto_repairs' in stats
        assert 'pass_rate' in stats
        assert 'average_quality' in stats

        print(f"\n[TEST] Validation statistics:")
        print(f"  Total: {stats['total_validations']}")
        print(f"  Passed: {stats['passed_validations']}")
        print(f"  Failed: {stats['failed_validations']}")
        print(f"  Pass rate: {stats['pass_rate']:.1%}")
        print(f"  Average quality: {stats['average_quality']:.3f}")

    # ===== Singleton Tests =====

    def test_singleton_pattern(self) -> None:
        """Test singleton pattern for validator"""
        validator1 = get_quality_validator()
        validator2 = get_quality_validator()

        assert validator1 is validator2  # Same instance

        print("\n[TEST] Singleton pattern: PASSED")

    # ===== Edge Cases =====

    def test_validation_with_none_inputs(self, validator: Any, sample_image: Any) -> None:
        """Test validation handles None inputs gracefully"""
        result = validator.validate_generation_pipeline(
            original_image=sample_image,
            bg_removed_image=None,
            generated_mesh=None,
            texture_image=None
        )

        assert 'overall_score' in result
        # Should handle None gracefully

        print(f"\n[TEST] Validation with None inputs: {result['overall_score']:.3f}")

    def test_validation_error_handling(self, validator: Any) -> None:
        """Test error handling in validation"""
        # Create invalid mesh
        invalid_mesh = trimesh.Trimesh(vertices=[], faces=[])

        result = validator.validate_shape_generation(invalid_mesh)

        # Should return result even with errors
        assert 'score' in result

        print(f"\n[TEST] Error handling: {result.get('error', 'No error')}")


if __name__ == '__main__':
    # Run tests with verbose output
    pytest.main([__file__, '-v', '--tb=short'])
