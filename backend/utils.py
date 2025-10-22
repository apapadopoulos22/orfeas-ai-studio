"""
+==============================================================================â•—
|            ORFEAS AI 2D→3D Studio - Utility Functions Module                |
|              Comprehensive helper utilities and converters                   |
|                        ORFEAS AI                        |
+==============================================================================

Features:
- String manipulation (sanitization, normalization, truncation)
- Path handling (absolute paths, safe joining, security validation)
- DateTime utilities (formatting, parsing, timestamps)
- File size conversion (bytes to human-readable and vice versa)
- Hash generation (MD5, SHA256, SHA1 for strings and files)
- Data converters (JSON, CSV, flattening)
- Validation helpers (email, URL, JSON validation)
- Error handling (safe execution, retry decorator)
- Performance utilities (Timer, execution measurement)
- Memory utilities (usage tracking, formatting)
- Config helpers (environment variables, boolean parsing)
- Miscellaneous utilities (UUID, random strings, list operations)
"""

import os
import re
import json
import hashlib
import uuid
import time
import psutil
import logging
from pathlib import Path
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Union
from functools import wraps

logger = logging.getLogger(__name__)


# =============================================================================
# STRING UTILITIES
# =============================================================================

def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename by removing/replacing invalid characters

    Args:
        filename: Original filename

    Returns:
        Sanitized filename safe for file system
    """
    # Remove invalid characters for Windows/Unix filesystems
    invalid_chars = r'[<>:"|?*\\/]'
    sanitized = re.sub(invalid_chars, '_', filename)

    # Remove control characters
    sanitized = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', sanitized)

    # Limit length
    name, ext = os.path.splitext(sanitized)
    if len(name) > 200:
        name = name[:200]

    return name + ext


def normalize_string(s: str) -> str:
    """
    Normalize string to lowercase with underscores

    Args:
        s: Input string

    Returns:
        Normalized string
    """
    # Convert to lowercase
    normalized = s.lower()

    # Replace spaces and hyphens with underscores
    normalized = re.sub(r'[\s-]+', '_', normalized)

    # Remove multiple consecutive underscores
    normalized = re.sub(r'_+', '_', normalized)

    # Strip leading/trailing underscores
    normalized = normalized.strip('_')

    return normalized


def truncate_string(s: str, max_length: int = 50, suffix: str = "...") -> str:
    """
    Truncate string to maximum length with optional suffix

    Args:
        s: Input string
        max_length: Maximum length
        suffix: Suffix to append (default: "...")

    Returns:
        Truncated string
    """
    if len(s) <= max_length:
        return s

    return s[:max_length] + suffix


# =============================================================================
# PATH UTILITIES
# =============================================================================

def ensure_absolute_path(path: Union[str, Path]) -> str:
    """
    Convert path to absolute path

    Args:
        path: Input path (relative or absolute)

    Returns:
        Absolute path as string
    """
    return str(Path(path).resolve())


def safe_path_join(*parts: str) -> str:
    """
    Safely join path components

    Args:
        *parts: Path components to join

    Returns:
        Joined path
    """
    return str(Path(*parts))


def is_safe_path(path: str, base_dir: Optional[str] = None) -> bool:
    """
    Check if path is safe (no directory traversal)

    Args:
        path: Path to validate
        base_dir: Base directory to check against

    Returns:
        True if path is safe, False otherwise
    """
    # Check for directory traversal patterns
    if '..' in path or path.startswith('/'):
        return False

    # If base_dir provided, ensure path stays within it
    if base_dir:
        try:
            full_path = Path(base_dir) / path
            full_path.resolve().relative_to(Path(base_dir).resolve())
        except ValueError:
            return False

    return True


def get_file_extension(filename: str) -> str:
    """
    Get file extension from filename

    Args:
        filename: File name or path

    Returns:
        File extension (including dot)
    """
    return Path(filename).suffix


def change_file_extension(filename: str, new_extension: str) -> str:
    """
    Change file extension

    Args:
        filename: Original filename
        new_extension: New extension (with or without dot)

    Returns:
        Filename with new extension
    """
    if not new_extension.startswith('.'):
        new_extension = '.' + new_extension

    path = Path(filename)
    return str(path.with_suffix(new_extension))


# =============================================================================
# DATETIME UTILITIES
# =============================================================================

def format_timestamp(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Format datetime object to string

    Args:
        dt: Datetime object
        format_str: Format string (default: ISO-like)

    Returns:
        Formatted datetime string
    """
    return dt.strftime(format_str)


def get_current_timestamp() -> str:
    """
    Get current timestamp as formatted string

    Returns:
        Current timestamp string
    """
    return format_timestamp(datetime.now())


