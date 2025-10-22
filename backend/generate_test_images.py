"""
Generate Test Images for Comprehensive Format Testing
=======================================================
Creates test images in all supported formats (PNG, JPG, JPEG, GIF, BMP, TIFF, WEBP)
"""

from PIL import Image, ImageDraw, ImageFont
import os
from typing import Any, Tuple

# Create test_images directory
test_images_dir = "test_images"
os.makedirs(test_images_dir, exist_ok=True)

# Image formats to test
formats = {
    'png': 'PNG',
    'jpg': 'JPEG',
    'jpeg': 'JPEG',
    'gif': 'GIF',
    'bmp': 'BMP',
    'tiff': 'TIFF',
    'webp': 'WEBP'
}

def create_test_image(format_ext: Any, format_name: Any, size: Any = (512, 512)) -> Tuple:
    """Create a test image with gradient and text"""
    # Create image with gradient
    img = Image.new('RGB', size)
    draw = ImageDraw.Draw(img)

    # Draw gradient
    for y in range(size[1]):
        color_value = int(255 * (y / size[1]))
        draw.rectangle([(0, y), (size[0], y+1)], fill=(color_value, 100, 255-color_value))

    # Draw circle
    circle_bbox = [size[0]//4, size[1]//4, 3*size[0]//4, 3*size[1]//4]
    draw.ellipse(circle_bbox, fill=(255, 255, 0), outline=(0, 0, 0), width=5)

    # Add text
    text = f"Test {format_ext.upper()}"
    try:
        # Try to use a default font
        font = ImageFont.truetype("arial.ttf", 40)
    except:
        # Fallback to default font
        font = ImageFont.load_default()

    # Calculate text position (center)
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    text_x = (size[0] - text_width) // 2
    text_y = (size[1] - text_height) // 2

    draw.text((text_x, text_y), text, fill=(0, 0, 0), font=font)

    # Save image
    filename = f"{test_images_dir}/test_image.{format_ext}"

    # Special handling for formats
    if format_name == 'JPEG':
        # JPEG doesn't support transparency, convert to RGB
        img = img.convert('RGB')
        img.save(filename, format_name, quality=95)
    elif format_name == 'GIF':
        # GIF supports transparency but limited colors
        img = img.convert('RGB')
        img.save(filename, format_name)
    else:
        img.save(filename, format_name)

    file_size = os.path.getsize(filename)
    print(f"[OK] Created {filename} ({file_size:,} bytes)")
    return filename, file_size

print("\n" + "="*60)
print("[ART] GENERATING TEST IMAGES IN ALL FORMATS")
print("="*60 + "\n")

created_files = []

for ext, fmt in formats.items():
    try:
        filename, size = create_test_image(ext, fmt)
        created_files.append({
            'extension': ext,
            'format': fmt,
            'filename': filename,
            'size': size
        })
    except Exception as e:
        print(f"[FAIL] Failed to create {ext}: {e}")

print("\n" + "="*60)
print(f"[STATS] SUMMARY: Created {len(created_files)}/{len(formats)} test images")
print("="*60)

for file_info in created_files:
    print(f"  • {file_info['filename']}: {file_info['size']:,} bytes")

print("\n[OK] Test images ready for comprehensive testing!")
