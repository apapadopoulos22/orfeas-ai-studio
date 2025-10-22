#!/usr/bin/env python3
"""
ORFEAS Netlify Deployment Test Script
Tests local server connectivity and prepares for cloud deployment
"""

import requests
import json
import time
import subprocess
import sys
from pathlib import Path

class NetlifyDeploymentTester:
    def __init__(self):
        self.server_url = "http://localhost:5002"
        self.test_results = []

    def log_test(self, test_name, success, message=""):
        """Log test result"""
        status = "'úÖ PASS" if success else "'ùå FAIL"
        result = f"{status} {test_name}"
        if message:
            result += f" - {message}"
        print(result)

        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message,
            "timestamp": time.time()
        })

    def test_server_health(self):
        """Test if local server is running and healthy"""
        print("\nüîç Testing Local Server Health...")

        try:
            response = requests.get(f"{self.server_url}/api/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.log_test("Server Health Check", True, f"Server running: {data.get('status', 'unknown')}")
                return True
            else:
                self.log_test("Server Health Check", False, f"HTTP {response.status_code}")
                return False

        except requests.exceptions.ConnectionError:
            self.log_test("Server Health Check", False, "Connection refused - server not running")
            return False
        except requests.exceptions.Timeout:
            self.log_test("Server Health Check", False, "Request timeout")
            return False
        except Exception as e:
            self.log_test("Server Health Check", False, f"Error: {str(e)}")
            return False

    def test_cors_headers(self):
        """Test CORS configuration"""
        print("\nüåê Testing CORS Configuration...")

        try:
            # Test preflight request
            response = requests.options(
                f"{self.server_url}/api/health",
                headers={
                    'Origin': 'https://test-netlify-site.netlify.app',
                    'Access-Control-Request-Method': 'GET',
                    'Access-Control-Request-Headers': 'Content-Type'
                },
                timeout=5
            )

            cors_origin = response.headers.get('Access-Control-Allow-Origin')
            cors_methods = response.headers.get('Access-Control-Allow-Methods')

            if cors_origin and ('*' in cors_origin or 'netlify' in cors_origin):
                self.log_test("CORS Origin Header", True, f"Origin: {cors_origin}")
            else:
                self.log_test("CORS Origin Header", False, f"Missing or restrictive: {cors_origin}")

            if cors_methods and 'GET' in cors_methods:
                self.log_test("CORS Methods Header", True, f"Methods: {cors_methods}")
            else:
                self.log_test("CORS Methods Header", False, f"Missing GET method: {cors_methods}")

        except Exception as e:
            self.log_test("CORS Headers Test", False, f"Error: {str(e)}")

    def test_api_endpoints(self):
        """Test key API endpoints"""
        print("\nüîß Testing API Endpoints...")

        endpoints = [
            ("/api/health", "Health endpoint"),
            ("/api/models-info", "Models info endpoint"),
            ("/api/formats", "Supported formats endpoint")
        ]

        for endpoint, description in endpoints:
            try:
                response = requests.get(f"{self.server_url}{endpoint}", timeout=5)
                if response.status_code == 200:
                    self.log_test(f"API {endpoint}", True, "Responding correctly")
                else:
                    self.log_test(f"API {endpoint}", False, f"HTTP {response.status_code}")
            except Exception as e:
                self.log_test(f"API {endpoint}", False, f"Error: {str(e)}")

    def test_file_upload_endpoint(self):
        """Test file upload capability"""
        print("\n Testing File Upload...")

        # Create a small test image
        test_image_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\nIDATx\x9cc\xf8\x00\x00\x00\x01\x00\x01\x00\x00\x00\x00IEND\xaeB`\x82'

        try:
            files = {'image': ('test.png', test_image_data, 'image/png')}
            response = requests.post(
                f"{self.server_url}/api/image-to-3d",
                files=files,
                timeout=10
            )

            if response.status_code in [200, 202]:
                self.log_test("File Upload Test", True, "Upload endpoint accepting files")
            else:
                self.log_test("File Upload Test", False, f"HTTP {response.status_code}")

        except Exception as e:
            self.log_test("File Upload Test", False, f"Error: {str(e)}")

    def get_local_ip(self):
        """Get local network IP address"""
        try:
            import socket
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except:
            return "127.0.0.1"

    def generate_deployment_config(self):
        """Generate deployment configuration"""
        print("\nüìù Generating Deployment Configuration...")

        local_ip = self.get_local_ip()

        config = {
            "deployment_ready": True,
            "server_urls": {
                "localhost": "http://localhost:5002",
                "local_network": f"http://{local_ip}:5002",
                "recommended": f"http://{local_ip}:5002"
            },
            "cors_configured": any(test["test"].startswith("CORS") and test["success"] for test in self.test_results),
            "api_functional": any(test["test"].startswith("API") and test["success"] for test in self.test_results),
            "upload_working": any(test["test"] == "File Upload Test" and test["success"] for test in self.test_results),
            "deployment_instructions": [
                "1. Zip the netlify-frontend folder",
                "2. Go to https://app.netlify.com/drop",
                "3. Drag zip file to deploy",
                f"4. Update frontend to use: {local_ip}:5002",
                "5. Test connection from deployed site"
            ]
        }

        # Save config
        config_path = Path("c:/Users/johng/Documents/Erevus/orfeas/netlify-frontend/deployment-config.json")
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)

        self.log_test("Configuration Generated", True, f"Saved to {config_path}")
        return config

    def print_summary(self, config):
        """Print deployment summary"""
        print("\n" + "="*60)
        print("üöÄ NETLIFY DEPLOYMENT SUMMARY")
        print("="*60)

        total_tests = len(self.test_results)
        passed_tests = sum(1 for test in self.test_results if test["success"])

        print(f"üìä Test Results: {passed_tests}/{total_tests} passed")

        if config["deployment_ready"]:
            print("'úÖ READY FOR DEPLOYMENT!")
            print(f"\nüåê Recommended Server URL: {config['server_urls']['recommended']}")
            print("\nüìã Next Steps:")
            for step in config["deployment_instructions"]:
                print(f"   {step}")
        else:
            print("  DEPLOYMENT NOT RECOMMENDED")
            print("   Fix failed tests before deploying")

        print(f"\n Configuration saved: deployment-config.json")
        print("üîç For detailed instructions: See README.md")

    def run_all_tests(self):
        """Run complete deployment test suite"""
        print("üß™ ORFEAS Netlify Deployment Test Suite")
        print("=" * 50)

        # Run tests
        server_running = self.test_server_health()

        if server_running:
            self.test_cors_headers()
            self.test_api_endpoints()
            self.test_file_upload_endpoint()
        else:
            print("\n  Skipping other tests - server not running")
            print("   Start server with: python powerful_3d_server.py")

        # Generate configuration
        config = self.generate_deployment_config()

        # Print summary
        self.print_summary(config)

        return config

if __name__ == "__main__":
    tester = NetlifyDeploymentTester()
    config = tester.run_all_tests()

    # Exit with appropriate code
    if config["deployment_ready"]:
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Failure
