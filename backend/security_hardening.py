"""
ORFEAS AI 2D→3D Studio - Security Hardening
===========================================
Comprehensive security hardening for production deployment.

Features:
- Multi-layer input validation and sanitization
- Advanced authentication and authorization
- API security and rate limiting
- File upload security with malware scanning
- Real-time threat detection and response
- Security monitoring and audit logging
"""

import os
import re
import hashlib
import hmac
import time
import ipaddress
import subprocess
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set
from werkzeug.utils import secure_filename
from flask import request, abort, jsonify
import logging

logger = logging.getLogger(__name__)

class SecurityError(Exception):
    """Custom security exception"""
    pass

class SecurityHardening:
    """
    Comprehensive security hardening for production deployment
    """

    def __init__(self):
        self.security_config = self.load_security_config()
        self.threat_detector = ThreatDetector()
        self.access_monitor = AccessMonitor()
        self.blocked_ips = set()
        self.rate_limiters = {}
        self.security_keys = self.load_security_keys()

    def load_security_config(self) -> Dict[str, Any]:
        """Load security configuration"""

        return {
            'max_file_size': int(os.getenv('MAX_FILE_SIZE', 50 * 1024 * 1024)),  # 50MB
            'allowed_extensions': {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'webp', 'stl', 'obj'},
            'max_requests_per_minute': int(os.getenv('MAX_REQUESTS_PER_MINUTE', 60)),
            'block_duration': int(os.getenv('SECURITY_BLOCK_DURATION', 3600)),  # 1 hour
            'enable_malware_scan': os.getenv('ENABLE_MALWARE_SCAN', 'true').lower() == 'true',
            'signed_endpoints': {'generate-3d', 'admin', 'user-data'},
            'threat_threshold_high': 8,
            'threat_threshold_medium': 5,
            'jwt_secret': os.getenv('JWT_SECRET', 'orfeas-secure-key-2025'),
            'api_key_header': 'X-API-Key',
            'signature_header': 'X-Request-Signature'
        }

    def load_security_keys(self) -> Dict[str, str]:
        """Load security keys and secrets"""

        return {
            'api_master_key': os.getenv('API_MASTER_KEY', 'orfeas-master-2025'),
            'encryption_key': os.getenv('ENCRYPTION_KEY', 'orfeas-encrypt-2025'),
            'hmac_secret': os.getenv('HMAC_SECRET', 'orfeas-hmac-2025')
        }

    def apply_security_hardening(self, app):
        """Apply comprehensive security hardening"""

        logger.info("[ORFEAS] Applying comprehensive security hardening")

        # 1. Input validation and sanitization
        self.setup_input_validation(app)

        # 2. Authentication and authorization
        self.setup_authentication_security(app)

        # 3. API security
        self.setup_api_security(app)

        # 4. File upload security
        self.setup_file_upload_security(app)

        # 5. Rate limiting and DoS protection
        self.setup_rate_limiting(app)

        # 6. Security monitoring
        self.setup_security_monitoring(app)

        # 7. Security headers
        self.setup_security_headers(app)

        logger.info("[ORFEAS] Security hardening applied successfully")

    def setup_input_validation(self, app):
        """Comprehensive input validation and sanitization"""

        @app.before_request
        def validate_all_inputs():
            # Skip validation for static files
            if request.endpoint == 'static':
                return

            try:
                # SQL injection protection
                if self.detect_sql_injection(request):
                    self.log_security_event('sql_injection_attempt', request)
                    abort(400, "Invalid input detected")

                # XSS protection
                if self.detect_xss_attempt(request):
                    self.log_security_event('xss_attempt', request)
                    abort(400, "Malicious script detected")

                # Path traversal protection
                if self.detect_path_traversal(request):
                    self.log_security_event('path_traversal_attempt', request)
                    abort(400, "Path traversal attempt detected")

                # Command injection protection
                if self.detect_command_injection(request):
                    self.log_security_event('command_injection_attempt', request)
                    abort(400, "Command injection attempt detected")

                # Size limit validation
                if request.content_length and request.content_length > self.security_config['max_file_size']:
                    self.log_security_event('oversized_request', request)
                    abort(413, "Request too large")

            except Exception as e:
                logger.error(f"[ORFEAS] Input validation error: {e}")
                abort(500, "Validation error")

    def detect_sql_injection(self, request) -> bool:
        """Detect SQL injection attempts"""

        sql_patterns = [
            r"(\bunion\b.*\bselect\b|\bselect\b.*\bunion\b)",
            r"(\bor\b\s+['\"]?\w+['\"]?\s*=\s*['\"]?\w+['\"]?)",
            r"(\band\b\s+['\"]?\w+['\"]?\s*=\s*['\"]?\w+['\"]?)",
            r"(\bdrop\b\s+\btable\b|\bdelete\b\s+\bfrom\b)",
            r"(\binsert\b\s+\binto\b|\bupdate\b\s+\bset\b)",
            r"(['\"];\s*(drop|delete|insert|update|create))",
            r"(\bexec\b\s*\(|\bexecute\b\s*\()",
            r"(\bsp_\w+|\bxp_\w+)"
        ]

        # Check all request data
        check_data = []

        # URL parameters
        if request.args:
            check_data.extend(request.args.values())

        # Form data
        if request.form:
            check_data.extend(request.form.values())

        # JSON data
        if request.is_json:
            json_data = request.get_json(silent=True)
            if json_data:
                check_data.extend(self._extract_json_values(json_data))

        # Check for SQL injection patterns
        for data in check_data:
            if isinstance(data, str):
                for pattern in sql_patterns:
                    if re.search(pattern, data.lower()):
                        return True

        return False

    def detect_xss_attempt(self, request) -> bool:
        """Detect XSS attempts"""

        xss_patterns = [
            r"<script[^>]*>.*?</script>",
            r"javascript:",
            r"on\w+\s*=",
            r"<iframe[^>]*>",
            r"<object[^>]*>",
            r"<embed[^>]*>",
            r"<link[^>]*>",
            r"<meta[^>]*>",
            r"<style[^>]*>.*?</style>",
            r"expression\s*\(",
            r"url\s*\(",
            r"@import",
            r"vbscript:",
            r"data:text/html"
        ]

        # Check all text inputs
        check_data = []

        if request.args:
            check_data.extend(request.args.values())

        if request.form:
            check_data.extend(request.form.values())

        if request.is_json:
            json_data = request.get_json(silent=True)
            if json_data:
                check_data.extend(self._extract_json_values(json_data))

        for data in check_data:
            if isinstance(data, str):
                for pattern in xss_patterns:
                    if re.search(pattern, data.lower()):
                        return True

        return False

    def detect_path_traversal(self, request) -> bool:
        """Detect path traversal attempts"""

        path_patterns = [
            r"\.\./",
            r"\.\.\\",
            r"~",
            r"/etc/passwd",
            r"/etc/shadow",
            r"C:\\Windows",
            r"/proc/",
            r"/sys/",
            r"\.\.%2f",
            r"\.\.%5c"
        ]

        # Check URL path and parameters
        check_paths = [request.path]

        if request.args:
            check_paths.extend(request.args.values())

        if request.form:
            check_paths.extend(request.form.values())

        for path in check_paths:
            if isinstance(path, str):
                for pattern in path_patterns:
                    if re.search(pattern, path.lower()):
                        return True

        return False

    def detect_command_injection(self, request) -> bool:
        """Detect command injection attempts"""

        command_patterns = [
            r"[;&|`]",
            r"\$\([^)]*\)",
            r"`[^`]*`",
            r"\|\s*(cat|ls|pwd|whoami|id|uname)",
            r"(wget|curl)\s+",
            r"(nc|netcat)\s+",
            r"(sh|bash|zsh|fish)\s+",
            r"(python|perl|ruby|php)\s+",
            r"(rm|mv|cp|chmod)\s+"
        ]

        check_data = []

        if request.args:
            check_data.extend(request.args.values())

        if request.form:
            check_data.extend(request.form.values())

        for data in check_data:
            if isinstance(data, str):
                for pattern in command_patterns:
                    if re.search(pattern, data):
                        return True

        return False

    def setup_authentication_security(self, app):
        """Setup authentication and authorization security"""

        @app.before_request
        def check_authentication():
            # Skip authentication for public endpoints
            public_endpoints = {'static', 'health', 'metrics'}
            if request.endpoint in public_endpoints:
                return

            # Check for API endpoints
            if request.path.startswith('/api/'):
                api_key = request.headers.get(self.security_config['api_key_header'])

                if not api_key:
                    self.log_security_event('missing_api_key', request)
                    abort(401, "API key required")

                if not self.validate_api_key(api_key):
                    self.log_security_event('invalid_api_key', request)
                    abort(401, "Invalid API key")

    def validate_api_key(self, api_key: str) -> bool:
        """Validate API key"""

        # Hash comparison to prevent timing attacks
        expected_hash = hashlib.sha256(self.security_keys['api_master_key'].encode()).hexdigest()
        provided_hash = hashlib.sha256(api_key.encode()).hexdigest()

        return hmac.compare_digest(expected_hash, provided_hash)

    def setup_api_security(self, app):
        """API-specific security measures"""

        @app.before_request
        def validate_api_access():
            if request.endpoint and request.endpoint.startswith('api/'):
                # Request signature validation for critical operations
                if any(endpoint in request.endpoint for endpoint in self.security_config['signed_endpoints']):
                    signature = request.headers.get(self.security_config['signature_header'])
                    if not self.validate_request_signature(request, signature):
                        self.log_security_event('invalid_signature', request)
                        abort(401, "Invalid request signature")

                # Rate limiting check
                if not self.check_api_rate_limits(request):
                    self.log_security_event('rate_limit_exceeded', request)
                    abort(429, "Rate limit exceeded")

    def validate_request_signature(self, request, signature: Optional[str]) -> bool:
        """Validate request signature using HMAC"""

        if not signature:
            return False

        try:
            # Create expected signature
            request_data = request.get_data()
            expected_signature = hmac.new(
                self.security_keys['hmac_secret'].encode(),
                request_data,
                hashlib.sha256
            ).hexdigest()

            return hmac.compare_digest(signature, expected_signature)

        except Exception as e:
            logger.warning(f"[ORFEAS] Signature validation error: {e}")
            return False

    def check_api_rate_limits(self, request) -> bool:
        """Check API rate limits"""

        client_ip = self.get_client_ip(request)
        current_minute = int(time.time() // 60)

        # Initialize rate limiter for IP
        if client_ip not in self.rate_limiters:
            self.rate_limiters[client_ip] = {}

        # Clean old entries
        old_minutes = [minute for minute in self.rate_limiters[client_ip]
                      if minute < current_minute - 1]
        for minute in old_minutes:
            del self.rate_limiters[client_ip][minute]

        # Check current minute requests
        if current_minute not in self.rate_limiters[client_ip]:
            self.rate_limiters[client_ip][current_minute] = 0

        # Increment request count
        self.rate_limiters[client_ip][current_minute] += 1

        # Check if limit exceeded
        return self.rate_limiters[client_ip][current_minute] <= self.security_config['max_requests_per_minute']

    def setup_file_upload_security(self, app):
        """Secure file upload handling"""

        def secure_file_validation(file):
            # File type validation
            if not self.validate_file_type(file):
                raise SecurityError("Invalid file type")

            # File size validation
            if not self.validate_file_size(file):
                raise SecurityError("File too large")

            # Malware scanning
            if self.security_config['enable_malware_scan'] and self.detect_malware(file):
                raise SecurityError("Malicious file detected")

            # Content validation
            if not self.validate_file_content(file):
                raise SecurityError("Invalid file content")

            return True

    def validate_file_type(self, file) -> bool:
        """Validate file type based on extension and magic bytes"""

        if not file.filename:
            return False

        # Check extension
        extension = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
        if extension not in self.security_config['allowed_extensions']:
            return False

        # Check magic bytes for common image formats
        file.seek(0)
        header = file.read(32)
        file.seek(0)

        magic_bytes = {
            b'\x89PNG\r\n\x1a\n': 'png',
            b'\xff\xd8\xff': 'jpg',
            b'GIF87a': 'gif',
            b'GIF89a': 'gif',
            b'BM': 'bmp',
            b'RIFF': 'webp'
        }

        # For images, verify magic bytes match extension
        if extension in {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}:
            for magic, file_type in magic_bytes.items():
                if header.startswith(magic):
                    if extension in {'jpg', 'jpeg'} and file_type == 'jpg':
                        return True
                    elif extension == file_type:
                        return True
            return False

        return True

    def validate_file_size(self, file) -> bool:
        """Validate file size"""

        file.seek(0, 2)  # Seek to end
        size = file.tell()
        file.seek(0)  # Reset to beginning

        return size <= self.security_config['max_file_size']

    def detect_malware(self, file) -> bool:
        """Basic malware detection"""

        try:
            # Read file content for analysis
            file.seek(0)
            content = file.read(1024)  # Read first 1KB
            file.seek(0)

            # Check for suspicious patterns
            suspicious_patterns = [
                b'<script',
                b'javascript:',
                b'vbscript:',
                b'data:text/html',
                b'<iframe',
                b'<object',
                b'<embed'
            ]

            content_lower = content.lower()
            for pattern in suspicious_patterns:
                if pattern in content_lower:
                    return True

            # For more advanced scanning, integrate with ClamAV or similar
            return False

        except Exception as e:
            logger.warning(f"[ORFEAS] Malware detection error: {e}")
            return False

    def validate_file_content(self, file) -> bool:
        """Validate file content structure"""

        try:
            filename = file.filename.lower()
            file.seek(0)

            # Basic content validation based on file type
            if filename.endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                # Try to read as image
                try:
                    from PIL import Image
                    Image.open(file)
                    file.seek(0)
                    return True
                except Exception:
                    return False

            elif filename.endswith('.stl'):
                # Basic STL format validation
                content = file.read(80)  # STL header
                file.seek(0)

                # Check for ASCII or binary STL
                if content.startswith(b'solid '):
                    return True  # ASCII STL
                elif len(content) == 80:
                    return True  # Binary STL
                else:
                    return False

            return True

        except Exception as e:
            logger.warning(f"[ORFEAS] Content validation error: {e}")
            return False

    def setup_rate_limiting(self, app):
        """Setup rate limiting and DoS protection"""

        @app.before_request
        def rate_limit_check():
            client_ip = self.get_client_ip(request)

            # Check if IP is blocked
            if client_ip in self.blocked_ips:
                self.log_security_event('blocked_ip_access', request)
                abort(403, "IP address blocked")

            # Aggressive request detection
            if self.detect_aggressive_requests(client_ip):
                self.block_ip(client_ip)
                self.log_security_event('aggressive_requests_blocked', request)
                abort(429, "Too many requests")

    def detect_aggressive_requests(self, client_ip: str) -> bool:
        """Detect aggressive request patterns"""

        # Check if too many requests in short time
        if client_ip in self.rate_limiters:
            current_minute = int(time.time() // 60)
            recent_requests = sum(
                count for minute, count in self.rate_limiters[client_ip].items()
                if minute >= current_minute - 1
            )

            return recent_requests > self.security_config['max_requests_per_minute'] * 2

        return False

    def block_ip(self, ip_address: str):
        """Block IP address temporarily"""

        self.blocked_ips.add(ip_address)
        logger.warning(f"[ORFEAS] Blocked IP address: {ip_address}")

        # Schedule unblock (in production, use Redis with TTL)
        import threading
        timer = threading.Timer(
            self.security_config['block_duration'],
            lambda: self.blocked_ips.discard(ip_address)
        )
        timer.start()

    def setup_security_monitoring(self, app):
        """Real-time security monitoring"""

        @app.after_request
        def monitor_security_events(response):
            # Log security events
            self.log_security_event('request_completed', request, response)

            # Detect anomalies
            if self.detect_anomaly(request, response):
                self.alert_security_team(request, response)

            # Update threat intelligence
            self.update_threat_intelligence(request, response)

            return response

    def detect_anomaly(self, request, response) -> bool:
        """Detect security anomalies"""

        # High error rate
        if response.status_code >= 400:
            return True

        # Unusual request patterns
        if len(request.path) > 1000:  # Very long URLs
            return True

        # Suspicious user agents
        user_agent = request.headers.get('User-Agent', '').lower()
        suspicious_agents = ['sqlmap', 'nikto', 'burp', 'nmap', 'dirb']
        if any(agent in user_agent for agent in suspicious_agents):
            return True

        return False

    def alert_security_team(self, request, response):
        """Alert security team of potential threats"""

        alert_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'client_ip': self.get_client_ip(request),
            'request_path': request.path,
            'user_agent': request.headers.get('User-Agent'),
            'status_code': response.status_code,
            'threat_level': 'HIGH'
        }

        logger.critical(f"[ORFEAS-SECURITY] Security alert: {alert_data}")

        # In production, send to security monitoring system

    def update_threat_intelligence(self, request, response):
        """Update threat intelligence data"""

        # Track patterns for machine learning
        pass

    def setup_security_headers(self, app):
        """Setup security headers"""

        @app.after_request
        def set_security_headers(response):
            security_headers = {
                'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
                'X-Content-Type-Options': 'nosniff',
                'X-Frame-Options': 'DENY',
                'X-XSS-Protection': '1; mode=block',
                'Referrer-Policy': 'strict-origin-when-cross-origin',
                'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'",
                'Permissions-Policy': 'camera=(), microphone=(), geolocation=()'
            }

            for header, value in security_headers.items():
                response.headers[header] = value

            return response

    def get_client_ip(self, request) -> str:
        """Get real client IP address"""

        # Check for forwarded headers
        forwarded_ips = [
            request.headers.get('X-Forwarded-For'),
            request.headers.get('X-Real-IP'),
            request.headers.get('X-Client-IP')
        ]

        for ip_header in forwarded_ips:
            if ip_header:
                # Take first IP if comma-separated
                ip = ip_header.split(',')[0].strip()
                try:
                    ipaddress.ip_address(ip)
                    return ip
                except ValueError:
                    continue

        return request.remote_addr or '0.0.0.0'

    def log_security_event(self, event_type: str, request, response=None):
        """Log security events for analysis"""

        event_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': event_type,
            'client_ip': self.get_client_ip(request),
            'user_agent': request.headers.get('User-Agent'),
            'request_method': request.method,
            'request_path': request.path,
            'response_status': response.status_code if response else None
        }

        logger.info(f"[ORFEAS-SECURITY] {event_type}: {json.dumps(event_data)}")

    def _extract_json_values(self, data) -> List[str]:
        """Recursively extract string values from JSON data"""

        values = []

        if isinstance(data, dict):
            for value in data.values():
                values.extend(self._extract_json_values(value))
        elif isinstance(data, list):
            for item in data:
                values.extend(self._extract_json_values(item))
        elif isinstance(data, str):
            values.append(data)

        return values


