"""
+==============================================================================â•—
| [WARRIOR] ORFEAS PHASE 2.4 - ADVANCED CAMERA SYSTEM [WARRIOR]                           |
| Camera Position Management & Animation Processor                            |
+==============================================================================

ORFEAS Phase 2.4 - Advanced Camera System Backend
Professional camera positioning, animation paths, and preset management

Author: ORFEAS 3D WEB SPECIALIST
Date: October 15, 2025
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Tuple, Optional
import logging
import json
import math
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class CameraPreset(Enum):
    """Standard camera position presets"""
    FRONT = "front"
    BACK = "back"
    LEFT = "left"
    RIGHT = "right"
    TOP = "top"
    BOTTOM = "bottom"
    ANGLE_3_4 = "angle1"
    ISOMETRIC = "angle2"


class ProjectionMode(Enum):
    """Camera projection types"""
    PERSPECTIVE = "perspective"
    ORTHOGRAPHIC = "orthographic"


class AnimationType(Enum):
    """Camera animation types"""
    TURNTABLE = "turntable"
    ORBITAL = "orbital"
    PATH = "path"
    NONE = "none"


@dataclass
class CameraPosition:
    """Camera position and orientation"""
    position: Tuple[float, float, float]  # (x, y, z) camera location
    target: Tuple[float, float, float]  # (x, y, z) look-at point
    fov: float = 50.0  # Field of view in degrees (perspective only)
    projection: str = "perspective"  # "perspective" or "orthographic"

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON export"""
        return {
            "position": {
                "x": self.position[0],
                "y": self.position[1],
                "z": self.position[2]
            },
            "target": {
                "x": self.target[0],
                "y": self.target[1],
                "z": self.target[2]
            },
            "fov": self.fov,
            "projection": self.projection
        }

    def to_three_js(self) -> Dict:
        """Convert to Three.js compatible format"""
        return {
            "position": [self.position[0], self.position[1], self.position[2]],
            "target": [self.target[0], self.target[1], self.target[2]],
            "fov": self.fov,
            "projectionMode": self.projection
        }


@dataclass
class CameraAnimationConfig:
    """Camera animation configuration"""
    animation_type: str  # "turntable", "orbital", "path"
    duration: float = 10.0  # Animation duration in seconds
    speed: float = 1.0  # Speed multiplier
    loop: bool = True  # Loop animation
    ease: str = "linear"  # Easing function: "linear", "ease-in", "ease-out"

    # Turntable specific
    rotation_axis: str = "y"  # "x", "y", or "z"

    # Orbital specific
    orbital_radius: float = 10.0
    orbital_height_variation: float = 3.0

    # Path specific
    path_points: List[Tuple[float, float, float]] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "animation_type": self.animation_type,
            "duration": self.duration,
            "speed": self.speed,
            "loop": self.loop,
            "ease": self.ease,
            "rotation_axis": self.rotation_axis,
            "orbital_radius": self.orbital_radius,
            "orbital_height_variation": self.orbital_height_variation,
            "path_points": self.path_points
        }


