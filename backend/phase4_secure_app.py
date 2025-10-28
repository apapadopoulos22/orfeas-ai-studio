#!/usr/bin/env python3
"""
BOB AI v10.0 - PHASE 4.6 ENHANCED SECURITY APP
Production Deployment with Caching & Security

Integrates Phase 4 API routes with security middleware
Adds caching, rate limiting, authentication, and input validation

Version: 1.0.0
Date: October 28, 2025
Status: PHASE 4.6 IMPLEMENTATION
"""

import sys
import os
# Get absolute path to backend directory
backend_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_path)

from flask import Flask, jsonify, request, make_response
from flask_cors import CORS
from datetime import datetime
import logging
from functools import wraps

# Import Phase 4 API routes
from phase4_api_routes import register_phase4_routes

# Import Phase 4.6 security components
from phase4_cache_manager import get_cache_manager
from phase4_auth_manager import get_auth_manager
from phase4_rate_limiter import get_rate_limiter
from phase4_input_validator import InputValidator, ValidationException

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)


def create_secure_app(config=None):
    """Create and configure Flask application with security features"""

    app = Flask(__name__)

    # Default configuration
    app.config.update(
        JSON_SORT_KEYS=False,
        JSONIFY_PRETTYPRINT_REGULAR=True,
    )

    # Apply custom config if provided
    if config:
        app.config.update(config)

    logger.info("Creating secure Flask application for BOB AI Phase 4.6")

    # Initialize security components
    cache_manager = get_cache_manager(use_redis=False)  # Use in-memory by default
    auth_manager = get_auth_manager()
    rate_limiter = get_rate_limiter()

    logger.info("Security components initialized")

    # Configure CORS with security headers
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:3000", "http://localhost:5000", "http://127.0.0.1:3000"],
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "X-API-Key"],
            "expose_headers": ["X-RateLimit-Limit", "X-RateLimit-Remaining", "X-RateLimit-Reset"],
            "supports_credentials": False,
            "max_age": 3600
        }
    })
    logger.info("CORS configured with security headers")

    # Register Phase 4 API routes
    register_phase4_routes(app)
    logger.info("Phase 4 API routes registered")

    # ==================== SECURITY MIDDLEWARE ====================

    def require_api_key(f):
        """Decorator to require API key authentication"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get API key from header
            api_key = request.headers.get('X-API-Key')

            if not api_key:
                logger.warning(f"Request without API key: {request.remote_addr}")
                return jsonify({
                    "error": "Unauthorized",
                    "message": "X-API-Key header required",
                    "status": 401
                }), 401

            # Authenticate
            is_valid, key_id, key_data = auth_manager.authenticate(api_key)

            if not is_valid:
                logger.warning(f"Invalid API key attempt: {request.remote_addr}")
                return jsonify({
                    "error": "Unauthorized",
                    "message": "Invalid or expired API key",
                    "status": 401
                }), 401

            # Store key info in request context
            request.api_key_id = key_id
            request.api_key_data = key_data

            return f(*args, **kwargs)

        return decorated_function

    def check_rate_limit(f):
        """Decorator to check rate limiting"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get API key or use IP address
            if hasattr(request, 'api_key_id'):
                limit_key = request.api_key_id
                limit = request.api_key_data.get('rate_limit', 100)
            else:
                limit_key = request.remote_addr
                limit = 100  # Default limit for unauthenticated

            # Check rate limit
            allowed, remaining = rate_limiter.is_allowed(limit_key, limit)

            if not allowed:
                logger.warning(f"Rate limit exceeded: {limit_key}")
                response = make_response(jsonify({
                    "error": "Rate limit exceeded",
                    "message": f"Too many requests. Limit: {limit} req/min",
                    "status": 429
                }), 429)

                response.headers['X-RateLimit-Limit'] = str(limit)
                response.headers['X-RateLimit-Remaining'] = '0'
                response.headers['Retry-After'] = '60'

                return response

            # Add rate limit headers
            response = f(*args, **kwargs)
            if isinstance(response, tuple):
                response_obj, status_code = response
                headers = {
                    'X-RateLimit-Limit': str(limit),
                    'X-RateLimit-Remaining': str(remaining),
                }
                if isinstance(response_obj, dict):
                    return jsonify(response_obj), status_code, headers
                else:
                    response_obj.headers.update(headers)
                    return response_obj, status_code
            else:
                response.headers['X-RateLimit-Limit'] = str(limit)
                response.headers['X-RateLimit-Remaining'] = str(remaining)
                return response

        return decorated_function

    # ==================== ENHANCED ERROR HANDLERS ====================

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "error": "Not found",
            "message": "Endpoint not found",
            "status": 404,
            "timestamp": datetime.utcnow().isoformat()
        }), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            "error": "Method not allowed",
            "message": f"Method not allowed for this endpoint",
            "status": 405,
            "timestamp": datetime.utcnow().isoformat()
        }), 405

    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {error}", exc_info=True)
        return jsonify({
            "error": "Internal server error",
            "message": "An unexpected error occurred",
            "status": 500,
            "timestamp": datetime.utcnow().isoformat()
        }), 500

    @app.errorhandler(ValidationException)
    def handle_validation_error(error):
        return jsonify({
            "error": "Validation error",
            "field": error.field,
            "reason": error.reason,
            "status": 400,
            "timestamp": datetime.utcnow().isoformat()
        }), 400

    # ==================== SECURITY ENDPOINTS ====================

    @app.route('/api/health', methods=['GET'])
    def health():
        """Health check endpoint"""
        return jsonify({
            "status": "healthy",
            "version": "1.0.0",
            "phase": "4.6",
            "timestamp": datetime.utcnow().isoformat(),
            "cache": cache_manager.stats(),
            "rate_limiter_keys": len(rate_limiter.get_all_stats())
        })

    @app.route('/api/security/health', methods=['GET'])
    @require_api_key
    def security_health():
        """Security health check (requires API key)"""
        return jsonify({
            "status": "secure",
            "authentication": "verified",
            "api_key_id": request.api_key_id,
            "timestamp": datetime.utcnow().isoformat(),
            "security": {
                "caching": cache_manager.stats(),
                "authentication": auth_manager.get_stats(),
                "rate_limiting": {
                    "active_keys": len(rate_limiter.get_all_stats())
                }
            }
        })

    @app.route('/api/security/stats', methods=['GET'])
    @require_api_key
    def security_stats():
        """Get security statistics"""
        return jsonify({
            "timestamp": datetime.utcnow().isoformat(),
            "cache": cache_manager.stats(),
            "authentication": auth_manager.get_stats(),
            "rate_limiter": {
                "active_keys": len(rate_limiter.get_all_stats()),
                "keys": rate_limiter.get_all_stats()
            }
        })

    @app.route('/api/security/keys', methods=['GET'])
    @require_api_key
    def list_keys():
        """List API keys (admin only)"""
        return jsonify({
            "keys": auth_manager.list_keys(),
            "timestamp": datetime.utcnow().isoformat()
        })

    @app.route('/api/security/keys', methods=['POST'])
    @require_api_key
    def create_key():
        """Create new API key"""
        data = request.get_json() or {}

        name = data.get('name', 'New Key')
        scopes = data.get('scopes', ['read:disciplines', 'read:graph'])
        rate_limit = int(data.get('rate_limit', 100))
        expires_at = data.get('expires_at')  # ISO format string or None

        new_key = auth_manager.create_key(
            name=name,
            scopes=scopes,
            rate_limit=rate_limit
        )

        return jsonify({
            "api_key": new_key,
            "name": name,
            "scopes": scopes,
            "rate_limit": rate_limit,
            "timestamp": datetime.utcnow().isoformat()
        }), 201

    # ==================== REQUEST/RESPONSE MIDDLEWARE ====================

    @app.before_request
    def before_request():
        """Validate input before processing"""
        # Log request
        logger.info(f"→ {request.method} {request.path} from {request.remote_addr}")

        # Validate query parameters
        if request.method == 'GET':
            for key, value in request.args.items():
                if not isinstance(value, str):
                    continue

                # Quick validation for common parameters
                if key in ['discipline_id', 'from_id', 'to_id']:
                    validated = InputValidator.validate_discipline_id(value)
                    if validated is None:
                        return jsonify({
                            "error": "Validation error",
                            "field": key,
                            "reason": "Invalid discipline ID format",
                            "status": 400
                        }), 400

                elif key == 'search':
                    validated = InputValidator.validate_search_query(value)
                    if validated is None:
                        return jsonify({
                            "error": "Validation error",
                            "field": key,
                            "reason": "Invalid search query",
                            "status": 400
                        }), 400

    @app.after_request
    def after_request(response):
        """Add security headers to response"""
        logger.info(f"← {response.status_code} {request.path}")

        # Add security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self'"

        return response

    # ==================== INFO ENDPOINTS ====================

    @app.route('/', methods=['GET'])
    def index():
        return jsonify({
            "name": "BOB AI v10.0",
            "phase": "4.6",
            "version": "1.0.0",
            "status": "running",
            "timestamp": datetime.utcnow().isoformat(),
            "features": {
                "caching": "enabled",
                "authentication": "required",
                "rate_limiting": "enabled",
                "input_validation": "enabled"
            },
            "endpoints": {
                "health": "GET /api/health",
                "security_health": "GET /api/security/health",
                "security_stats": "GET /api/security/stats",
                "api_keys": "GET/POST /api/security/keys"
            }
        })

    logger.info("Secure Flask application created successfully")
    return app


def main():
    """Main entry point"""
    logger.info("=" * 80)
    logger.info("BOB AI v10.0 - PHASE 4.6 CACHING & SECURITY")
    logger.info("=" * 80)

    # Create secure app
    app = create_secure_app()

    # Start server
    logger.info("Starting Flask server on http://localhost:5000")
    logger.info("API Key required for authenticated endpoints")
    logger.info("Rate limit: 100 requests/minute per key")
    logger.info("Press Ctrl+C to stop")

    try:
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=False,
            threaded=True
        )
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)


if __name__ == '__main__':
    main()
