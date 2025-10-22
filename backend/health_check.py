# +==============================================================================â•—
# | [WARRIOR] ORFEAS AI STUDIO - HEALTH CHECK ENDPOINTS [WARRIOR]                              |
# | Kubernetes/Docker health monitoring                                         |
# +==============================================================================

"""
Health Check Endpoints
======================
Provides /health and /ready endpoints for container orchestration
"""

import torch
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Global readiness state
_is_ready = False

def set_ready_state(ready: bool):
    """Set application readiness state"""
    global _is_ready
    _is_ready = ready
    logger.info(f"Application readiness: {ready}")

def check_health() -> Dict[str, Any]:
    """
    Basic health check - is the application running?

    Returns:
        Dict with health status
    """
    return {
        "status": "healthy",
        "service": "orfeas-backend",
        "version": "1.0.0"
    }

def check_readiness() -> Dict[str, Any]:
    """
    Readiness check - is the application ready to serve requests?

    Checks:
    - Global ready state
    - GPU availability (if expected)
    - Model loading status

    Returns:
        Dict with readiness status and details
    """
    checks = {
        "application": _is_ready,
        "gpu": False,
        "models": False
    }

    # Check GPU
    try:
        if torch.cuda.is_available():
            checks["gpu"] = True
            checks["gpu_name"] = torch.cuda.get_device_name(0)
            checks["gpu_memory_total"] = f"{torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB"
    except Exception as e:
        logger.warning(f"GPU check failed: {e}")

    # Check model loading (simplified - extend as needed)
    checks["models"] = _is_ready

    # Overall ready if application is ready
    all_ready = checks["application"]

    return {
        "status": "ready" if all_ready else "not_ready",
        "checks": checks
    }

def register_health_endpoints(app):
    """
    Register health check endpoints with Flask app

    Args:
        app: Flask application instance
    """

    @app.route('/health', methods=['GET'])
    def health():
        """Liveness probe - is the container alive?"""
        result = check_health()
        return result, 200

    @app.route('/ready', methods=['GET'])
    def ready():
        """Readiness probe - is the container ready to serve?"""
        result = check_readiness()
        status_code = 200 if result["status"] == "ready" else 503
        return result, status_code

    logger.info("Health check endpoints registered: /health, /ready")
