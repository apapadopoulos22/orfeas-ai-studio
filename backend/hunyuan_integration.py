"""
Hunyuan3D Integration Module
Connects ORFEAS Backend with Hunyuan3D-2.1 engine for real 3D model generation

This file was repaired to resolve indentation and mojibake issues while preserving
the public API expected by the backend. The implementation prioritizes safe
fallback to a lightweight processor when full Hunyuan3D dependencies are absent.
"""

from __future__ import annotations

import os
import sys
import logging
from pathlib import Path
from typing import Any, Dict, Union

# CRITICAL: Disable xformers before any potential torch import (Windows DLL crash prevention)
os.environ.setdefault("XFORMERS_DISABLED", "1")
os.environ.setdefault("DISABLE_XFORMERS", "1")
os.environ.setdefault("XFORMERS_MORE_DETAILS", "0")

# Optional torch import (graceful if unavailable during tests/CI)
try:
    import torch  # type: ignore
    try:
        import torch._dynamo  # type: ignore
        torch._dynamo.config.suppress_errors = True  # suppress compile errors
    except Exception:
        pass
    TORCH_AVAILABLE = True
except Exception:
    torch = None  # type: ignore
    TORCH_AVAILABLE = False

import numpy as np  # type: ignore
from PIL import Image  # type: ignore

logger = logging.getLogger(__name__)

# Attempt to add Hunyuan3D repository to path if present
HUNYUAN_PATH = Path(__file__).parent.parent / "Hunyuan3D-2.1" / "Hunyuan3D-2"
if HUNYUAN_PATH.exists():
    sys.path.append(str(HUNYUAN_PATH))
    sys.path.append(str(HUNYUAN_PATH / "hy3dgen"))


