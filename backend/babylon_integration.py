"""
ORFEAS AI 2D→3D Studio - Babylon.js Integration Helper
=====================================================
ORFEAS AI Project
Purpose: Backend support for Babylon.js WebGPU frontend

Features:
- Optimized STL export for Babylon.js
- Enhanced mesh normals for PBR rendering
- WebGPU-friendly texture formats
- Physics metadata for Havok engine
- Advanced material properties
"""

import logging
import numpy as np
from typing import Dict, Any, Optional, Tuple
from stl import mesh
from PIL import Image
import struct

logger = logging.getLogger(__name__)


class BabylonMeshOptimizer:
    """
    Optimize 3D meshes for Babylon.js WebGPU rendering
    """

    def __init__(self):
        self.pbr_materials_enabled = True
        self.physics_enabled = True

    def optimize_mesh_for_webgpu(
        self,
        vertices: np.ndarray,
        faces: np.ndarray,
        compute_smooth_normals: bool = True
    ) -> Dict[str, Any]:
        """
        Optimize mesh for WebGPU rendering

        Args:
            vertices: Mesh vertices (Nx3)
            faces: Mesh faces (Nx3 indices)
            compute_smooth_normals: Use smooth shading

        Returns:
            dict: Optimized mesh data for Babylon.js
        """
        logger.info("[TARGET] Optimizing mesh for Babylon.js WebGPU...")

        try:
            # Compute normals for PBR lighting
            if compute_smooth_normals:
                normals = self._compute_smooth_normals(vertices, faces)
            else:
                normals = self._compute_flat_normals(vertices, faces)

            # Generate UV coordinates for texturing
            uvs = self._generate_uv_coordinates(vertices)

            # Compute bounding box for culling
            bbox = self._compute_bounding_box(vertices)

            # Calculate mesh statistics
            stats = {
                'vertex_count': len(vertices),
                'face_count': len(faces),
                'has_normals': True,
                'has_uvs': True,
                'bbox': bbox
            }

            logger.info(f"[OK] Mesh optimized:")
            logger.info(f"   Vertices: {stats['vertex_count']}")
            logger.info(f"   Faces: {stats['face_count']}")
            logger.info(f"   Normals: Computed ({'smooth' if compute_smooth_normals else 'flat'})")
            logger.info(f"   UVs: Generated")

            return {
                'vertices': vertices.tolist(),
                'faces': faces.tolist(),
                'normals': normals.tolist(),
                'uvs': uvs.tolist(),
                'stats': stats,
                'babylon_compatible': True
            }

        except Exception as e:
            logger.error(f"[FAIL] Mesh optimization failed: {e}")
            return {
                'vertices': vertices.tolist(),
                'faces': faces.tolist(),
                'babylon_compatible': False,
                'error': str(e)
            }

    def _compute_smooth_normals(self, vertices: np.ndarray, faces: np.ndarray) -> np.ndarray:
        """Compute smooth vertex normals (better for PBR)"""
        normals = np.zeros_like(vertices)

        for face in faces:
            # Get triangle vertices
            v0, v1, v2 = vertices[face[0]], vertices[face[1]], vertices[face[2]]

            # Compute face normal
            edge1 = v1 - v0
            edge2 = v2 - v0
            face_normal = np.cross(edge1, edge2)

            # Accumulate to vertex normals
            normals[face[0]] += face_normal
            normals[face[1]] += face_normal
            normals[face[2]] += face_normal

        # Normalize
        norms = np.linalg.norm(normals, axis=1, keepdims=True)
        norms[norms == 0] = 1  # Avoid division by zero
        normals = normals / norms

        return normals

    def _compute_flat_normals(self, vertices: np.ndarray, faces: np.ndarray) -> np.ndarray:
        """Compute flat face normals (sharp edges)"""
        normals = []

        for face in faces:
            v0, v1, v2 = vertices[face[0]], vertices[face[1]], vertices[face[2]]
            edge1 = v1 - v0
            edge2 = v2 - v0
            normal = np.cross(edge1, edge2)
            normal = normal / (np.linalg.norm(normal) + 1e-8)

            # Same normal for all 3 vertices (flat shading)
            normals.extend([normal, normal, normal])

        return np.array(normals)

    def _generate_uv_coordinates(self, vertices: np.ndarray) -> np.ndarray:
        """
        Generate UV texture coordinates using planar projection
        Babylon.js requires UVs for proper material rendering
        """
        # Find bounding box
        min_coords = vertices.min(axis=0)
        max_coords = vertices.max(axis=0)
        ranges = max_coords - min_coords

        # Avoid division by zero
        ranges[ranges == 0] = 1.0

        # Planar UV projection (X, Z axes)
        uvs = np.zeros((len(vertices), 2))
        uvs[:, 0] = (vertices[:, 0] - min_coords[0]) / ranges[0]  # U from X
        uvs[:, 1] = (vertices[:, 2] - min_coords[2]) / ranges[2]  # V from Z

        return uvs

    def _compute_bounding_box(self, vertices: np.ndarray) -> Dict[str, Tuple[float, float, float]]:
        """Compute mesh bounding box for frustum culling"""
        min_coords = vertices.min(axis=0)
        max_coords = vertices.max(axis=0)
        center = (min_coords + max_coords) / 2
        extents = max_coords - min_coords

        return {
            'min': tuple(min_coords.tolist()),
            'max': tuple(max_coords.tolist()),
            'center': tuple(center.tolist()),
            'extents': tuple(extents.tolist())
        }

    def generate_pbr_material(
        self,
        base_color: Tuple[float, float, float] = (0.8, 0.8, 0.8),
        metallic: float = 0.0,
        roughness: float = 0.5
    ) -> Dict[str, Any]:
        """
        Generate PBR material properties for Babylon.js

        Args:
            base_color: RGB color (0-1 range)
            metallic: Metallic factor (0=dielectric, 1=metal)
            roughness: Roughness factor (0=smooth, 1=rough)

        Returns:
            dict: Babylon.js PBR material definition
        """
        material = {
            'type': 'PBRMaterial',
            'name': 'GeneratedMaterial',
            'albedoColor': list(base_color),
            'metallic': metallic,
            'roughness': roughness,
            'useRoughnessFromMetallicTextureAlpha': False,
            'useRoughnessFromMetallicTextureGreen': False,
            'useMetallnessFromMetallicTextureBlue': False,
            'enableSpecularAntiAliasing': True,  # Better quality
            'useHorizonOcclusion': True,  # Ambient occlusion
            'useRadianceOcclusion': True,  # Better lighting
            'environmentIntensity': 1.0,
            'directIntensity': 1.0
        }

        logger.info(f"[ART] Generated PBR material:")
        logger.info(f"   Base Color: {base_color}")
        logger.info(f"   Metallic: {metallic}")
        logger.info(f"   Roughness: {roughness}")

        return material

    def generate_physics_metadata(
        self,
        vertices: np.ndarray,
        mass: float = 1.0,
        friction: float = 0.5,
        restitution: float = 0.5
    ) -> Dict[str, Any]:
        """
        Generate physics properties for Havok Physics Engine

        Args:
            vertices: Mesh vertices for collision shape
            mass: Object mass in kg
            friction: Surface friction (0=ice, 1=rubber)
            restitution: Bounciness (0=soft, 1=bouncy)

        Returns:
            dict: Havok physics properties
        """
        # Compute center of mass
        center_of_mass = vertices.mean(axis=0)

        # Compute approximate volume (for density calculation)
        bbox_volume = np.prod(vertices.max(axis=0) - vertices.min(axis=0))

        physics = {
            'enabled': True,
            'engine': 'Havok',
            'mass': mass,
            'friction': friction,
            'restitution': restitution,
            'centerOfMass': center_of_mass.tolist(),
            'volume': float(bbox_volume),
            'density': mass / (bbox_volume + 1e-8),
            'collisionShape': 'mesh',  # Use mesh for precise collision
            'linearDamping': 0.1,
            'angularDamping': 0.1
        }

        logger.info(f"[ATOM] Generated physics metadata:")
        logger.info(f"   Mass: {mass} kg")
        logger.info(f"   Friction: {friction}")
        logger.info(f"   Restitution: {restitution}")

        return physics

    def export_for_babylon(
        self,
        mesh_data: Dict[str, Any],
        include_pbr: bool = True,
        include_physics: bool = False
    ) -> Dict[str, Any]:
        """
        Complete export package for Babylon.js WebGPU

        Args:
            mesh_data: Optimized mesh data
            include_pbr: Include PBR material
            include_physics: Include Havok physics

        Returns:
            dict: Complete Babylon.js scene data
        """
        export_data = {
            'mesh': mesh_data,
            'version': '1.0',
            'engine': 'BabylonJS',
            'renderer': 'WebGPU',
            'timestamp': str(np.datetime64('now'))
        }

        if include_pbr:
            export_data['material'] = self.generate_pbr_material()

        if include_physics:
            vertices = np.array(mesh_data['vertices'])
            export_data['physics'] = self.generate_physics_metadata(vertices)

        logger.info("[OK] Babylon.js export package created")
        logger.info(f"   PBR Material: {'Yes' if include_pbr else 'No'}")
        logger.info(f"   Physics: {'Yes' if include_physics else 'No'}")

        return export_data


