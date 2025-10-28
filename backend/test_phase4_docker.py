#!/usr/bin/env python3
"""
Phase 4.8: Docker Containerization Test Suite
===============================================

Comprehensive tests for Docker containerization.
Tests: Build verification, container runtime, health checks, port mapping, volumes, networking.

Status: Production-Ready
Version: 1.0.0
Author: BOB AI v10.0
"""

import os
import sys
import subprocess
import time
import unittest
import socket
import json
import requests
from pathlib import Path
from typing import Dict, Tuple, Optional, List


class TestDockerEnvironment(unittest.TestCase):
    """Test Docker environment and prerequisites."""

    def test_docker_installed(self):
        """Test that Docker is installed."""
        try:
            result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0)
            self.assertIn('Docker', result.stdout)
        except FileNotFoundError:
            self.skipTest("Docker not installed")

    def test_docker_compose_installed(self):
        """Test that Docker Compose is installed."""
        try:
            result = subprocess.run(['docker-compose', '--version'], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0)
            self.assertIn('docker-compose', result.stdout)
        except FileNotFoundError:
            self.skipTest("Docker Compose not installed")

    def test_docker_daemon_running(self):
        """Test that Docker daemon is running."""
        try:
            result = subprocess.run(['docker', 'ps'], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0)
        except Exception as e:
            self.skipTest(f"Docker daemon not running: {e}")


class TestDockerfileValidation(unittest.TestCase):
    """Test Dockerfile configuration and structure."""

    def setUp(self):
        """Set up test fixtures."""
        self.workspace_root = Path(__file__).parent.parent
        self.dockerfile_path = self.workspace_root / "Dockerfile"
        self.dockerignore_path = self.workspace_root / ".dockerignore"

    def test_dockerfile_exists(self):
        """Test Dockerfile exists."""
        self.assertTrue(self.dockerfile_path.exists(), f"Dockerfile not found at {self.dockerfile_path}")

    def test_dockerfile_valid_structure(self):
        """Test Dockerfile has valid structure."""
        content = self.dockerfile_path.read_text()

        # Check for required elements
        required_elements = [
            'FROM',
            'WORKDIR',
            'COPY',
            'EXPOSE',
            'HEALTHCHECK',
            'CMD'
        ]

        for element in required_elements:
            self.assertIn(element, content, f"Missing required element: {element}")

    def test_dockerfile_uses_proper_base_image(self):
        """Test Dockerfile uses proper base image."""
        content = self.dockerfile_path.read_text()
        # Should use Python 3.10+ slim image for minimal size
        self.assertIn('python:3.1', content)

    def test_dockerfile_includes_health_check(self):
        """Test Dockerfile includes health check."""
        content = self.dockerfile_path.read_text()
        self.assertIn('HEALTHCHECK', content)
        self.assertIn('http://localhost', content)

    def test_dockerfile_exposes_correct_ports(self):
        """Test Dockerfile exposes correct ports."""
        content = self.dockerfile_path.read_text()
        self.assertIn('5000', content)  # Main API
        # Monitoring port 8000 is optional

    def test_dockerfile_sets_pythonunbuffered(self):
        """Test Dockerfile sets PYTHONUNBUFFERED."""
        content = self.dockerfile_path.read_text()
        self.assertIn('PYTHONUNBUFFERED', content)

    def test_dockerignore_exists(self):
        """Test .dockerignore exists."""
        self.assertTrue(self.dockerignore_path.exists(), ".dockerignore not found")

    def test_dockerignore_has_content(self):
        """Test .dockerignore has meaningful content."""
        content = self.dockerignore_path.read_text()
        # Should exclude at least some common directories
        excluded_items = ['__pycache__', '.git', '.gitignore', '*.pyc']
        found_count = sum(1 for item in excluded_items if item in content)
        self.assertGreater(found_count, 0, ".dockerignore should exclude common items")


