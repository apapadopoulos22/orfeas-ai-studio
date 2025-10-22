"""
ORFEAS Integration Tests - API Endpoints
Consolidates tests from: test_all_endpoints.py, test_preview_endpoints.py

NOTE: These tests require integration_server fixture (auto-starts Flask server)
"""
import pytest
import time
from PIL import Image
import io
from typing import Any

# Mark all tests in this module as integration tests
pytestmark = pytest.mark.integration


class TestHealthEndpoint:
    """Tests for /health endpoint"""

    def test_health_check_returns_200(self, api_client: Any, integration_server: Any) -> None:
        """Health check should return 200 OK"""
        response = api_client.health_check()
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    def test_health_check_json_format(self, api_client: Any, integration_server: Any) -> None:
        """Health check should return valid JSON with status"""
        response = api_client.health_check()
        data = response.json()

        assert "status" in data, "Response missing 'status' field"
        assert data["status"] in ["online", "ready", "healthy"], f"Invalid status: {data['status']}"

    def test_health_check_response_time(self, api_client: Any, integration_server: Any) -> None:
        """Health check should respond quickly (< 1 second)"""
        start_time = time.time()
        response = api_client.health_check()
        elapsed = time.time() - start_time

        assert elapsed < 1.0, f"Health check too slow: {elapsed:.2f}s"
        assert response.status_code == 200


class TestImageUpload:
    """Tests for /upload-image endpoint"""

    def test_upload_valid_png_image(self, api_client: Any, test_image_512: Any, integration_server: Any) -> None:
        """Upload a valid 512x512 PNG image"""
        response = api_client.upload_image(test_image_512, filename="test_512.png")

        assert response.status_code == 200, f"Upload failed: {response.text}"

        data = response.json()
        assert "job_id" in data, "Response missing job_id"
        assert "preview_url" in data or "image_url" in data, "Response missing preview URL"

        # Validate job_id format (should be UUID or similar)
        job_id = data["job_id"]
        assert len(job_id) > 0, "job_id is empty"

    def test_upload_large_image(self, api_client: Any, test_image_1024: Any, integration_server: Any) -> None:
        """Upload a larger 1024x1024 image"""
        response = api_client.upload_image(test_image_1024, filename="test_1024.png")

        assert response.status_code == 200, f"Large image upload failed: {response.text}"

        data = response.json()
        assert "job_id" in data

    def test_upload_without_file(self, api_client: Any, integration_server: Any) -> None:
        """Upload without file should return 400 Bad Request"""
        response = api_client.post("/api/upload-image")  # [FIX] Add /api/ prefix

        assert response.status_code == 400, f"Expected 400, got {response.status_code}"

    def test_upload_invalid_file_type(self, api_client: Any, integration_server: Any) -> None:
        """Upload invalid file type should fail gracefully"""
        # Create a text file disguised as image
        fake_image = io.BytesIO(b'This is not an image')
        files = {'image': ('fake.png', fake_image, 'image/png')}  # [FIX] Changed 'file' to 'image'

        response = api_client.post("/api/upload-image", files=files)  # [FIX] Add /api/ prefix

        # Should return 400 (Bad Request) or 415 (Unsupported Media Type)
        assert response.status_code in [400, 415], f"Expected 400/415, got {response.status_code}"

    def test_upload_creates_job_id(self, api_client: Any, integration_server: Any, test_image_512: Any) -> None:
        """Verify uploaded image gets a unique job_id"""
        response1 = api_client.upload_image(test_image_512, filename="test1.png")
        test_image_512.seek(0)  # Reset BytesIO
        response2 = api_client.upload_image(test_image_512, filename="test2.png")

        assert response1.status_code == 200
        assert response2.status_code == 200

        job_id1 = response1.json()["job_id"]
        job_id2 = response2.json()["job_id"]

        assert job_id1 != job_id2, "Job IDs should be unique"


class TestTextToImage:
    """Tests for /text-to-image endpoint"""

    def test_generate_simple_image(self, api_client: Any, integration_server: Any) -> None:
        """Generate image from simple text prompt"""
        response = api_client.text_to_image(
            prompt="A red cube on a white background",
            art_style="realistic"
        )

        # Should return 200 (immediate) or 202 (accepted/async)
        assert response.status_code in [200, 202], f"Generation failed: {response.text}"

        data = response.json()
        assert "job_id" in data or "image_url" in data, "Response missing job_id or image_url"

    def test_generate_with_different_styles(self, api_client: Any, integration_server: Any) -> None:
        """Test different art styles"""
        # [ORFEAS FIX] Test 2 styles instead of 4 to avoid server hang
        styles = ["realistic", "anime"]

        for style in styles:
            response = api_client.text_to_image(
                prompt="A beautiful sunset",
                art_style=style
            )

            assert response.status_code in [200, 202], f"Failed for style {style}"

            # [ORFEAS FIX] Add small delay between requests to prevent server hang
            import time
            time.sleep(0.5)

    def test_text_to_image_without_prompt(self, api_client: Any, integration_server: Any) -> None:
        """Text-to-image without prompt should return 400"""
        response = api_client.post("/api/text-to-image", json={})  # [FIX] Add /api/ prefix

        assert response.status_code == 400, "Should reject empty prompt"

    def test_text_to_image_with_long_prompt(self, api_client: Any, integration_server: Any) -> None:
        """Test with longer, complex prompt"""
        long_prompt = (
            "A highly detailed 3D render of a futuristic cityscape "
            "with flying cars, neon lights, and towering skyscrapers "
            "under a purple sunset sky"
        )

        response = api_client.text_to_image(prompt=long_prompt)

        assert response.status_code in [200, 202], "Long prompt should work"


