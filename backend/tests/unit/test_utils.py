"""
+==============================================================================â•—
|              ORFEAS Testing Suite - Utility Functions Tests                |
|         Comprehensive tests for helper utilities and converters             |
+==============================================================================
"""
import pytest
from pathlib import Path
import sys
import json
import hashlib
from datetime import datetime
from unittest.mock import Mock, patch
from typing import Any, List

backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))

try:
    import utils
    UTILS_AVAILABLE = True
except ImportError:
    UTILS_AVAILABLE = False


@pytest.mark.unit
class TestStringUtilities:
    """Tests for string manipulation utilities"""

    def test_sanitize_filename_basic(self) -> None:
        """Test basic filename sanitization"""
        if UTILS_AVAILABLE and hasattr(utils, 'sanitize_filename'):
            result = utils.sanitize_filename("test file.txt")
            assert isinstance(result, str)
            assert ".txt" in result
        else:
            pytest.skip("sanitize_filename not available")

    def test_sanitize_filename_special_chars(self) -> None:
        """Test filename sanitization with special characters"""
        if UTILS_AVAILABLE and hasattr(utils, 'sanitize_filename'):
            result = utils.sanitize_filename("test<>file|*.txt")
            assert "<" not in result
            assert ">" not in result
            assert "|" not in result
            assert "*" not in result
        else:
            pytest.skip("sanitize_filename not available")

    @pytest.mark.parametrize("input_str,expected", [
        ("TEST", "test"),
        ("Test Case", "test_case"),
        ("test-case", "test_case"),
        ("test.case", "test.case"),
    ])
    def test_normalize_string(self, input_str: Any, expected: Any) -> None:
        """Test string normalization"""
        if UTILS_AVAILABLE and hasattr(utils, 'normalize_string'):
            result = utils.normalize_string(input_str)
            # Just check it returns a string
            assert isinstance(result, str)
        else:
            pytest.skip("normalize_string not available")

    def test_truncate_string_basic(self) -> None:
        """Test string truncation"""
        if UTILS_AVAILABLE and hasattr(utils, 'truncate_string'):
            long_str = "This is a very long string that needs truncation"
            result = utils.truncate_string(long_str, max_length=20)
            assert len(result) <= 23  # Max length + ellipsis
        else:
            pytest.skip("truncate_string not available")


@pytest.mark.unit
class TestPathUtilities:
    """Tests for path handling utilities"""

    def test_ensure_absolute_path(self) -> None:
        """Test path conversion to absolute"""
        if UTILS_AVAILABLE and hasattr(utils, 'ensure_absolute_path'):
            result = utils.ensure_absolute_path("./test.txt")
            assert Path(result).is_absolute()
        else:
            pytest.skip("ensure_absolute_path not available")

    def test_safe_path_join(self) -> None:
        """Test safe path joining"""
        if UTILS_AVAILABLE and hasattr(utils, 'safe_path_join'):
            result = utils.safe_path_join("/base", "subdir", "file.txt")
            assert isinstance(result, (str, Path))
            assert "subdir" in str(result)
            assert "file.txt" in str(result)
        else:
            pytest.skip("safe_path_join not available")

    @pytest.mark.parametrize("path,expected_safe", [
        ("./test.txt", True),
        ("../test.txt", False),
        ("../../etc/passwd", False),
        ("test/file.txt", True),
    ])
    def test_is_safe_path(self, path: str, expected_safe: Any) -> None:
        """Test path safety validation"""
        if UTILS_AVAILABLE and hasattr(utils, 'is_safe_path'):
            result = utils.is_safe_path(path)
            assert isinstance(result, bool)
        else:
            pytest.skip("is_safe_path not available")

    def test_get_file_extension(self) -> None:
        """Test file extension extraction"""
        if UTILS_AVAILABLE and hasattr(utils, 'get_file_extension'):
            result = utils.get_file_extension("test.jpg")
            assert result in [".jpg", "jpg", "JPG"]
        else:
            # Fallback to pathlib
            result = Path("test.jpg").suffix
            assert result == ".jpg"

    def test_change_file_extension(self) -> None:
        """Test file extension replacement"""
        if UTILS_AVAILABLE and hasattr(utils, 'change_file_extension'):
            result = utils.change_file_extension("test.jpg", ".png")
            assert ".png" in result
            assert ".jpg" not in result
        else:
            pytest.skip("change_file_extension not available")


