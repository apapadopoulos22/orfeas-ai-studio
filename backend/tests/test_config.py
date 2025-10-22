"""
ORFEAS Testing Configuration
Lightweight configuration for test server startup
"""
import os

# Set environment variables for testing BEFORE importing main
os.environ["XFORMERS_DISABLED"] = "1"
os.environ["FLASK_ENV"] = "testing"
os.environ["LOG_LEVEL"] = "ERROR"
os.environ["SKIP_GPU_INIT"] = "1"  # Skip GPU initialization
os.environ["SKIP_MODEL_LOAD"] = "1"  # Skip model loading
os.environ["TESTING"] = "1"

# Mock-friendly configuration
TEST_CONFIG = {
    "skip_model_init": True,
    "skip_gpu_check": True,
    "lightweight_mode": True,
    "port": None,  # Will be set by fixture
}
