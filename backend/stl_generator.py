"""
STL Generator Module - Creates valid binary STL files with actual 3D geometry

This module provides functions to generate proper STL files that can be previewed
in 3D viewers, unlike the test mode placeholders.
"""

import struct
import math
import logging
from pathlib import Path
from typing import Tuple, List, Union

logger = logging.getLogger(__name__)


def create_cube_stl(output_path: Union[str, Path], size: float = 10.0) -> bool:
    """
    Create a binary STL file containing a cube.

    Args:
        output_path: Path to save the STL file
        size: Size of the cube (default 10 mm)

    Returns:
        True if successful, False otherwise
    """
    try:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Define cube vertices
        vertices = [
            (0, 0, 0), (size, 0, 0), (size, size, 0), (0, size, 0),  # Bottom face
            (0, 0, size), (size, 0, size), (size, size, size), (0, size, size)  # Top face
        ]

        # Define triangles (each face as 2 triangles)
        triangles = [
            # Bottom face (z=0)
            (0, 1, 2), (0, 2, 3),
            # Top face (z=size)
            (4, 6, 5), (4, 7, 6),
            # Front face (y=0)
            (0, 5, 1), (0, 4, 5),
            # Back face (y=size)
            (2, 7, 3), (2, 6, 7),
            # Left face (x=0)
            (0, 3, 7), (0, 7, 4),
            # Right face (x=size)
            (1, 5, 6), (1, 6, 2),
        ]

        return write_binary_stl(output_path, vertices, triangles)

    except Exception as e:
        logger.error(f"Failed to create cube STL: {e}")
        return False


def create_sphere_stl(output_path: Union[str, Path], radius: float = 5.0, subdivisions: int = 4) -> bool:
    """
    Create a binary STL file containing a sphere (icosphere).

    Args:
        output_path: Path to save the STL file
        radius: Radius of the sphere (default 5 mm)
        subdivisions: Number of subdivision levels (default 4)

    Returns:
        True if successful, False otherwise
    """
    try:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        vertices, triangles = create_icosphere(radius, subdivisions)
        return write_binary_stl(output_path, vertices, triangles)

    except Exception as e:
        logger.error(f"Failed to create sphere STL: {e}")
        return False


def create_icosphere(radius: float = 5.0, subdivisions: int = 4) -> Tuple[List[Tuple[float, float, float]], List[Tuple[int, int, int]]]:
    """Create icosphere vertices and triangles."""
    phi = (1 + math.sqrt(5)) / 2

    # Initial icosahedron vertices
    vertices = [
        (-1, phi, 0), (1, phi, 0), (-1, -phi, 0), (1, -phi, 0),
        (0, -1, phi), (0, 1, phi), (0, -1, -phi), (0, 1, -phi),
        (phi, 0, -1), (phi, 0, 1), (-phi, 0, -1), (-phi, 0, 1),
    ]

    # Normalize and scale
    vertices = [tuple(v / math.sqrt(v[0]**2 + v[1]**2 + v[2]**2) * radius for v in vertex) for vertex in vertices]

    # Initial triangles
    triangles = [
        (0, 11, 5), (0, 5, 1), (0, 1, 7), (0, 7, 10), (0, 10, 11),
        (1, 5, 9), (5, 11, 4), (11, 10, 2), (10, 7, 6), (7, 1, 8),
        (3, 9, 4), (3, 4, 2), (3, 2, 6), (3, 6, 8), (3, 8, 9),
        (4, 9, 5), (2, 4, 11), (6, 2, 10), (8, 6, 7), (9, 8, 1),
    ]

    # Subdivide
    for _ in range(subdivisions):
        triangles, vertices = subdivide_triangles(triangles, vertices, radius)

    return vertices, triangles


def subdivide_triangles(triangles: List[Tuple[int, int, int]], vertices: List[Tuple[float, float, float]], radius: float) -> Tuple[List[Tuple[int, int, int]], List[Tuple[float, float, float]]]:
    """Subdivide triangles for smoother sphere."""
    edge_map = {}
    new_triangles = []

    def get_midpoint(v1_idx: int, v2_idx: int) -> int:
        edge = tuple(sorted([v1_idx, v2_idx]))
        if edge not in edge_map:
            v1 = vertices[v1_idx]
            v2 = vertices[v2_idx]
            midpoint = ((v1[0] + v2[0]) / 2, (v1[1] + v2[1]) / 2, (v1[2] + v2[2]) / 2)
            # Normalize to sphere surface
            length = math.sqrt(midpoint[0]**2 + midpoint[1]**2 + midpoint[2]**2)
            midpoint = tuple(v / length * radius for v in midpoint)
            edge_map[edge] = len(vertices)
            vertices.append(midpoint)
        return edge_map[edge]

    for v1, v2, v3 in triangles:
        m12 = get_midpoint(v1, v2)
        m23 = get_midpoint(v2, v3)
        m31 = get_midpoint(v3, v1)
        new_triangles.extend([(v1, m12, m31), (m12, v2, m23), (m31, m23, v3), (m12, m23, m31)])

    return new_triangles, vertices