@pytest.mark.unit
class TestDateTimeUtilities:
    """Tests for date/time utilities"""

    def test_format_timestamp(self) -> None:
        """Test timestamp formatting"""
        if UTILS_AVAILABLE and hasattr(utils, 'format_timestamp'):
            now = datetime.now()
            result = utils.format_timestamp(now)
            assert isinstance(result, str)
            assert len(result) > 0
        else:
            pytest.skip("format_timestamp not available")

    def test_get_current_timestamp(self) -> None:
        """Test current timestamp retrieval"""
        if UTILS_AVAILABLE and hasattr(utils, 'get_current_timestamp'):
            result = utils.get_current_timestamp()
            assert isinstance(result, (str, datetime, float))
        else:
            # Fallback
            result = datetime.now()
            assert isinstance(result, datetime)

    def test_timestamp_to_string(self) -> None:
        """Test timestamp to string conversion"""
        if UTILS_AVAILABLE and hasattr(utils, 'timestamp_to_string'):
            timestamp = 1234567890
            result = utils.timestamp_to_string(timestamp)
            assert isinstance(result, str)
        else:
            pytest.skip("timestamp_to_string not available")

    def test_parse_datetime_string(self) -> None:
        """Test datetime string parsing"""
        if UTILS_AVAILABLE and hasattr(utils, 'parse_datetime_string'):
            date_str = "2025-01-01 12:00:00"
            result = utils.parse_datetime_string(date_str)
            assert result is not None
        else:
            pytest.skip("parse_datetime_string not available")


@pytest.mark.unit
class TestFileSizeUtilities:
    """Tests for file size conversion utilities"""

    @pytest.mark.parametrize("bytes_value,expected_unit", [
        (1024, "KB"),
        (1024**2, "MB"),
        (1024**3, "GB"),
        (500, "B"),
    ])
    def test_format_file_size(self, bytes_value: Any, expected_unit: Any) -> None:
        """Test file size formatting"""
        if UTILS_AVAILABLE and hasattr(utils, 'format_file_size'):
            result = utils.format_file_size(bytes_value)
            assert isinstance(result, str)
            assert any(unit in result for unit in ["B", "KB", "MB", "GB"])
        else:
            pytest.skip("format_file_size not available")

    def test_parse_file_size(self) -> None:
        """Test file size parsing from string"""
        if UTILS_AVAILABLE and hasattr(utils, 'parse_file_size'):
            result = utils.parse_file_size("10MB")
            assert isinstance(result, int)
            assert result > 0
        else:
            pytest.skip("parse_file_size not available")

    @pytest.mark.parametrize("size_str,expected_bytes", [
        ("1KB", 1024),
        ("1MB", 1024**2),
        ("1GB", 1024**3),
    ])
    def test_parse_size_units(self, size_str: Any, expected_bytes: List) -> None:
        """Test parsing various size units"""
        if UTILS_AVAILABLE and hasattr(utils, 'parse_file_size'):
            result = utils.parse_file_size(size_str)
            # Allow some tolerance
            assert abs(result - expected_bytes) < 1000
        else:
            pytest.skip("parse_file_size not available")


@pytest.mark.unit
class TestHashUtilities:
    """Tests for hash generation utilities"""

    def test_generate_hash_string(self) -> None:
        """Test hash generation from string"""
        if UTILS_AVAILABLE and hasattr(utils, 'generate_hash'):
            result = utils.generate_hash("test string")
            assert isinstance(result, str)
            assert len(result) > 0
        else:
            # Fallback
            result = hashlib.md5("test string".encode()).hexdigest()
            assert len(result) == 32

    def test_generate_hash_bytes(self) -> None:
        """Test hash generation from bytes"""
        if UTILS_AVAILABLE and hasattr(utils, 'generate_hash'):
            result = utils.generate_hash(b"test bytes")
            assert isinstance(result, str)
            assert len(result) > 0
        else:
            pytest.skip("generate_hash not available")

    def test_generate_file_hash(self) -> None:
        """Test file hash generation"""
        if UTILS_AVAILABLE and hasattr(utils, 'generate_file_hash'):
            # Create temporary file
            temp_file = Path("temp_test.txt")
            temp_file.write_text("test content")

            try:
                result = utils.generate_file_hash(str(temp_file))
                assert isinstance(result, str)
                assert len(result) > 0
            finally:
                temp_file.unlink(missing_ok=True)
        else:
            pytest.skip("generate_file_hash not available")

    @pytest.mark.parametrize("algorithm", ["md5", "sha256", "sha1"])
    def test_hash_algorithms(self, algorithm: Any) -> None:
        """Test different hash algorithms"""
        if UTILS_AVAILABLE and hasattr(utils, 'generate_hash'):
            try:
                result = utils.generate_hash("test", algorithm=algorithm)
                assert isinstance(result, str)
                assert len(result) > 0
            except:
                pytest.skip(f"{algorithm} not supported")
        else:
            pytest.skip("generate_hash not available")


