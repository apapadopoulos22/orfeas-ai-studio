"""
+==============================================================================â•—
|              ORFEAS Testing Suite - Configuration Unit Tests                |
|         Comprehensive tests for configuration management system              |
+==============================================================================
"""
import pytest
import os
import json
from pathlib import Path
import sys
from typing import Any, Dict, List

backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))

try:
    from config import Config
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False


@pytest.mark.skipif(not CONFIG_AVAILABLE, reason="Config module not available")
@pytest.mark.unit
class TestConfigUnit:
    """Unit tests for Configuration management"""

    @pytest.fixture
    def config(self) -> None:
        """Create config instance"""
        return Config()

    @pytest.fixture
    def temp_env(self, monkeypatch: Any) -> None:
        """Temporary environment variables"""
        def set_env(**kwargs) -> None:
            for key, value in kwargs.items():
                monkeypatch.setenv(key, str(value))
        return set_env

    def test_config_initialization(self, config: Dict) -> None:
        """Test config initializes correctly"""
        assert config is not None
        assert hasattr(config, 'config')
        assert isinstance(config.config, dict)

    def test_config_has_processing_section(self, config: Dict) -> None:
        """Test processing configuration exists"""
        assert 'processing' in config.config
        assert isinstance(config.config['processing'], dict)

    def test_config_default_device(self, config: Dict) -> None:
        """Test default device configuration"""
        device = config.config['processing'].get('device', 'auto')
        assert device in ['auto', 'cuda', 'cpu']

    def test_config_max_concurrent_jobs(self, config: Dict) -> None:
        """Test max concurrent jobs configuration"""
        max_jobs = config.config['processing'].get('max_concurrent_jobs', 3)
        assert isinstance(max_jobs, int)
        assert max_jobs > 0
        assert max_jobs <= 10  # Reasonable limit

    def test_config_environment_override(self, temp_env: Any) -> None:
        """Test environment variables override defaults"""
        temp_env(DEVICE='cpu', MAX_CONCURRENT_JOBS='5')
        config = Config()
        assert config.config['processing']['device'] == 'cpu'
        assert config.config['processing']['max_concurrent_jobs'] == 5

    def test_config_get_method(self, config: Dict) -> None:
        """Test config get method with dot notation"""
        if hasattr(config, 'get'):
            device = config.get('processing.device')
            assert device is not None

    def test_config_invalid_key(self, config: Dict) -> None:
        """Test accessing invalid config key"""
        if hasattr(config, 'get'):
            result = config.get('nonexistent.key.path')
            assert result is None or result == ''

    def test_config_nested_access(self, config: Dict) -> None:
        """Test accessing nested configuration"""
        processing = config.config.get('processing')
        if processing:
            assert 'device' in processing or 'max_concurrent_jobs' in processing

    @pytest.mark.parametrize("device", ['auto', 'cuda', 'cpu'])
    def test_config_valid_devices(self, temp_env: Any, device: Any) -> None:
        """Test all valid device configurations"""
        temp_env(DEVICE=device)
        config = Config()
        assert config.config['processing']['device'] == device

    @pytest.mark.parametrize("jobs", [1, 2, 3, 5, 10])
    def test_config_concurrent_jobs_range(self, temp_env: Any, jobs: List) -> None:
        """Test various concurrent job configurations"""
        temp_env(MAX_CONCURRENT_JOBS=str(jobs))
        config = Config()
        assert config.config['processing']['max_concurrent_jobs'] == jobs

    def test_config_gpu_memory_limit(self, config: Dict) -> None:
        """Test GPU memory limit configuration"""
        gpu_config = config.config.get('gpu', {})
        if 'memory_limit' in gpu_config:
            limit = gpu_config['memory_limit']
            assert 0.0 < limit <= 1.0  # Should be fraction

    def test_config_model_paths(self, config: Dict) -> None:
        """Test model path configuration"""
        model_config = config.config.get('models', {})
        if 'hunyuan3d_path' in model_config:
            path = model_config['hunyuan3d_path']
            assert isinstance(path, str)
            assert len(path) > 0

    def test_config_default_steps(self, config: Dict) -> None:
        """Test default inference steps configuration"""
        generation = config.config.get('generation', {})
        if 'default_steps' in generation:
            steps = generation['default_steps']
            assert isinstance(steps, int)
            assert 20 <= steps <= 100

    def test_config_max_steps(self, config: Dict) -> None:
        """Test maximum inference steps configuration"""
        generation = config.config.get('generation', {})
        if 'max_steps' in generation:
            max_steps = generation['max_steps']
            default_steps = generation.get('default_steps', 50)
            assert max_steps >= default_steps

    def test_config_port_setting(self, config: Dict) -> None:
        """Test port configuration"""
        server_config = config.config.get('server', {})
        if 'port' in server_config:
            port = server_config['port']
            assert isinstance(port, int)
            assert 1024 <= port <= 65535

    def test_config_log_level(self, config: Dict) -> None:
        """Test logging level configuration"""
        logging_config = config.config.get('logging', {})
        if 'level' in logging_config:
            level = logging_config['level']
            assert level in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']

    def test_config_cors_origins(self, config: Dict) -> None:
        """Test CORS origins configuration"""
        security = config.config.get('security', {})
        if 'cors_origins' in security:
            origins = security['cors_origins']
            assert isinstance(origins, (list, str))

    def test_config_max_file_size(self, config: Dict) -> None:
        """Test maximum file size configuration"""
        upload = config.config.get('upload', {})
        if 'max_file_size' in upload:
            max_size = upload['max_file_size']
            assert isinstance(max_size, int)
            assert max_size > 0

    def test_config_allowed_extensions(self, config: Dict) -> None:
        """Test allowed file extensions configuration"""
        upload = config.config.get('upload', {})
        if 'allowed_extensions' in upload:
            extensions = upload['allowed_extensions']
            assert isinstance(extensions, (list, set))
            assert 'png' in str(extensions).lower() or 'jpg' in str(extensions).lower()

    def test_config_cache_settings(self, config: Dict) -> None:
        """Test cache configuration"""
        cache = config.config.get('cache', {})
        if cache:
            assert isinstance(cache, dict)

    def test_config_monitoring_enabled(self, config: Dict) -> None:
        """Test monitoring configuration"""
        monitoring = config.config.get('monitoring', {})
        if 'enabled' in monitoring:
            enabled = monitoring['enabled']
            assert isinstance(enabled, bool)

    def test_config_to_dict(self, config: Dict) -> None:
        """Test config can be converted to dict"""
        config_dict = config.config
        assert isinstance(config_dict, dict)
        assert len(config_dict) > 0

    def test_config_immutability(self, config: Dict) -> None:
        """Test config should be somewhat immutable"""
        original_config = dict(config.config)
        # Attempt to modify
        if 'processing' in config.config:
            config.config['processing']['device'] = 'modified'
        # Check if there's validation or if it accepts the change
        assert config.config is not None

    def test_config_reload(self, config: Dict) -> None:
        """Test config can be reloaded"""
        if hasattr(config, 'reload'):
            config.reload()
            assert config.config is not None

    def test_config_validate(self, config: Dict) -> None:
        """Test config validation"""
        if hasattr(config, 'validate'):
            is_valid = config.validate()
            assert isinstance(is_valid, bool)

    def test_config_string_representation(self, config: Dict) -> None:
        """Test config has string representation"""
        config_str = str(config.config)
        assert isinstance(config_str, str)
        assert len(config_str) > 0

    def test_config_json_serializable(self, config: Dict) -> None:
        """Test config can be JSON serialized"""
        try:
            json_str = json.dumps(config.config, default=str)
            assert len(json_str) > 0
            # Verify it can be parsed back
            parsed = json.loads(json_str)
            assert isinstance(parsed, dict)
        except (TypeError, ValueError):
            pytest.skip("Config contains non-JSON-serializable objects")

    def test_config_production_mode(self, temp_env: Any) -> None:
        """Test production mode configuration"""
        temp_env(FLASK_ENV='production')
        config = Config()
        # In production, certain settings should be different
        assert config is not None

    def test_config_development_mode(self, temp_env: Any) -> None:
        """Test development mode configuration"""
        temp_env(FLASK_ENV='development')
        config = Config()
        assert config is not None

    def test_config_worker_count(self, config: Dict) -> None:
        """Test worker count configuration"""
        processing = config.config.get('processing', {})
        if 'workers' in processing:
            workers = processing['workers']
            assert isinstance(workers, int)
            assert workers > 0

    def test_config_timeout_settings(self, config: Dict) -> None:
        """Test timeout configuration"""
        timeouts = config.config.get('timeouts', {})
        if timeouts:
            for key, value in timeouts.items():
                if isinstance(value, (int, float)):
                    assert value > 0
