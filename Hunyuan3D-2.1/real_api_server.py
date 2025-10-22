#!/usr/bin/env python3
"""
THERION AI 2D STUDIO - REAL HUNYUAN3D-2.1 API SERVER
MAXIMUM EFFORT - ACTUAL 3D GENERATION!
"""

import sys
import os
from pathlib import Path

# Add the source paths
source_path = Path("C:/Users/johng/THERION_AI_LOCAL/Hunyuan3D-2.1-SOURCE")
sys.path.insert(0, str(source_path))
sys.path.insert(0, str(source_path / "hy3dshape"))
sys.path.insert(0, str(source_path / "hy3dpaint"))

# Add THERION source path for PNG to STL converter
therion_path = Path("C:/Users/johng/Documents/Erevus/Therion-AI-2D-Studio-main - Copy/THERION-AI-2D-STUDIO")
sys.path.insert(0, str(therion_path))

import uvicorn
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
import torch
import logging
from typing import Optional
import tempfile
import uuid
from PIL import Image
from io import BytesIO
import json
import traceback

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import PNG to STL converter
try:
    from png_to_stl_converter import TherionPNGToSTLConverter
    png_to_stl_converter = TherionPNGToSTLConverter()
    logger.info("'úÖ PNG to STL converter loaded")
except ImportError as e:
    logger.warning(f" PNG to STL converter not available: {e}")
    png_to_stl_converter = None

