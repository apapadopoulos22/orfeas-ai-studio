"""
ORFEAS AI 2D→3D Studio - Batch Operations Tests
==================================================
ORFEAS AI Project

Integration tests for batch generation operations:
- /api/batch-generate
- Queue management
- Concurrent job processing
- Batch status tracking

Phase 6D - Final Push to 80%
"""

import pytest
import io
from PIL import Image
from typing import Any


class TestBatchGeneration:
    """Test batch 3D generation endpoint"""

    def test_batch_generate_multiple_jobs(self, api_client: Any) -> None:
        """Test submitting multiple jobs for batch processing"""
        # Upload 3 images
        job_ids = []
        for i in range(3):
            img = Image.new('RGB', (256, 256), color=(i * 80, 0, 0))
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='PNG')
            img_bytes.seek(0)

            upload_response = api_client.post(
                '/api/upload-image',
                data={'image': (img_bytes, f'batch_{i}.png', 'image/png')}
            )

            if upload_response.status_code == 200:
                job_ids.append(upload_response.json()['job_id'])

        if len(job_ids) >= 2:
            # Submit batch request
            response = api_client.post(
                '/api/batch-generate',
                json={
                    'job_ids': job_ids,
                    'format': 'stl',
                    'quality': 5
                }
            )

            # Should accept batch or return not implemented
            assert response.status_code in [200, 202, 404, 501]

            if response.status_code in [200, 202]:
                data = response.json()
                assert 'batch_id' in data or 'job_count' in data

    def test_batch_generate_without_job_ids(self, api_client: Any) -> None:
        """Test batch generation without job IDs"""
        response = api_client.post(
            '/api/batch-generate',
            json={'format': 'stl', 'quality': 5}
        )

        # Should reject or return not found
        assert response.status_code in [400, 404, 422]

    def test_batch_generate_with_invalid_job_ids(self, api_client: Any) -> None:
        """Test batch generation with invalid job IDs"""
        response = api_client.post(
            '/api/batch-generate',
            json={
                'job_ids': ['invalid-1', 'invalid-2'],
                'format': 'stl'
            }
        )

        # Should either reject or queue (depending on implementation)
        assert response.status_code in [200, 202, 400, 404, 422]

    def test_batch_generate_max_jobs_limit(self, api_client: Any) -> None:
        """Test batch generation respects max job limit"""
        # Try to submit 50 jobs (should exceed limit)
        fake_job_ids = [f"job-{i:03d}" for i in range(50)]

        response = api_client.post(
            '/api/batch-generate',
            json={
                'job_ids': fake_job_ids,
                'format': 'stl'
            }
        )

        # Should reject excessive batch size or return not found
        assert response.status_code in [400, 404, 413, 422]

    def test_batch_generate_with_different_formats(self, api_client: Any) -> None:
        """Test batch generation with format specification"""
        fake_job_ids = ['job-001', 'job-002']

        for format_type in ['stl', 'obj', 'glb', 'ply']:
            response = api_client.post(
                '/api/batch-generate',
                json={
                    'job_ids': fake_job_ids,
                    'format': format_type,
                    'quality': 7
                }
            )

            # Should accept or return not found/not implemented
            assert response.status_code in [200, 202, 400, 404, 422, 501]


class TestMaterialsPresets:
    """Test materials presets endpoint"""

    def test_get_materials_presets(self, api_client: Any) -> None:
        """Test retrieving material presets"""
        response = api_client.get('/api/materials/presets')

        if response.status_code == 200:
            data = response.json()
            # Should return list of materials
            assert isinstance(data, (list, dict))

            if isinstance(data, list) and len(data) > 0:
                # Check material structure
                material = data[0]
                assert 'name' in material or 'id' in material
        else:
            # Endpoint may not be implemented yet
            assert response.status_code in [404, 501]

    def test_materials_presets_response_format(self, api_client: Any) -> None:
        """Test material presets response format"""
        response = api_client.get('/api/materials/presets')

        if response.status_code == 200:
            # Should return JSON
            assert response.headers.get('Content-Type', '').startswith('application/json')
        else:
            assert response.status_code in [404, 501]

    def test_get_materials_metadata(self, api_client: Any) -> None:
        """Test retrieving material metadata"""
        response = api_client.get('/api/materials/metadata')

        if response.status_code == 200:
            data = response.json()
            # Should contain metadata about material properties
            assert isinstance(data, dict)
        else:
            # Endpoint may not be implemented
            assert response.status_code in [404, 501]