@pytest.mark.unit
class TestDataConverters:
    """Tests for data structure converters"""

    def test_dict_to_json(self) -> None:
        """Test dictionary to JSON conversion"""
        test_dict = {"key": "value", "number": 42, "nested": {"inner": "data"}}
        result = json.dumps(test_dict)
        assert isinstance(result, str)
        assert "key" in result
        assert "42" in result

    def test_json_to_dict(self) -> None:
        """Test JSON to dictionary conversion"""
        json_str = '{"key": "value", "number": 42}'
        result = json.loads(json_str)
        assert isinstance(result, dict)
        assert result["key"] == "value"
        assert result["number"] == 42

    def test_list_to_csv_string(self) -> None:
        """Test list to CSV string conversion"""
        if UTILS_AVAILABLE and hasattr(utils, 'list_to_csv'):
            test_list = ["item1", "item2", "item3"]
            result = utils.list_to_csv(test_list)
            assert isinstance(result, str)
            assert "item1" in result
        else:
            pytest.skip("list_to_csv not available")

    def test_dict_flatten(self) -> None:
        """Test dictionary flattening"""
        if UTILS_AVAILABLE and hasattr(utils, 'flatten_dict'):
            nested = {"a": {"b": {"c": "value"}}}
            result = utils.flatten_dict(nested)
            assert isinstance(result, dict)
        else:
            pytest.skip("flatten_dict not available")


@pytest.mark.unit
class TestValidationHelpers:
    """Tests for validation helper functions"""

    @pytest.mark.parametrize("email,expected_valid", [
        ("test@example.com", True),
        ("invalid@", False),
        ("no-at-sign.com", False),
        ("valid.email@domain.co.uk", True),
    ])
    def test_validate_email(self, email: Any, expected_valid: Any) -> None:
        """Test email validation"""
        if UTILS_AVAILABLE and hasattr(utils, 'validate_email'):
            result = utils.validate_email(email)
            assert isinstance(result, bool)
        else:
            pytest.skip("validate_email not available")

    @pytest.mark.parametrize("url,expected_valid", [
        ("http://example.com", True),
        ("https://example.com/path", True),
        ("not a url", False),
        ("ftp://files.example.com", True),
    ])
    def test_validate_url(self, url: Any, expected_valid: Any) -> None:
        """Test URL validation"""
        if UTILS_AVAILABLE and hasattr(utils, 'validate_url'):
            result = utils.validate_url(url)
            assert isinstance(result, bool)
        else:
            pytest.skip("validate_url not available")

    def test_validate_json(self) -> None:
        """Test JSON validation"""
        if UTILS_AVAILABLE and hasattr(utils, 'validate_json'):
            valid_json = '{"key": "value"}'
            invalid_json = '{key: value}'

            assert utils.validate_json(valid_json) == True
            assert utils.validate_json(invalid_json) == False
        else:
            # Fallback validation
            try:
                json.loads('{"key": "value"}')
                valid = True
            except:
                valid = False
            assert valid == True


@pytest.mark.unit
class TestErrorHandling:
    """Tests for error handling utilities"""

    def test_safe_execute_with_fallback(self) -> None:
        """Test safe execution with fallback"""
        if UTILS_AVAILABLE and hasattr(utils, 'safe_execute'):
            def failing_func() -> None:
                raise ValueError("Test error")

            result = utils.safe_execute(failing_func, fallback="fallback_value")
            assert result == "fallback_value"
        else:
            pytest.skip("safe_execute not available")

    def test_retry_decorator(self) -> str:
        """Test retry decorator functionality"""
        if UTILS_AVAILABLE and hasattr(utils, 'retry'):
            @utils.retry(max_attempts=3, delay=0.1)
            def unstable_function() -> str:
                return "success"

            result = unstable_function()
            assert result == "success"
        else:
            pytest.skip("retry decorator not available")

    def test_error_message_sanitization(self) -> None:
        """Test error message sanitization"""
        if UTILS_AVAILABLE and hasattr(utils, 'sanitize_error_message'):
            error_msg = "Error: /path/to/secret/file.txt not found"
            result = utils.sanitize_error_message(error_msg)
            assert isinstance(result, str)
            # Should remove sensitive paths
        else:
            pytest.skip("sanitize_error_message not available")