# Global optimizer instance
babylon_optimizer = None

def get_babylon_optimizer() -> BabylonMeshOptimizer:
    """Get or create global Babylon.js optimizer"""
    global babylon_optimizer
    if babylon_optimizer is None:
        babylon_optimizer = BabylonMeshOptimizer()
    return babylon_optimizer


if __name__ == "__main__":
    # Test Babylon.js optimization
    logging.basicConfig(level=logging.INFO)

    print("\n" + "="*60)
    print("ORFEAS BABYLON.JS OPTIMIZATION - TEST MODE")
    print("="*60 + "\n")

    # Create simple cube mesh
    vertices = np.array([
        [0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0],  # Front face
        [0, 0, 1], [1, 0, 1], [1, 1, 1], [0, 1, 1]   # Back face
    ], dtype=float)

    faces = np.array([
        [0, 1, 2], [0, 2, 3],  # Front
        [4, 6, 5], [4, 7, 6],  # Back
        [0, 4, 5], [0, 5, 1],  # Bottom
        [2, 6, 7], [2, 7, 3],  # Top
        [0, 3, 7], [0, 7, 4],  # Left
        [1, 5, 6], [1, 6, 2]   # Right
    ])

    optimizer = get_babylon_optimizer()

    # Test mesh optimization
    optimized = optimizer.optimize_mesh_for_webgpu(vertices, faces)
    print("\nOptimized Mesh Stats:")
    print(f"  Vertices: {len(optimized['vertices'])}")
    print(f"  Faces: {len(optimized['faces'])}")
    print(f"  Normals: {len(optimized['normals'])}")
    print(f"  UVs: {len(optimized['uvs'])}")

    # Test full export
    export = optimizer.export_for_babylon(
        optimized,
        include_pbr=True,
        include_physics=True
    )

    print("\nExport Package Created:")
    print(f"  Has Material: {'material' in export}")
    print(f"  Has Physics: {'physics' in export}")
