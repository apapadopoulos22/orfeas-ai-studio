#!/usr/bin/env python3
"""
Frontend Complex Shape STL Test - Direct Browser Integration
Tests the complete workflow: Image creation -> Upload -> 3D Generation -> STL Download -> Analysis
"""

import time
import requests
from pathlib import Path
from PIL import Image, ImageDraw
import numpy as np
import json

class FrontendSTLTester:
    def __init__(self):
        self.server_url = "http://localhost:5000"
        self.api_base = f"{self.server_url}/api"

    def create_complex_test_shapes(self):
        """Create complex shape images for testing"""
        print("[ART] Creating complex test shapes...")

        shapes = {}

        # 1. Fractal Tree Structure
        img = Image.new('RGB', (512, 512), 'white')
        draw = ImageDraw.Draw(img)

        def draw_tree(x, y, angle, length, depth):
            if depth > 0:
                end_x = x + length * np.cos(np.radians(angle))
                end_y = y + length * np.sin(np.radians(angle))

                # Draw branch
                draw.line([(x, y), (end_x, end_y)], fill='black', width=max(1, depth))

                # Recursively draw smaller branches
                new_length = length * 0.7
                draw_tree(end_x, end_y, angle - 30, new_length, depth - 1)
                draw_tree(end_x, end_y, angle + 30, new_length, depth - 1)

        # Draw fractal tree
        draw_tree(256, 450, -90, 100, 8)

        tree_path = Path("complex_fractal_tree.png")
        img.save(tree_path)
        shapes['fractal_tree'] = tree_path

        # 2. Complex Mechanical Gear
        img = Image.new('RGB', (512, 512), 'white')
        draw = ImageDraw.Draw(img)

        center_x, center_y = 256, 256
        outer_radius = 200
        inner_radius = 50
        teeth = 24

        # Draw gear teeth
        points = []
        for i in range(teeth * 2):
            angle = (i * 360) / (teeth * 2)
            if i % 2 == 0:
                radius = outer_radius
            else:
                radius = outer_radius - 20

            x = center_x + radius * np.cos(np.radians(angle))
            y = center_y + radius * np.sin(np.radians(angle))
            points.append((x, y))

        draw.polygon(points, fill='lightgray', outline='black', width=2)

        # Inner circle
        draw.ellipse([center_x-inner_radius, center_y-inner_radius,
                     center_x+inner_radius, center_y+inner_radius],
                    fill='white', outline='black', width=3)

        # Add mounting holes
        for angle in [0, 120, 240]:
            hole_x = center_x + 30 * np.cos(np.radians(angle))
            hole_y = center_y + 30 * np.sin(np.radians(angle))
            draw.ellipse([hole_x-8, hole_y-8, hole_x+8, hole_y+8],
                        fill='white', outline='black', width=2)

        gear_path = Path("complex_mechanical_gear.png")
        img.save(gear_path)
        shapes['mechanical_gear'] = gear_path

        # 3. Organic Cellular Structure
        img = Image.new('RGB', (512, 512), 'white')
        draw = ImageDraw.Draw(img)

        # Create Voronoi-like cellular pattern
        np.random.seed(42)  # For reproducible results
        num_cells = 50

        # Generate random cell centers
        centers = []
        for _ in range(num_cells):
            x = np.random.randint(50, 462)
            y = np.random.randint(50, 462)
            centers.append((x, y))

        # Draw cells
        for i, (cx, cy) in enumerate(centers):
            # Variable cell size
            size = np.random.randint(15, 40)

            # Create organic shape
            points = []
            for angle in range(0, 360, 20):
                variation = np.random.uniform(0.7, 1.3)
                radius = size * variation
                x = cx + radius * np.cos(np.radians(angle))
                y = cy + radius * np.sin(np.radians(angle))
                points.append((x, y))

            # Color based on position for variety
            gray_level = int(100 + 100 * (i / num_cells))
            color = (gray_level, gray_level, gray_level)

            draw.polygon(points, fill=color, outline='black', width=1)

        cellular_path = Path("complex_organic_cellular.png")
        img.save(cellular_path)
        shapes['organic_cellular'] = cellular_path

        # 4. Mathematical Surface (Mandelbrot-inspired)
        img = Image.new('RGB', (512, 512), 'white')
        pixels = img.load()

        def mandelbrot_iteration(c, max_iter=100):
            z = 0
            for n in range(max_iter):
                if abs(z) > 2:
                    return n
                z = z*z + c
            return max_iter

        # Create height map based on Mandelbrot set
        for x in range(512):
            for y in range(512):
                # Map pixel coordinates to complex plane
                real = (x - 256) / 128.0
                imag = (y - 256) / 128.0
                c = complex(real, imag)

                iterations = mandelbrot_iteration(c, 50)

                # Convert to grayscale
                if iterations == 50:
                    gray = 0
                else:
                    gray = int(255 * (iterations / 50))

                pixels[x, y] = (gray, gray, gray)

        mandelbrot_path = Path("complex_mathematical_surface.png")
        img.save(mandelbrot_path)
        shapes['mathematical_surface'] = mandelbrot_path

        print(f"[OK] Created {len(shapes)} complex test shapes")
        return shapes

    def test_api_health(self):
        """Test if server is responding"""
        try:
            response = requests.get(f"{self.api_base}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"[OK] Server healthy: {data.get('status', 'unknown')}")
                return True
            else:
                print(f"[FAIL] Server unhealthy: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"[FAIL] Server connection failed: {e}")
            return False

    def upload_and_generate_stl(self, image_path, shape_name, dimensions=None):
        """Complete workflow: upload -> generate -> download -> analyze"""

        print(f"\n[CONFIG] Testing shape: {shape_name}")
        print(f"[FOLDER] Image: {image_path}")

        # Default dimensions for different shape types
        if dimensions is None:
            if 'gear' in shape_name:
                dimensions = {'width': 80, 'height': 80, 'depth': 8}  # Thin gear
            elif 'tree' in shape_name:
                dimensions = {'width': 60, 'height': 100, 'depth': 15}  # Tall tree
            elif 'cellular' in shape_name:
                dimensions = {'width': 70, 'height': 70, 'depth': 12}  # Organic structure
            else:
                dimensions = {'width': 50, 'height': 50, 'depth': 10}  # Default

        print(f" Dimensions: {dimensions['width']}×{dimensions['height']}×{dimensions['depth']}mm")

        # Step 1: Upload image
        try:
            with open(image_path, 'rb') as f:
                files = {'image': (image_path.name, f, 'image/png')}
                response = requests.post(f"{self.api_base}/upload-image", files=files)

            if response.status_code != 200:
                print(f"[FAIL] Upload failed: HTTP {response.status_code}")
                return None

            upload_data = response.json()
            job_id = upload_data.get('job_id')
            print(f"[OK] Upload successful: {job_id}")

        except Exception as e:
            print(f"[FAIL] Upload error: {e}")
            return None

        # Step 2: Generate 3D model
        try:
            payload = {
                'job_id': job_id,
                'format': 'stl',
                'dimensions': dimensions
            }

            response = requests.post(
                f"{self.api_base}/generate-3d",
                json=payload,
                headers={'Content-Type': 'application/json'}
            )

            if response.status_code != 200:
                print(f"[FAIL] 3D generation failed: HTTP {response.status_code}")
                return None

            print("[OK] 3D generation started")

        except Exception as e:
            print(f"[FAIL] 3D generation error: {e}")
            return None

        # Step 3: Wait for completion
        print("[WAIT] Waiting for completion...")
        max_wait = 60  # seconds
        start_time = time.time()

        while time.time() - start_time < max_wait:
            try:
                response = requests.get(f"{self.api_base}/job-status/{job_id}")

                if response.status_code == 200:
                    status_data = response.json()
                    status = status_data.get('status')

                    if status == 'completed':
                        print("[OK] Generation completed!")
                        return self.analyze_generated_stl(job_id, shape_name, status_data)
                    elif status == 'failed':
                        error = status_data.get('error', 'Unknown error')
                        print(f"[FAIL] Generation failed: {error}")
                        return None
                    else:
                        print(f"   Status: {status}")

                time.sleep(2)

            except Exception as e:
                print(f"[FAIL] Status check error: {e}")
                return None

        print("[FAIL] Generation timeout")
        return None

    def analyze_generated_stl(self, job_id, shape_name, status_data):
        """Download and analyze the generated STL file"""

        try:
            # Get download URL
            download_url = status_data.get('download_url')
            if not download_url:
                print("[FAIL] No download URL provided")
                return None

            # Download file
            full_url = f"{self.server_url}{download_url}"
            response = requests.get(full_url)

            if response.status_code != 200:
                print(f"[FAIL] Download failed: HTTP {response.status_code}")
                return None

            # Save file
            output_filename = f"test_{shape_name}_{job_id}.stl"
            output_path = Path(output_filename)

            with open(output_path, 'wb') as f:
                f.write(response.content)

            file_size = len(response.content)
            print(f"[OK] Downloaded: {output_filename} ({file_size:,} bytes)")

            # Quick STL analysis
            analysis = self.quick_stl_analysis(response.content, shape_name)
            analysis['filename'] = output_filename
            analysis['file_size'] = file_size
            analysis['job_id'] = job_id

            return analysis

        except Exception as e:
            print(f"[FAIL] Download/analysis error: {e}")
            return None

    def quick_stl_analysis(self, content, shape_name):
        """Quick analysis of STL content"""

        analysis = {
            'shape_name': shape_name,
            'format': 'unknown',
            'triangles': 0,
            'valid': False,
            'errors': []
        }

        try:
            if len(content) < 84:
                analysis['errors'].append("File too small")
                return analysis

            # Check if ASCII STL
            if content.startswith(b'solid '):
                analysis['format'] = 'ASCII STL'
                content_str = content.decode('utf-8', errors='ignore')
                analysis['triangles'] = content_str.count('facet normal')
            else:
                # Binary STL
                analysis['format'] = 'Binary STL'

                if len(content) >= 84:
                    import struct
                    triangle_count = struct.unpack('<I', content[80:84])[0]
                    analysis['triangles'] = triangle_count

                    # Check file size
                    expected_size = 84 + (triangle_count * 50)
                    actual_size = len(content)

                    if abs(expected_size - actual_size) <= 2:
                        analysis['valid'] = True
                    else:
                        analysis['errors'].append(f"Size mismatch: expected {expected_size}, got {actual_size}")

            if analysis['triangles'] > 0 and not analysis['errors']:
                analysis['valid'] = True

        except Exception as e:
            analysis['errors'].append(f"Analysis failed: {str(e)}")

        # Print analysis
        status = "[OK] VALID" if analysis['valid'] else "[FAIL] INVALID"
        print(f"   {status} | {analysis['format']} | {analysis['triangles']:,} triangles")

        if analysis['errors']:
            for error in analysis['errors']:
                print(f"    {error}")

        return analysis

    def run_comprehensive_test(self):
        """Run complete STL generation test suite"""

        print("[LAUNCH] COMPREHENSIVE FRONTEND STL GENERATION TEST")
        print("=" * 60)

        # Check server
        if not self.test_api_health():
            print("[FAIL] Server not available - aborting test")
            return False

        # Create test images
        shapes = self.create_complex_test_shapes()

        if not shapes:
            print("[FAIL] Failed to create test shapes")
            return False

        # Test each shape
        results = []

        for shape_name, image_path in shapes.items():
            result = self.upload_and_generate_stl(image_path, shape_name)
            if result:
                results.append(result)

            time.sleep(1)  # Brief pause between tests

        # Generate summary report
        self.generate_test_report(results)

        # Cleanup test images
        for image_path in shapes.values():
            if image_path.exists():
                image_path.unlink()

        return len(results) > 0

    def generate_test_report(self, results):
        """Generate test summary report"""

        print("\n" + "="*60)
        print("[STATS] FRONTEND STL GENERATION TEST REPORT")
        print("="*60)

        if not results:
            print("[FAIL] No successful generations to report")
            return

        valid_count = sum(1 for r in results if r['valid'])
        total_count = len(results)

        print(f"[METRICS] Test Summary:")
        print(f"   Total Tests: {total_count}")
        print(f"   Successful: {valid_count} ({valid_count/total_count*100:.1f}%)")
        print(f"   Failed: {total_count - valid_count}")

        # Statistics
        total_triangles = sum(r['triangles'] for r in results if r['valid'])
        total_size = sum(r['file_size'] for r in results)

        print(f"\n[STATS] Generation Statistics:")
        print(f"   Total Triangles Generated: {total_triangles:,}")
        print(f"   Total File Size: {total_size/1024/1024:.2f} MB")
        print(f"   Average Triangles: {total_triangles/valid_count:,.0f}" if valid_count > 0 else "   Average Triangles: 0")
        print(f"   Average File Size: {(total_size/total_count)/1024:.1f} KB")

        # Individual results
        print(f"\n[TARGET] Individual Shape Results:")
        for result in results:
            status = "[OK]" if result['valid'] else "[FAIL]"
            print(f"   {status} {result['shape_name']}: {result['triangles']:,} triangles, {result['file_size']/1024:.1f} KB")

        # Save results
        report_data = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'test_type': 'Frontend STL Generation',
            'summary': {
                'total_tests': total_count,
                'successful': valid_count,
                'success_rate': valid_count/total_count*100 if total_count > 0 else 0
            },
            'results': results
        }

        report_file = Path(f"frontend_stl_test_report_{int(time.time())}.json")
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2, default=str)

        print(f"\n Detailed report saved to: {report_file}")
        print("="*60)

def main():
    """Main test function"""
    tester = FrontendSTLTester()

    success = tester.run_comprehensive_test()

    if success:
        print("\n Frontend STL generation test completed successfully!")
    else:
        print("\n[FAIL] Frontend STL generation test failed!")
        exit(1)

if __name__ == "__main__":
    main()