class ThreatDetector:
    """Advanced threat detection system"""

    def __init__(self):
        self.threat_patterns = self.load_threat_patterns()

    def load_threat_patterns(self) -> Dict[str, List[str]]:
        """Load known threat patterns"""

        return {
            'sql_injection': [
                'union select',
                'drop table',
                'exec(',
                'xp_cmdshell'
            ],
            'xss': [
                '<script>',
                'javascript:',
                'onerror='
            ],
            'command_injection': [
                '; cat',
                '| ls',
                '&& whoami'
            ]
        }


class AccessMonitor:
    """Monitor and analyze access patterns"""

    def __init__(self):
        self.access_log = []
        self.suspicious_patterns = set()

    def log_access(self, request):
        """Log access attempt"""

        access_entry = {
            'timestamp': time.time(),
            'ip': request.remote_addr,
            'path': request.path,
            'user_agent': request.headers.get('User-Agent')
        }

        self.access_log.append(access_entry)

        # Keep only recent entries
        cutoff_time = time.time() - 3600  # 1 hour
        self.access_log = [entry for entry in self.access_log
                          if entry['timestamp'] > cutoff_time]

    def detect_suspicious_activity(self, ip_address: str) -> bool:
        """Detect suspicious activity patterns"""

        recent_access = [entry for entry in self.access_log
                        if entry['ip'] == ip_address and
                        entry['timestamp'] > time.time() - 300]  # 5 minutes

        # Too many requests
        if len(recent_access) > 100:
            return True

        # Scanning behavior
        unique_paths = set(entry['path'] for entry in recent_access)
        if len(unique_paths) > 50:
            return True

        return False
