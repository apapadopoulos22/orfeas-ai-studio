"""
+==============================================================================â•—
| [WARRIOR] ORFEAS MATERIAL SYSTEM - PBR MATERIAL PROCESSOR [WARRIOR] |
| Professional Material & Lighting Metadata Management |
+==============================================================================

ORFEAS Material Processor - PBR Material & Lighting Management
Handles material properties, lighting configurations, and metadata export

Features:
- PBR material presets (metal, plastic, wood, glass, ceramic, rubber)
- HDR lighting environments (studio, outdoor, dramatic, night, warm)
- Material metadata generation
- Three.js compatible configuration export
- OBJ/MTL file generation with materials

Author: ORFEAS 3D WEB SPECIALIST
Date: October 15, 2025
"""

import json
import logging
from dataclasses import dataclass, asdict
from typing import Dict, Optional, Tuple
from pathlib import Path
from enum import Enum

logger = logging.getLogger(__name__)


class MaterialType(Enum):
    """PBR Material Types"""
    METAL = "metal"
    PLASTIC = "plastic"
    WOOD = "wood"
    GLASS = "glass"
    CERAMIC = "ceramic"
    RUBBER = "rubber"


class LightingEnvironment(Enum):
    """HDR Lighting Environment Presets"""
    STUDIO = "studio"
    OUTDOOR = "outdoor"
    DRAMATIC = "dramatic"
    NIGHT = "night"
    WARM = "warm"


@dataclass
class PBRMaterialProperties:
    """
    Physically Based Rendering Material Properties

    Based on metallic-roughness PBR workflow (glTF 2.0 standard)
    """
    material_type: str
    base_color: Tuple[float, float, float]  # RGB (0.0-1.0)
    metalness: float  # 0.0 = dielectric, 1.0 = metallic
    roughness: float  # 0.0 = smooth/glossy, 1.0 = rough/matte
    reflectivity: float  # Additional reflectivity control
    opacity: float = 1.0  # 0.0 = transparent, 1.0 = opaque
    emissive_color: Optional[Tuple[float, float, float]] = None
    emissive_intensity: float = 0.0
    normal_scale: float = 1.0

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON export"""
        return asdict(self)

    def to_three_js(self) -> Dict:
        """Convert to Three.js MeshStandardMaterial compatible format"""
        return {
            'color': self._rgb_to_hex(self.base_color),
            'metalness': self.metalness,
            'roughness': self.roughness,
            'reflectivity': self.reflectivity,
            'transparent': self.opacity < 1.0,
            'opacity': self.opacity,
            'emissive': self._rgb_to_hex(self.emissive_color) if self.emissive_color else 0x000000,
            'emissiveIntensity': self.emissive_intensity
        }

    @staticmethod
    def _rgb_to_hex(rgb: Tuple[float, float, float]) -> int:
        """Convert RGB (0-1) to hex color"""
        r = int(rgb[0] * 255)
        g = int(rgb[1] * 255)
        b = int(rgb[2] * 255)
        return (r << 16) + (g << 8) + b


@dataclass
class LightingConfiguration:
    """
    Lighting Environment Configuration

    Three-point lighting setup with ambient
    """
    environment_type: str
    ambient_intensity: float
    main_light_intensity: float
    main_light_position: Tuple[float, float, float]
    main_light_color: Tuple[float, float, float]
    fill_light_intensity: float
    fill_light_position: Tuple[float, float, float]
    back_light_intensity: float
    back_light_position: Tuple[float, float, float]
    background_color: Tuple[float, float, float]
    shadow_intensity: float = 0.5

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON export"""
        return asdict(self)

    def to_three_js(self) -> Dict:
        """Convert to Three.js compatible format"""
        return {
            'ambient': {
                'intensity': self.ambient_intensity,
                'color': self._rgb_to_hex(self.main_light_color)
            },
            'main': {
                'intensity': self.main_light_intensity,
                'position': self.main_light_position,
                'color': self._rgb_to_hex(self.main_light_color)
            },
            'fill': {
                'intensity': self.fill_light_intensity,
                'position': self.fill_light_position
            },
            'back': {
                'intensity': self.back_light_intensity,
                'position': self.back_light_position
            },
            'background': self._rgb_to_hex(self.background_color),
            'shadowIntensity': self.shadow_intensity
        }

    @staticmethod
    def _rgb_to_hex(rgb: Tuple[float, float, float]) -> int:
        """Convert RGB (0-1) to hex color"""
        r = int(rgb[0] * 255)
        g = int(rgb[1] * 255)
        b = int(rgb[2] * 255)
        return (r << 16) + (g << 8) + b


