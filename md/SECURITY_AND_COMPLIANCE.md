# ORFEAS Security & Compliance Reference

## Overview

Comprehensive security hardening framework for the ORFEAS AI platform, providing multi-layer protection through input validation, threat detection, authentication, authorization, and real-time security monitoring.

### Core Security Modules

- `backend/security_hardening.py` - Comprehensive security hardening with threat detection
- `backend/validation.py` - Input validation, rate limiting, and security headers
- `backend/quality_validator.py` - Generation pipeline quality validation

### Key Capabilities

- Multi-layer input validation (SQL injection, XSS, path traversal, command injection)
- Real-time threat detection and IP blocking
- Rate limiting and DoS protection
- Secure file upload with malware scanning
- API authentication and request signing
- Security monitoring and audit logging
- Compliance frameworks (SOC2, ISO27001, GDPR, HIPAA)

## Key Security Concepts

### 1. Defense in Depth

Multiple security layers provide comprehensive protection:

- **Layer 1**: Input validation and sanitization (validation.py)
- **Layer 2**: Threat detection and pattern matching (security_hardening.py)
- **Layer 3**: Authentication and authorization (API keys, JWT)
- **Layer 4**: Rate limiting and DoS protection (RateLimiter)
- **Layer 5**: Security monitoring and alerting (AccessMonitor, ThreatDetector)
- **Layer 6**: Audit logging and compliance tracking

### 2. Threat Detection

Real-time threat detection using pattern matching and behavior analysis:

- **SQL Injection**: Detects UNION, DROP, DELETE, INSERT patterns
- **XSS Attacks**: Identifies script tags, event handlers, iframes
- **Path Traversal**: Blocks ../, ~, /etc/passwd attempts
- **Command Injection**: Prevents shell command execution
- **Oversized Requests**: Enforces size limits (default 50MB)

### 3. Security Scoring

Threat assessment with configurable thresholds:

- **High Threat (≥8)**: Block immediately and alert security team
- **Medium Threat (≥5)**: Enable enhanced monitoring
- **Low Threat (<5)**: Log for analysis

### 4. Compliance Validation

Enterprise compliance framework support:

- **SOC2 Type 2**: Security and availability controls
- **ISO27001:2022**: Information security management
- **GDPR**: Data privacy and protection
- **HIPAA**: Healthcare data security
- **ISO9001:2015**: Quality management systems

## Implementation Details

### SecurityHardening Class

```python

## backend/security_hardening.py

from security_hardening import SecurityHardening

## Initialize security system

security = SecurityHardening()

## Apply comprehensive security hardening

security.apply_security_hardening(app)

```text

### Key Methods

- `setup_input_validation(app)` - Multi-layer input validation
- `setup_authentication_security(app)` - Authentication and authorization
- `setup_api_security(app)` - API keys and request signing
- `setup_file_upload_security(app)` - Secure file uploads
- `setup_rate_limiting(app)` - DoS protection
- `setup_security_monitoring(app)` - Real-time monitoring
- `setup_security_headers(app)` - Security headers (CSP, HSTS)

### Threat Detection

- `detect_sql_injection(request)` - SQL injection pattern matching
- `detect_xss_attempt(request)` - XSS attack detection
- `detect_path_traversal(request)` - Path traversal blocking
- `detect_command_injection(request)` - Command injection prevention

### Security Monitoring

- `log_security_event(event_type, request)` - Audit logging
- `assess_request_threat_level(request)` - Threat scoring
- `block_request_and_alert(request, threat_level)` - Automatic blocking

### FileUploadValidator Class

```python

## backend/validation.py

from validation import FileUploadValidator

## Initialize validator

validator = FileUploadValidator()

## Validate filename

is_valid, error = validator.validate_filename(filename)
if not is_valid:
    raise ValueError(error)

## Validate file size

is_valid, error = validator.validate_file_size(file_size)
if not is_valid:
    raise ValueError(error)

## Validate MIME type

is_valid, error = validator.validate_mime_type(mime_type)
if not is_valid:
    raise ValueError(error)

```text

### Configuration

