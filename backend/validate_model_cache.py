#!/usr/bin/env python3
"""
ORFEAS Model Cache Validation
Verifies that the cache configuration is correct and models can be found
"""

import os
import sys
from pathlib import Path
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s'
)
logger = logging.getLogger(__name__)

def check_environment_variables():
    """Verify environment variables are set correctly"""

    logger.info("")
    logger.info("=" * 80)
    logger.info("[CHECK] Environment Variables")
    logger.info("=" * 80)

    required_vars = {
        'HF_HOME': 'HuggingFace cache root',
        'TRANSFORMERS_CACHE': 'Transformer models cache',
        'HY3DGEN_CACHE': 'Hunyuan3D models cache',
    }

    all_set = True

    for var_name, description in required_vars.items():
        value = os.environ.get(var_name)
        if value:
            logger.info(f"✅ {var_name:30s} = {value}")
            # Check for mixed path separators
            if '/' in value and '\\' in value:
                logger.warning(f"   ⚠️  WARNING: Mixed path separators detected!")
                all_set = False
        else:
            logger.warning(f"❌ {var_name:30s} = NOT SET")
            all_set = False

    return all_set


def check_cache_directories():
    """Verify cache directories exist"""

    logger.info("")
    logger.info("=" * 80)
    logger.info("[CHECK] Cache Directories")
    logger.info("=" * 80)

    hf_home = os.environ.get('HF_HOME')

    if not hf_home:
        logger.error("❌ HF_HOME not set, cannot check directories")
        return False

    base_cache = Path(hf_home)

    if not base_cache.exists():
        logger.error(f"❌ Cache directory does not exist: {base_cache}")
        return False

    logger.info(f"✅ Cache root exists: {base_cache}")

    required_dirs = [
        ('transformers', 'Transformer models'),
        ('datasets', 'Dataset files'),
        ('hy3dgen', 'Hunyuan3D models'),
    ]

    all_exist = True

    for dir_name, description in required_dirs:
        dir_path = base_cache / dir_name
        if dir_path.exists():
            logger.info(f"✅ {dir_name:20s} / {description}")
        else:
            logger.warning(f"⚠️  {dir_name:20s} / {description} (will be created on first use)")

    return all_exist


def check_huggingface_cache_validity():
    """Check if cache paths use consistent separators"""

    logger.info("")
    logger.info("=" * 80)
    logger.info("[CHECK] Path Separator Consistency")
    logger.info("=" * 80)

    hf_home = os.environ.get('HF_HOME', '')
    hy3dgen_cache = os.environ.get('HY3DGEN_CACHE', '')
    transformers_cache = os.environ.get('TRANSFORMERS_CACHE', '')

    paths_to_check = {
        'HF_HOME': hf_home,
        'HY3DGEN_CACHE': hy3dgen_cache,
        'TRANSFORMERS_CACHE': transformers_cache,
    }

    is_valid = True

    for var_name, path_str in paths_to_check.items():
        if not path_str:
            continue

        # Check for mixed separators
        has_forward = '/' in path_str
        has_back = '\\' in path_str

        if has_forward and has_back:
            logger.error(f"❌ {var_name}: Mixed separators detected!")
            logger.error(f"   Path: {path_str}")
            is_valid = False
        elif has_forward:
            logger.warning(f"⚠️  {var_name}: Uses forward slashes (Unix-style)")
            logger.warning(f"   Path: {path_str}")
            logger.info(f"   ℹ️  Windows prefers backslashes, but this may work")
        elif has_back:
            logger.info(f"✅ {var_name}: Uses backslashes (Windows-style)")
        else:
            logger.info(f"✅ {var_name}: No path separators (should be fine)")

    return is_valid


