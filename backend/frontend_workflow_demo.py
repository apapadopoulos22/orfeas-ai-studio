#!/usr/bin/env python3
"""
COMPLETE FRONTEND STL WORKFLOW DEMONSTRATION
Shows the full process: Import Image 'Üí Generate STL 'Üí Save 'Üí Verify
"""

from pathlib import Path
import struct
from PIL import Image, ImageDraw, ImageFilter
import numpy as np

def create_demo_image() -> None:
    """Create a demonstration image for STL conversion"""
    print("[ART] CREATING DEMONSTRATION IMAGE")
    print("=" * 50)

    # Create a realistic coin/medallion image with clear depth
    img = Image.new('RGB', (200, 200), 'lightgray')
    draw = ImageDraw.Draw(img)

    center_x, center_y = 100, 100

    # Background (deepest - dark)
    draw.rectangle([0, 0, 200, 200], fill=(60, 60, 60))

    # Outer coin rim (raised - bright)
    draw.ellipse([10, 10, 190, 190], fill=(200, 200, 200), outline=(220, 220, 220), width=4)

    # Inner coin area (medium depth)
    draw.ellipse([25, 25, 175, 175], fill=(140, 140, 140))

    # Central emblem - letter "O" for ORFEAS (highest - brightest)
    draw.ellipse([60, 60, 140, 140], fill=(240, 240, 240), outline=(255, 255, 255), width=3)
    draw.ellipse([80, 80, 120, 120], fill=(140, 140, 140))  # Inner hole

    # Decorative border dots (raised)
    for angle in range(0, 360, 30):
        rad = np.radians(angle)
        x = center_x + 70 * np.cos(rad)
        y = center_y + 70 * np.sin(rad)
        draw.ellipse([x-5, y-5, x+5, y+5], fill=(180, 180, 180))

    # Text around the edge (recessed - dark)
    text_points = "ORFEAS·3D·STL·MAKER·"
    for i, char in enumerate(text_points):
        if char != '·':
            angle = i * 15  # Degrees
            rad = np.radians(angle)
            x = center_x + 85 * np.cos(rad)
            y = center_y + 85 * np.sin(rad)
            draw.text((x-3, y-3), char, fill=(80, 80, 80))

    # Apply slight blur for realistic depth transitions
    img = img.filter(ImageFilter.GaussianBlur(radius=0.5))

    # Save the image
    demo_path = Path("demo_coin.jpg")
    img.save(demo_path, "JPEG", quality=95)

    file_size = demo_path.stat().st_size
    print(f"[OK] Demo image created: {demo_path}")
    print(f"üìè Size: 200x200 pixels")
    print(f"üíæ File size: {file_size} bytes")
    print(f"[TARGET] Features: Coin with 'O' emblem, border dots, text ring")
    print(f"[SEARCH] Depth levels: Background(dark) 'Üí Coin(medium) 'Üí Rim(bright) 'Üí Emblem(brightest)")

    return demo_path

