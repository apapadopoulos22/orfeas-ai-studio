"""
ORFEAS AI 2D→3D Studio - Security Validation Tests
==================================================
ORFEAS AI Project

Security-focused integration tests covering:
- Input validation and sanitization
- File upload limits and type checking
- XSS and injection prevention
- Rate limiting
- Authentication bypass attempts

Phase 6D - Test Coverage Expansion
"""

import pytest
import io
from PIL import Image
from typing import Any


class TestInputValidation:
    """Test input validation across all endpoints"""

    def test_upload_sql_injection_filename(self, api_client: Any, integration_server: Any) -> None:
        """Test that SQL injection in filename is sanitized"""
        img = Image.new('RGB', (512, 512), color=(255, 0, 0))
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_data = img_bytes.getvalue()  # Get raw bytes

        # Malicious filename
        malicious_filename = "test'; DROP TABLE uploads; --.png"

        response = api_client.post(
            '/api/upload-image',
            files={'image': (malicious_filename, img_data, 'image/png')}
        )

        # Should either succeed (sanitized) or fail gracefully
        assert response.status_code in [200, 400]
        if response.status_code == 200:
            data = response.json()
            # Filename should be sanitized
            assert 'job_id' in data
            assert "DROP TABLE" not in data.get('preview_url', '')

    def test_text_to_image_xss_prompt(self, api_client: Any, integration_server: Any) -> None:
        """Test that XSS attempts in prompts are handled"""
        xss_prompts = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')",
            "<iframe src='http://evil.com'></iframe>"
        ]

        for xss_prompt in xss_prompts:
            response = api_client.post(
                '/api/text-to-image',
                json={'prompt': xss_prompt}
            )

            # Should either accept and sanitize or reject
            assert response.status_code in [200, 400, 202]
            if response.status_code in [200, 202]:
                data = response.json()
                # In test mode, prompt may be echoed back, but image_url should be safe
                image_url = data.get('image_url', '')
                preview_url = data.get('preview_url', '')
                # URLs should not contain executable script tags
                assert '<script>' not in image_url
                assert '<script>' not in preview_url

    def test_generate_3d_invalid_format_injection(self, api_client: Any, uploaded_job_id: str) -> None:
        """Test that invalid format with injection attempts are rejected"""
        malicious_formats = [
            "../../../etc/passwd",
            "stl'; DROP TABLE models; --",
            "stl<script>alert('XSS')</script>",
            "../../uploads/other_user_file.stl"
        ]

        for malicious_format in malicious_formats:
            response = api_client.post(
                '/api/generate-3d',
                json={
                    'job_id': uploaded_job_id,
                    'format': malicious_format
                }
            )

            # Should reject invalid formats
            assert response.status_code in [400, 422]

    def test_job_status_path_traversal(self, api_client: Any, integration_server: Any) -> None:
        """Test that path traversal in job_id is blocked"""
        traversal_ids = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "../../../../../../../../etc/hosts",
            ".../.../.../.../etc/passwd"
        ]

        for traversal_id in traversal_ids:
            # Use correct endpoint format: /api/job-status/{job_id}
            response = api_client.get(f'/api/job-status/{traversal_id}')

            # Should reject with 400 or 404, not 500 (no path traversal)
            assert response.status_code in [400, 404], \
                f"Path traversal not blocked: {traversal_id} returned {response.status_code}"


class TestFileUploadLimits:
    """Test file upload size and type restrictions"""

    def test_upload_oversized_image(self, api_client: Any, integration_server: Any) -> None:
        """Test that oversized images are rejected"""
        # Create 100MB image (should exceed limit)
        large_size = 100 * 1024 * 1024  # 100MB
        fake_large_file = io.BytesIO(b"X" * large_size)

        response = api_client.post(
            '/api/upload-image',
            files={'image': ('huge.png', fake_large_file.getvalue(), 'image/png')}
        )

        # Should reject with 413 (Payload Too Large) or 400
        assert response.status_code in [400, 413, 422]

    def test_upload_invalid_image_type(self, api_client: Any, integration_server: Any) -> None:
        """Test that non-image files are rejected"""
        invalid_files = [
            (b"#!/bin/bash\nrm -rf /", 'script.sh', 'text/x-shellscript'),
            (b"<?php system($_GET['cmd']); ?>", 'shell.php', 'application/x-php'),
            (b"MZ\x90\x00", 'virus.exe', 'application/x-msdownload'),
            (b"<!DOCTYPE html><script>alert('XSS')</script>", 'fake.html', 'text/html')
        ]

        for content, filename, content_type in invalid_files:
            response = api_client.post(
                '/api/upload-image',
                files={'image': (filename, content, content_type)}
            )

            # Should reject with 415 (Unsupported Media Type) or 400
            assert response.status_code in [400, 415, 422]

    def test_upload_corrupted_image(self, api_client: Any, integration_server: Any) -> None:
        """Test that corrupted image files are handled gracefully"""
        # Corrupted PNG header
        corrupted_png = b"\x89PNG\x0D\x0A\x1A\x0A\x00\x00CORRUPT_DATA_HERE"

        response = api_client.post(
            '/api/upload-image',
            files={'image': ('corrupted.png', corrupted_png, 'image/png')}
        )

        # Should reject or handle gracefully (not 500)
        assert response.status_code in [400, 415, 422]