def check_model_files():
    """Check if model files exist in cache"""

    logger.info("")
    logger.info("=" * 80)
    logger.info("[CHECK] Model Files")
    logger.info("=" * 80)

    hy3dgen_cache = Path(os.environ.get('HY3DGEN_CACHE', ''))

    if not hy3dgen_cache.exists():
        logger.info("ℹ️  HY3DGEN_CACHE directory not yet created (will be populated on first model load)")
        return None  # Not an error, just not populated yet

    # Look for model files
    model_files = list(hy3dgen_cache.rglob('*.safetensors')) + \
                  list(hy3dgen_cache.rglob('*.bin')) + \
                  list(hy3dgen_cache.rglob('*.pt'))

    if model_files:
        logger.info(f"✅ Found {len(model_files)} model files in cache")
        for model_file in model_files[:5]:  # Show first 5
            size_mb = model_file.stat().st_size / (1024 * 1024)
            logger.info(f"   - {model_file.name:40s} ({size_mb:6.1f} MB)")
        if len(model_files) > 5:
            logger.info(f"   ... and {len(model_files) - 5} more files")
        return True
    else:
        logger.info("ℹ️  No model files found in cache yet (models will download on first use)")
        return None


def check_dotenv_file():
    """Check if .env file contains cache settings"""

    logger.info("")
    logger.info("=" * 80)
    logger.info("[CHECK] .env File Configuration")
    logger.info("=" * 80)

    base_dir = Path(__file__).parent.parent
    env_file = base_dir / ".env"

    if not env_file.exists():
        logger.warning(f"⚠️  .env file not found: {env_file}")
        return False

    logger.info(f"✅ .env file found: {env_file}")

    # Read and check for cache variables
    with open(env_file, 'r') as f:
        content = f.read()

    cache_vars = ['HF_HOME', 'TRANSFORMERS_CACHE', 'HY3DGEN_CACHE']
    found_vars = []

    for var in cache_vars:
        if f'{var}=' in content:
            found_vars.append(var)

    if found_vars:
        logger.info(f"✅ Found {len(found_vars)} cache variables in .env:")
        for var in found_vars:
            logger.info(f"   - {var}")
        return True
    else:
        logger.warning("⚠️  No cache variables found in .env file")
        return False


def print_validation_summary(results):
    """Print summary of all checks"""

    logger.info("")
    logger.info("=" * 80)
    logger.info("[SUMMARY] Validation Results")
    logger.info("=" * 80)
    logger.info("")

    all_passed = all(results.values())

    for check_name, passed in results.items():
        status = "✅ PASS" if passed else "⚠️  NEEDS ATTENTION" if passed is None else "❌ FAIL"
        logger.info(f"{status:20s} {check_name}")

    logger.info("")

    if all_passed:
        logger.info("✅ All validations passed! Model cache is properly configured.")
        logger.info("")
        logger.info("Next steps:")
        logger.info("1. Start the backend: python main.py")
        logger.info("2. Models will load from the configured cache")
        logger.info("3. Check logs for: '[SUCCESS] Hunyuan3D model FULLY LOADED'")
    else:
        logger.info("⚠️  Some validations need attention. See details above.")
        logger.info("")
        logger.info("Recommended:")
        logger.info("1. Run setup: python setup_model_cache.py")
        logger.info("2. Check the output for any errors")
        logger.info("3. Run this validation again: python validate_model_cache.py")

    logger.info("")


def main():
    """Run all validation checks"""

    logger.info("")
    logger.info("╔" + "=" * 78 + "╗")
    logger.info("║" + " " * 78 + "║")
    logger.info("║" + "[VALIDATE] ORFEAS Model Cache Configuration".center(78) + "║")
    logger.info("║" + " " * 78 + "║")
    logger.info("╚" + "=" * 78 + "╝")

    results = {
        'Environment Variables': check_environment_variables(),
        'Cache Directories': check_cache_directories(),
        'Path Consistency': check_huggingface_cache_validity(),
        '.env Configuration': check_dotenv_file(),
    }

    # Model files check can return None (not yet populated)
    model_check = check_model_files()
    if model_check is not None:
        results['Model Files'] = model_check

    print_validation_summary(results)

    # Return success if all non-None values are True
    critical_checks = {k: v for k, v in results.items() if v is not None}
    return all(critical_checks.values()) if critical_checks else True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"[ERROR] Validation failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