- `ALLOWED_EXTENSIONS` - Permitted file types: png, jpg, jpeg, gif, bmp, tiff, webp
- `ALLOWED_MIME_TYPES` - Permitted MIME types for images
- `MAX_FILE_SIZE` - Maximum upload size (default: 50MB)

### Security Checks

- Path traversal detection (blocks ../, /, \\)
- Extension validation against whitelist
- MIME type verification
- File size enforcement

### RateLimiter Class

```python

## backend/validation.py

from validation import get_rate_limiter

## Get rate limiter instance (singleton)

rate_limiter = get_rate_limiter(max_requests=60, window_seconds=60)

## Check if request is allowed

is_allowed, error = rate_limiter.is_allowed(client_ip)
if not is_allowed:
    return jsonify({'error': error}), 429

```text

### Configuration

- `max_requests` - Maximum requests per window (default: 60)
- `window_seconds` - Time window in seconds (default: 60)

### Features

- In-memory request tracking per IP address
- Automatic cleanup of expired requests
- Configurable rate limits per endpoint

### SecurityHeaders Class

```python

## backend/validation.py

from validation import SecurityHeaders

## Apply security headers to response

@app.after_request
def add_security_headers(response):
    return SecurityHeaders.apply_security_headers(response)

```text

### Headers Applied

- `Content-Security-Policy` - Controls resource loading
- `X-Content-Type-Options: nosniff` - Prevents MIME sniffing
- `X-Frame-Options: DENY` - Prevents clickjacking
- `X-XSS-Protection: 1; mode=block` - XSS filter
- `Referrer-Policy: strict-origin-when-cross-origin` - Referrer control
- `Permissions-Policy` - Restricts browser features
- `Strict-Transport-Security` - HTTPS enforcement (production only)

### Content Security Policy Details

- `default-src 'self'` - Default to same-origin
- `script-src` - Allow CDN scripts (Socket.IO, Cloudflare)
- `style-src` - Allow Google Fonts, Cloudflare CSS
- `img-src` - Allow data URLs, blobs, external images
- `connect-src` - Allow API connections (OpenAI, Stability AI, Hugging Face)
- `frame-src 'none'` - Block iframes
- `object-src 'none'` - Block plugins
- `upgrade-insecure-requests` - Force HTTPS

## Environment Variables

Configure security behavior through environment variables:

```bash

## Security Configuration

MAX_FILE_SIZE=52428800                    # Maximum file size (50MB default)
MAX_REQUESTS_PER_MINUTE=60                # Rate limit per IP
SECURITY_BLOCK_DURATION=3600              # IP block duration (1 hour)
ENABLE_MALWARE_SCAN=true                  # Enable malware scanning

## Threat Thresholds

SECURITY_THREAT_HIGH=8                    # High threat level threshold
SECURITY_THREAT_MEDIUM=5                  # Medium threat level threshold

## Authentication

JWT_SECRET=your-secret-key                # JWT token secret
API_MASTER_KEY=your-master-key            # Master API key
HMAC_SECRET=your-hmac-secret              # Request signing secret

## Security Headers

API_KEY_HEADER=X-API-Key                  # API key header name
SIGNATURE_HEADER=X-Request-Signature      # Request signature header

## Compliance

ENABLE_SECURITY_AUDIT_LOGGING=true        # Audit logging
COMPLIANCE_FRAMEWORK=SOC2                 # SOC2, ISO27001, GDPR, HIPAA
ENABLE_VULNERABILITY_SCANNING=true        # Automated vulnerability scanning

```text

## Usage Patterns

### 1. Secure API Endpoint

