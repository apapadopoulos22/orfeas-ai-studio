"""
Configuration module for ORFEAS Backend
Handles environment variables, model paths, and system settings
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
import json
import logging

logger = logging.getLogger(__name__)

class Config:
    """Configuration management for ORFEAS Backend"""

    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.workspace_dir = self.base_dir.parent

        # Load configuration from environment and files
        self.load_config()

    def load_config(self):
        """Load configuration from various sources"""

        # Default configuration
        self.config = {
            # Server settings
            "server": {
                "host": os.getenv("ORFEAS_HOST", "127.0.0.1"),
                "port": int(os.getenv("ORFEAS_PORT", 5000)),
                "debug": os.getenv("ORFEAS_DEBUG", "false").lower() == "true",
                "max_file_size": int(os.getenv("MAX_FILE_SIZE", 50 * 1024 * 1024))  # 50MB
            },

            # GPU and processing settings
            "processing": {
                "device": os.getenv("DEVICE", "auto"),  # auto, cuda, cpu
                "max_concurrent_jobs": int(os.getenv("MAX_CONCURRENT_JOBS", 3)),
                "gpu_memory_limit": os.getenv("GPU_MEMORY_LIMIT", "0.8"),  # 80% of GPU memory
                "fallback_to_cpu": os.getenv("FALLBACK_TO_CPU", "true").lower() == "true"
            },

            # Model paths and settings
            "models": {
                "hunyuan3d_path": os.getenv("HUNYUAN3D_PATH", str(self.workspace_dir / "Hunyuan3D-2.1")),
                "stable_diffusion_model": os.getenv("SD_MODEL", "runwayml/stable-diffusion-v1-5"),
                "controlnet_model": os.getenv("CONTROLNET_MODEL", "lllyasviel/sd-controlnet-depth"),
                "model_cache_dir": os.getenv("MODEL_CACHE_DIR", str(self.base_dir / "models"))
            },

            # File handling
            "files": {
                "upload_dir": str(self.base_dir / "uploads"),
                "output_dir": str(self.base_dir / "outputs"),
                "temp_dir": str(self.base_dir / "temp"),
                "allowed_image_formats": ["png", "jpg", "jpeg", "gif", "bmp", "tiff", "webp"],
                "output_formats": ["stl", "obj", "ply", "gltf", "fbx", "png", "svg"],
                "cleanup_after_hours": int(os.getenv("CLEANUP_AFTER_HOURS", 24))
            },

            # Generation settings
            "generation": {
                "default_steps": int(os.getenv("DEFAULT_STEPS", 50)),
                "max_steps": int(os.getenv("MAX_STEPS", 100)),
                "default_guidance_scale": float(os.getenv("DEFAULT_GUIDANCE_SCALE", 7.0)),
                "default_image_size": int(os.getenv("DEFAULT_IMAGE_SIZE", 512)),
                "max_image_size": int(os.getenv("MAX_IMAGE_SIZE", 1024)),
                "default_model_quality": int(os.getenv("DEFAULT_MODEL_QUALITY", 7))
            },

            # WebSocket settings
            "websocket": {
                "cors_allowed_origins": os.getenv("CORS_ORIGINS", "*").split(","),
                "ping_timeout": int(os.getenv("WS_PING_TIMEOUT", 60)),
                "ping_interval": int(os.getenv("WS_PING_INTERVAL", 25))
            },

            # Logging settings
            "logging": {
                "level": os.getenv("LOG_LEVEL", "INFO"),
                "file": os.getenv("LOG_FILE", ""),
                "max_size_mb": int(os.getenv("LOG_MAX_SIZE_MB", 100)),
                "backup_count": int(os.getenv("LOG_BACKUP_COUNT", 5))
            }
        }

        # Load from config file if exists
        config_file = self.base_dir / "config.json"
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    file_config = json.load(f)
                self.merge_config(file_config)
                logger.info(f"Loaded configuration from {config_file}")
            except Exception as e:
                logger.warning(f"Failed to load config file: {e}")

        # Create directories
        self.create_directories()

    def merge_config(self, new_config: Dict[str, Any]):
        """Merge new configuration with existing config"""
        def deep_merge(base: Dict, update: Dict) -> Dict:
            for key, value in update.items():
                if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                    base[key] = deep_merge(base[key], value)
                else:
                    base[key] = value
            return base

        self.config = deep_merge(self.config, new_config)

    def create_directories(self):
        """Create necessary directories"""
        dirs_to_create = [
            self.config["files"]["upload_dir"],
            self.config["files"]["output_dir"],
            self.config["files"]["temp_dir"],
            self.config["models"]["model_cache_dir"]
        ]

        for dir_path in dirs_to_create:
            Path(dir_path).mkdir(parents=True, exist_ok=True)

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation"""
        keys = key.split('.')
        value = self.config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key: str, value: Any):
        """Set configuration value using dot notation"""
        keys = key.split('.')
        config = self.config

        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        config[keys[-1]] = value

    def save_config(self, file_path: Optional[Path] = None):
        """Save current configuration to file"""
        if file_path is None:
            file_path = self.base_dir / "config.json"

        try:
            with open(file_path, 'w') as f:
                json.dump(self.config, f, indent=2, default=str)
            logger.info(f"Configuration saved to {file_path}")
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")

    def validate_config(self) -> bool:
        """Validate current configuration"""
        try:
            # Check required paths
            hunyuan_path = Path(self.get("models.hunyuan3d_path", ""))
            if not hunyuan_path.exists():
                logger.warning(f"Hunyuan3D path not found: {hunyuan_path}")

            # Check numeric values
            max_jobs = self.get("processing.max_concurrent_jobs", 1)
            if not isinstance(max_jobs, int) or max_jobs < 1:
                logger.error("max_concurrent_jobs must be a positive integer")
                return False

            # Check port range
            port = self.get("server.port", 5000)
            if not isinstance(port, int) or port < 1024 or port > 65535:
                logger.error("server port must be between 1024 and 65535")
                return False

            return True

        except Exception as e:
            logger.error(f"Configuration validation failed: {e}")
            return False

    def get_hunyuan_config(self) -> Dict[str, Any]:
        """Get Hunyuan3D specific configuration"""
        return {
            "path": self.get("models.hunyuan3d_path"),
            "device": self.get("processing.device"),
            "memory_limit": self.get("processing.gpu_memory_limit"),
            "fallback_to_cpu": self.get("processing.fallback_to_cpu")
        }

    def get_server_config(self) -> Dict[str, Any]:
        """Get server configuration for Flask app"""
        return {
            "host": self.get("server.host"),
            "port": self.get("server.port"),
            "debug": self.get("server.debug"),
            "max_content_length": self.get("server.max_file_size")
        }

    def get_websocket_config(self) -> Dict[str, Any]:
        """Get WebSocket configuration"""
        return {
            "cors_allowed_origins": self.get("websocket.cors_allowed_origins"),
            "ping_timeout": self.get("websocket.ping_timeout"),
            "ping_interval": self.get("websocket.ping_interval")
        }

# Global configuration instance
config = Config()

# Convenience functions
def get_config(key: str, default: Any = None) -> Any:
    """Get configuration value"""
    return config.get(key, default)

def set_config(key: str, value: Any):
    """Set configuration value"""
    config.set(key, value)

def validate_config() -> bool:
    """Validate configuration"""
    return config.validate_config()

def save_config(file_path: Optional[Path] = None):
    """Save configuration to file"""
    config.save_config(file_path)

# AI Model Configuration
AI_CONFIG = {
    "enable_hunyuan3d": True,
    "gpu_memory_limit": 0.9,  # Use 90% of GPU memory
    "max_concurrent_jobs": 3,  # Limit concurrent AI jobs
    "model_precision": "fp16",  # Use half precision for speed
    "enable_model_caching": True,  # Keep models in memory
    "hunyuan3d_path": str(Path(__file__).parent.parent / "Hunyuan3D-2.1"),
    "comfyui_path": str(Path(__file__).parent.parent / "ComfyUI")
}