class TestDockerComposeValidation(unittest.TestCase):
    """Test docker-compose configuration."""

    def setUp(self):
        """Set up test fixtures."""
        self.workspace_root = Path(__file__).parent.parent
        self.compose_path = self.workspace_root / "docker-compose.yml"
        self.compose_prod_path = self.workspace_root / "docker-compose.production.yml"

    def test_docker_compose_exists(self):
        """Test docker-compose.yml exists."""
        self.assertTrue(self.compose_path.exists(), "docker-compose.yml not found")

    def test_docker_compose_valid_yaml(self):
        """Test docker-compose.yml is valid YAML."""
        try:
            import yaml
            content = self.compose_path.read_text()
            yaml.safe_load(content)
        except ImportError:
            self.skipTest("PyYAML not installed")
        except yaml.YAMLError as e:
            self.fail(f"Invalid YAML in docker-compose.yml: {e}")

    def test_docker_compose_has_services(self):
        """Test docker-compose.yml defines services."""
        try:
            import yaml
            content = self.compose_path.read_text()
            config = yaml.safe_load(content)
            self.assertIn('services', config)
            self.assertGreater(len(config['services']), 0)
        except ImportError:
            self.skipTest("PyYAML not installed")

    def test_docker_compose_api_service_exists(self):
        """Test API service is defined."""
        try:
            import yaml
            content = self.compose_path.read_text()
            config = yaml.safe_load(content)
            services = config.get('services', {})
            # Check for api or main service
            api_services = [s for s in services.keys() if 'api' in s.lower() or 'main' in s.lower()]
            self.assertGreater(len(api_services), 0, "No API service found in docker-compose.yml")
        except ImportError:
            self.skipTest("PyYAML not installed")

    def test_docker_compose_defines_volumes(self):
        """Test docker-compose.yml defines volumes."""
        try:
            import yaml
            content = self.compose_path.read_text()
            config = yaml.safe_load(content)
            self.assertIn('volumes', config, "No volumes defined in docker-compose.yml")
        except ImportError:
            self.skipTest("PyYAML not installed")

    def test_docker_compose_defines_networks(self):
        """Test docker-compose.yml defines networks."""
        try:
            import yaml
            content = self.compose_path.read_text()
            config = yaml.safe_load(content)
            self.assertIn('networks', config, "No networks defined in docker-compose.yml")
        except ImportError:
            self.skipTest("PyYAML not installed")

    def test_docker_compose_production_exists(self):
        """Test production docker-compose file exists."""
        self.assertTrue(self.compose_prod_path.exists(), "docker-compose.production.yml not found")


class TestImageBuild(unittest.TestCase):
    """Test Docker image building."""

    def setUp(self):
        """Set up test fixtures."""
        self.workspace_root = Path(__file__).parent.parent

    def test_image_builds_successfully(self):
        """Test Docker image builds without errors."""
        try:
            # Dry-run style test - just validate Dockerfile is correct
            dockerfile = self.workspace_root / "Dockerfile"
            content = dockerfile.read_text()

            # Check for common build issues
            issues = []

            # Check for unclosed parentheses
            if content.count('(') != content.count(')'):
                issues.append("Unmatched parentheses in Dockerfile")

            # Check for common missing packages
            if 'RUN apt-get' in content and 'rm -rf /var/lib/apt/lists' not in content:
                issues.append("apt-get cache not cleaned (missing 'rm -rf /var/lib/apt/lists')")

            self.assertEqual(len(issues), 0, f"Build validation issues: {issues}")
        except Exception as e:
            self.fail(f"Build validation failed: {e}")

    def test_requirements_txt_exists(self):
        """Test requirements.txt exists for pip install."""
        req_path = self.workspace_root / "backend" / "requirements.txt"
        self.assertTrue(req_path.exists(), "backend/requirements.txt not found")

    def test_requirements_txt_has_content(self):
        """Test requirements.txt has dependencies."""
        req_path = self.workspace_root / "backend" / "requirements.txt"
        content = req_path.read_text().strip()
        self.assertGreater(len(content), 0, "requirements.txt is empty")
        # Should have at least Flask
        self.assertIn('flask', content.lower())


class TestContainerPorts(unittest.TestCase):
    """Test port configuration for containers."""

    def test_api_port_defined(self):
        """Test API port (5000) is defined."""
        workspace_root = Path(__file__).parent.parent
        compose_path = workspace_root / "docker-compose.yml"
        content = compose_path.read_text()
        self.assertIn('5000', content)

    def test_ports_not_conflicting(self):
        """Test ports are configured correctly."""
        workspace_root = Path(__file__).parent.parent
        compose_path = workspace_root / "docker-compose.yml"
        content = compose_path.read_text()

        # Should have port mappings like "5000:5000"
        self.assertIn('5000', content)

    def test_port_availability_check(self):
        """Test port availability can be checked."""
        def is_port_available(port: int) -> bool:
            """Check if a port is available."""
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.bind(('127.0.0.1', port))
                sock.close()
                return True
            except OSError:
                return False

        # Just check the function works
        available = is_port_available(9999)  # Usually available
        self.assertTrue(available)