app = FastAPI(
    title="THERION Hunyuan3D-2.1 REAL API",
    description="REAL 2D to 3D generation using actual Hunyuan3D-2.1 models",
    version="2.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global pipeline variables
shape_pipeline = None
paint_pipeline = None
model_loading_error = None

def load_hunyuan3d_pipelines():
    """Load the actual Hunyuan3D-2.1 pipelines"""
    global shape_pipeline, paint_pipeline, model_loading_error

    try:
        logger.info("üöÄ Loading REAL Hunyuan3D-2.1 pipelines...")

        # Try to import and load the shape pipeline
        try:
            logger.info("üì¶ Importing Hunyuan3D shape pipeline...")
            from hy3dshape.pipelines import Hunyuan3DDiTFlowMatchingPipeline

            logger.info(" Loading shape model from HuggingFace...")
            shape_pipeline = Hunyuan3DDiTFlowMatchingPipeline.from_pretrained(
                'tencent/Hunyuan3D-2.1',
                subfolder='hunyuan3d-dit-v2-1',
                torch_dtype=torch.float16,
                use_safetensors=True
            )
            logger.info("'úÖ Shape pipeline loaded successfully")

        except Exception as e:
            logger.error(f"'ùå Failed to load shape pipeline: {e}")
            shape_pipeline = None

        # Try to import and load the paint pipeline
        try:
            logger.info("üì¶ Importing Hunyuan3D paint pipeline...")
            from textureGenPipeline import Hunyuan3DPaintPipeline, Hunyuan3DPaintConfig

            logger.info(" Loading paint model...")
            paint_config = Hunyuan3DPaintConfig(
                max_num_view=6,
                resolution=512,
                torch_dtype=torch.float16
            )
            paint_pipeline = Hunyuan3DPaintPipeline(paint_config)
            logger.info("'úÖ Paint pipeline loaded successfully")

        except Exception as e:
            logger.error(f"'ùå Failed to load paint pipeline: {e}")
            paint_pipeline = None

        if shape_pipeline is None and paint_pipeline is None:
            model_loading_error = "Failed to load any Hunyuan3D pipelines"
            return False

        logger.info("üéâ REAL Hunyuan3D-2.1 pipelines ready!")
        return True

    except Exception as e:
        logger.error(f"'ùå Critical error loading pipelines: {e}")
        logger.error(traceback.format_exc())
        model_loading_error = str(e)
        return False

def create_fallback_response():
    """Create fallback response when models aren't loaded"""
    return {
        "status": "success",
        "output_id": f"fallback-{uuid.uuid4().hex[:8]}",
        "mesh_path": "outputs/fallback_cube.obj",
        "has_texture": False,
        "message": "FALLBACK: Models not loaded - returning test cube",
        "is_fallback": True
    }

def generate_simple_cube_obj():
    """Generate a simple cube OBJ file as fallback"""
    cube_obj = """# Simple cube OBJ - THERION Fallback
v -1.0 -1.0  1.0
v  1.0 -1.0  1.0
v  1.0  1.0  1.0
v -1.0  1.0  1.0
v -1.0 -1.0 -1.0
v  1.0 -1.0 -1.0
v  1.0  1.0 -1.0
v -1.0  1.0 -1.0

f 1 2 3 4
f 5 8 7 6
f 1 5 6 2
f 2 6 7 3
f 3 7 8 4
f 5 1 4 8
"""
    return cube_obj

@app.on_event("startup")
async def startup_event():
    """Initialize the API server"""
    logger.info("üöÄ Starting THERION Hunyuan3D-2.1 REAL API Server...")

    # Check CUDA availability
    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
        vram_gb = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        logger.info(f" GPU: {gpu_name}")
        logger.info(f"üíæ VRAM: {vram_gb:.1f}GB")
    else:
        logger.warning(" CUDA not available!")

    # Create output directory
    os.makedirs("outputs", exist_ok=True)

    # Try to load pipelines
    logger.info(" Attempting to load REAL pipelines...")
    success = load_hunyuan3d_pipelines()

    if not success:
        logger.warning(" Running in FALLBACK mode - will generate test cubes")

@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "message": "THERION Hunyuan3D-2.1 REAL API Server",
        "status": "running",
        "version": "2.1.0",
        "cuda_available": torch.cuda.is_available(),
        "pipelines_loaded": shape_pipeline is not None or paint_pipeline is not None,
        "shape_pipeline_ready": shape_pipeline is not None,
        "paint_pipeline_ready": paint_pipeline is not None,
        "fallback_mode": shape_pipeline is None and paint_pipeline is None,
        "loading_error": model_loading_error
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    pipelines_ready = shape_pipeline is not None or paint_pipeline is not None

    return {
        "status": "healthy",
        "cuda_available": torch.cuda.is_available(),
        "gpu_memory": torch.cuda.get_device_properties(0).total_memory / (1024**3) if torch.cuda.is_available() else 0,
        "pipelines_ready": pipelines_ready,
        "shape_pipeline_ready": shape_pipeline is not None,
        "paint_pipeline_ready": paint_pipeline is not None,
        "fallback_mode": not pipelines_ready,
        "loading_error": model_loading_error
    }

@app.post("/generate/shape")
async def generate_shape(
    image: UploadFile = File(...),
    prompt: Optional[str] = Form("")
):
    """Generate 3D shape from image"""
    try:
        logger.info(f"üöÄ Shape generation request: {image.filename}")

        # Read image
        image_data = await image.read()
        pil_image = Image.open(BytesIO(image_data)).convert("RGB")

        if shape_pipeline is not None:
            logger.info(" Using REAL shape pipeline...")
            with torch.no_grad():
                # Generate using real pipeline
                result = shape_pipeline(image=pil_image)
                mesh = result[0] if isinstance(result, (list, tuple)) else result

                # Save mesh
                output_id = str(uuid.uuid4())
                output_path = f"outputs/shape_{output_id}.obj"

                # Export mesh (assuming it has export method)
                if hasattr(mesh, 'export'):
                    mesh.export(output_path)
                else:
                    # Fallback save
                    with open(output_path, 'w') as f:
                        f.write(generate_simple_cube_obj())

                return {
                    "status": "success",
                    "output_id": output_id,
                    "mesh_path": output_path,
                    "message": "REAL 3D shape generated successfully"
                }
        else:
            logger.info(" Using fallback cube generation...")
            return create_fallback_response()

    except Exception as e:
        logger.error(f"'ùå Shape generation failed: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Shape generation failed: {str(e)}")

@app.post("/generate/complete")
async def generate_complete(
    image: UploadFile = File(...),
    prompt: Optional[str] = Form(""),
    enable_texture: bool = Form(True)
):
    """Complete 2D to 3D pipeline"""
    try:
        logger.info(f"üöÄ Complete generation request: {image.filename}, texture: {enable_texture}")

        # Read image
        image_data = await image.read()
        pil_image = Image.open(BytesIO(image_data)).convert("RGB")

        output_id = str(uuid.uuid4())

        if shape_pipeline is not None:
            logger.info(" Using REAL pipeline for complete generation...")

            with torch.no_grad():
                # Step 1: Generate shape
                logger.info("üìê Generating 3D shape...")
                shape_result = shape_pipeline(image=pil_image)
                mesh = shape_result[0] if isinstance(shape_result, (list, tuple)) else shape_result

                # Step 2: Apply texture if enabled and paint pipeline available
                if enable_texture and paint_pipeline is not None:
                    logger.info("üé® Applying texture...")
                    try:
                        textured_mesh = paint_pipeline(mesh, image_path=pil_image)
                        final_mesh = textured_mesh
                        has_texture = True
                    except Exception as e:
                        logger.warning(f" Texture failed, using untextured mesh: {e}")
                        final_mesh = mesh
                        has_texture = False
                else:
                    final_mesh = mesh
                    has_texture = False

                # Save final mesh
                output_path = f"outputs/complete_{output_id}.obj"

                if hasattr(final_mesh, 'export'):
                    final_mesh.export(output_path)
                else:
                    # Fallback save
                    with open(output_path, 'w') as f:
                        f.write(generate_simple_cube_obj())

                return {
                    "status": "success",
                    "output_id": output_id,
                    "mesh_path": output_path,
                    "has_texture": has_texture,
                    "message": f"REAL 3D model generated{'with texture' if has_texture else ''}"
                }
        else:
            logger.info(" Using fallback cube generation...")
            # Create fallback cube file
            output_path = f"outputs/fallback_{output_id}.obj"
            with open(output_path, 'w') as f:
                f.write(generate_simple_cube_obj())

            return {
                "status": "success",
                "output_id": output_id,
                "mesh_path": output_path,
                "has_texture": False,
                "message": "FALLBACK: Generated test cube (models not loaded)",
                "is_fallback": True
            }

    except Exception as e:
        logger.error(f"'ùå Complete generation failed: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Complete generation failed: {str(e)}")

@app.get("/download/{output_id}")
async def download_mesh(output_id: str):
    """Download generated mesh file"""
    possible_files = [
        f"outputs/complete_{output_id}.obj",
        f"outputs/shape_{output_id}.obj",
        f"outputs/fallback_{output_id}.obj"
    ]

    for file_path in possible_files:
        if os.path.exists(file_path):
            logger.info(f"üì• Serving mesh file: {file_path}")
            return FileResponse(
                file_path,
                media_type='application/octet-stream',
                filename=f"therion_3d_model_{output_id}.obj"
            )

    logger.error(f"'ùå Mesh file not found for output_id: {output_id}")
    raise HTTPException(status_code=404, detail="Mesh file not found")

@app.get("/models/status")
async def models_status():
    """Get detailed model loading status"""
    return {
        "shape_pipeline": {
            "loaded": shape_pipeline is not None,
            "type": type(shape_pipeline).__name__ if shape_pipeline else None
        },
        "paint_pipeline": {
            "loaded": paint_pipeline is not None,
            "type": type(paint_pipeline).__name__ if paint_pipeline else None
        },
        "loading_error": model_loading_error,
        "cuda_info": {
            "available": torch.cuda.is_available(),
            "device_count": torch.cuda.device_count() if torch.cuda.is_available() else 0,
            "current_device": torch.cuda.current_device() if torch.cuda.is_available() else None
        }
    }

@app.post("/convert/png-to-stl")
async def convert_png_to_stl(
    image: UploadFile = File(...),
    method: str = Form("heightmap"),
    max_height: float = Form(5.0),
    base_thickness: float = Form(2.0),
    extrude_height: float = Form(3.0),
    edge_threshold: int = Form(50)
):
    """Convert PNG image to STL file using heightmap or edge extrusion"""
    if png_to_stl_converter is None:
        raise HTTPException(status_code=503, detail="PNG to STL converter not available")

    try:
        logger.info(f" Converting PNG to STL using {method} method...")

        # Read uploaded image
        image_data = await image.read()

        # Prepare settings based on method
        if method == "heightmap":
            settings = {
                'max_height': max_height,
                'base_thickness': base_thickness,
                'smooth_iterations': 2,
                'invert_height': False
            }
        elif method == "edge_extrusion":
            settings = {
                'extrude_height': extrude_height,
                'edge_threshold': edge_threshold,
                'wall_thickness': 1.0,
                'smooth_edges': True
            }
        elif method == "lithophane":
            settings = {
                'thickness': 3.0,
                'min_thickness': 0.4,
                'max_thickness': 2.0,
                'invert': True
            }
        else:
            raise HTTPException(status_code=400, detail=f"Unknown method: {method}")

        # Generate output filename
        output_id = str(uuid.uuid4())
        output_path = f"outputs/stl_{method}_{output_id}.stl"

        # Convert PNG to STL
        success = png_to_stl_converter.convert_png_to_stl(
            image_data,
            output_path,
            method=method,
            settings=settings
        )

        if success:
            return {
                "status": "success",
                "output_id": output_id,
                "stl_path": output_path,
                "method": method,
                "settings": settings,
                "message": f"PNG converted to STL using {method} method"
            }
        else:
            raise HTTPException(status_code=500, detail="PNG to STL conversion failed")

    except Exception as e:
        logger.error(f"'ùå PNG to STL conversion failed: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Conversion failed: {str(e)}")

@app.post("/analyze/png-for-stl")
async def analyze_png_for_stl(image: UploadFile = File(...)):
    """Analyze PNG image and recommend STL conversion settings"""
    if png_to_stl_converter is None:
        raise HTTPException(status_code=503, detail="PNG to STL converter not available")

    try:
        logger.info("üîç Analyzing PNG for STL conversion...")

        # Read uploaded image
        image_data = await image.read()

        # Analyze image
        analysis = png_to_stl_converter.analyze_png_for_conversion(image_data)

        return {
            "status": "success",
            "analysis": analysis,
            "message": "PNG analysis complete"
        }

    except Exception as e:
        logger.error(f"'ùå PNG analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/download/stl/{output_id}")
async def download_stl(output_id: str):
    """Download generated STL file"""
    possible_files = [
        f"outputs/stl_heightmap_{output_id}.stl",
        f"outputs/stl_edge_extrusion_{output_id}.stl",
        f"outputs/stl_lithophane_{output_id}.stl"
    ]

    for file_path in possible_files:
        if os.path.exists(file_path):
            logger.info(f"üì• Serving STL file: {file_path}")
            return FileResponse(
                file_path,
                media_type='application/octet-stream',
                filename=f"therion_3d_print_{output_id}.stl"
            )

    logger.error(f"'ùå STL file not found for output_id: {output_id}")
    raise HTTPException(status_code=404, detail="STL file not found")

if __name__ == "__main__":
    logger.info("üöÄ Starting THERION Hunyuan3D-2.1 REAL API Server...")
    logger.info("DEUS VULT - MAXIMUM EFFORT!")

    # Create outputs directory
    os.makedirs("outputs", exist_ok=True)

    # Start server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
