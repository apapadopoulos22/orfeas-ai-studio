"""
Quick batch inference test - minimal version
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from PIL import Image
import numpy as np

logger.info("Creating test image...")
img_array = np.random.randint(0, 255, (512, 512, 3), dtype=np.uint8)
img = Image.fromarray(img_array)
logger.info(f" Test image created: {img.size}, {img.mode}")

logger.info("\nTesting processor initialization...")
from hunyuan_integration import get_3d_processor

try:
    processor = get_3d_processor()
    logger.info(" Processor initialized")

    # Check for batch capability
    if hasattr(processor, 'generate_shape_batch'):
        logger.info(" Batch inference capability found!")

        logger.info("\nTesting batch generation with 1 image...")
        import time
        start = time.time()

        meshes = processor.generate_shape_batch(
            images=[img],
            num_inference_steps=15  # Reduced for quick test
        )

        elapsed = time.time() - start
        logger.info(f" Batch generation complete in {elapsed:.2f}s")
        logger.info(f"   Meshes returned: {len(meshes)}")

    else:
        logger.error(" Batch inference NOT available")

except Exception as e:
    logger.error(f" Test failed: {e}")
    import traceback
    traceback.print_exc()

logger.info("\n Quick test complete")
