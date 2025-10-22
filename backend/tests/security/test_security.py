"""
ORFEAS Security Tests
Consolidates security testing from test_security_features.py
"""
import pytest
import requests
import io
from PIL import Image
from typing import Any

pytestmark = pytest.mark.security


class TestInputValidation:
    """Tests for input validation and sanitization"""

    def test_sql_injection_in_prompt(self, api_client: Any, integration_server: Any) -> None:
        """Test SQL injection attempts in text prompts"""
        malicious_prompts = [
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "admin' --",
            "<script>alert('XSS')</script>"
        ]

        for prompt in malicious_prompts:
            response = api_client.text_to_image(prompt=prompt)

            # Should handle gracefully (not crash)
            assert response.status_code in [200, 202, 400], \
                f"Server crashed on malicious input: {prompt}"

    def test_path_traversal_attempts(self, api_client: Any, integration_server: Any) -> None:
        """Test path traversal in job_id"""
        traversal_attempts = [
            "../../../etc/passwd",
            "..\\..\\windows\\system32",
            "%2e%2e%2f%2e%2e%2f",
        ]

        for attempt in traversal_attempts:
            response = api_client.get_job_status(attempt)

            # Should return 400 or 404, not 200
            assert response.status_code in [400, 404], \
                f"Path traversal not blocked: {attempt}"

    def test_command_injection_attempts(self, api_client: Any, integration_server: Any) -> None:
        """Test command injection in parameters"""
        malicious_inputs = [
            "; ls -la",
            "| cat /etc/passwd",
            "$(whoami)",
            "`id`"
        ]

        for cmd in malicious_inputs:
            response = api_client.text_to_image(prompt=cmd)

            # Should handle safely
            assert response.status_code in [200, 202, 400]


class TestFileUploadSecurity:
    """Tests for file upload security"""

    def test_oversized_file_rejection(self, api_client: Any, integration_server: Any) -> None:
        """Test that oversized files are rejected"""
        # Create a large fake image (10MB+)
        large_data = b'X' * (10 * 1024 * 1024)
        fake_image = io.BytesIO(large_data)

        files = {'file': ('huge.png', fake_image, 'image/png')}
        response = api_client.post("/upload-image", files=files)

        # Should reject (413 or 400)
        assert response.status_code in [400, 413, 500], \
            "Oversized file should be rejected"

    def test_executable_file_rejection(self, api_client: Any, integration_server: Any) -> None:
        """Test that executable files are rejected"""
        malicious_files = [
            ('virus.exe', b'MZ\x90\x00', 'application/octet-stream'),
            ('script.sh', b'#!/bin/bash\nrm -rf /', 'text/x-shellscript'),
            ('code.py', b'import os; os.system("ls")', 'text/x-python'),
        ]

        for filename, content, mime in malicious_files:
            fake_file = io.BytesIO(content)
            files = {'file': (filename, fake_file, mime)}

            response = api_client.post("/upload-image", files=files)

            # Should reject non-image files
            assert response.status_code in [400, 415], \
                f"Executable file not rejected: {filename}"

    def test_filename_sanitization(self, api_client: Any, test_image_512: Any) -> None:
        """Test that dangerous filenames are sanitized"""
        dangerous_names = [
            "../../../etc/passwd.png",
            "test; rm -rf /.png",
            "test$(whoami).png",
            "<script>alert(1)</script>.png"
        ]

        for dangerous_name in dangerous_names:
            response = api_client.upload_image(
                test_image_512,
                filename=dangerous_name
            )
            test_image_512.seek(0)

            # Should either sanitize or reject
            if response.status_code == 200:
                # If accepted, filename should be sanitized
                data = response.json()
                job_id = data.get("job_id", "")
                # Job ID shouldn't contain malicious characters
                assert not any(char in job_id for char in ['<', '>', ';', '|', '$'])


class TestSecurityHeaders:
    """Tests for security headers"""

    def test_security_headers_present(self, api_client: Any, integration_server: Any) -> None:
        """Verify essential security headers are present"""
        response = api_client.health_check()
        headers = response.headers

        # Check for key security headers
        expected_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": ["DENY", "SAMEORIGIN"],
            "X-XSS-Protection": "1; mode=block",
        }

        for header, expected_value in expected_headers.items():
            assert header in headers, f"Missing security header: {header}"

            if isinstance(expected_value, list):
                assert headers[header] in expected_value, \
                    f"Invalid {header}: {headers[header]}"
            else:
                assert headers[header] == expected_value, \
                    f"Invalid {header}: {headers[header]}"

    def test_csp_header_present(self, api_client: Any, integration_server: Any) -> None:
        """Verify Content-Security-Policy header exists"""
        response = api_client.health_check()
        headers = response.headers

        # CSP should be present
        assert "Content-Security-Policy" in headers, "Missing CSP header"

        csp = headers["Content-Security-Policy"]

        # Should contain basic directives
        assert "default-src" in csp, "CSP missing default-src"
        assert "script-src" in csp, "CSP missing script-src"

    def test_no_server_version_disclosure(self, api_client: Any, integration_server: Any) -> None:
        """Verify server doesn't disclose version info"""
        response = api_client.health_check()
        headers = response.headers

        # Server header shouldn't reveal too much
        if "Server" in headers:
            server = headers["Server"].lower()
            # Shouldn't contain version numbers
            assert not any(ver in server for ver in ["python/", "flask/", "werkzeug/"]), \
                f"Server header reveals too much: {server}"


class TestRateLimiting:
    """Tests for rate limiting (if enabled)"""

    @pytest.mark.slow
    def test_rate_limit_on_api_calls(self, api_client: Any, integration_server: Any) -> None:
        """Test rate limiting on rapid API calls"""
        # Make rapid requests
        responses = []
        for i in range(100):
            try:
                response = api_client.health_check()
                responses.append(response.status_code)
            except Exception:
                # Rate limit may cause connection errors
                pass

        # If rate limiting is enabled, we should see 429 responses
        # If not enabled, all should be 200
        # Either way, server shouldn't crash
        assert len(responses) > 0, "No responses received"
        assert all(code in [200, 429] for code in responses), \
            "Unexpected status codes during rapid requests"


class TestAuthenticationBypass:
    """Tests for authentication bypass attempts"""

    def test_missing_authentication_handling(self, api_client: Any, integration_server: Any) -> None:
        """Test endpoints handle missing authentication gracefully"""
        # If authentication is required, these should fail appropriately
        # If not required, should succeed

        response = api_client.health_check()

        # Should return valid response (not crash)
        assert response.status_code in [200, 401, 403], \
            "Unexpected response for auth check"


# ============================================================================
# Test Suite Execution
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short", "-m", "security"])