class Hunyuan3DProcessor:
    """
    Interface to Hunyuan3D-2.1 3D generation engine (safe wrapper)

    Notes:
    - Uses a singleton-like cache to avoid repeated heavy initialization
    - Gracefully degrades when model files are not present
    - Exposes the expected public methods used elsewhere in the backend
    """

    _model_cache: Dict[str, Any] = {
        "initialized": False,
        "device": None,
        "shapegen_pipeline": None,
        "texgen_pipeline": None,
        "rembg": None,
        "text2image_pipeline": None,
    }

    def __init__(self, device: Union[str, None] = None) -> None:
        self.device = device or ("cuda" if TORCH_AVAILABLE and getattr(torch, "cuda", None) and torch.cuda.is_available() else "cpu")  # type: ignore[attr-defined]
        self.model_loaded = False
        self.has_text2image = False
        self.shapegen_pipeline = None
        self.texgen_pipeline = None
        self.rembg = None
        self.text2image_pipeline = None

        # Use cached instance if available for this device
        if Hunyuan3DProcessor._model_cache.get("initialized") and Hunyuan3DProcessor._model_cache.get("device") == self.device:
            self._load_from_cache()
            return

        # Defer model initialization to lazy loading on first request to avoid startup crash
        logger.info("[ORFEAS] Hunyuan3D: Deferring model load to first request (lazy loading to prevent crashes)")

    # ---- Internal helpers ----
    def _load_from_cache(self) -> None:
        self.rembg = Hunyuan3DProcessor._model_cache.get("rembg")
        self.shapegen_pipeline = Hunyuan3DProcessor._model_cache.get("shapegen_pipeline")
        self.texgen_pipeline = Hunyuan3DProcessor._model_cache.get("texgen_pipeline")
        self.text2image_pipeline = Hunyuan3DProcessor._model_cache.get("text2image_pipeline")
        self.has_text2image = self.text2image_pipeline is not None
        self.model_loaded = True
        logger.info("[ORFEAS] Hunyuan3D models loaded from cache")

    def _initialize_model(self) -> None:
        try:
            if not HUNYUAN_PATH.exists():
                logger.warning(f"Hunyuan3D path not found: {HUNYUAN_PATH}")
                self.model_loaded = False
                return

            # Lazy import of heavy modules; wrap in try so backend can still start
            try:
                from hy3dgen.rembg import BackgroundRemover  # type: ignore
                from hy3dgen.shapegen import Hunyuan3DDiTFlowMatchingPipeline  # type: ignore
                # Texture/text2image are optional; can be enabled later
            except Exception as e:
                logger.warning(f"Hunyuan3D modules not importable: {e}")
                self.model_loaded = False
                return

            # Initialize lightweight components first
            try:
                self.rembg = BackgroundRemover()
            except Exception:
                self.rembg = None

            # Initialize heavy shapegen pipeline
            try:
                # Load actual Hunyuan3D model for true volumetric 3D generation
                from hy3dgen.shapegen import Hunyuan3DDiTFlowMatchingPipeline  # type: ignore
                model_path = 'tencent/Hunyuan3D-2'
                logger.info(f"[ORFEAS] Loading Hunyuan3D shapegen model from {model_path}...")

                # Use safer loading options for Windows CUDA compatibility
                # Force fp32 to reduce memory requirements (from 4.59GB fp16 to ~9GB fp32, but load in chunks)
                try:
                    logger.info("[ORFEAS] Attempting to load Hunyuan3D with memory-optimized settings...")
                    # Try with device_map="auto" and smaller batch sizes for stability
                    self.shapegen_pipeline = Hunyuan3DDiTFlowMatchingPipeline.from_pretrained(
                        model_path,
                        torch_dtype=torch.float16,  # Keep fp16 to use less VRAM (4.59GB)
                        device_map="auto",  # Distribute across devices
                        low_cpu_mem_usage=True,  # Use sequential loading
                        max_memory={0: "20GB"},  # RTX 3090 has 24GB, leave headroom
                    )
                    logger.info("[ORFEAS] Model loaded successfully with device_map='auto'")
                except RuntimeError as e:
                    if "CUDA" in str(e) or "out of memory" in str(e).lower():
                        logger.warning(f"CUDA memory error: {e}, trying with explicit GPU placement...")
                        # Fallback: try loading directly to GPU with explicit memory management
                        torch.cuda.empty_cache()
                        self.shapegen_pipeline = Hunyuan3DDiTFlowMatchingPipeline.from_pretrained(
                            model_path,
                            torch_dtype=torch.float16,
                            device_map="cuda:0",
                            low_cpu_mem_usage=True,
                        )
                        logger.info("[ORFEAS] Model loaded to GPU after memory cleanup")
                    else:
                        raise
                except Exception as inner_e:
                    logger.warning(f"Model loading failed: {inner_e}, trying CPU-side loading...")
                    # Fallback: load to CPU first, then move to GPU
                    self.shapegen_pipeline = Hunyuan3DDiTFlowMatchingPipeline.from_pretrained(
                        model_path,
                        torch_dtype=torch.float32,
                        device_map="cpu",
                        low_cpu_mem_usage=True,
                    )
                    if self.device == "cuda":
                        logger.info("[ORFEAS] Moving model to CUDA after CPU-side loading...")
                        self.shapegen_pipeline = self.shapegen_pipeline.to("cuda", torch.float16)

                logger.info("[ORFEAS] Hunyuan3D shapegen model loaded successfully (FULL MODE)")
            except Exception as e:
                logger.error(f"Failed to initialize Hunyuan3D shapegen: {e}", exc_info=True)
                self.shapegen_pipeline = None
                self.model_loaded = False
                return

            # Cache references
            Hunyuan3DProcessor._model_cache.update(
                {
                    "initialized": True,
                    "device": self.device,
                    "rembg": self.rembg,
                    "shapegen_pipeline": self.shapegen_pipeline,
                    "texgen_pipeline": None,
                    "text2image_pipeline": None,
                }
            )

            self.has_text2image = False
            self.model_loaded = True
            logger.info("[ORFEAS] Hunyuan3D initialization completed (FULL AI MODE - volumetric 3D generation enabled)")
        except Exception as e:
            logger.error(f"Hunyuan3D initialization failed: {e}")
            self.model_loaded = False

    # [ORFEAS FIX 4] Add properties to expose 'model' and 'pipeline' attributes for test compatibility
    @property
    def model(self) -> Any:
        """Property to expose the model (for test compatibility)"""
        return self.shapegen_pipeline if self.model_loaded else None

    @property
    def pipeline(self) -> Any:
        """Property to expose the pipeline (for test compatibility)"""
        return self.shapegen_pipeline if self.model_loaded else None

    # ---- Public API (kept stable) ----
    def remove_background(self, image: Union[str, Path, Image.Image]) -> Image.Image:  # type: ignore[name-defined]
        try:
            img = Image.open(image) if isinstance(image, (str, Path)) else image
            if img.mode not in ("RGB", "RGBA"):
                img = img.convert("RGB")
            if getattr(self, "rembg", None) is None:
                return img.convert("RGBA")
            result = self.rembg.remove(img)  # type: ignore[attr-defined]
            return result.convert("RGBA") if result.mode != "RGBA" else result
        except Exception:
            # Safe fallback image
            return Image.new("RGBA", (512, 512))

    def text_to_image_generation(self, prompt: str, **kwargs: Any) -> bool:
        if not self.model_loaded or not self.has_text2image:
            logger.error("Hunyuan text-to-image model not available")
            return False
        # Placeholder return path; real implementation omitted in light mode
        return False

    def load_model_background_safe(self) -> bool:
        """Load model in background thread with error handling. Safe for long operations."""
        if self.model_loaded:
            return True

        if Hunyuan3DProcessor._model_cache.get("initialized"):
            self._load_from_cache()
            return self.model_loaded

        logger.info("[ORFEAS] Starting background model loading...")
        try:
            self._initialize_model()
            if self.model_loaded:
                logger.info("[SUCCESS] Hunyuan3D model loaded successfully")
                # Cache the model for future instances
                Hunyuan3DProcessor._model_cache.update({
                    "initialized": True,
                    "device": self.device,
                    "rembg": self.rembg,
                    "shapegen_pipeline": self.shapegen_pipeline,
                    "texgen_pipeline": self.texgen_pipeline,
                })
                return True
            else:
                logger.warning("[FAIL] Model initialization completed but model_loaded=False")
                return False
        except Exception as e:
            logger.error(f"[ERROR] Model loading failed: {e}", exc_info=True)
            return False

    def _lazy_load_model(self) -> bool:
        """Lazy load the model on first use. Returns True if successful.

        NOTE: With eager loading during startup, this should rarely be called.
        But if called, it will attempt to load the model.
        """
        if self.model_loaded:
            return True

        if Hunyuan3DProcessor._model_cache.get("initialized"):
            self._load_from_cache()
            return self.model_loaded

        # If we reach here, model wasn't loaded at startup - try to load now
        logger.warning("[ORFEAS] ⚠️  Model not loaded at startup, attempting emergency load...")
        try:
            self._initialize_model()
            if self.model_loaded:
                logger.info("[ORFEAS] ✅ Emergency load succeeded!")
                return True
            else:
                logger.error("[ORFEAS] ❌ Emergency load returned False")
                return False
        except Exception as e:
            logger.error(f"[ORFEAS] ❌ Emergency load failed: {e}")
            return False

    def _analyze_mesh(self, mesh: Any, label: str = "Mesh") -> None:
        """Log comprehensive mesh geometry information for debugging."""
        try:
            logger.info(f"[ORFEAS] 📊 Analyzing {label}:")
            logger.info(f"[ORFEAS]    Type: {type(mesh).__name__}")

            # Try to get vertex/face info
            if hasattr(mesh, 'vertices') and hasattr(mesh, 'faces'):
                v_count = len(mesh.vertices) if mesh.vertices is not None else 0
                f_count = len(mesh.faces) if mesh.faces is not None else 0
                logger.info(f"[ORFEAS]    Vertices: {v_count}")
                logger.info(f"[ORFEAS]    Faces/Triangles: {f_count}")

                if v_count > 0 and mesh.vertices is not None:
                    vertices = np.asarray(mesh.vertices)
                    bounds_min = np.min(vertices, axis=0)
                    bounds_max = np.max(vertices, axis=0)
                    logger.info(f"[ORFEAS]    Bounds: min={bounds_min.tolist()}, max={bounds_max.tolist()}")
                    logger.info(f"[ORFEAS]    Size: {(bounds_max - bounds_min).tolist()}")

            # Check other common attributes
            attrs = dir(mesh)
            if 'is_watertight' in attrs:
                try:
                    is_wt = mesh.is_watertight
                    logger.info(f"[ORFEAS]    Watertight: {is_wt}")
                except:
                    pass

            if 'volume' in attrs:
                try:
                    vol = mesh.volume
                    logger.info(f"[ORFEAS]    Volume: {vol}")
                except:
                    pass

            logger.info(f"[ORFEAS]    ✅ {label} analysis complete")
        except Exception as e:
            logger.warning(f"[ORFEAS] Could not analyze {label}: {e}")

    def image_to_3d_generation(self, image_path: Path, output_path: Path, **kwargs: Any):
        """Generate true volumetric 3D model from image using Hunyuan3D AI."""
        # Check if model is loaded; if not, this is a critical error
        if not self.model_loaded:
            logger.error(f"[ORFEAS] ❌ CRITICAL: Model not loaded at generation time!")
            logger.error(f"[ORFEAS]    model_loaded={self.model_loaded}")
            logger.error(f"[ORFEAS]    shapegen_pipeline={self.shapegen_pipeline is not None}")
            logger.error(f"[ORFEAS] This should have been loaded during backend startup!")
            logger.error(f"[ORFEAS] Generation cannot proceed without the model.")
            return False

        try:
            from PIL import Image

            # Load and prepare image
            logger.info(f"[ORFEAS] 📸 Loading image: {image_path}")
            image = Image.open(image_path)
            logger.info(f"[ORFEAS]    Original size: {image.size}, mode: {image.mode}")

            # Convert to RGB first (required by rembg and Hunyuan3D)
            if image.mode != 'RGB':
                image = image.convert("RGB")
                logger.info("[ORFEAS]    ✓ Converted to RGB mode")

            # Remove background if needed (BEFORE other conversions)
            if self.rembg is not None:
                logger.info("[ORFEAS] 🎨 Removing background with rembg...")
                image = self.rembg(image)
                logger.info(f"[ORFEAS]    ✓ Background removed, new mode: {image.mode}")
            else:
                logger.info("[ORFEAS] ⚠️  rembg not available, skipping background removal")

            # Convert to RGBA for Hunyuan3D pipeline (ensures proper alpha channel handling)
            if image.mode != 'RGBA':
                image = image.convert("RGBA")
                logger.info("[ORFEAS]    ✓ Converted to RGBA mode for pipeline")

            logger.info(f"[ORFEAS]    Final image: {image.size}, mode: {image.mode}")

            # Generate volumetric 3D mesh using Hunyuan3D AI
            logger.info("[ORFEAS] 🚀 Calling Hunyuan3D shapegen_pipeline...")
            logger.info(f"[ORFEAS]    Pipeline type: {type(self.shapegen_pipeline).__name__}")

            result = self.shapegen_pipeline(image=image)
            logger.info(f"[ORFEAS] 📦 Pipeline returned: {type(result).__name__}")

            if result is None:
                raise Exception("Pipeline returned None")

            if not isinstance(result, (list, tuple)) or len(result) == 0:
                raise Exception(f"Pipeline returned invalid result: {type(result).__name__}, expected list/tuple with mesh")

            mesh = result[0]
            logger.info(f"[ORFEAS]    Extracted mesh object: {type(mesh).__name__}")

            # Analyze mesh before validation
            self._analyze_mesh(mesh, "Generated mesh from pipeline")

            # Validate mesh object
            if mesh is None:
                raise Exception("Mesh extraction from pipeline returned None")

            if not hasattr(mesh, 'export'):
                raise Exception(f"Mesh object has no export method. Type: {type(mesh).__name__}, attributes: {dir(mesh)[:5]}")

            # Export mesh - ensure proper file extension
            output_path = Path(output_path)
            if output_path.suffix.lower() not in ['.stl', '.obj', '.gltf', '.glb', '.ply']:
                output_path = output_path.with_suffix('.stl')

            logger.info(f"[ORFEAS] 💾 Exporting 3D model to: {output_path}")
            try:
                mesh.export(str(output_path))
                logger.info(f"[ORFEAS]    ✓ mesh.export() completed successfully")
            except Exception as export_err:
                logger.error(f"[ORFEAS] ❌ mesh.export() FAILED: {type(export_err).__name__}: {export_err}")
                raise Exception(f"mesh.export() failed: {export_err}") from export_err

            # [CRITICAL FIX] Validate file after export to catch silent failures
            import struct
            import os

            # 1. Check file exists and has content
            if not output_path.exists():
                raise Exception(f"STL export failed - file not created at {output_path}")

            file_size = output_path.stat().st_size
            if file_size == 0:
                raise Exception("STL export failed - file is empty (0 bytes)")

            logger.info(f"[ORFEAS]    File exported: {file_size} bytes")

            # 2. Validate STL format (binary format expected)
            if str(output_path).lower().endswith('.stl'):
                try:
                    with open(output_path, 'rb') as f:
                        # Read header (80 bytes)
                        header = f.read(80)
                        if len(header) < 80:
                            raise Exception(f"STL header incomplete: {len(header)} bytes (expected 80)")

                        # Read triangle count (4 bytes, little-endian uint32)
                        triangle_count_bytes = f.read(4)
                        if len(triangle_count_bytes) < 4:
                            raise Exception("STL triangle count incomplete")

                        triangle_count = struct.unpack('<I', triangle_count_bytes)[0]
                        logger.info(f"[ORFEAS] 📊 STL Format Validation:")
                        logger.info(f"[ORFEAS]    Triangles: {triangle_count}")
                        logger.info(f"[ORFEAS]    File size: {file_size} bytes")

                        # Sanity check: reasonable triangle count
                        if triangle_count == 0:
                            raise Exception("STL file contains 0 triangles (invalid)")
                        if triangle_count > 10000000:  # 10 million triangles = sanity limit
                            raise Exception(f"STL contains excessive triangles: {triangle_count} (likely corrupted)")

                        # 3. Verify file size matches STL format
                        # STL binary: 80-byte header + 4-byte count + (50 bytes per triangle)
                        expected_size = 80 + 4 + (triangle_count * 50)
                        if file_size != expected_size:
                            logger.warning(f"[ORFEAS] File size mismatch - expected {expected_size}, got {file_size}")
                            # Don't fail here as some STL writers may add padding or metadata
                            # but log warning for debugging

                        # 4. Try to read first triangle to validate data integrity
                        first_triangle = f.read(50)
                        if len(first_triangle) < 50:
                            raise Exception("First triangle incomplete - file may be corrupted")

                        logger.info(f"[ORFEAS]    ✓ STL format validation passed")

                except struct.error as e:
                    raise Exception(f"STL format validation failed: {e}")

            # 5. Force disk flush to ensure data is written
            try:
                import sys
                if sys.platform.startswith('win'):
                    # Windows: flush file buffers
                    import ctypes
                    try:
                        handle = ctypes.windll.kernel32.CreateFileW(
                            str(output_path), 0xC0000000, 0, None, 3, 0x80, None
                        )
                        if handle != -1:
                            ctypes.windll.kernel32.FlushFileBuffers(handle)
                            ctypes.windll.kernel32.CloseHandle(handle)
                            logger.info("[ORFEAS] File buffers flushed (Windows)")
                    except Exception as flush_err:
                        logger.warning(f"[ORFEAS] Could not flush file buffers: {flush_err}")
                else:
                    # Linux/Mac: use os.sync()
                    try:
                        os.sync()
                        logger.info("[ORFEAS] File buffers flushed (Unix)")
                    except Exception:
                        pass  # os.sync() not always available
            except Exception as e:
                logger.warning(f"[ORFEAS] File flush warning (non-critical): {e}")

            logger.info(f"[ORFEAS] Successfully generated volumetric 3D model: {output_path}")
            return True

        except Exception as e:
            logger.error(f"[ORFEAS] ❌ Hunyuan3D generation EXCEPTION: {type(e).__name__}: {e}")
            import traceback
            logger.error("Full traceback:")
            logger.error(traceback.format_exc())
            logger.error(f"[ORFEAS] Generation failed for output_path: {output_path if 'output_path' in locals() else 'UNKNOWN'}")
            return False

    def generate_3d(self, image_path: Union[str, Path], output_path: Union[str, Path], **kwargs: Any) -> Union[Dict[str, Any], bool]:
        """
        Generate 3D model from image.

        Args:
            image_path: Path to input image
            output_path: Path for output 3D model
            **kwargs: Additional parameters (quality, format, etc.)

        Returns:
            Success status (bool) or dict with generation details
        """
        try:
            image_path = Path(image_path)
            output_path = Path(output_path)

            if not image_path.exists():
                logger.error(f"Input image not found: {image_path}")
                return False

            # Use the existing generation method
            success = self.image_to_3d_generation(image_path, output_path, **kwargs)

            if success:
                return {
                    "success": True,
                    "output_path": str(output_path),
                    "format": output_path.suffix.lstrip("."),
                    "device": str(self.device),
                    "model_type": "Hunyuan3D",
                    "file_size": output_path.stat().st_size if output_path.exists() else 0
                }
            else:
                logger.warning("3D generation returned False")
                return False

        except Exception as e:
            logger.error(f"Error in generate_3d: {e}")
            return False

    def is_available(self) -> bool:
        return bool(self.model_loaded)

    def get_model_info(self) -> Dict[str, Any]:
        if not self.model_loaded:
            return {"status": "not_loaded", "error": "Hunyuan3D model not available"}
        capabilities = ["image_to_3d"]
        if self.has_text2image:
            capabilities.append("text_to_image")
        return {
            "status": "loaded",
            "device": str(self.device),
            "model_type": "Hunyuan3D-2.1",
            "model_path": str(HUNYUAN_PATH),
            "capabilities": capabilities,
            "formats": ["glb", "gltf", "obj", "stl"],
            "has_text2image": self.has_text2image,
        }