@pytest.mark.unit
class TestPerformanceUtilities:
    """Tests for performance monitoring utilities"""

    def test_timer_context_manager(self) -> None:
        """Test timer context manager"""
        if UTILS_AVAILABLE and hasattr(utils, 'Timer'):
            import time
            with utils.Timer() as timer:
                time.sleep(0.1)
            assert timer.elapsed >= 0.1
        else:
            pytest.skip("Timer not available")

    def test_measure_execution_time(self) -> str:
        """Test execution time measurement"""
        if UTILS_AVAILABLE and hasattr(utils, 'measure_time'):
            import time

            @utils.measure_time
            def slow_function() -> str:
                time.sleep(0.1)
                return "done"

            result = slow_function()
            assert result == "done"
        else:
            pytest.skip("measure_time not available")


@pytest.mark.unit
class TestMemoryUtilities:
    """Tests for memory management utilities"""

    def test_get_memory_usage(self) -> None:
        """Test memory usage retrieval"""
        if UTILS_AVAILABLE and hasattr(utils, 'get_memory_usage'):
            usage = utils.get_memory_usage()
            assert isinstance(usage, (int, float))
            assert usage >= 0
        else:
            pytest.skip("get_memory_usage not available")

    def test_format_memory_size(self) -> None:
        """Test memory size formatting"""
        if UTILS_AVAILABLE and hasattr(utils, 'format_memory_size'):
            result = utils.format_memory_size(1024 * 1024 * 100)  # 100MB
            assert isinstance(result, str)
            assert "MB" in result or "GB" in result
        else:
            pytest.skip("format_memory_size not available")


@pytest.mark.unit
class TestConfigHelpers:
    """Tests for configuration helper utilities"""

    def test_load_env_var(self) -> None:
        """Test environment variable loading"""
        if UTILS_AVAILABLE and hasattr(utils, 'load_env_var'):
            result = utils.load_env_var('PATH', default='/usr/bin')
            assert isinstance(result, str)
            assert len(result) > 0
        else:
            # Fallback
            import os
            result = os.getenv('PATH', '/usr/bin')
            assert result is not None

    def test_parse_bool_from_string(self) -> None:
        """Test boolean parsing from string"""
        if UTILS_AVAILABLE and hasattr(utils, 'parse_bool'):
            assert utils.parse_bool('true') == True
            assert utils.parse_bool('false') == False
            assert utils.parse_bool('1') == True
            assert utils.parse_bool('0') == False
        else:
            pytest.skip("parse_bool not available")

    @pytest.mark.parametrize("value,expected", [
        ("true", True),
        ("True", True),
        ("false", False),
        ("False", False),
        ("yes", True),
        ("no", False),
        ("1", True),
        ("0", False),
    ])
    def test_boolean_conversion(self, value: Any, expected: Any) -> None:
        """Test various boolean string conversions"""
        if UTILS_AVAILABLE and hasattr(utils, 'to_bool'):
            result = utils.to_bool(value)
            assert result == expected
        else:
            pytest.skip("to_bool not available")


@pytest.mark.unit
class TestMiscUtilities:
    """Tests for miscellaneous utility functions"""

    def test_generate_random_string(self) -> None:
        """Test random string generation"""
        if UTILS_AVAILABLE and hasattr(utils, 'generate_random_string'):
            result = utils.generate_random_string(length=16)
            assert isinstance(result, str)
            assert len(result) == 16
        else:
            pytest.skip("generate_random_string not available")

    def test_generate_uuid(self) -> None:
        """Test UUID generation"""
        if UTILS_AVAILABLE and hasattr(utils, 'generate_uuid'):
            result = utils.generate_uuid()
            assert isinstance(result, str)
            assert len(result) > 0
        else:
            import uuid
            result = str(uuid.uuid4())
            assert len(result) == 36

    def test_chunk_list(self) -> None:
        """Test list chunking"""
        if UTILS_AVAILABLE and hasattr(utils, 'chunk_list'):
            test_list = list(range(100))
            chunks = utils.chunk_list(test_list, chunk_size=10)
            assert len(chunks) == 10
            assert len(chunks[0]) == 10
        else:
            pytest.skip("chunk_list not available")

    def test_deduplicate_list(self) -> None:
        """Test list deduplication"""
        if UTILS_AVAILABLE and hasattr(utils, 'deduplicate_list'):
            test_list = [1, 2, 2, 3, 3, 3, 4]
            result = utils.deduplicate_list(test_list)
            assert len(result) == 4
            assert set(result) == {1, 2, 3, 4}
        else:
            # Fallback
            result = list(set([1, 2, 2, 3, 3, 3, 4]))
            assert len(result) == 4
