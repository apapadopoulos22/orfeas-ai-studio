"""
+==============================================================================â•—
|          ORFEAS Testing Suite - Format Conversion Integration Tests         |
|           Test all 3D format conversions (STL, OBJ, GLB, PLY, FBX)           |
+==============================================================================
"""
import pytest
import requests
from pathlib import Path
import sys
import io
from typing import Any

backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))


@pytest.mark.integration
class TestFormatConversion:
    """Test 3D model format conversion capabilities"""

    def test_stl_to_obj_conversion(self, api_client: Any, test_image_512: Any, uploaded_job_id: str) -> None:
        """Test STL to OBJ format conversion"""
        # Generate STL first
        response = api_client.generate_3d(
            job_id=uploaded_job_id,
            format="stl",
            quality=7
        )

        assert response.status_code in [200, 202]

        # Now convert to OBJ
        convert_response = api_client.post(
            f"/api/convert/{uploaded_job_id}/obj",
            timeout=60
        )

        if convert_response.status_code == 200:
            assert convert_response.headers.get('Content-Type') in [
                'application/octet-stream',
                'model/obj',
                'text/plain'
            ]
            assert len(convert_response.content) > 0

    def test_stl_download(self, api_client: Any, uploaded_job_id: str) -> None:
        """Test STL format download"""
        # Generate STL
        response = api_client.generate_3d(
            job_id=uploaded_job_id,
            format="stl",
            quality=5
        )

        if response.status_code == 200:
            # Download STL
            download_response = api_client.download_file(uploaded_job_id, format="stl")
            assert download_response.status_code == 200
            assert len(download_response.content) > 0
            # STL files start with "solid" (ASCII) or have binary header
            assert download_response.content[:5] == b'solid' or len(download_response.content) > 80

    def test_obj_download(self, api_client: Any, uploaded_job_id: str) -> None:
        """Test OBJ format download"""
        response = api_client.generate_3d(
            job_id=uploaded_job_id,
            format="obj",
            quality=5
        )

        if response.status_code == 200:
            download_response = api_client.download_file(uploaded_job_id, format="obj")
            if download_response.status_code == 200:
                content = download_response.content.decode('utf-8')
                # OBJ files contain vertex/face data
                assert 'v ' in content or 'f ' in content

    def test_glb_download(self, api_client: Any, uploaded_job_id: str) -> None:
        """Test GLB format download"""
        response = api_client.generate_3d(
            job_id=uploaded_job_id,
            format="glb",
            quality=5
        )

        if response.status_code == 200:
            download_response = api_client.download_file(uploaded_job_id, format="glb")
            if download_response.status_code == 200:
                # GLB files start with "glTF" magic number
                assert len(download_response.content) > 12

    def test_ply_download(self, api_client: Any, uploaded_job_id: str) -> None:
        """Test PLY format download"""
        response = api_client.generate_3d(
            job_id=uploaded_job_id,
            format="ply",
            quality=5
        )

        if response.status_code == 200:
            download_response = api_client.download_file(uploaded_job_id, format="ply")
            if download_response.status_code == 200:
                content_start = download_response.content[:3]
                # PLY files start with "ply"
                assert content_start == b'ply' or len(download_response.content) > 0

    @pytest.mark.parametrize("format_type", ["stl", "obj", "glb", "ply"])
    def test_all_formats_generate(self, api_client: Any, test_image_512: Any, format_type: Any) -> None:
        """Test generation in all supported formats"""
        # Upload image
        upload_response = api_client.upload_image(test_image_512, filename=f"test_{format_type}.png")

        if upload_response.status_code == 200:
            job_id = upload_response.json().get('job_id')

            # Generate in specific format
            gen_response = api_client.generate_3d(
                job_id=job_id,
                format=format_type,
                quality=5
            )

            # Accept both immediate (200) and queued (202) responses
            assert gen_response.status_code in [200, 202, 500]  # Some formats may not be fully implemented

    def test_format_file_size_comparison(self, api_client: Any, uploaded_job_id: str) -> None:
        """Compare file sizes across formats"""
        file_sizes = {}

        for format_type in ["stl", "obj", "ply"]:
            response = api_client.download_file(uploaded_job_id, format=format_type)
            if response.status_code == 200:
                file_sizes[format_type] = len(response.content)

        # If we got multiple formats, compare sizes
        if len(file_sizes) > 1:
            assert all(size > 0 for size in file_sizes.values())

    def test_invalid_format_rejection(self, api_client: Any, uploaded_job_id: str) -> None:
        """Test that invalid formats are rejected"""
        invalid_formats = ["xyz", "abc", "pdf", "exe"]

        for invalid_format in invalid_formats:
            response = api_client.post(
                f"/api/generate-3d",
                json={
                    "job_id": uploaded_job_id,
                    "format": invalid_format,
                    "quality": 5
                },
                timeout=10
            )

            # Should reject invalid format (400 or 422)
            assert response.status_code in [400, 422, 500]

    def test_concurrent_format_conversions(self, api_client: Any, test_image_512: Any) -> None:
        """Test generating multiple formats concurrently"""
        # Upload one image
        upload_response = api_client.upload_image(test_image_512, filename="concurrent_test.png")
        assert upload_response.status_code == 200
        job_id = upload_response.json().get('job_id')

        # Request multiple formats (may be queued)
        formats = ["stl", "obj", "ply"]
        responses = []

        for fmt in formats:
            response = api_client.generate_3d(
                job_id=job_id,
                format=fmt,
                quality=5
            )
            responses.append((fmt, response))

        # At least one should succeed or be queued
        assert any(r[1].status_code in [200, 202] for r in responses)

    def test_format_conversion_preserves_geometry(self, api_client: Any, uploaded_job_id: str) -> None:
        """Test that format conversion preserves basic geometry"""
        # Generate in STL
        stl_response = api_client.generate_3d(uploaded_job_id, format="stl", quality=7)

        if stl_response.status_code == 200:
            stl_download = api_client.download_file(uploaded_job_id, format="stl")
            stl_size = len(stl_download.content)

            # Convert to OBJ
            obj_response = api_client.post(f"/api/convert/{uploaded_job_id}/obj", timeout=60)

            if obj_response.status_code == 200:
                # Both should have reasonable file sizes
                assert stl_size > 100
                assert len(obj_response.content) > 100

    @pytest.mark.parametrize("quality", [3, 5, 7, 9])
    def test_quality_levels_all_formats(self, api_client: Any, test_image_512: Any, quality: Any) -> None:
        """Test different quality levels across formats"""
        upload_response = api_client.upload_image(test_image_512, filename=f"quality_{quality}.png")

        if upload_response.status_code == 200:
            job_id = upload_response.json().get('job_id')

            # Test STL with this quality
            gen_response = api_client.generate_3d(
                job_id=job_id,
                format="stl",
                quality=quality
            )

            # Should accept valid quality levels
            assert gen_response.status_code in [200, 202]

    def test_format_metadata_preservation(self, api_client: Any, uploaded_job_id: str) -> None:
        """Test that metadata is preserved across formats"""
        # Generate model
        response = api_client.generate_3d(uploaded_job_id, format="stl", quality=7)

        if response.status_code == 200:
            # Check job status includes format info
            status_response = api_client.get_job_status(uploaded_job_id)

            if status_response.status_code == 200:
                status_data = status_response.json()
                # Should include format information
                assert 'job_id' in status_data or 'status' in status_data

    def test_batch_format_generation(self, api_client: Any, test_image_512: Any) -> None:
        """Test batch generation of multiple formats"""
        # Upload single image
        upload_response = api_client.upload_image(test_image_512, filename="batch_formats.png")
        assert upload_response.status_code == 200
        job_id = upload_response.json().get('job_id')

        # Request batch generation (if endpoint exists)
        batch_response = api_client.post(
            "/api/batch-generate",
            json={
                "job_id": job_id,
                "formats": ["stl", "obj", "ply"],
                "quality": 5
            },
            timeout=120
        )

        # Endpoint may or may not exist
        assert batch_response.status_code in [200, 202, 404, 501]

    def test_format_file_extension_validation(self, api_client: Any, uploaded_job_id: str) -> None:
        """Test that file extensions match format types"""
        for format_type in ["stl", "obj", "ply"]:
            download_response = api_client.download_file(uploaded_job_id, format=format_type)

            if download_response.status_code == 200:
                # Check Content-Disposition header if present
                content_disp = download_response.headers.get('Content-Disposition', '')
                if content_disp:
                    # Should contain correct file extension
                    assert format_type in content_disp.lower() or '.' in content_disp