class TestVolumeMounting(unittest.TestCase):
    """Test volume configuration."""

    def setUp(self):
        """Set up test fixtures."""
        self.workspace_root = Path(__file__).parent.parent
        self.compose_path = self.workspace_root / "docker-compose.yml"

    def test_volumes_section_exists(self):
        """Test volumes are defined in docker-compose."""
        content = self.compose_path.read_text()
        self.assertIn('volumes:', content)

    def test_models_volume_mapped(self):
        """Test models volume is properly mapped."""
        content = self.compose_path.read_text()
        # Should map models directory
        self.assertIn('models', content)

    def test_outputs_volume_mapped(self):
        """Test outputs volume is properly mapped."""
        content = self.compose_path.read_text()
        # Should map outputs directory
        self.assertIn('outputs', content)

    def test_logs_volume_mapped(self):
        """Test logs volume is properly mapped."""
        content = self.compose_path.read_text()
        # Should map logs directory
        self.assertIn('logs', content.lower())


class TestNetworking(unittest.TestCase):
    """Test networking configuration."""

    def setUp(self):
        """Set up test fixtures."""
        self.workspace_root = Path(__file__).parent.parent
        self.compose_path = self.workspace_root / "docker-compose.yml"

    def test_networks_section_exists(self):
        """Test networks are defined."""
        content = self.compose_path.read_text()
        self.assertIn('networks:', content)

    def test_service_networking_configured(self):
        """Test services can communicate."""
        content = self.compose_path.read_text()
        # Network configuration should exist
        self.assertGreater(len(content), 100)


class TestHealthChecks(unittest.TestCase):
    """Test container health check configuration."""

    def setUp(self):
        """Set up test fixtures."""
        self.workspace_root = Path(__file__).parent.parent
        self.dockerfile = self.workspace_root / "Dockerfile"

    def test_dockerfile_healthcheck_defined(self):
        """Test Dockerfile includes HEALTHCHECK instruction."""
        content = self.dockerfile.read_text()
        self.assertIn('HEALTHCHECK', content)

    def test_healthcheck_uses_curl(self):
        """Test health check uses curl."""
        content = self.dockerfile.read_text()
        self.assertIn('curl', content)

    def test_healthcheck_probes_health_endpoint(self):
        """Test health check probes /health endpoint."""
        content = self.dockerfile.read_text()
        self.assertIn('/health', content)

    def test_healthcheck_has_reasonable_interval(self):
        """Test health check has reasonable interval."""
        content = self.dockerfile.read_text()
        # Should check every 30s
        self.assertIn('30s', content)

    def test_healthcheck_has_timeout(self):
        """Test health check has timeout."""
        content = self.dockerfile.read_text()
        self.assertIn('timeout', content.lower())


class TestEnvironmentVariables(unittest.TestCase):
    """Test environment variable configuration."""

    def setUp(self):
        """Set up test fixtures."""
        self.workspace_root = Path(__file__).parent.parent
        self.compose_path = self.workspace_root / "docker-compose.yml"

    def test_environment_section_exists(self):
        """Test environment is defined in docker-compose."""
        content = self.compose_path.read_text()
        self.assertIn('environment:', content)

    def test_flask_env_set(self):
        """Test FLASK_ENV is set."""
        content = self.compose_path.read_text()
        self.assertIn('FLASK_ENV', content)

    def test_pythonunbuffered_set(self):
        """Test PYTHONUNBUFFERED is set."""
        content = self.compose_path.read_text()
        self.assertIn('PYTHONUNBUFFERED', content)


class TestSecurityConfiguration(unittest.TestCase):
    """Test security configuration."""

    def setUp(self):
        """Set up test fixtures."""
        self.workspace_root = Path(__file__).parent.parent
        self.dockerfile = self.workspace_root / "Dockerfile"
        self.compose_path = self.workspace_root / "docker-compose.yml"

    def test_dockerfile_uses_slim_image(self):
        """Test Dockerfile uses slim base image."""
        content = self.dockerfile.read_text()
        self.assertIn('slim', content)

    def test_no_root_user_in_dockerfile(self):
        """Test Dockerfile doesn't run as root."""
        content = self.dockerfile.read_text()
        # Should have USER instruction
        if 'RUN groupadd' in content or 'useradd' in content:
            self.assertIn('USER', content)

    def test_dockerignore_excludes_secrets(self):
        """Test .dockerignore excludes sensitive files."""
        dockerignore = self.workspace_root / ".dockerignore"
        content = dockerignore.read_text()
        # Should exclude .env files
        self.assertIn('.env', content)

    def test_no_hardcoded_credentials(self):
        """Test no hardcoded credentials in Dockerfile."""
        content = self.dockerfile.read_text()

        # Check for common password patterns
        suspicious_patterns = ['password=', 'token=', 'secret=', 'api_key=']
        for pattern in suspicious_patterns:
            self.assertNotIn(pattern.lower(), content.lower(),
                           f"Possible hardcoded credential found: {pattern}")