def create_cylinder_stl(output_path: Union[str, Path], radius: float = 5.0, height: float = 10.0, segments: int = 16) -> bool:
    """
    Create a binary STL file containing a cylinder.

    Args:
        output_path: Path to save the STL file
        radius: Radius of the cylinder (default 5 mm)
        height: Height of the cylinder (default 10 mm)
        segments: Number of segments around the circumference (default 16)

    Returns:
        True if successful, False otherwise
    """
    try:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        vertices = []
        triangles = []

        # Bottom and top circle vertices
        for i in range(segments):
            angle = 2 * math.pi * i / segments
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            vertices.append((x, y, 0))  # Bottom
            vertices.append((x, y, height))  # Top

        # Add center vertices for caps
        bottom_center = len(vertices)
        vertices.append((0, 0, 0))
        top_center = len(vertices)
        vertices.append((0, 0, height))

        # Side triangles
        for i in range(segments):
            curr = i * 2
            next_idx = ((i + 1) % segments) * 2
            triangles.append((curr, next_idx, curr + 1))
            triangles.append((next_idx, next_idx + 1, curr + 1))

        # Bottom cap
        for i in range(segments):
            curr = i * 2
            next_idx = ((i + 1) % segments) * 2
            triangles.append((bottom_center, next_idx, curr))

        # Top cap
        for i in range(segments):
            curr = i * 2 + 1
            next_idx = ((i + 1) % segments) * 2 + 1
            triangles.append((top_center, curr, next_idx))

        return write_binary_stl(output_path, vertices, triangles)

    except Exception as e:
        logger.error(f"Failed to create cylinder STL: {e}")
        return False


def write_binary_stl(output_path: Path, vertices: List[Tuple[float, float, float]], triangles: List[Tuple[int, int, int]]) -> bool:
    """
    Write a binary STL file.

    Args:
        output_path: Path to save the STL file
        vertices: List of (x, y, z) vertices
        triangles: List of (v1, v2, v3) triangle vertex indices

    Returns:
        True if successful, False otherwise
    """
    try:
        with open(output_path, 'wb') as f:
            # Write 80-byte header
            header = b'ORFEAS Generated STL Model - Valid 3D Geometry'
            header = header + b'\x00' * (80 - len(header))
            f.write(header[:80])

            # Write number of triangles
            num_triangles = len(triangles)
            f.write(struct.pack('<I', num_triangles))

            # Write each triangle
            for v1_idx, v2_idx, v3_idx in triangles:
                v1 = vertices[v1_idx]
                v2 = vertices[v2_idx]
                v3 = vertices[v3_idx]

                # Calculate normal vector
                normal = calculate_normal(v1, v2, v3)

                # Write normal
                f.write(struct.pack('<fff', *normal))

                # Write vertices
                f.write(struct.pack('<fff', *v1))
                f.write(struct.pack('<fff', *v2))
                f.write(struct.pack('<fff', *v3))

                # Write attribute byte count (unused, but required)
                f.write(struct.pack('<H', 0))

        logger.info(f"STL file created: {output_path} ({len(triangles)} triangles)")
        return True

    except Exception as e:
        logger.error(f"Failed to write STL file: {e}")
        return False


def calculate_normal(v1: Tuple[float, float, float], v2: Tuple[float, float, float], v3: Tuple[float, float, float]) -> Tuple[float, float, float]:
    """Calculate normal vector for a triangle using cross product."""
    # Vectors from v1 to v2 and v1 to v3
    a = (v2[0] - v1[0], v2[1] - v1[1], v2[2] - v1[2])
    b = (v3[0] - v1[0], v3[1] - v1[1], v3[2] - v1[2])

    # Cross product
    normal = (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0]
    )

    # Normalize
    length = math.sqrt(normal[0]**2 + normal[1]**2 + normal[2]**2)
    if length > 0:
        normal = (normal[0] / length, normal[1] / length, normal[2] / length)

    return normal
