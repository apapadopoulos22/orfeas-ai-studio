"""
+==============================================================================â•—
| [WARRIOR] ORFEAS PWA ICON GENERATOR [WARRIOR]                                           |
| Generate all required PWA icons for ORFEAS Studio                            |
| ORFEAS AI                                                |
+==============================================================================
"""

from PIL import Image, ImageDraw, ImageFont
import os

def generate_pwa_icons() -> None:
    """Generate all PWA icons with ORFEAS branding"""

    # Icon sizes required by PWA manifest
    sizes = [72, 96, 128, 144, 152, 192, 384, 512]

    # Create icons directory if it doesn't exist
    icons_dir = "icons"
    os.makedirs(icons_dir, exist_ok=True)

    print("[ORFEAS] ORFEAS PWA Icon Generator - Starting...")
    print(f"[FOLDER] Output directory: {icons_dir}/")
    print(f"[ART] Generating {len(sizes)} icons...")
    print()

    for size in sizes:
        # Create new image with ORFEAS brand color
        img = Image.new('RGB', (size, size), color='#e74c3c')
        draw = ImageDraw.Draw(img)

        # Draw simple "O" letter for ORFEAS
        # Calculate font size (70% of icon size)
        font_size = int(size * 0.7)

        # Draw white circle for "O" shape
        circle_padding = size // 6
        circle_bbox = [
            circle_padding,
            circle_padding,
            size - circle_padding,
            size - circle_padding
        ]

        # Draw outer white circle
        draw.ellipse(circle_bbox, fill='white')

        # Draw inner red circle to create "O" shape
        inner_padding = size // 4
        inner_bbox = [
            inner_padding,
            inner_padding,
            size - inner_padding,
            size - inner_padding
        ]
        draw.ellipse(inner_bbox, fill='#e74c3c')

        # Save icon
        filename = f"{icons_dir}/icon-{size}x{size}.png"
        img.save(filename, 'PNG', optimize=True)

        # Get file size
        file_size = os.path.getsize(filename)
        print(f"[OK] Generated: {filename} ({file_size:,} bytes)")

    print()
    print(" PWA Icon Generation Complete!")
    print(f"[STATS] Total icons: {len(sizes)}")

    # Calculate total size
    total_size = sum(os.path.getsize(f"{icons_dir}/icon-{s}x{s}.png") for s in sizes)
    print(f" Total size: {total_size:,} bytes")
    print()
    print("[ORFEAS] Icons ready for PWA deployment!")

if __name__ == "__main__":
    generate_pwa_icons()