def analyze_existing_stl_files() -> None:
    """Analyze existing STL files to show what good output looks like"""
    print("\n[SEARCH] ANALYZING EXISTING STL FILES")
    print("=" * 50)

    # Find STL files in current directory
    stl_files = list(Path(".").glob("*.stl"))

    if not stl_files:
        print("No STL files found in current directory")
        return

    print(f"Found {len(stl_files)} STL files:")

    for i, stl_file in enumerate(stl_files[:3], 1):  # Analyze first 3
        print(f"\n[FOLDER] {i}. {stl_file.name}")

        try:
            file_size = stl_file.stat().st_size
            print(f"   üíæ File size: {file_size:,} bytes ({file_size/1024:.1f} KB)")

            if file_size < 84:
                print("   [FAIL] Too small to be valid STL")
                continue

            with open(stl_file, 'rb') as f:
                # Read header
                header = f.read(80)
                header_text = header.decode('ascii', errors='ignore').strip()
                print(f"   üìã Header: {header_text[:30]}{'...' if len(header_text) > 30 else ''}")

                # Read triangle count
                triangle_bytes = f.read(4)
                if len(triangle_bytes) == 4:
                    triangle_count = struct.unpack('<I', triangle_bytes)[0]
                    print(f"   üìê Triangles: {triangle_count:,}")

                    # Quality assessment
                    if triangle_count >= 100000:
                        quality = "ULTRA HIGH"
                    elif triangle_count >= 10000:
                        quality = "HIGH"
                    elif triangle_count >= 1000:
                        quality = "MEDIUM"
                    elif triangle_count >= 100:
                        quality = "LOW"
                    else:
                        quality = "BASIC"

                    print(f"    Quality: {quality}")

                    # Check first triangle
                    normal = struct.unpack('<3f', f.read(12))
                    v1 = struct.unpack('<3f', f.read(12))
                    v2 = struct.unpack('<3f', f.read(12))
                    v3 = struct.unpack('<3f', f.read(12))

                    # Verify triangle is valid
                    vertices = v1 + v2 + v3
                    if any(abs(coord) > 0.001 for coord in vertices):
                        print(f"   [OK] Contains valid geometry")
                    else:
                        print(f"   [WARN] May contain degenerate triangles")
                else:
                    print("   [FAIL] Invalid STL format")

        except Exception as e:
            print(f"   [FAIL] Analysis failed: {e}")

def show_frontend_workflow_steps() -> None:
    """Show the complete frontend workflow steps"""
    print("\n[LAUNCH] COMPLETE FRONTEND WORKFLOW STEPS")
    print("=" * 60)

    print("STEP 1: PREPARE YOUR IMAGE [IMAGE]")
    print("   • Use high contrast image (bright = close, dark = far)")
    print("   • Recommended size: 150x150 to 500x500 pixels")
    print("   • Formats: JPG, PNG, or other common image formats")
    print("   • Example: Face (nose bright, eyes dark) or coin (rim bright, background dark)")

    print("\nSTEP 2: ACCESS ORFEAS FRONTEND [WEB]")
    print("   • Open browser to one of these:")
    print("     - http://localhost:5000/studio (if safe_server.py running)")
    print("     - http://localhost:5002/studio (if powerful_3d_server.py running)")
    print("     - Use ORFEAS_MAKERS_PORTAL.html or orfeas-studio.html")
    print("   • Wait for interface to fully load")

    print("\nSTEP 3: IMPORT IMAGE TO FRONTEND üì§")
    print("   • Method 1: Click 'Choose File' or 'Upload Image' button")
    print("   • Method 2: Drag and drop image onto upload area")
    print("   • Wait for upload confirmation")
    print("   • Note the Job ID that appears")

    print("\nSTEP 4: CONFIGURE STL SETTINGS [SETTINGS]")
    print("   • Format: STL (for 3D printing compatibility)")
    print("   • Quality Options:")
    print("     - Low: Fast generation, ~500-2K triangles")
    print("     - Medium: Balanced, ~2K-10K triangles (recommended)")
    print("     - High: Detailed, ~10K-50K triangles")
    print("     - Ultra: Maximum detail, 50K+ triangles")
    print("   • Method: Auto (lets system choose optimal algorithm)")
    print("   • Dimensions: Set width, height, depth in mm or units")

    print("\nSTEP 5: GENERATE STL üè≠")
    print("   • Click 'Generate 3D Model' or 'Generate STL' button")
    print("   • Watch progress bar and status messages:")
    print("     - 'Processing image...'")
    print("     - 'Estimating depth...' (neural networks working)")
    print("     - 'Generating mesh...' (creating triangles)")
    print("     - 'Optimizing geometry...' (smoothing/cleanup)")
    print("   • Processing time: 30 seconds to 3 minutes depending on quality")

    print("\nSTEP 6: PREVIEW GENERATED STL ")
    print("   • 3D model appears in Three.js viewer")
    print("   • Interactive controls:")
    print("     - Mouse drag: Rotate model")
    print("     - Mouse wheel: Zoom in/out")
    print("     - Right-click drag: Pan view")
    print("   • Check that depth looks correct:")
    print("     - Bright areas should protrude (nose, rim, text)")
    print("     - Dark areas should be recessed (eyes, holes, background)")

    print("\nSTEP 7: SAVE/DOWNLOAD STL üíæ")
    print("   • Click 'Download STL' or 'Save Model' button")
    print("   • File downloads as 'model.stl' or similar")
    print("   • Note the file size and triangle count in status")
    print("   • Typical sizes:")
    print("     - Small models: 50KB-500KB")
    print("     - Medium models: 500KB-5MB")
    print("     - Large models: 5MB-50MB+")

    print("\nSTEP 8: VERIFY SAVED STL [OK]")
    print("   • Check file exists and has reasonable size (>84 bytes)")
    print("   • Triangle count should match expected quality level")
    print("   • Open in 3D software to verify (optional):")
    print("     - Blender (free): File 'Üí Import 'Üí STL")
    print("     - MeshLab (free): File 'Üí Import Mesh")
    print("     - 3D Builder (Windows): Built-in app")
    print("   • For 3D printing: Check for holes, thin walls, support needs")

    print("\n[TARGET] TROUBLESHOOTING TIPS")
    print("   • Flat/bad STL: Increase image contrast, try different quality")
    print("   • Generation fails: Reduce image size, lower quality setting")
    print("   • Preview not working: Check browser supports WebGL")
    print("   • Server issues: Restart backend server")
    print("   • Wrong depth: Bright areas = high, dark areas = low")

