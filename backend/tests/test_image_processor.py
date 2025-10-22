"""
+==============================================================================â•—
|              ORFEAS Testing Suite - Image Processing Tests                  |
|                    Unit tests for image processing (ORFEAS Backend)          |
+==============================================================================
"""
import pytest
import numpy as np
from PIL import Image, ImageEnhance
from pathlib import Path
import sys
from typing import Any

backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

# Image processing is integrated in main.py
from main import sanitize_filename


@pytest.mark.unit
class TestImageProcessing:
    """Test suite for image processing functionality."""

    def test_filename_sanitization(self) -> None:
        """Test filename sanitization."""
        result = sanitize_filename("test file.png")
        assert result is not None
        assert len(result) > 0

    def test_load_image(self, test_image_file: Any) -> None:
        """Test image loading with PIL."""
        img = Image.open(str(test_image_file))
        assert img is not None
        assert isinstance(img, Image.Image)

    def test_resize_image(self) -> None:
        """Test image resizing."""
        test_img = Image.new('RGB', (1024, 768), color='red')
        resized = test_img.resize((512, 512), Image.Resampling.LANCZOS)
        assert resized.size == (512, 512)

    def test_image_conversion(self) -> None:
        """Test image mode conversion."""
        test_img = Image.new('RGB', (256, 256), color='blue')
        assert test_img.mode == 'RGB'

        # Convert to grayscale
        gray = test_img.convert('L')
        assert gray.mode == 'L'