```python
from security_hardening import SecurityHardening
from validation import FileUploadValidator, get_rate_limiter

security = SecurityHardening()
validator = FileUploadValidator()
rate_limiter = get_rate_limiter()

@app.route('/api/generate-3d', methods=['POST'])
def generate_3d():

    # Rate limiting

    is_allowed, error = rate_limiter.is_allowed(request.remote_addr)
    if not is_allowed:
        return jsonify({'error': error}), 429

    # File validation

    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400

    file = request.files['image']

    # Validate filename

    is_valid, error = validator.validate_filename(file.filename)
    if not is_valid:
        security.log_security_event('invalid_filename', request)
        return jsonify({'error': error}), 400

    # Validate file size

    file.seek(0, 2)  # Seek to end
    size = file.tell()
    file.seek(0)  # Reset

    is_valid, error = validator.validate_file_size(size)
    if not is_valid:
        security.log_security_event('oversized_file', request)
        return jsonify({'error': error}), 413

    # Validate MIME type

    is_valid, error = validator.validate_mime_type(file.content_type)
    if not is_valid:
        security.log_security_event('invalid_mime_type', request)
        return jsonify({'error': error}), 400

    # Process generation

    result = process_3d_generation(file)
    return jsonify(result)

```text

### 2. Threat Detection Workflow

```python
from security_hardening import SecurityHardening

security = SecurityHardening()

@app.before_request
def check_security_threats():

    # Assess threat level

    threat_level = security.assess_request_threat_level(request)

    # High threat - block immediately

    if threat_level >= security.THREAT_HIGH:
        security.block_request_and_alert(request, threat_level)
        abort(403, "Request blocked due to security threat")

    # Medium threat - enhanced monitoring

    elif threat_level >= security.THREAT_MEDIUM:
        security.enable_enhanced_monitoring(request)
        g.security_enhanced = True

    # Log threat assessment

    security.log_threat_assessment(request, threat_level)

```text

### 3. Input Validation with Pydantic

```python
from validation import Generate3DRequest, TextToImageRequest
from pydantic import ValidationError

@app.route('/api/generate-3d', methods=['POST'])
def generate_3d_validated():
    try:

        # Validate request with Pydantic

        request_data = Generate3DRequest(**request.get_json())

        # Request is validated and safe to use

        job_id = request_data.job_id
        format_type = request_data.format
        quality = request_data.quality
        dimensions = request_data.dimensions

        # Process generation

        result = process_generation(job_id, format_type, quality, dimensions)
        return jsonify(result)

    except ValidationError as e:

        # Validation failed

        security.log_security_event('validation_error', request)
        return jsonify({'error': str(e)}), 400

```text

### 4. API Authentication

```python
from security_hardening import SecurityHardening

security = SecurityHardening()

@app.before_request
def authenticate_api_request():

    # Skip authentication for public endpoints

    if request.endpoint in ['health', 'static']:
        return

    # Check API key

    api_key = request.headers.get(security.security_config['api_key_header'])
    if not api_key:
        security.log_security_event('missing_api_key', request)
        abort(401, "API key required")

    # Validate API key

    if not security.validate_api_key(api_key):
        security.log_security_event('invalid_api_key', request)
        abort(401, "Invalid API key")

    # Check request signature for sensitive endpoints

    if request.endpoint in security.security_config['signed_endpoints']:
        signature = request.headers.get(security.security_config['signature_header'])
        if not security.validate_request_signature(request, signature, api_key):
            security.log_security_event('invalid_signature', request)
            abort(401, "Invalid request signature")

```text

### 5. Security Monitoring Dashboard

```python
from security_hardening import SecurityHardening

security = SecurityHardening()

@app.route('/api/security-dashboard', methods=['GET'])
def security_dashboard():
    """Get comprehensive security metrics"""

    # Collect security metrics

    metrics = {
        'threat_events': security.access_monitor.get_threat_events(),
        'blocked_ips': list(security.blocked_ips),
        'rate_limit_violations': security.access_monitor.get_rate_limit_violations(),
        'authentication_failures': security.access_monitor.get_auth_failures(),
        'sql_injection_attempts': security.access_monitor.get_sql_injection_count(),
        'xss_attempts': security.access_monitor.get_xss_attempt_count(),
        'path_traversal_attempts': security.access_monitor.get_path_traversal_count(),
        'security_score': security.calculate_security_score()
    }

    return jsonify(metrics)

```text

### 6. Compliance Audit