def show_quality_examples() -> None:
    """Show what different quality levels produce"""
    print("\n[STATS] STL QUALITY LEVEL EXAMPLES")
    print("=" * 50)

    quality_levels = [
        ("Low", "500-2,000", "50-200 KB", "30-60 sec", "Fast preview, basic detail"),
        ("Medium", "2,000-10,000", "200 KB-1 MB", "1-2 min", "Good balance, recommended"),
        ("High", "10,000-50,000", "1-5 MB", "2-4 min", "Detailed, smooth surfaces"),
        ("Ultra", "50,000-200,000", "5-20 MB", "3-8 min", "Maximum detail, print-ready")
    ]

    print(f"{'Quality':<8} {'Triangles':<12} {'File Size':<12} {'Time':<10} {'Description'}")
    print("-" * 70)

    for quality, triangles, size, time, desc in quality_levels:
        print(f"{quality:<8} {triangles:<12} {size:<12} {time:<10} {desc}")

def main() -> None:
    """Main demonstration function"""

    print("[TARGET] COMPLETE FRONTEND STL WORKFLOW DEMONSTRATION")
    print("=" * 70)

    # Create demo image
    demo_image = create_demo_image()

    # Analyze existing STL files
    analyze_existing_stl_files()

    # Show workflow steps
    show_frontend_workflow_steps()

    # Show quality examples
    show_quality_examples()

    print(f"\n" + "=" * 70)
    print("[OK] WORKFLOW DEMONSTRATION COMPLETE")
    print("=" * 70)

    print("üìã Summary:")
    print(f"   [IMAGE] Demo image created: {demo_image}")
    print("   [SEARCH] Existing STL files analyzed")
    print("   üìñ Complete workflow steps documented")
    print("   [STATS] Quality levels explained")

    print(f"\n[TARGET] Next Steps:")
    print("   1. Start a server (safe_server.py or powerful_3d_server.py)")
    print("   2. Open frontend interface in browser")
    print("   3. Use the demo image or your own image")
    print("   4. Follow the workflow steps above")
    print("   5. Generate, preview, and save your STL!")

    print(f"\n[WEB] Frontend URLs to try:")
    print("   • http://localhost:5000/studio (safe server)")
    print("   • http://localhost:5002/studio (powerful server)")
    print("   • Open ORFEAS_MAKERS_PORTAL.html directly")
    print("   • Open orfeas-studio.html directly")

if __name__ == "__main__":
    main()