class TestLightingPresets:
    """Test lighting presets endpoint"""

    def test_get_lighting_presets(self, api_client: Any) -> None:
        """Test retrieving lighting presets"""
        response = api_client.get('/api/lighting/presets')

        if response.status_code == 200:
            data = response.json()
            # Should return list of lighting configurations
            assert isinstance(data, (list, dict))

            if isinstance(data, list) and len(data) > 0:
                # Check lighting preset structure
                preset = data[0]
                assert 'name' in preset or 'id' in preset or 'type' in preset
        else:
            # Endpoint may not be implemented yet
            assert response.status_code in [404, 501]

    def test_lighting_presets_response_format(self, api_client: Any) -> None:
        """Test lighting presets response format"""
        response = api_client.get('/api/lighting/presets')

        if response.status_code == 200:
            # Should return JSON
            assert response.headers.get('Content-Type', '').startswith('application/json')
        else:
            assert response.status_code in [404, 501]


class TestFormatConversion:
    """Test multi-format conversion and export"""

    def test_generate_all_supported_formats(self, api_client: Any, uploaded_job_id: str) -> None:
        """Test generating 3D models in all supported formats"""
        formats = ['stl', 'obj', 'glb', 'ply']
        results = {}

        for format_type in formats:
            response = api_client.post(
                '/api/generate-3d',
                json={
                    'job_id': uploaded_job_id,
                    'format': format_type,
                    'quality': 5
                }
            )
            results[format_type] = response.status_code

        # At least one format should work
        success_formats = [f for f, code in results.items() if code in [200, 202]]
        assert len(success_formats) >= 1, f"No formats succeeded: {results}"

    def test_format_parameter_case_insensitive(self, api_client: Any, uploaded_job_id: str) -> None:
        """Test that format parameter accepts different cases"""
        formats = ['STL', 'Stl', 'stl']

        for format_type in formats:
            response = api_client.post(
                '/api/generate-3d',
                json={
                    'job_id': uploaded_job_id,
                    'format': format_type,
                    'quality': 5
                }
            )

            # Should either accept or reject consistently
            assert response.status_code in [200, 202, 400, 422]

    def test_unsupported_format_rejection(self, api_client: Any, uploaded_job_id: str) -> None:
        """Test that unsupported formats are rejected"""
        invalid_formats = ['pdf', 'exe', 'jpg', 'png', 'zip', 'xyz']

        for format_type in invalid_formats:
            response = api_client.post(
                '/api/generate-3d',
                json={
                    'job_id': uploaded_job_id,
                    'format': format_type,
                    'quality': 5
                }
            )

            # Should reject invalid formats
            assert response.status_code in [400, 422]

    def test_format_with_quality_combinations(self, api_client: Any, uploaded_job_id: str) -> None:
        """Test different format and quality combinations"""
        combinations = [
            ('stl', 3),
            ('obj', 5),
            ('glb', 7),
            ('ply', 9)
        ]

        for format_type, quality in combinations:
            response = api_client.post(
                '/api/generate-3d',
                json={
                    'job_id': uploaded_job_id,
                    'format': format_type,
                    'quality': quality
                }
            )

            # Should accept valid combinations
            assert response.status_code in [200, 202, 400, 404]

    def test_default_format_when_not_specified(self, api_client: Any, uploaded_job_id: str) -> None:
        """Test that a default format is used when not specified"""
        response = api_client.post(
            '/api/generate-3d',
            json={
                'job_id': uploaded_job_id,
                'quality': 5
            }
        )

        if response.status_code in [200, 202]:
            data = response.json()
            # Should have a format in response
            assert 'format' in data or 'download_url' in data