def timestamp_to_string(timestamp: float, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Convert Unix timestamp to string

    Args:
        timestamp: Unix timestamp (seconds since epoch)
        format_str: Format string

    Returns:
        Formatted datetime string
    """
    dt = datetime.fromtimestamp(timestamp)
    return dt.strftime(format_str)


def parse_datetime_string(date_str: str, format_str: Optional[str] = None) -> Optional[datetime]:
    """
    Parse datetime string to datetime object

    Args:
        date_str: Datetime string
        format_str: Format string (if None, tries common formats)

    Returns:
        Datetime object or None if parsing fails
    """
    if format_str:
        try:
            return datetime.strptime(date_str, format_str)
        except ValueError:
            return None

    # Try common formats
    common_formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
        "%Y/%m/%d %H:%M:%S",
        "%Y/%m/%d",
        "%d-%m-%Y %H:%M:%S",
        "%d-%m-%Y",
    ]

    for fmt in common_formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue

    return None


# =============================================================================
# FILE SIZE UTILITIES
# =============================================================================

def format_file_size(bytes_value: int) -> str:
    """
    Format bytes to human-readable size

    Args:
        bytes_value: Size in bytes

    Returns:
        Human-readable size string (e.g., "1.5 MB")
    """
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    size = float(bytes_value)
    unit_index = 0

    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1

    return f"{size:.2f} {units[unit_index]}"


def parse_file_size(size_str: str) -> int:
    """
    Parse human-readable size to bytes

    Args:
        size_str: Size string (e.g., "10MB", "1.5GB")

    Returns:
        Size in bytes
    """
    size_str = size_str.strip().upper()

    # Extract number and unit
    match = re.match(r'([\d.]+)\s*([KMGT]?B?)', size_str)
    if not match:
        raise ValueError(f"Invalid size format: {size_str}")

    number = float(match.group(1))
    unit = match.group(2)

    # Convert to bytes
    multipliers = {
        'B': 1,
        'KB': 1024,
        'K': 1024,
        'MB': 1024**2,
        'M': 1024**2,
        'GB': 1024**3,
        'G': 1024**3,
        'TB': 1024**4,
        'T': 1024**4,
    }

    multiplier = multipliers.get(unit, 1)
    return int(number * multiplier)


# =============================================================================
# HASH UTILITIES
# =============================================================================

def generate_hash(data: Union[str, bytes], algorithm: str = "md5") -> str:
    """
    Generate hash from string or bytes

    Args:
        data: Input data (string or bytes)
        algorithm: Hash algorithm (md5, sha256, sha1)

    Returns:
        Hexadecimal hash string
    """
    if isinstance(data, str):
        data = data.encode('utf-8')

    if algorithm == "md5":
        hasher = hashlib.md5(data)
    elif algorithm == "sha256":
        hasher = hashlib.sha256(data)
    elif algorithm == "sha1":
        hasher = hashlib.sha1(data)
    else:
        raise ValueError(f"Unsupported algorithm: {algorithm}")

    return hasher.hexdigest()


def generate_file_hash(file_path: str, algorithm: str = "md5") -> str:
    """
    Generate hash of file contents

    Args:
        file_path: Path to file
        algorithm: Hash algorithm (md5, sha256, sha1)

    Returns:
        Hexadecimal hash string
    """
    if algorithm == "md5":
        hasher = hashlib.md5()
    elif algorithm == "sha256":
        hasher = hashlib.sha256()
    elif algorithm == "sha1":
        hasher = hashlib.sha1()
    else:
        raise ValueError(f"Unsupported algorithm: {algorithm}")

    with open(file_path, 'rb') as f:
        while chunk := f.read(8192):
            hasher.update(chunk)

    return hasher.hexdigest()


# =============================================================================
# DATA CONVERTERS
# =============================================================================

def list_to_csv(items: List[Any], separator: str = ",") -> str:
    """
    Convert list to CSV string

    Args:
        items: List of items
        separator: Separator character

    Returns:
        CSV string
    """
    return separator.join(str(item) for item in items)


def flatten_dict(d: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
    """
    Flatten nested dictionary

    Args:
        d: Input dictionary
        parent_key: Parent key prefix
        sep: Separator for keys

    Returns:
        Flattened dictionary
    """
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


# =============================================================================
# VALIDATION HELPERS
# =============================================================================

def validate_email(email: str) -> bool:
    """
    Validate email address format

    Args:
        email: Email address

    Returns:
        True if valid, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_url(url: str) -> bool:
    """
    Validate URL format

    Args:
        url: URL string

    Returns:
        True if valid, False otherwise
    """
    pattern = r'^(https?|ftp)://[^\s/$.?#].[^\s]*$'
    return bool(re.match(pattern, url, re.IGNORECASE))


def validate_json(json_str: str) -> bool:
    """
    Validate JSON string

    Args:
        json_str: JSON string

    Returns:
        True if valid JSON, False otherwise
    """
    try:
        json.loads(json_str)
        return True
    except (json.JSONDecodeError, TypeError):
        return False


# =============================================================================
# ERROR HANDLING
# =============================================================================

def safe_execute(func: Callable, fallback: Any = None, *args, **kwargs) -> Any:
    """
    Execute function with fallback on error

    Args:
        func: Function to execute
        fallback: Value to return on error
        *args: Function arguments
        **kwargs: Function keyword arguments

    Returns:
        Function result or fallback value
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        logger.warning(f"[ORFEAS] safe_execute failed: {e}")
        return fallback


def retry(max_attempts: int = 3, delay: float = 1.0, exceptions: tuple = (Exception,)):
    """
    Retry decorator for unstable functions

    Args:
        max_attempts: Maximum retry attempts
        delay: Delay between retries (seconds)
        exceptions: Tuple of exceptions to catch

    Returns:
        Decorated function
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        logger.warning(f"[ORFEAS] Retry {attempt + 1}/{max_attempts} for {func.__name__}: {e}")
                        time.sleep(delay)

            # All retries failed
            logger.error(f"[ORFEAS] All {max_attempts} retries failed for {func.__name__}")
            raise last_exception

        return wrapper
    return decorator


def sanitize_error_message(error_msg: str) -> str:
    """
    Sanitize error message to remove sensitive information

    Args:
        error_msg: Original error message

    Returns:
        Sanitized error message
    """
    # Remove file paths
    sanitized = re.sub(r'[A-Za-z]:\\[^:\s]*', '[PATH]', error_msg)
    sanitized = re.sub(r'/[^\s:]*/', '[PATH]/', sanitized)

    # Remove potential API keys/tokens
    sanitized = re.sub(r'[A-Za-z0-9]{32,}', '[KEY]', sanitized)

    return sanitized


# =============================================================================
# PERFORMANCE UTILITIES
# =============================================================================

class Timer:
    """Context manager for timing code execution"""

    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.elapsed = 0

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, *args):
        self.end_time = time.time()
        self.elapsed = self.end_time - self.start_time