class MaterialProcessor:
    """Process and manage PBR materials and lighting"""

    def __init__(self):
        """Initialize material processor"""
        logger.info("[PREMIUM] MaterialProcessor initialized")

    def get_material_preset(self, material_type: str) -> PBRMaterialProperties:
        """
        Get PBR material preset by type

        Args:
            material_type: Material type name

        Returns:
            PBRMaterialProperties with preset values
        """
        presets = {
            MaterialType.METAL.value: PBRMaterialProperties(
                material_type="metal",
                base_color=(0.53, 0.53, 0.53),  # Gray metallic
                metalness=0.8,
                roughness=0.3,
                reflectivity=0.5
            ),
            MaterialType.PLASTIC.value: PBRMaterialProperties(
                material_type="plastic",
                base_color=(0.20, 0.60, 0.86),  # Blue plastic
                metalness=0.0,
                roughness=0.5,
                reflectivity=0.3
            ),
            MaterialType.WOOD.value: PBRMaterialProperties(
                material_type="wood",
                base_color=(0.55, 0.27, 0.07),  # Brown wood
                metalness=0.0,
                roughness=0.8,
                reflectivity=0.1
            ),
            MaterialType.GLASS.value: PBRMaterialProperties(
                material_type="glass",
                base_color=(1.0, 1.0, 1.0),  # Clear glass
                metalness=0.0,
                roughness=0.1,
                reflectivity=0.9,
                opacity=0.6
            ),
            MaterialType.CERAMIC.value: PBRMaterialProperties(
                material_type="ceramic",
                base_color=(0.96, 0.96, 0.86),  # Beige ceramic
                metalness=0.0,
                roughness=0.4,
                reflectivity=0.4
            ),
            MaterialType.RUBBER.value: PBRMaterialProperties(
                material_type="rubber",
                base_color=(0.17, 0.24, 0.31),  # Dark gray rubber
                metalness=0.0,
                roughness=0.9,
                reflectivity=0.1
            )
        }

        if material_type not in presets:
            logger.warning(f"Unknown material type: {material_type}, using metal")
            material_type = MaterialType.METAL.value

        return presets[material_type]

    def get_lighting_preset(self, environment_type: str) -> LightingConfiguration:
        """
        Get lighting configuration preset

        Args:
            environment_type: Lighting environment name

        Returns:
            LightingConfiguration with preset values
        """
        presets = {
            LightingEnvironment.STUDIO.value: LightingConfiguration(
                environment_type="studio",
                ambient_intensity=0.3,
                main_light_intensity=1.0,
                main_light_position=(5.0, 10.0, 5.0),
                main_light_color=(1.0, 1.0, 1.0),
                fill_light_intensity=0.3,
                fill_light_position=(-5.0, 5.0, -5.0),
                back_light_intensity=0.2,
                back_light_position=(0.0, 5.0, -10.0),
                background_color=(0.10, 0.10, 0.10),
                shadow_intensity=0.5
            ),
            LightingEnvironment.OUTDOOR.value: LightingConfiguration(
                environment_type="outdoor",
                ambient_intensity=0.5,
                main_light_intensity=1.5,
                main_light_position=(10.0, 15.0, 5.0),
                main_light_color=(1.0, 1.0, 0.93),  # Warm sunlight
                fill_light_intensity=0.4,
                fill_light_position=(-8.0, 8.0, -5.0),
                back_light_intensity=0.3,
                back_light_position=(0.0, 10.0, -15.0),
                background_color=(0.53, 0.81, 0.92),  # Sky blue
                shadow_intensity=0.6
            ),
            LightingEnvironment.DRAMATIC.value: LightingConfiguration(
                environment_type="dramatic",
                ambient_intensity=0.1,
                main_light_intensity=2.0,
                main_light_position=(10.0, 10.0, 2.0),
                main_light_color=(1.0, 1.0, 1.0),
                fill_light_intensity=0.1,
                fill_light_position=(-10.0, 5.0, -5.0),
                back_light_intensity=0.05,
                back_light_position=(0.0, 5.0, -10.0),
                background_color=(0.04, 0.04, 0.04),  # Almost black
                shadow_intensity=0.8
            ),
            LightingEnvironment.NIGHT.value: LightingConfiguration(
                environment_type="night",
                ambient_intensity=0.2,
                main_light_intensity=0.8,
                main_light_position=(3.0, 8.0, 3.0),
                main_light_color=(0.4, 0.6, 1.0),  # Cool blue moonlight
                fill_light_intensity=0.2,
                fill_light_position=(-5.0, 5.0, -5.0),
                back_light_intensity=0.3,
                back_light_position=(0.0, 5.0, -10.0),
                background_color=(0.06, 0.06, 0.12),  # Dark blue
                shadow_intensity=0.7
            ),
            LightingEnvironment.WARM.value: LightingConfiguration(
                environment_type="warm",
                ambient_intensity=0.4,
                main_light_intensity=1.2,
                main_light_position=(5.0, 10.0, 5.0),
                main_light_color=(1.0, 0.87, 0.67),  # Warm orange
                fill_light_intensity=0.4,
                fill_light_position=(-5.0, 5.0, -5.0),
                back_light_intensity=0.2,
                back_light_position=(0.0, 5.0, -10.0),
                background_color=(0.16, 0.12, 0.10),  # Dark warm brown
                shadow_intensity=0.4
            )
        }

        if environment_type not in presets:
            logger.warning(f"Unknown lighting type: {environment_type}, using studio")
            environment_type = LightingEnvironment.STUDIO.value

        return presets[environment_type]

    def create_material_metadata(
        self,
        material_type: str,
        lighting_environment: str,
        custom_properties: Optional[Dict] = None
    ) -> Dict:
        """
        Create complete material and lighting metadata

        Args:
            material_type: Material type name
            lighting_environment: Lighting environment name
            custom_properties: Optional custom material properties

        Returns:
            Complete metadata dictionary
        """
        material = self.get_material_preset(material_type)
        lighting = self.get_lighting_preset(lighting_environment)

        # Apply custom properties if provided
        if custom_properties:
            for key, value in custom_properties.items():
                if hasattr(material, key):
                    setattr(material, key, value)

        metadata = {
            'orfeas_version': '1.0.0',
            'material': material.to_dict(),
            'material_threejs': material.to_three_js(),
            'lighting': lighting.to_dict(),
            'lighting_threejs': lighting.to_three_js(),
            'timestamp': None  # Will be set by caller
        }

        return metadata

    def export_mtl_file(
        self,
        material_properties: PBRMaterialProperties,
        material_name: str = "orfeas_material"
    ) -> str:
        """
        Generate OBJ MTL (Material Template Library) file content

        Args:
            material_properties: PBR material properties
            material_name: Name for the material

        Returns:
            MTL file content as string
        """
        r, g, b = material_properties.base_color

        mtl_content = f"""# ORFEAS Material Studio - MTL Export
# Material: {material_name}
# Type: {material_properties.material_type}

newmtl {material_name}
Ka {r:.6f} {g:.6f} {b:.6f}  # Ambient color
Kd {r:.6f} {g:.6f} {b:.6f}  # Diffuse color
Ks {material_properties.reflectivity:.6f} {material_properties.reflectivity:.6f} {material_properties.reflectivity:.6f}  # Specular color
Ns {(1.0 - material_properties.roughness) * 1000:.2f}  # Specular exponent
d {material_properties.opacity:.6f}  # Opacity
illum 2  # Illumination model (2 = highlight on)

# PBR Properties (custom)
# metalness {material_properties.metalness:.6f}
# roughness {material_properties.roughness:.6f}
# reflectivity {material_properties.reflectivity:.6f}
"""

        return mtl_content

    def save_material_metadata(
        self,
        metadata: Dict,
        output_path: Path
    ) -> Path:
        """
        Save material metadata to JSON file

        Args:
            metadata: Material metadata dictionary
            output_path: Output file path

        Returns:
            Path to saved file
        """
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2)

            logger.info(f"[OK] Material metadata saved: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"[FAIL] Failed to save material metadata: {e}")
            raise


# Convenience functions for quick access
def get_material_preset(material_type: str) -> PBRMaterialProperties:
    """Get material preset (convenience function)"""
    processor = MaterialProcessor()
    return processor.get_material_preset(material_type)


def get_lighting_preset(environment_type: str) -> LightingConfiguration:
    """Get lighting preset (convenience function)"""
    processor = MaterialProcessor()
    return processor.get_lighting_preset(environment_type)


def create_complete_metadata(
    material_type: str,
    lighting_environment: str,
    custom_properties: Optional[Dict] = None
) -> Dict:
    """Create complete metadata (convenience function)"""
    processor = MaterialProcessor()
    return processor.create_material_metadata(
        material_type,
        lighting_environment,
        custom_properties
    )


if __name__ == "__main__":
    # Test material processor
    logging.basicConfig(level=logging.INFO)

    processor = MaterialProcessor()

    # Test all material presets
    print("\n" + "="*80)
    print("TESTING MATERIAL PRESETS")
    print("="*80)

    for material_type in MaterialType:
        material = processor.get_material_preset(material_type.value)
        print(f"\n{material_type.value.upper()}:")
        print(f"  Base Color: {material.base_color}")
        print(f"  Metalness: {material.metalness}")
        print(f"  Roughness: {material.roughness}")
        print(f"  Reflectivity: {material.reflectivity}")

    # Test all lighting presets
    print("\n" + "="*80)
    print("TESTING LIGHTING PRESETS")
    print("="*80)

    for env_type in LightingEnvironment:
        lighting = processor.get_lighting_preset(env_type.value)
        print(f"\n{env_type.value.upper()}:")
        print(f"  Ambient: {lighting.ambient_intensity}")
        print(f"  Main Light: {lighting.main_light_intensity}")
        print(f"  Background: {lighting.background_color}")

    # Test complete metadata generation
    print("\n" + "="*80)
    print("TESTING COMPLETE METADATA")
    print("="*80)

    metadata = processor.create_material_metadata("metal", "studio")
    print(f"\nGenerated metadata keys: {list(metadata.keys())}")
    print(f"Material type: {metadata['material']['material_type']}")
    print(f"Lighting type: {metadata['lighting']['environment_type']}")

    # Test MTL export
    print("\n" + "="*80)
    print("TESTING MTL EXPORT")
    print("="*80)

    material = processor.get_material_preset("metal")
    mtl_content = processor.export_mtl_file(material, "test_material")
    print(f"\nMTL Content:\n{mtl_content}")

    print("\n[OK] All tests passed!")