class FallbackProcessor:
    """
    Fallback 3D processor when Hunyuan3D is not available.
    Generates simple OBJ geometry for testing/development.
    """

    def __init__(self, device: Union[str, None] = None) -> None:
        self.device = device or "cpu"
        logger.info("Using fallback 3D processor")

    def text_to_3d_generation(self, prompt: str, output_path: Path, **kwargs: Any) -> bool:
        # Map prompts to simple shapes; default to cube
        shapes = {
            "cube": self.create_cube,
            "sphere": self.create_cube,
            "cylinder": self.create_cube,
            "pyramid": self.create_cube,
        }
        prompt_lower = (prompt or "").lower()
        for name, fn in shapes.items():
            if name in prompt_lower:
                return fn(output_path, **kwargs)
        return self.create_cube(output_path, **kwargs)

    def image_to_3d_generation(self, image_path: Path, output_path: Path, **kwargs: Any) -> bool:
        # Ignore image; generate a cube placeholder
        return self.create_cube(output_path, **kwargs)

    def generate_3d(self, image_path: Union[str, Path], output_path: Union[str, Path], **kwargs: Any) -> Union[Dict[str, Any], bool]:
        """
        Generate 3D model from image (fallback implementation).

        Args:
            image_path: Path to input image (ignored in fallback)
            output_path: Path for output 3D model
            **kwargs: Additional parameters

        Returns:
            Success status (bool) or dict with generation details
        """
        try:
            image_path = Path(image_path)
            output_path = Path(output_path)

            # Generate fallback cube
            success = self.create_cube(output_path, **kwargs)

            if success:
                return {
                    "success": True,
                    "output_path": str(output_path),
                    "format": output_path.suffix.lstrip("."),
                    "device": str(self.device),
                    "model_type": "Fallback",
                    "file_size": output_path.stat().st_size if output_path.exists() else 0,
                    "note": "Fallback processor - simplified geometry"
                }
            else:
                return False

        except Exception as e:
            logger.error(f"Error in fallback generate_3d: {e}")
            return False

    def _icosphere_vertices(self, subdivisions: int = 4) -> tuple:
        """Generate icosphere geometry (geodesic polyhedron).

        Creates a sphere-like polyhedron starting from a base icosahedron
        and recursively subdividing to desired level. Much better fallback
        than cube (12 vs ~1280 triangles at subdivision 4).

        Args:
            subdivisions: Level of subdivision (1=12 triangles, 4=1280 triangles)

        Returns:
            tuple: (vertices_array, faces_array) for STL/OBJ export
        """
        logger.info(f"[ORFEAS] Generating icosphere (subdivisions={subdivisions})...")

        # Golden ratio
        t = (1.0 + np.sqrt(5.0)) / 2.0

        # Base icosahedron vertices (12 points)
        vertices = np.array(
            [
                [-1, t, -1],
                [1, t, -1],
                [-1, t, 1],
                [1, t, 1],
                [-1, -t, -1],
                [1, -t, -1],
                [-1, -t, 1],
                [1, -t, 1],
                [-t, -1, 1],
                [t, -1, 1],
                [-t, 1, 1],
                [t, 1, 1],
                [-t, -1, -1],
                [t, -1, -1],
                [-t, 1, -1],
                [t, 1, -1],
            ],
            dtype=np.float32,
        )

        # Base icosahedron faces (20 triangles)
        faces = np.array(
            [
                [0, 11, 5],
                [0, 5, 1],
                [0, 1, 7],
                [0, 7, 10],
                [0, 10, 11],
                [1, 5, 13],
                [5, 11, 13],
                [11, 7, 13],
                [7, 1, 13],
                [1, 3, 7],
                [7, 3, 9],
                [3, 1, 15],
                [1, 5, 15],
                [5, 13, 15],
                [13, 9, 15],
                [9, 3, 15],
                [4, 8, 12],
                [8, 0, 12],
                [0, 4, 12],
                [4, 6, 8],
                [6, 10, 8],
                [10, 0, 8],
                [12, 2, 4],
                [4, 2, 6],
                [6, 2, 10],
                [2, 14, 10],
                [10, 14, 11],
                [11, 14, 5],
                [5, 14, 13],
                [13, 14, 9],
                [9, 14, 3],
                [3, 14, 15],
                [15, 14, 5],
                [14, 2, 11],
                [2, 8, 10],
                [8, 6, 4],
                [12, 8, 2],
            ],
            dtype=np.int32,
        )

        # Subdivide recursively
        for sub_level in range(subdivisions):
            logger.info(f"[ORFEAS]    Subdivision level {sub_level + 1}/{subdivisions}...")
            faces_list = faces.tolist()
            new_faces = []
            midpoint_cache = {}

            def midpoint(v1_idx: int, v2_idx: int) -> int:
                """Get or create midpoint vertex between two vertices."""
                nonlocal vertices
                key = tuple(sorted([v1_idx, v2_idx]))
                if key not in midpoint_cache:
                    v1 = vertices[v1_idx]
                    v2 = vertices[v2_idx]
                    midpoint_vertex = (v1 + v2) / 2.0
                    # Normalize to sphere surface
                    midpoint_vertex = midpoint_vertex / np.linalg.norm(midpoint_vertex)
                    midpoint_cache[key] = len(vertices)
                    vertices = np.vstack([vertices, midpoint_vertex])
                return midpoint_cache[key]

            # Subdivide each triangle
            for face in faces_list:
                v1, v2, v3 = face
                a = midpoint(v1, v2)
                b = midpoint(v2, v3)
                c = midpoint(v3, v1)
                new_faces.extend(
                    [[v1, a, c], [v2, b, a], [v3, c, b], [a, b, c]]
                )

            faces = np.array(new_faces, dtype=np.int32)

        logger.info(
            f"[ORFEAS]    ✅ Icosphere generated: {len(vertices)} vertices, "
            f"{len(faces)} triangles"
        )
        return vertices, faces

    def create_icosphere(self, output_path: Path, **kwargs: Any) -> bool:
        """Create icosphere fallback geometry (much better than cube)."""
        try:
            scale = float(kwargs.get("scale", 50.0))
            subdivisions = int(kwargs.get("subdivisions", 4))

            logger.info(f"[ORFEAS] Creating icosphere fallback (scale={scale}, subdivisions={subdivisions})...")
            vertices, faces = self._icosphere_vertices(subdivisions=subdivisions)

            # Scale vertices
            vertices = vertices * scale

            # Generate proper STL file with valid geometry
            output_format = str(output_path).lower()
            if output_format.endswith(".stl"):
                self.save_stl(vertices, faces, output_path)
            else:
                self.save_obj(vertices, faces, output_path.with_suffix(".obj"))

            logger.info(
                f"[ORFEAS] ✅ Icosphere fallback created: {output_path} "
                f"({len(vertices)} vertices, {len(faces)} triangles)"
            )
            return True
        except Exception as e:
            logger.error(f"[ORFEAS] ❌ Icosphere creation failed: {e}", exc_info=True)
            return False

    def create_cube(self, output_path: Path, **kwargs: Any) -> bool:
        try:
            size = float(kwargs.get("size", 10.0))
            vertices = np.array(
                [
                    [0, 0, 0],
                    [size, 0, 0],
                    [size, size, 0],
                    [0, size, 0],
                    [0, 0, size],
                    [size, 0, size],
                    [size, size, size],
                    [0, size, size],
                ],
                dtype=np.float32,
            )
            faces = np.array(
                [
                    [0, 1, 2],
                    [0, 2, 3],
                    [4, 7, 6],
                    [4, 6, 5],
                    [0, 4, 5],
                    [0, 5, 1],
                    [2, 6, 7],
                    [2, 7, 3],
                    [0, 3, 7],
                    [0, 7, 4],
                    [1, 5, 6],
                    [1, 6, 2],
                ]
            )
            # Generate proper STL file with valid geometry
            output_format = str(output_path).lower()
            if output_format.endswith('.stl'):
                self.save_stl(vertices, faces, output_path)
            else:
                self.save_obj(vertices, faces, output_path.with_suffix(".obj"))
            logger.info(f"Fallback 3D model created: {output_path}")
            return True
        except Exception as e:
            logger.error(f"Cube creation failed: {e}")
            return False

    def save_obj(self, vertices: np.ndarray, faces: np.ndarray, output_path: Path) -> None:  # type: ignore[name-defined]
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("# Generated by ORFEAS Backend\n")
            f.write("# Fallback 3D Model\n\n")
            for v in vertices:
                f.write(f"v {v[0]} {v[1]} {v[2]}\n")
            f.write("\n")
            for face in faces:
                # OBJ uses 1-based indices
                f.write(f"f {face[0] + 1} {face[1] + 1} {face[2] + 1}\n")

    def save_stl(self, vertices: np.ndarray, faces: np.ndarray, output_path: Path) -> None:  # type: ignore[name-defined]
        """Save model as binary STL file (valid 3D geometry)"""
        import struct
        try:
            with open(output_path, "wb") as f:
                # Write 80-byte header
                header = b"ORFEAS Generated STL - Fallback"
                header = header + b"\x00" * (80 - len(header))
                f.write(header[:80])

                # Write triangle count
                f.write(struct.pack("<I", len(faces)))

                # Write each triangle
                for face in faces:
                    v1, v2, v3 = vertices[face[0]], vertices[face[1]], vertices[face[2]]

                    # Calculate normal (cross product)
                    a = v2 - v1
                    b = v3 - v1
                    normal = np.cross(a, b)
                    norm_len = np.linalg.norm(normal)
                    if norm_len > 0:
                        normal = normal / norm_len

                    # Write normal
                    f.write(struct.pack("<fff", *normal))

                    # Write vertices
                    f.write(struct.pack("<fff", *v1))
                    f.write(struct.pack("<fff", *v2))
                    f.write(struct.pack("<fff", *v3))

                    # Write attribute count (unused)
                    f.write(struct.pack("<H", 0))

            logger.info(f"STL file created: {output_path} ({len(faces)} triangles)")
        except Exception as e:
            logger.error(f"Failed to save STL: {e}")

    def is_available(self) -> bool:
        return True

    def get_model_info(self) -> Dict[str, Any]:
        return {
            "status": "loaded",
            "device": str(self.device),
            "model_type": "Fallback Processor",
            "capabilities": ["simple_shapes", "basic_3d"],
            "formats": ["obj"],
        }


def get_3d_processor(device: Union[str, None] = None):
    """
    Factory function to get appropriate 3D processor.

    Returns Hunyuan3D processor with lazy loading enabled.
    Model will load on first request to avoid startup crashes.
    """
    processor = Hunyuan3DProcessor(device)
    logger.info("[ORFEAS] Hunyuan3D processor created - lazy loading enabled for first request")
    return processor