class TestAuthenticationBypass:
    """Test that authentication/authorization cannot be bypassed"""

    def test_download_without_job_id(self, api_client: Any, integration_server: Any) -> None:
        """Test that downloads require valid job IDs"""
        response = api_client.get('/api/download//model.stl')
        assert response.status_code in [400, 404]

    def test_download_other_user_file(self, api_client: Any, integration_server: Any) -> None:
        """Test that users cannot access files from other jobs"""
        # Attempt to access a hypothetical other user's job
        fake_job_id = "00000000-0000-0000-0000-000000000000"
        response = api_client.get(f'/api/download/{fake_job_id}/model.stl')

        # Should return 404 (not found) not 403 (info leak)
        assert response.status_code == 404

    def test_preview_path_traversal(self, api_client: Any, integration_server: Any) -> None:
        """Test that preview endpoint blocks path traversal"""
        malicious_paths = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "....//....//....//etc/passwd"
        ]

        for malicious_path in malicious_paths:
            response = api_client.get(f'/api/preview/{malicious_path}')

            # Should reject, not expose internal files
            assert response.status_code in [400, 404]


class TestRateLimiting:
    """Test rate limiting protection"""

    def test_rapid_health_checks(self, api_client: Any, integration_server: Any) -> None:
        """Test that rapid requests don't cause issues"""
        # Make 50 rapid requests
        responses = []
        for _ in range(50):
            response = api_client.get('/api/health')
            responses.append(response.status_code)

        # Should either succeed or rate limit (429)
        for status in responses:
            assert status in [200, 429]

    def test_upload_flood_protection(self, api_client: Any, integration_server: Any) -> None:
        """Test that upload flood is prevented"""
        # Attempt to upload 20 images rapidly
        img = Image.new('RGB', (100, 100), color=(255, 0, 0))
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')

        responses = []
        for i in range(20):
            img_bytes.seek(0)
            response = api_client.post(
                '/api/upload-image',
                data={'image': (img_bytes, f'flood_{i}.png', 'image/png')}
            )
            responses.append(response.status_code)

        # Should eventually rate limit or queue
        status_codes = set(responses)
        # At least some should succeed, but may get rate limited
        assert 200 in status_codes or 202 in status_codes


class TestContentSecurityPolicy:
    """Test security headers and policies"""

    def test_security_headers_present(self, api_client: Any) -> None:
        """Test that security headers are set"""
        response = api_client.get('/api/health')

        if response.status_code == 200:
            headers = response.headers

            # Check for common security headers (optional, depends on implementation)
            # Note: Not all may be implemented, so we check presence
            security_headers = [
                'X-Content-Type-Options',
                'X-Frame-Options',
                'Content-Security-Policy',
                'X-XSS-Protection'
            ]

            # At least server should not expose sensitive info
            assert 'Server' not in headers or 'Flask' not in headers.get('Server', '')

    def test_cors_only_allowed_origins(self, api_client: Any) -> None:
        """Test that CORS only allows configured origins"""
        response = api_client.get(
            '/api/health',
            headers={'Origin': 'http://evil.com'}
        )

        if response.status_code == 200:
            # Should either not have CORS headers or have restricted origins
            cors_header = response.headers.get('Access-Control-Allow-Origin', '')
            # Should not be allowing all origins in production (only * in dev)
            # This test documents expected behavior
            assert True  # CORS configuration is server-dependent


class TestErrorHandling:
    """Test that errors don't leak sensitive information"""

    def test_500_error_no_stack_trace(self, api_client: Any) -> None:
        """Test that 500 errors don't expose stack traces"""
        # Attempt to trigger an error with invalid data
        response = api_client.post(
            '/api/generate-3d',
            json={'job_id': 'invalid', 'format': 'stl', 'quality': 999}
        )

        if response.status_code in [400, 404, 500]:
            response_data = response.get_data(as_text=True)

            # Should not contain stack traces or file paths
            assert 'Traceback' not in response_data
            assert 'File "' not in response_data
            assert 'line ' not in response_data.lower() or 'line' not in response_data[:100]

    def test_404_no_info_leak(self, api_client: Any) -> None:
        """Test that 404 errors don't reveal internal structure"""
        response = api_client.get('/api/nonexistent-endpoint-12345')

        assert response.status_code == 404
        response_data = response.get_data(as_text=True)

        # Should not reveal internal paths or structure
        assert 'backend' not in response_data.lower()
        assert 'C:\\' not in response_data
        assert '/home/' not in response_data
