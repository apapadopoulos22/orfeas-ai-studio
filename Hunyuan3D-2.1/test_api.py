#!/usr/bin/env python3
"""
THERION HUNYUAN3D TEST API SERVER
"""

from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import torch
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="THERION Hunyuan3D Test API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "THERION Hunyuan3D Test API Server",
        "status": "running",
        "cuda_available": torch.cuda.is_available(),
        "gpu_count": torch.cuda.device_count() if torch.cuda.is_available() else 0
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "cuda_available": torch.cuda.is_available(),
        "gpu_memory": torch.cuda.get_device_properties(0).total_memory / (1024**3) if torch.cuda.is_available() else 0,
        "pipelines_ready": False  # Will be True when real pipelines are loaded
    }

@app.post("/generate/complete")
async def generate_complete(
    image: UploadFile = File(...),
    prompt: str = Form(""),
    enable_texture: bool = Form(True)
):
    logger.info(f"Received generation request: {image.filename}, prompt: '{prompt}', texture: {enable_texture}")
    
    return {
        "status": "success",
        "output_id": "test-123",
        "mesh_path": "outputs/test_model.obj",
        "has_texture": enable_texture,
        "message": "Test response - real implementation coming soon!"
    }

@app.get("/download/{output_id}")
async def download_model(output_id: str):
    return {"error": "Download not implemented in test API"}

if __name__ == "__main__":
    print(" Starting THERION Hunyuan3D Test API Server...")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