```python
from security_hardening import SecurityHardening

security = SecurityHardening()

def run_compliance_audit(framework: str = 'SOC2'):
    """Run compliance audit for specified framework"""

    audit_results = {
        'framework': framework,
        'timestamp': datetime.utcnow().isoformat(),
        'controls_tested': [],
        'passed_controls': [],
        'failed_controls': [],
        'compliance_score': 0.0
    }

    if framework == 'SOC2':

        # SOC2 Type 2 controls

        controls = {
            'CC1.1': security.test_security_policy_enforcement(),
            'CC2.1': security.test_communication_security(),
            'CC3.1': security.test_change_management(),
            'CC6.1': security.test_logical_access_controls(),
            'CC7.1': security.test_system_monitoring()
        }
    elif framework == 'ISO27001':

        # ISO27001:2022 controls

        controls = {
            'A.5.1': security.test_information_security_policies(),
            'A.8.1': security.test_asset_management(),
            'A.9.1': security.test_access_control(),
            'A.12.1': security.test_operations_security(),
            'A.14.1': security.test_secure_development()
        }

    # Evaluate controls

    for control_id, test_result in controls.items():
        audit_results['controls_tested'].append(control_id)
        if test_result['passed']:
            audit_results['passed_controls'].append(control_id)
        else:
            audit_results['failed_controls'].append(control_id)

    # Calculate compliance score

    total_controls = len(audit_results['controls_tested'])
    passed_controls = len(audit_results['passed_controls'])
    audit_results['compliance_score'] = (passed_controls / total_controls) * 100

    return audit_results

```text

## Security Best Practices

### 1. Always Validate User Input

```python

## CORRECT: Validate all user input

validator = FileUploadValidator()
is_valid, error = validator.validate_filename(filename)
if not is_valid:
    raise SecurityError(error)

## WRONG: Trust user input

filename = request.files['image'].filename  # ❌ No validation

```text

### 2. Use Rate Limiting

```python

## CORRECT: Enforce rate limits

rate_limiter = get_rate_limiter()
is_allowed, error = rate_limiter.is_allowed(client_ip)
if not is_allowed:
    return jsonify({'error': error}), 429

## WRONG: No rate limiting

## Process every request without limits ❌

```text

### 3. Apply Security Headers

```python

## CORRECT: Add security headers

@app.after_request
def add_headers(response):
    return SecurityHeaders.apply_security_headers(response)

## WRONG: No security headers

## Return response without protection ❌

```text

### 4. Log Security Events

```python

## CORRECT: Log all security events

security.log_security_event('authentication_failure', request)

## WRONG: Silent security failures

## Fail without logging ❌

```text

### 5. Use Threat Detection

```python

## CORRECT: Assess threat level

threat_level = security.assess_request_threat_level(request)
if threat_level >= security.THREAT_HIGH:
    security.block_request_and_alert(request, threat_level)

## WRONG: No threat detection

## Process all requests without assessment ❌

```text

## References

- **Core Security Module**: `backend/security_hardening.py` (769 lines)

  - SecurityHardening class with comprehensive protection
  - ThreatDetector for real-time threat analysis
  - AccessMonitor for security event tracking
  - Multi-layer input validation (SQL injection, XSS, path traversal, command injection)
  - API authentication and request signing
  - Security monitoring and audit logging

- **Input Validation Module**: `backend/validation.py` (229 lines)

  - FileUploadValidator for secure file uploads
  - RateLimiter for DoS protection
  - SecurityHeaders for HTTP security headers
  - Pydantic models for request validation (Generate3DRequest, TextToImageRequest)

- **Quality Validation**: `backend/quality_validator.py`

  - GenerationQualityValidator for pipeline validation
  - Background removal validation
  - Shape generation validation
  - Texture coherence validation
  - Final mesh validation

- **Copilot Instructions**: `.github/copilot-instructions.md`

  - Section [3.4]: Error handling patterns with security validation
  - Section [5.8]: Security hardening implementation details
  - Section [6.4]: File upload validation patterns

- **Environment Configuration**: `.env`

  - Security-related environment variables
  - Threat thresholds and rate limits
  - Authentication secrets and keys
  - Compliance framework configuration
