"""
Real 3D generation test with actual image
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(message)s')
logger = logging.getLogger(__name__)

from PIL import Image, ImageDraw
import time

# Create a test image with recognizable shape
logger.info("Creating test images...")
images = []

for i in range(2):  # Test with 2 images
    img = Image.new('RGB', (512, 512), color=(240, 240, 240))
    draw = ImageDraw.Draw(img)

    # Draw a simple shape
    color = (100 + i*50, 150, 200)
    draw.ellipse([100, 100, 400, 400], fill=color, outline=(0, 0, 0), width=3)
    draw.rectangle([200, 150, 300, 350], fill=(255, 255, 255))

    images.append(img)

logger.info(f" Created {len(images)} test images")

# Initialize processor
logger.info("\nInitializing Hunyuan3D processor...")
from hunyuan_integration import get_3d_processor

try:
    processor = get_3d_processor()
    logger.info(" Processor initialized")
except Exception as e:
    logger.error(f" Failed to initialize: {e}")
    sys.exit(1)

# Test batch generation
if hasattr(processor, 'generate_shape_batch'):
    logger.info("\n" + "="*80)
    logger.info(f"BATCH TEST: Processing {len(images)} images")
    logger.info("="*80)

    start = time.time()

    try:
        meshes = processor.generate_shape_batch(
            images=images,
            num_inference_steps=30  # Balanced quality/speed
        )

        elapsed = time.time() - start
        successful = [m for m in meshes if m is not None]

        logger.info(""*80)
        logger.info(f" Batch complete in {elapsed:.2f}s")
        logger.info(f"   Per image: {elapsed/len(images):.2f}s")
        logger.info(f"   Success: {len(successful)}/{len(meshes)}")
        logger.info("="*80)

        if len(successful) > 0:
            logger.info("\n   BATCH INFERENCE WORKING!   ")
        else:
            logger.warning("\n  Batch inference ran but generated no valid meshes")

    except Exception as e:
        logger.error(f"\n Batch generation failed: {e}")
        import traceback
        traceback.print_exc()
else:
    logger.error(" Batch inference not available")
