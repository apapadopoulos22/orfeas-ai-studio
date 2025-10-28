#!/usr/bin/env python3
"""
BOB AI v10.0 - PHASE 4 FLASK APP INTEGRATION
Production Deployment - Main Application

Integrates Phase 4 API routes with Flask application
Configures middleware, error handlers, and startup

Version: 1.0.0
Date: October 28, 2025
Status: PHASE 4 IMPLEMENTATION
"""

import sys
import os
# Get absolute path to backend directory
backend_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_path)

from flask import Flask, jsonify
from flask_cors import CORS
from datetime import datetime
import logging

# Import Phase 4 API routes
from phase4_api_routes import register_phase4_routes

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)


def create_app(config=None):
    """Create and configure Flask application"""

    app = Flask(__name__)

    # Default configuration
    app.config.update(
        JSON_SORT_KEYS=False,
        JSONIFY_PRETTYPRINT_REGULAR=True,
    )

    # Apply custom config if provided
    if config:
        app.config.update(config)

    logger.info("Creating Flask application for BOB AI Phase 4")

    # Configure CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:3000", "http://localhost:5000"],
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type"]
        }
    })
    logger.info("CORS configured")

    # Register Phase 4 API routes
    register_phase4_routes(app)
    logger.info("Phase 4 API routes registered")

    # Global error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "error": "Not found",
            "message": "Endpoint not found",
            "status": 404
        }), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            "error": "Method not allowed",
            "message": f"Method not allowed for this endpoint",
            "status": 405
        }), 405

    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {error}", exc_info=True)
        return jsonify({
            "error": "Internal server error",
            "message": "An unexpected error occurred",
            "status": 500
        }), 500

    # Root endpoint
    @app.route('/', methods=['GET'])
    def index():
        return jsonify({
            "name": "BOB AI v10.0",
            "phase": "4",
            "version": "1.0.0",
            "status": "running",
            "timestamp": datetime.utcnow().isoformat(),
            "endpoints": {
                "health": "GET /api/health",
                "ready": "GET /api/ready",
                "disciplines": "GET /api/disciplines",
                "discipline_detail": "GET /api/disciplines/{id}",
                "related_disciplines": "GET /api/disciplines/{id}/related",
                "knowledge_graph": "GET /api/knowledge-graph",
                "pathfinding": "GET /api/disciplines/path/{from}/{to}",
                "tier_connections": "GET /api/tier/{tier}/connections",
                "statistics": "GET /api/statistics/phase3",
                "query": "POST /api/query"
            }
        })

    # Request/response logging middleware
    @app.before_request
    def log_request():
        logger.info(f"→ {__import__('flask').request.method} {__import__('flask').request.path}")

    @app.after_request
    def log_response(response):
        logger.info(f"← {response.status_code} {__import__('flask').request.path}")
        return response

    logger.info("Flask application created successfully")
    return app


def main():
    """Main entry point"""
    logger.info("=" * 80)
    logger.info("BOB AI v10.0 - PHASE 4 PRODUCTION DEPLOYMENT")
    logger.info("=" * 80)

    # Create app
    app = create_app()

    # Start server
    logger.info("Starting Flask server on http://localhost:5000")
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
