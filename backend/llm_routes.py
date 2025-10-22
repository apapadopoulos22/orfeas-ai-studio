#!/usr/bin/env python3
"""
Flask blueprint exposing Local LLM (Ollama) endpoints
- POST /api/llm/generate
- GET  /api/llm/status

This blueprint is conditionally registered by backend/main.py based on ENABLE_LOCAL_LLMS.
"""
import os
import logging
from typing import Any, Dict
from flask import Blueprint, request, jsonify

# Project monitoring decorator (safe to import here)
try:
    from monitoring import track_request_metrics
except Exception:  # pragma: no cover - fallback if monitoring not available in test mode
    def track_request_metrics(_):
        def _noop(f):
            return f
        return _noop

# Local LLM router (Ollama client)
from local_llm_router import local_llm  # local module in backend/

logger = logging.getLogger(__name__)

llm_bp = Blueprint("local_llm", __name__)  # Changed from "llm" to avoid conflict with /api/llm routes

def _enabled() -> bool:
    return os.getenv("ENABLE_LOCAL_LLMS", "true").lower() == "true"  # Default to enabled

@llm_bp.route("/status", methods=["GET"])
@track_request_metrics('/api/local-llm/status')
def llm_status():
    """Report local LLM availability and configuration."""
    enabled = _enabled()
    available = local_llm.is_available() if enabled else False
    return jsonify({
        "enabled": enabled,
        "available": available,
        "server": os.getenv("LOCAL_LLM_SERVER", "http://localhost:11434"),
        "model": "Bob AI",  # Display name instead of internal "mistral"
        "internal_model": os.getenv("LOCAL_LLM_MODEL", "mistral"),  # Actual model name
        "temperature": float(os.getenv("LOCAL_LLM_TEMPERATURE", "0.3")),
    }), (200 if enabled else 503)

@llm_bp.route("/generate", methods=["POST"])
@track_request_metrics('/api/local-llm/generate')
def llm_generate():
    """Generate text from a prompt using local LLM (Ollama).

    Request JSON:
    - prompt: str (required)
    - max_tokens: int (optional, default 2048)

    Response JSON (success):
    - response: str
    - model: str
    - source: "local"
    - latency_ms: int
    """
    if not _enabled():
        return jsonify({"error": "Local LLM disabled (ENABLE_LOCAL_LLMS=false)"}), 503

    if not request.is_json:
        return jsonify({"error": "Expected application/json body"}), 400

    data = request.get_json(silent=True) or {}
    prompt = data.get("prompt")
    if not isinstance(prompt, str) or not prompt.strip():
        return jsonify({"error": "Field 'prompt' (non-empty string) is required"}), 400

    max_tokens = data.get("max_tokens", 2048)
    try:
        max_tokens = int(max_tokens)
        if max_tokens <= 0:
            raise ValueError
    except Exception:
        return jsonify({"error": "Field 'max_tokens' must be a positive integer"}), 400

    try:
        result = local_llm.generate(prompt.strip(), max_tokens=max_tokens)
        if isinstance(result, dict) and result.get("error"):
            # Distinguish availability vs server errors
            status = 503 if "not available" in result["error"].lower() else 500
            return jsonify(result), status
        return jsonify(result)
    except Exception as e:  # Defensive catch-all
        logger.error(f"[LLM] Generation failed: {e}")
        return jsonify({"error": str(e)}), 500