class CameraProcessor:
    """
    Process and manage camera positions, animations, and presets

    Features:
    - Standard camera presets (8 views)
    - Custom camera positioning
    - Camera animation paths (turntable, orbital, custom)
    - Preset save/load
    - Perspective/Orthographic switching
    - FOV adjustment
    - Distance control
    """

    def __init__(self, base_output_dir: Optional[Path] = None):
        """
        Initialize camera processor

        Args:
            base_output_dir: Base directory for saving camera presets
        """
        self.base_output_dir = base_output_dir or Path("./outputs")
        self.presets_dir = self.base_output_dir / "camera_presets"
        self.presets_dir.mkdir(parents=True, exist_ok=True)

        logger.info("[IMAGE] CameraProcessor initialized")
        logger.info(f"   Presets directory: {self.presets_dir}")

    def get_camera_preset(self, preset_name: str, distance: float = 10.0) -> CameraPosition:
        """
        Get standard camera preset position

        Args:
            preset_name: Preset name (front, back, left, right, top, bottom, angle1, angle2)
            distance: Distance from origin

        Returns:
            CameraPosition with preset configuration
        """
        preset_positions = {
            "front": (0, 0, distance),
            "back": (0, 0, -distance),
            "left": (-distance, 0, 0),
            "right": (distance, 0, 0),
            "top": (0, distance, 0),
            "bottom": (0, -distance, 0),
            "angle1": (distance * 0.7, distance * 0.5, distance * 0.7),  # 3/4 view
            "angle2": (distance * 0.577, distance * 0.577, distance * 0.577)  # Isometric
        }

        position = preset_positions.get(preset_name, (0, 0, distance))

        return CameraPosition(
            position=position,
            target=(0, 0, 0),
            fov=50.0,
            projection="perspective"
        )

    def create_custom_position(
        self,
        position: Tuple[float, float, float],
        target: Tuple[float, float, float] = (0, 0, 0),
        fov: float = 50.0,
        projection: str = "perspective"
    ) -> CameraPosition:
        """
        Create custom camera position

        Args:
            position: Camera position (x, y, z)
            target: Look-at point (x, y, z)
            fov: Field of view in degrees
            projection: "perspective" or "orthographic"

        Returns:
            CameraPosition with custom configuration
        """
        return CameraPosition(
            position=position,
            target=target,
            fov=fov,
            projection=projection
        )

    def generate_turntable_animation(
        self,
        distance: float = 10.0,
        height: float = 5.0,
        duration: float = 10.0,
        speed: float = 1.0,
        axis: str = "y"
    ) -> CameraAnimationConfig:
        """
        Generate turntable (360° rotation) animation

        Args:
            distance: Distance from center
            height: Camera height
            duration: Animation duration in seconds
            speed: Speed multiplier
            axis: Rotation axis ("x", "y", "z")

        Returns:
            CameraAnimationConfig for turntable
        """
        return CameraAnimationConfig(
            animation_type="turntable",
            duration=duration,
            speed=speed,
            loop=True,
            ease="linear",
            rotation_axis=axis,
            orbital_radius=distance
        )

    def generate_orbital_animation(
        self,
        radius: float = 10.0,
        height_variation: float = 3.0,
        duration: float = 15.0,
        speed: float = 1.0
    ) -> CameraAnimationConfig:
        """
        Generate orbital path animation (rotating + height changes)

        Args:
            radius: Orbital radius
            height_variation: Vertical movement range
            duration: Animation duration in seconds
            speed: Speed multiplier

        Returns:
            CameraAnimationConfig for orbital path
        """
        return CameraAnimationConfig(
            animation_type="orbital",
            duration=duration,
            speed=speed,
            loop=True,
            ease="ease-in-out",
            orbital_radius=radius,
            orbital_height_variation=height_variation
        )

    def generate_path_animation(
        self,
        path_points: List[Tuple[float, float, float]],
        duration: float = 20.0,
        speed: float = 1.0,
        loop: bool = True
    ) -> CameraAnimationConfig:
        """
        Generate custom path animation through multiple points

        Args:
            path_points: List of (x, y, z) positions for camera path
            duration: Animation duration in seconds
            speed: Speed multiplier
            loop: Loop animation

        Returns:
            CameraAnimationConfig for custom path
        """
        return CameraAnimationConfig(
            animation_type="path",
            duration=duration,
            speed=speed,
            loop=loop,
            ease="ease-in-out",
            path_points=path_points
        )

    def calculate_look_at(
        self,
        position: Tuple[float, float, float],
        target: Tuple[float, float, float]
    ) -> Dict[str, float]:
        """
        Calculate look-at angles from camera position to target

        Args:
            position: Camera position (x, y, z)
            target: Target position (x, y, z)

        Returns:
            Dictionary with rotation angles (radians)
        """
        dx = target[0] - position[0]
        dy = target[1] - position[1]
        dz = target[2] - position[2]

        distance = math.sqrt(dx*dx + dy*dy + dz*dz)

        # Spherical coordinates
        theta = math.atan2(dx, dz)  # Horizontal angle
        phi = math.asin(dy / distance) if distance > 0 else 0  # Vertical angle

        return {
            "theta": theta,
            "phi": phi,
            "distance": distance
        }

    def save_camera_preset(
        self,
        preset_name: str,
        camera_position: CameraPosition,
        description: str = ""
    ) -> str:
        """
        Save camera preset to file

        Args:
            preset_name: Name for the preset
            camera_position: CameraPosition to save
            description: Optional description

        Returns:
            Path to saved preset file
        """
        preset_data = {
            "name": preset_name,
            "description": description,
            "timestamp": datetime.now().isoformat(),
            "camera": camera_position.to_dict()
        }

        preset_file = self.presets_dir / f"{preset_name}.json"
        with open(preset_file, 'w') as f:
            json.dump(preset_data, f, indent=2)

        logger.info(f" Camera preset saved: {preset_name}")
        return str(preset_file)

    def load_camera_preset(self, preset_name: str) -> Optional[CameraPosition]:
        """
        Load camera preset from file

        Args:
            preset_name: Name of preset to load

        Returns:
            CameraPosition if found, None otherwise
        """
        preset_file = self.presets_dir / f"{preset_name}.json"

        if not preset_file.exists():
            logger.warning(f"[WARN] Preset not found: {preset_name}")
            return None

        with open(preset_file, 'r') as f:
            preset_data = json.load(f)

        camera_data = preset_data['camera']

        return CameraPosition(
            position=(
                camera_data['position']['x'],
                camera_data['position']['y'],
                camera_data['position']['z']
            ),
            target=(
                camera_data['target']['x'],
                camera_data['target']['y'],
                camera_data['target']['z']
            ),
            fov=camera_data.get('fov', 50.0),
            projection=camera_data.get('projection', 'perspective')
        )

    def list_saved_presets(self) -> List[Dict]:
        """
        List all saved camera presets

        Returns:
            List of preset metadata dictionaries
        """
        presets = []

        for preset_file in self.presets_dir.glob("*.json"):
            try:
                with open(preset_file, 'r') as f:
                    preset_data = json.load(f)
                    presets.append({
                        "name": preset_data['name'],
                        "description": preset_data.get('description', ''),
                        "timestamp": preset_data.get('timestamp', ''),
                        "file": str(preset_file)
                    })
            except Exception as e:
                logger.warning(f"[WARN] Failed to load preset {preset_file}: {e}")

        return presets

    def create_multi_view_sequence(
        self,
        distance: float = 10.0,
        include_diagonals: bool = True
    ) -> List[CameraPosition]:
        """
        Create sequence of camera positions for multi-view rendering

        Args:
            distance: Distance from origin
            include_diagonals: Include 3/4 and isometric views

        Returns:
            List of CameraPosition objects
        """
        views = ["front", "back", "left", "right", "top", "bottom"]

        if include_diagonals:
            views.extend(["angle1", "angle2"])

        return [self.get_camera_preset(view, distance) for view in views]

    def export_camera_metadata(
        self,
        camera_position: CameraPosition,
        animation_config: Optional[CameraAnimationConfig] = None,
        save_to_file: bool = False,
        filename: str = "camera_metadata.json"
    ) -> Dict:
        """
        Export complete camera metadata

        Args:
            camera_position: CameraPosition to export
            animation_config: Optional animation configuration
            save_to_file: Save to JSON file
            filename: Output filename if saving

        Returns:
            Complete camera metadata dictionary
        """
        metadata = {
            "orfeas_version": "1.0.0",
            "camera_position": camera_position.to_dict(),
            "camera_threejs": camera_position.to_three_js(),
            "timestamp": datetime.now().isoformat()
        }

        if animation_config:
            metadata["animation"] = animation_config.to_dict()

        if save_to_file:
            output_file = self.base_output_dir / filename
            with open(output_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            logger.info(f" Camera metadata saved: {output_file}")
            metadata["saved_file"] = str(output_file)

        return metadata


# Convenience functions for direct import
def get_camera_preset(preset_name: str, distance: float = 10.0) -> CameraPosition:
    """Get standard camera preset"""
    processor = CameraProcessor()
    return processor.get_camera_preset(preset_name, distance)


def create_turntable_animation(
    distance: float = 10.0,
    height: float = 5.0,
    duration: float = 10.0
) -> CameraAnimationConfig:
    """Create turntable animation"""
    processor = CameraProcessor()
    return processor.generate_turntable_animation(distance, height, duration)


def create_orbital_animation(
    radius: float = 10.0,
    height_variation: float = 3.0,
    duration: float = 15.0
) -> CameraAnimationConfig:
    """Create orbital animation"""
    processor = CameraProcessor()
    return processor.generate_orbital_animation(radius, height_variation, duration)


if __name__ == "__main__":
    # Test camera processor
    logging.basicConfig(level=logging.INFO)

    processor = CameraProcessor()

    # Test presets
    print("\n[IMAGE] Testing Camera Presets:")
    for preset in ["front", "back", "angle1", "angle2"]:
        pos = processor.get_camera_preset(preset)
        print(f"  {preset}: {pos.position}")

    # Test turntable animation
    print("\n Testing Turntable Animation:")
    turntable = processor.generate_turntable_animation()
    print(f"  Duration: {turntable.duration}s")
    print(f"  Radius: {turntable.orbital_radius}")

    # Test custom position
    print("\n[TARGET] Testing Custom Position:")
    custom = processor.create_custom_position((5, 10, 15), (0, 0, 0))
    print(f"  Position: {custom.position}")
    print(f"  Target: {custom.target}")

    print("\n[OK] Camera processor tests complete!")
