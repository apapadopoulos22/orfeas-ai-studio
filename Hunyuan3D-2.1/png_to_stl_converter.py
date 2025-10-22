#!/usr/bin/env python3
"""
THERION AI 2D STUDIO - PNG TO STL CONVERTER
DEUS VULT - MAXIMUM 3D PRINTING OPTIMIZATION!

Advanced PNG to STL conversion with multiple techniques:
1. Heightmap-based displacement
2. Edge detection and extrusion
3. Depth estimation from luminance
4. Professional STL optimization for 3D printing

Author: EREVUS Collective
License: AGPL-3.0
"""

import numpy as np
from PIL import Image, ImageFilter, ImageEnhance
import trimesh
from pathlib import Path
import cv2
import logging
from typing import Tuple, Optional, Dict, Any, Union
import io
import base64

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TherionPNGToSTLConverter:
    """Professional PNG to STL converter with multiple conversion techniques"""

    def __init__(self):
        """Initialize the PNG to STL converter"""
        self.default_settings = {
            'heightmap': {
                'max_height': 5.0,      # Maximum height in mm
                'base_thickness': 2.0,   # Base thickness in mm
                'smooth_iterations': 2,  # Smoothing passes
                'invert_height': False   # Invert height values
            },
            'edge_extrusion': {
                'extrude_height': 3.0,   # Extrusion height in mm
                'edge_threshold': 50,    # Edge detection threshold
                'wall_thickness': 1.0,   # Wall thickness in mm
                'smooth_edges': True     # Smooth edge transitions
            },
            'lithophane': {
                'thickness': 3.0,        # Total thickness in mm
                'min_thickness': 0.4,    # Minimum wall thickness
                'max_thickness': 2.0,    # Maximum thickness variation
                'invert': True           # Invert for backlighting
            }
        }

    def convert_png_to_stl(
        self,
        png_path: Union[str, Path, bytes],
        output_path: Union[str, Path],
        method: str = 'heightmap',
        settings: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Convert PNG image to STL file using specified method

        Args:
            png_path: Path to PNG file or image bytes
            output_path: Output STL file path
            method: Conversion method ('heightmap', 'edge_extrusion', 'lithophane')
            settings: Method-specific settings

        Returns:
            bool: Success status
        """
        try:
            logger.info(f"üöÄ Converting PNG to STL using {method} method...")

            # Load and process image
            if isinstance(png_path, bytes):
                image = Image.open(io.BytesIO(png_path))
            else:
                image = Image.open(png_path)

            # Convert to RGBA if not already
            if image.mode != 'RGBA':
                image = image.convert('RGBA')

            # Merge settings
            method_settings = self.default_settings.get(method, {})
            if settings:
                method_settings.update(settings)

            # Select conversion method
            if method == 'heightmap':
                mesh = self._heightmap_to_mesh(image, method_settings)
            elif method == 'edge_extrusion':
                mesh = self._edge_extrusion_to_mesh(image, method_settings)
            elif method == 'lithophane':
                mesh = self._lithophane_to_mesh(image, method_settings)
            else:
                raise ValueError(f"Unknown conversion method: {method}")

            # Validate and clean mesh
            mesh = self._clean_mesh(mesh)

            # Export to STL
            mesh.export(output_path, file_type='stl')

            logger.info(f"'úÖ STL file created: {output_path}")
            logger.info(f"üìê Mesh stats: {len(mesh.vertices)} vertices, {len(mesh.faces)} faces")

            return True

        except Exception as e:
            logger.error(f"'ùå PNG to STL conversion failed: {e}")
            return False

    def _heightmap_to_mesh(self, image: Image.Image, settings: Dict[str, Any]) -> trimesh.Trimesh:
        """Convert PNG to 3D mesh using heightmap displacement"""
        logger.info("üìê Generating heightmap-based mesh...")

        # Convert to grayscale for height data
        grayscale = image.convert('L')
        width, height = grayscale.size

        # Get alpha channel for transparency handling
        alpha = None
        if image.mode == 'RGBA':
            alpha = np.array(image.split()[-1])

        # Convert to numpy array
        height_data = np.array(grayscale, dtype=np.float32) / 255.0

        # Apply alpha mask if available
        if alpha is not None:
            alpha_mask = alpha / 255.0
            height_data *= alpha_mask

        # Invert if requested
        if settings.get('invert_height', False):
            height_data = 1.0 - height_data

        # Scale height
        max_height = settings.get('max_height', 5.0)
        base_thickness = settings.get('base_thickness', 2.0)
        height_data = height_data * max_height + base_thickness

        # Smooth height data
        smooth_iterations = settings.get('smooth_iterations', 2)
        for _ in range(smooth_iterations):
            height_data = cv2.GaussianBlur(height_data, (3, 3), 0.5)

        # Generate mesh vertices
        vertices = []
        for y in range(height):
            for x in range(width):
                # Top surface
                vertices.append([x, y, height_data[y, x]])
                # Bottom surface
                vertices.append([x, y, 0])

        # Generate faces for heightmap
        faces = []
        for y in range(height - 1):
            for x in range(width - 1):
                # Current quad indices (top surface)
                tl = (y * width + x) * 2      # Top-left (top surface)
                tr = (y * width + x + 1) * 2  # Top-right (top surface)
                bl = ((y + 1) * width + x) * 2      # Bottom-left (top surface)
                br = ((y + 1) * width + x + 1) * 2  # Bottom-right (top surface)

                # Top surface triangles
                faces.append([tl, bl, tr])
                faces.append([tr, bl, br])

                # Bottom surface (with flipped normals)
                tl_b = tl + 1  # Top-left (bottom surface)
                tr_b = tr + 1  # Top-right (bottom surface)
                bl_b = bl + 1  # Bottom-left (bottom surface)
                br_b = br + 1  # Bottom-right (bottom surface)

                faces.append([tl_b, tr_b, bl_b])
                faces.append([tr_b, br_b, bl_b])

        # Add side walls
        self._add_side_walls(vertices, faces, width, height)

        vertices = np.array(vertices)
        faces = np.array(faces)

        return trimesh.Trimesh(vertices=vertices, faces=faces)

    def _edge_extrusion_to_mesh(self, image: Image.Image, settings: Dict[str, Any]) -> trimesh.Trimesh:
        """Convert PNG to 3D mesh using edge detection and extrusion"""
        logger.info("üîç Generating edge-extruded mesh...")

        # Convert to grayscale
        grayscale = image.convert('L')

        # Apply edge detection
        edge_threshold = settings.get('edge_threshold', 50)
        edges = grayscale.filter(ImageFilter.FIND_EDGES)

        # Enhance edges
        enhancer = ImageEnhance.Contrast(edges)
        edges = enhancer.enhance(2.0)

        # Convert to binary edge map
        edge_array = np.array(edges)
        edge_binary = (edge_array > edge_threshold).astype(np.uint8)

        # Apply morphological operations to clean edges
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        edge_binary = cv2.morphologyEx(edge_binary, cv2.MORPH_CLOSE, kernel)

        if settings.get('smooth_edges', True):
            edge_binary = cv2.GaussianBlur(edge_binary.astype(np.float32), (3, 3), 0.5)
            edge_binary = (edge_binary > 0.5).astype(np.uint8)

        # Create heightmap from edges
        height_data = edge_binary.astype(np.float32)
        extrude_height = settings.get('extrude_height', 3.0)
        base_thickness = settings.get('wall_thickness', 1.0)

        height_data = height_data * extrude_height + base_thickness

        return self._array_to_mesh(height_data)

    def _lithophane_to_mesh(self, image: Image.Image, settings: Dict[str, Any]) -> trimesh.Trimesh:
        """Convert PNG to lithophane mesh for backlighting"""
        logger.info("üí° Generating lithophane mesh...")

        # Convert to grayscale
        grayscale = image.convert('L')
        width, height = grayscale.size

        # Convert to numpy array
        luminance = np.array(grayscale, dtype=np.float32) / 255.0

        # Invert luminance for lithophane (bright = thin, dark = thick)
        if settings.get('invert', True):
            luminance = 1.0 - luminance

        # Scale thickness
        min_thickness = settings.get('min_thickness', 0.4)
        max_thickness = settings.get('max_thickness', 2.0)
        thickness_range = max_thickness - min_thickness

        thickness_data = luminance * thickness_range + min_thickness

        return self._array_to_mesh(thickness_data)

    def _array_to_mesh(self, height_array: np.ndarray) -> trimesh.Trimesh:
        """Convert 2D height array to 3D mesh"""
        height, width = height_array.shape

        # Generate vertices
        vertices = []
        for y in range(height):
            for x in range(width):
                # Top surface
                vertices.append([x, y, height_array[y, x]])
                # Bottom surface
                vertices.append([x, y, 0])

        # Generate faces
        faces = []
        for y in range(height - 1):
            for x in range(width - 1):
                # Quad indices
                tl = (y * width + x) * 2
                tr = (y * width + x + 1) * 2
                bl = ((y + 1) * width + x) * 2
                br = ((y + 1) * width + x + 1) * 2

                # Top surface
                faces.append([tl, bl, tr])
                faces.append([tr, bl, br])

                # Bottom surface
                faces.append([tl + 1, tr + 1, bl + 1])
                faces.append([tr + 1, br + 1, bl + 1])

        # Add side walls
        self._add_side_walls(vertices, faces, width, height)

        return trimesh.Trimesh(vertices=np.array(vertices), faces=np.array(faces))

    def _add_side_walls(self, vertices: list, faces: list, width: int, height: int):
        """Add side walls to create a closed mesh"""
        # Side walls implementation
        # Left wall
        for y in range(height - 1):
            tl = (y * width) * 2          # Top-left top
            bl = ((y + 1) * width) * 2    # Bottom-left top
            tl_b = tl + 1                 # Top-left bottom
            bl_b = bl + 1                 # Bottom-left bottom

            faces.append([tl, tl_b, bl])
            faces.append([bl, tl_b, bl_b])

        # Right wall
        for y in range(height - 1):
            tr = (y * width + width - 1) * 2      # Top-right top
            br = ((y + 1) * width + width - 1) * 2 # Bottom-right top
            tr_b = tr + 1                          # Top-right bottom
            br_b = br + 1                          # Bottom-right bottom

            faces.append([tr, br, tr_b])
            faces.append([br, br_b, tr_b])

        # Top wall
        for x in range(width - 1):
            tl = x * 2                    # Top-left top
            tr = (x + 1) * 2             # Top-right top
            tl_b = tl + 1                # Top-left bottom
            tr_b = tr + 1                # Top-right bottom

            faces.append([tl, tr, tl_b])
            faces.append([tr, tr_b, tl_b])

        # Bottom wall
        for x in range(width - 1):
            bl = ((height - 1) * width + x) * 2      # Bottom-left top
            br = ((height - 1) * width + x + 1) * 2  # Bottom-right top
            bl_b = bl + 1                             # Bottom-left bottom
            br_b = br + 1                             # Bottom-right bottom

            faces.append([bl, bl_b, br])
            faces.append([br, bl_b, br_b])

    def _clean_mesh(self, mesh: trimesh.Trimesh) -> trimesh.Trimesh:
        """Clean and validate mesh for 3D printing"""
        logger.info("üßπ Cleaning mesh for 3D printing...")

        try:
            # Remove duplicate faces (updated method)
            unique_faces = mesh.unique_faces()
            mesh.update_faces(unique_faces)
        except AttributeError:
            # Fallback for older trimesh versions
            try:
                mesh.remove_duplicate_faces()
            except:
                pass

        try:
            # Remove duplicate vertices (updated method)
            mesh.merge_vertices()
        except AttributeError:
            # Fallback for older trimesh versions
            try:
                mesh.remove_duplicated_vertices()
            except:
                pass

        try:
            # Fix normals
            mesh.fix_normals()
        except:
            pass

        try:
            # Fill holes if any
            mesh.fill_holes()
        except:
            pass

        # Ensure mesh is watertight
        try:
            if not mesh.is_watertight:
                logger.warning(" Mesh is not watertight, attempting repair...")
                mesh = mesh.convex_hull
        except:
            logger.warning(" Could not check if mesh is watertight")

        # Validate volume
        try:
            if mesh.volume <= 0:
                logger.warning(" Mesh has invalid volume")
        except:
            logger.warning(" Could not validate mesh volume")

        return mesh

    def analyze_png_for_conversion(self, png_path: Union[str, Path, bytes]) -> Dict[str, Any]:
        """Analyze PNG image and recommend conversion settings"""
        try:
            if isinstance(png_path, bytes):
                image = Image.open(io.BytesIO(png_path))
            else:
                image = Image.open(png_path)

            width, height = image.size
            has_alpha = image.mode in ('RGBA', 'LA')

            # Analyze image content
            grayscale = image.convert('L')
            gray_array = np.array(grayscale)

            # Calculate statistics
            mean_brightness = np.mean(gray_array)
            contrast = np.std(gray_array)

            # Edge detection analysis
            edges = cv2.Canny(gray_array, 50, 150)
            edge_density = np.sum(edges > 0) / (width * height)

            # Recommend method and settings
            recommendations = {
                'image_info': {
                    'width': width,
                    'height': height,
                    'has_transparency': has_alpha,
                    'mean_brightness': float(mean_brightness),
                    'contrast': float(contrast),
                    'edge_density': float(edge_density)
                },
                'recommended_method': None,
                'settings': {}
            }

            # Choose best method based on image characteristics
            if edge_density > 0.1:
                recommendations['recommended_method'] = 'edge_extrusion'
                recommendations['settings'] = {
                    'extrude_height': 3.0,
                    'edge_threshold': max(30, min(100, contrast * 0.5))
                }
            elif contrast > 100:
                recommendations['recommended_method'] = 'heightmap'
                recommendations['settings'] = {
                    'max_height': 5.0,
                    'smooth_iterations': 2 if contrast > 150 else 1
                }
            else:
                recommendations['recommended_method'] = 'lithophane'
                recommendations['settings'] = {
                    'thickness': 3.0,
                    'invert': True
                }

            return recommendations

        except Exception as e:
            logger.error(f"'ùå PNG analysis failed: {e}")
            return {}

# Example usage and testing functions
def test_png_to_stl():
    """Test the PNG to STL converter"""
    print("üß™ Testing PNG to STL Converter...")

    converter = TherionPNGToSTLConverter()

    # Create a test PNG
    test_image = Image.new('RGBA', (100, 100), (255, 255, 255, 0))

    # Draw a simple gradient circle
    from PIL import ImageDraw
    draw = ImageDraw.Draw(test_image)

    for radius in range(1, 40, 2):
        gray_value = int(255 * (1 - radius / 40))
        draw.ellipse([50-radius, 50-radius, 50+radius, 50+radius],
                    fill=(gray_value, gray_value, gray_value, 255))

    # Save test PNG
    test_png_path = "test_heightmap.png"
    test_image.save(test_png_path)

    # Test conversion
    success = converter.convert_png_to_stl(
        test_png_path,
        "test_output.stl",
        method='heightmap'
    )

    if success:
        print("'úÖ PNG to STL conversion successful!")
    else:
        print("'ùå PNG to STL conversion failed!")

    # Test analysis
    analysis = converter.analyze_png_for_conversion(test_png_path)
    print(f"üìä Analysis: {analysis}")

if __name__ == "__main__":
    test_png_to_stl()