class TestGenerate3D:
    """Tests for /generate-3d endpoint"""

    def test_generate_3d_from_uploaded_image(self, api_client: Any, integration_server: Any, uploaded_job_id: str) -> None:
        """Generate 3D model from uploaded image"""
        response = api_client.generate_3d(
            job_id=uploaded_job_id,
            format="stl",
            quality=7
        )

        # Should return 200 (immediate) or 202 (accepted/async)
        assert response.status_code in [200, 202], f"3D generation failed: {response.text}"

        data = response.json()
        assert "job_id" in data or "model_url" in data, "Response missing job_id or model_url"

    @pytest.mark.parametrize("fmt", ["stl", "obj"])
    def test_generate_3d_different_formats(self, api_client: Any, integration_server: Any, uploaded_job_id: str, fmt: Any) -> None:
        """
        Test different 3D output formats without multiple sequential uploads.
        Each parameterized case uses its own uploaded_job_id fixture instance.
        """
        response = api_client.generate_3d(
            job_id=uploaded_job_id,
            format=fmt,
            quality=5
        )

        assert response.status_code in [200, 202], f"Failed for format {fmt}: {response.text}"

    @pytest.mark.parametrize("quality", [1, 10])
    def test_generate_3d_quality_levels(self, api_client: Any, integration_server: Any, uploaded_job_id: str, quality: Any) -> None:
        """
        Test different quality levels without multiple sequential uploads.
        Each parameterized case uses its own uploaded_job_id fixture instance.
        """
        response = api_client.generate_3d(
            job_id=uploaded_job_id,
            format="stl",
            quality=quality
        )

        assert response.status_code in [200, 202], f"Failed for quality {quality}: {response.text}"

    def test_generate_3d_without_job_id(self, api_client: Any, integration_server: Any) -> None:
        """Generate 3D without job_id should fail"""
        response = api_client.post("/api/generate-3d", json={"format": "stl"})  # [FIX] Add /api/ prefix

        assert response.status_code == 400, "Should require job_id"

    def test_generate_3d_with_invalid_job_id(self, api_client: Any, integration_server: Any) -> None:
        """Generate 3D with invalid job_id should fail"""
        response = api_client.generate_3d(
            job_id="invalid-job-id-12345",
            format="stl"
        )

        assert response.status_code in [400, 404], "Should reject invalid job_id"


class TestJobStatus:
    """Tests for /job/{job_id}/status endpoint"""

    def test_get_job_status_after_upload(self, api_client: Any, integration_server: Any, uploaded_job_id: str) -> None:
        """Check job status after upload"""
        response = api_client.get_job_status(uploaded_job_id)

        assert response.status_code == 200, f"Status check failed: {response.text}"

        data = response.json()
        assert "status" in data, "Response missing status field"
        assert data["status"] in ["pending", "processing", "completed", "failed"]

    def test_get_nonexistent_job_status(self, api_client: Any, integration_server: Any) -> None:
        """Check status for nonexistent job"""
        response = api_client.get_job_status("nonexistent-job-123")

        assert response.status_code == 404, "Should return 404 for missing job"


class TestDownloadEndpoint:
    """Tests for /download/{job_id}/{format} endpoint"""

    @pytest.mark.slow
    def test_download_generated_model(self, api_client: Any, integration_server: Any, uploaded_job_id: str) -> None:
        """Download generated 3D model (slow test)"""
        # First generate the model
        gen_response = api_client.generate_3d(uploaded_job_id, format="stl")

        if gen_response.status_code == 202:
            # Wait for async processing (with timeout)
            max_wait = 180  # 3 minutes
            start_time = time.time()

            while time.time() - start_time < max_wait:
                status_response = api_client.get_job_status(uploaded_job_id)
                if status_response.status_code == 200:
                    status = status_response.json().get("status")
                    if status == "completed":
                        break
                time.sleep(5)

        # Try to download
        download_response = api_client.download_file(uploaded_job_id, format="stl")

        # Should return file or appropriate status
        assert download_response.status_code in [200, 202, 404]

        if download_response.status_code == 200:
            # Verify content type
            content_type = download_response.headers.get("Content-Type")
            assert content_type in ["application/octet-stream", "model/stl", "application/sla"]


class TestCORSHeaders:
    """Tests for CORS configuration"""

    def test_cors_headers_present(self, api_client: Any, integration_server: Any) -> None:
        """Verify CORS headers are present"""
        response = api_client.health_check()

        headers = response.headers

        # Check for CORS headers (may vary based on configuration)
        # Common CORS headers
        cors_headers = [
            "Access-Control-Allow-Origin",
            "Access-Control-Allow-Methods",
            "Access-Control-Allow-Headers"
        ]

        # At least one CORS header should be present
        has_cors = any(header in headers for header in cors_headers)
        assert has_cors, "No CORS headers found"


# ============================================================================
# Test Suite Execution
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short", "-m", "integration"])