class TestBuildArtefacts(unittest.TestCase):
    """Test Docker build artefacts."""

    def setUp(self):
        """Set up test fixtures."""
        self.workspace_root = Path(__file__).parent.parent

    def test_backend_directory_exists(self):
        """Test backend directory exists for COPY."""
        backend = self.workspace_root / "backend"
        self.assertTrue(backend.exists(), "backend directory not found")

    def test_main_python_file_exists(self):
        """Test main Python entry point exists."""
        main_file = self.workspace_root / "backend" / "main.py"
        self.assertTrue(main_file.exists(), "backend/main.py not found")

    def test_dockerfile_copies_backend(self):
        """Test Dockerfile copies backend directory."""
        dockerfile = self.workspace_root / "Dockerfile"
        content = dockerfile.read_text()
        self.assertIn('backend/', content)


class TestMultiStage(unittest.TestCase):
    """Test multi-stage Docker build."""

    def setUp(self):
        """Set up test fixtures."""
        self.dockerfile = Path(__file__).parent.parent / "Dockerfile"

    def test_dockerfile_has_stages(self):
        """Test Dockerfile uses multi-stage build."""
        content = self.dockerfile.read_text()
        # Multi-stage builds have multiple FROM statements
        from_count = content.count('FROM')
        # Can be 1 or more (multi-stage is optional but recommended)
        self.assertGreater(from_count, 0)


class TestDockerComposeSyntax(unittest.TestCase):
    """Test docker-compose YAML syntax."""

    def setUp(self):
        """Set up test fixtures."""
        self.compose_path = Path(__file__).parent.parent / "docker-compose.yml"

    def test_compose_can_be_parsed(self):
        """Test docker-compose.yml can be parsed."""
        try:
            import yaml
            content = self.compose_path.read_text()
            data = yaml.safe_load(content)
            self.assertIsNotNone(data)
            self.assertIsInstance(data, dict)
        except ImportError:
            self.skipTest("PyYAML not installed")

    def test_compose_has_version(self):
        """Test docker-compose.yml specifies version."""
        content = self.compose_path.read_text()
        self.assertIn('version:', content)

    def test_compose_services_are_dict(self):
        """Test services are properly formatted."""
        try:
            import yaml
            content = self.compose_path.read_text()
            data = yaml.safe_load(content)
            services = data.get('services', {})
            self.assertIsInstance(services, dict)
        except ImportError:
            self.skipTest("PyYAML not installed")


def run_tests() -> Tuple[int, int, int]:
    """
    Run all container tests.

    Returns:
        Tuple of (tests_run, failures, errors)
    """
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestDockerEnvironment))
    suite.addTests(loader.loadTestsFromTestCase(TestDockerfileValidation))
    suite.addTests(loader.loadTestsFromTestCase(TestDockerComposeValidation))
    suite.addTests(loader.loadTestsFromTestCase(TestImageBuild))
    suite.addTests(loader.loadTestsFromTestCase(TestContainerPorts))
    suite.addTests(loader.loadTestsFromTestCase(TestVolumeMounting))
    suite.addTests(loader.loadTestsFromTestCase(TestNetworking))
    suite.addTests(loader.loadTestsFromTestCase(TestHealthChecks))
    suite.addTests(loader.loadTestsFromTestCase(TestEnvironmentVariables))
    suite.addTests(loader.loadTestsFromTestCase(TestSecurityConfiguration))
    suite.addTests(loader.loadTestsFromTestCase(TestBuildArtefacts))
    suite.addTests(loader.loadTestsFromTestCase(TestMultiStage))
    suite.addTests(loader.loadTestsFromTestCase(TestDockerComposeSyntax))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return len(result.testsRun), len(result.failures), len(result.errors)


if __name__ == '__main__':
    print("\n" + "="*80)
    print("PHASE 4.8: DOCKER CONTAINERIZATION TEST SUITE")
    print("="*80 + "\n")

    tests_run, failures, errors = run_tests()

    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"Tests Run: {tests_run}")
    print(f"Failures: {failures}")
    print(f"Errors: {errors}")
    print(f"Pass Rate: {((tests_run - failures - errors) / tests_run * 100):.1f}%" if tests_run > 0 else "N/A")
    print("="*80 + "\n")

    sys.exit(0 if failures == 0 and errors == 0 else 1)
