"""
Direct Test of Enhanced Image Validator
======================================
Bypass endpoint testing to directly test validator logic
"""

from validation_enhanced import get_enhanced_validator
from PIL import Image
import io
from typing import Any

def test_malicious_script() -> None:
    """Test: Image with embedded script"""
    print("\n" + "="*60)
    print("TEST: Malicious Script Detection (Layer 3)")
    print("="*60)

    # Create normal image
    img = Image.new('RGB', (100, 100))
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')

    # Add malicious script AFTER PNG data
    buffer.write(b'<script>alert("XSS")</script>')
    buffer.seek(0)

    # Create mock file object
    class MockFile:
        def __init__(self, buffer: Any, filename: Any) -> None:
            self.stream = buffer
            self.filename = filename

        def read(self) -> None:
            return self.stream.read()

        def seek(self, *args) -> None:
            return self.stream.seek(*args)

    file = MockFile(buffer, 'malicious.png')

    validator = get_enhanced_validator()
    is_valid, error_msg, sanitized = validator.validate_image(file)

    if not is_valid:
        print(f" PASS: Malicious content BLOCKED")
        print(f"   Error: {error_msg}")
    else:
        print(f" FAIL: Malicious content NOT detected")
        print(f"   Validator returned: is_valid={is_valid}")

def test_oversized_image() -> None:
    """Test: Oversized image (Layer 2)"""
    print("\n" + "="*60)
    print("TEST: Oversized Image Detection (Layer 2)")
    print("="*60)

    # Create 5000x5000 image (exceeds 4096px limit)
    img = Image.new('RGB', (5000, 5000))
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)

    class MockFile:
        def __init__(self, buffer: Any, filename: Any) -> None:
            self.stream = buffer
            self.filename = filename

        def read(self) -> None:
            return self.stream.read()

        def seek(self, *args) -> None:
            return self.stream.seek(*args)

    file = MockFile(buffer, 'huge.png')

    validator = get_enhanced_validator()
    is_valid, error_msg, sanitized = validator.validate_image(file)

    if not is_valid:
        print(f" PASS: Oversized image BLOCKED")
        print(f"   Error: {error_msg}")
    else:
        print(f" FAIL: Oversized image NOT blocked")
        print(f"   Validator returned: is_valid={is_valid}")

def test_wrong_magic() -> None:
    """Test: Wrong file magic number (Layer 1)"""
    print("\n" + "="*60)
    print("TEST: Wrong Magic Number Detection (Layer 1)")
    print("="*60)

    # Create text file disguised as PNG
    buffer = io.BytesIO()
    buffer.write(b'This is not a PNG file, just text!')
    buffer.seek(0)

    class MockFile:
        def __init__(self, buffer: Any, filename: Any) -> None:
            self.stream = buffer
            self.filename = filename

        def read(self) -> None:
            return self.stream.read()

        def seek(self, *args) -> None:
            return self.stream.seek(*args)

    file = MockFile(buffer, 'fake.png')

    validator = get_enhanced_validator()
    is_valid, error_msg, sanitized = validator.validate_image(file)

    if not is_valid:
        print(f" PASS: Wrong magic number BLOCKED")
        print(f"   Error: {error_msg}")
    else:
        print(f" FAIL: Wrong magic number NOT detected")
        print(f"   Validator returned: is_valid={is_valid}")

def test_valid_image() -> None:
    """Test: Valid clean image"""
    print("\n" + "="*60)
    print("TEST: Valid Clean Image (All 6 Layers)")
    print("="*60)

    # Create normal 100x100 image
    img = Image.new('RGB', (100, 100), color=(255, 0, 0))
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)

    class MockFile:
        def __init__(self, buffer: Any, filename: Any) -> None:
            self.stream = buffer
            self.filename = filename

        def read(self) -> None:
            return self.stream.read()

        def seek(self, *args) -> None:
            return self.stream.seek(*args)

    file = MockFile(buffer, 'valid.png')

    validator = get_enhanced_validator()
    is_valid, error_msg, sanitized = validator.validate_image(file)

    if is_valid:
        print(f" PASS: Valid image ACCEPTED")
        print(f"   Sanitized image size: {sanitized.size}")
    else:
        print(f" FAIL: Valid image REJECTED")
        print(f"   Error: {error_msg}")

if __name__ == "__main__":
    print("\n")
    print("" + "="*58 + "")
    print("  DIRECT ENHANCED IMAGE VALIDATOR TEST SUITE" + " "*14 + "")
    print("  Testing 6-Layer Security System Logic" + " "*19 + "")
    print("" + "="*58 + "")

    # Run all tests
    test_valid_image()
    test_wrong_magic()
    test_oversized_image()
    test_malicious_script()

    print("\n" + "="*60)
    print(" Direct validator tests complete!")
    print("="*60 + "\n")