def measure_time(func: Callable) -> Callable:
    """
    Decorator to measure function execution time

    Args:
        func: Function to measure

    Returns:
        Decorated function
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start_time
        logger.info(f"[ORFEAS] {func.__name__} executed in {elapsed:.3f}s")
        return result

    return wrapper


# =============================================================================
# MEMORY UTILITIES
# =============================================================================

def get_memory_usage() -> int:
    """
    Get current process memory usage in bytes

    Returns:
        Memory usage in bytes
    """
    process = psutil.Process(os.getpid())
    return process.memory_info().rss


def format_memory_size(bytes_value: int) -> str:
    """
    Format memory size to human-readable string

    Args:
        bytes_value: Memory size in bytes

    Returns:
        Human-readable memory size
    """
    return format_file_size(bytes_value)


# =============================================================================
# CONFIG HELPERS
# =============================================================================

def load_env_var(var_name: str, default: Any = None) -> str:
    """
    Load environment variable with default

    Args:
        var_name: Environment variable name
        default: Default value if not found

    Returns:
        Environment variable value or default
    """
    return os.getenv(var_name, default)


def parse_bool(value: Union[str, bool, int]) -> bool:
    """
    Parse boolean value from string

    Args:
        value: Value to parse (string, bool, or int)

    Returns:
        Boolean value
    """
    if isinstance(value, bool):
        return value

    if isinstance(value, int):
        return value != 0

    if isinstance(value, str):
        value = value.lower().strip()
        return value in ('true', 'yes', '1', 'on', 'enabled')

    return False


def to_bool(value: Union[str, bool, int]) -> bool:
    """
    Alias for parse_bool for compatibility
    """
    return parse_bool(value)


# =============================================================================
# MISCELLANEOUS UTILITIES
# =============================================================================

def generate_random_string(length: int = 16, charset: str = 'alphanumeric') -> str:
    """
    Generate random string

    Args:
        length: String length
        charset: Character set ('alphanumeric', 'alpha', 'numeric', 'hex')

    Returns:
        Random string
    """
    import random
    import string

    if charset == 'alphanumeric':
        chars = string.ascii_letters + string.digits
    elif charset == 'alpha':
        chars = string.ascii_letters
    elif charset == 'numeric':
        chars = string.digits
    elif charset == 'hex':
        chars = string.hexdigits.lower()
    else:
        chars = string.ascii_letters + string.digits

    return ''.join(random.choice(chars) for _ in range(length))


def generate_uuid() -> str:
    """
    Generate UUID string

    Returns:
        UUID string
    """
    return str(uuid.uuid4())


def chunk_list(items: List[Any], chunk_size: int) -> List[List[Any]]:
    """
    Split list into chunks

    Args:
        items: Input list
        chunk_size: Size of each chunk

    Returns:
        List of chunks
    """
    return [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]


def deduplicate_list(items: List[Any], preserve_order: bool = True) -> List[Any]:
    """
    Remove duplicates from list

    Args:
        items: Input list
        preserve_order: Preserve original order (default: True)

    Returns:
        List without duplicates
    """
    if preserve_order:
        seen = set()
        result = []
        for item in items:
            if item not in seen:
                seen.add(item)
                result.append(item)
        return result
    else:
        return list(set(items))


# =============================================================================
# MODULE INITIALIZATION
# =============================================================================

logger.info("[ORFEAS] Utils module loaded successfully")
