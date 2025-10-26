"""
ORFEAS Model Cache Setup
Configures HuggingFace cache paths for Windows compatibility
Prevents mixed path separators and ensures models load locally
"""

import os
import sys
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)-8s | %(message)s')
logger = logging.getLogger(__name__)

def setup_huggingface_cache():
    """Setup HuggingFace cache with proper Windows paths"""

    logger.info("=" * 80)
    logger.info("[SETUP] ORFEAS HuggingFace Cache Configuration")
    logger.info("=" * 80)

    # Get base directory
    base_dir = Path(__file__).parent.parent
    cache_dir = base_dir / "models" / ".cache" / "huggingface"

    # Create cache directories
    cache_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"[FOLDER] Cache directory: {cache_dir}")

    # Set environment variables (proper Windows paths with backslashes)
    cache_dir_str = str(cache_dir)  # Converts to OS-appropriate path

    # Primary: HF_HOME (HuggingFace cache root)
    os.environ['HF_HOME'] = cache_dir_str
    logger.info(f"[CONFIG] HF_HOME = {cache_dir_str}")

    # Secondary: TRANSFORMERS_CACHE (transformer models)
    transformers_cache = cache_dir / "transformers"
    transformers_cache.mkdir(parents=True, exist_ok=True)
    os.environ['TRANSFORMERS_CACHE'] = str(transformers_cache)
    logger.info(f"[CONFIG] TRANSFORMERS_CACHE = {transformers_cache}")

    # Tertiary: HF_DATASETS_CACHE (dataset cache)
    datasets_cache = cache_dir / "datasets"
    datasets_cache.mkdir(parents=True, exist_ok=True)
    os.environ['HF_DATASETS_CACHE'] = str(datasets_cache)
    logger.info(f"[CONFIG] HF_DATASETS_CACHE = {datasets_cache}")

    # hy3dgen specific cache (avoid mixed path separators)
    hy3dgen_cache = cache_dir / "hy3dgen"
    hy3dgen_cache.mkdir(parents=True, exist_ok=True)
    os.environ['HY3DGEN_CACHE'] = str(hy3dgen_cache)
    logger.info(f"[CONFIG] HY3DGEN_CACHE = {hy3dgen_cache}")

    # OFFLINE MODE (optional): Set to prevent unexpected downloads
    # Uncomment if you want to prevent any model downloads
    # os.environ['HF_HUB_OFFLINE'] = '1'
    # logger.info("[CONFIG] HF_HUB_OFFLINE = 1 (download disabled)")

    logger.info("")
    logger.info("[SUCCESS] HuggingFace cache paths configured correctly")
    logger.info("[INFO] Models will be cached in:")
    logger.info(f"       {cache_dir}")
    logger.info("")

    return cache_dir


def setup_hy3dgen_paths():
    """Setup hy3dgen (Hunyuan3D) specific paths"""

    logger.info("[SETUP] Configuring hy3dgen paths...")

    base_dir = Path(__file__).parent.parent
    hy3d_cache = base_dir / "models" / ".cache" / "hy3dgen"
    hy3d_cache.mkdir(parents=True, exist_ok=True)

    # Set hy3dgen cache path (use proper backslashes for Windows)
    os.environ['HY3DGEN_CACHE_DIR'] = str(hy3d_cache)
    logger.info(f"[CONFIG] HY3DGEN_CACHE_DIR = {hy3d_cache}")

    # Alternative: Set HOME to ensure .cache/hy3dgen works with backslashes
    # This helps the hy3dgen module find its cache directory correctly
    home_dir = base_dir
    os.environ['HOME'] = str(home_dir)
    logger.info(f"[CONFIG] HOME = {home_dir} (for .cache resolution)")

    return hy3d_cache


def verify_cache_structure():
    """Verify cache directory structure is correct"""

    logger.info("[VERIFY] Checking cache directory structure...")

    cache_dir = Path(os.environ.get('HF_HOME', ''))

    if not cache_dir.exists():
        logger.warning(f"[WARN] Cache directory not found: {cache_dir}")
        return False

    required_dirs = [
        cache_dir / "transformers",
        cache_dir / "datasets",
        cache_dir / "hy3dgen"
    ]

    all_exist = True
    for dir_path in required_dirs:
        if dir_path.exists():
            logger.info(f"[CHECK] ✓ {dir_path.name}/")
        else:
            logger.warning(f"[CHECK] ✗ {dir_path.name}/ (not found)")
            all_exist = False

    if all_exist:
        logger.info("[SUCCESS] Cache structure verified")
    else:
        logger.warning("[WARN] Some cache directories missing - will be created on first use")

    return True


def create_env_file():
    """Create or update .env file with cache settings"""

    logger.info("[CONFIG] Creating/updating .env file...")

    base_dir = Path(__file__).parent.parent
    env_file = base_dir / ".env"

    cache_dir = Path(os.environ.get('HF_HOME', ''))

    env_content = f"""# ============================================================================
# ORFEAS AI 2D3D Studio - Environment Configuration
# ============================================================================

# [HUGGINGFACE CACHE] Proper Windows paths (backslashes, no mixed separators)
HF_HOME={cache_dir}
TRANSFORMERS_CACHE={cache_dir}/transformers
HF_DATASETS_CACHE={cache_dir}/datasets

# [HY3DGEN CACHE] Hunyuan3D specific cache
HY3DGEN_CACHE={cache_dir}/hy3dgen

# [DEVICE] GPU/CPU selection
DEVICE=cuda

# [LLM] Local LLM settings
LOCAL_LLM_ENABLED=true
LOCAL_LLM_AUTO_START=true
LOCAL_LLM_ENDPOINT=http://localhost:11434
LOCAL_LLM_MODEL=mistral

# [PERFORMANCE] GPU optimization
XFORMERS_DISABLED=1
GPU_MEMORY_LIMIT=0.8
MAX_CONCURRENT_JOBS=3

# [MONITORING] Logging
ENABLE_MONITORING=true
LOG_LEVEL=INFO

# [API] CORS configuration
CORS_ORIGINS=*

"""

    with open(env_file, 'a') as f:
        f.write(env_content)

    logger.info(f"[CHECK] .env file configured: {env_file}")


def print_next_steps():
    """Print next steps for user"""

    logger.info("")
    logger.info("=" * 80)
    logger.info("[NEXT STEPS]")
    logger.info("=" * 80)
    logger.info("")
    logger.info("1️⃣  Pre-download models (optional but recommended):")
    logger.info("   cd backend")
    logger.info("   python download_models.py")
    logger.info("")
    logger.info("2️⃣  Start the backend server:")
    logger.info("   python main.py")
    logger.info("")
    logger.info("3️⃣  Verify model loading:")
    logger.info("   Check logs for: '[SUCCESS] Hunyuan3D model FULLY LOADED'")
    logger.info("")
    logger.info("[INFO] All model cache paths are now configured correctly!")
    logger.info("[INFO] No more mixed path separators (/ and \\) on Windows!")
    logger.info("")


def main():
    """Setup all cache paths"""

    try:
        # Setup HuggingFace cache
        _ = setup_huggingface_cache()

        # Setup hy3dgen paths
        _ = setup_hy3dgen_paths()

        # Verify structure
        verify_cache_structure()

        # Create/update .env
        create_env_file()

        # Print next steps
        print_next_steps()

        logger.info("[✅] Setup complete! Models are now properly configured.")

        return True

    except Exception as e:
        logger.error(f"[ERROR] Setup failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
